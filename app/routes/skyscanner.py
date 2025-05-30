import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import SessionLocal
from ..models import User, UserGroupAssociation, Group, City
from ..schemas import FlightSearchRequest, AutoSuggestRequest, CityRequest, GroupInput
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from .recomanador import recomanar

router = APIRouter(prefix="/skyscanner", tags=["skyscanner"])

df = pd.read_csv("iata_airports_and_locations_with_vibes.csv")

geolocator = Nominatim(user_agent="iata-airports-app")
reverse = RateLimiter(geolocator.reverse, min_delay_seconds=1)
# Should be in a .env file
# but for now, hardcoded
API_KEY = "sh969210162413250384813708759185"
BASE_URL = "https://partners.api.skyscanner.net/apiservices/v3/flights/live/search/create"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Try to get just the top three results
# from the API
'''
@router.post("/search-flights")
async def search_flights(request: FlightSearchRequest, db: Session = Depends(get_db)):
    payload = {
        "query": {
            "market": request.market,
            "locale": request.locale,
            "currency": request.currency,
            "query_legs": [
                {
                    "origin_place_id": {"iata": request.origin_iata},
                    "destination_place_id": {"iata": request.destination_iata},
                    "date": {
                        "year": request.year,
                        "month": request.month,
                        "day": request.day
                    }
                }
            ],
            "adults": request.adults,
            "cabin_class": request.cabin_class
        },
        # Ask this to the mentors because doesn't work
        "limit": 1
    }

    headers = {
        "x-api-key": API_KEY
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(BASE_URL, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=response.status_code, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# I dont understand the difference between both endpoints
@router.post("/autosuggest-flights")
async def autosuggest_flights(request: AutoSuggestRequest):
    payload = {
        "query": {
            "market": request.market,
            "locale": request.locale,
            "searchTerm": request.searchTerm,
            "includedEntityTypes": request.includedEntityTypes
        },
        "limit": request.limit,
        "isDestination": request.isDestination
    }

    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(BASE_URL, json=payload, headers=headers)
            response.raise_for_status()

            return response.json()

        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=response.status_code, detail=f"HTTP error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
'''  
@router.post("/cheapest-flights")
async def search_flights(request: FlightSearchRequest):
    db = SessionLocal()
    try:
        input_data = request
        ciutat = recomanar(input=input_data, db=db)
        if not ciutat:
            raise HTTPException(status_code=404, detail="No hi ha cap ciutat recomanada")
        #Obtenir usuari pel correu
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuari no trobat")
        #Obtenir associació per obtenir l’origen
        associacio = db.query(UserGroupAssociation).filter(
            UserGroupAssociation.user_id == user.id,
            UserGroupAssociation.group_id == request.group_id
        ).first()
        # Comprovem si hi ha un aeroport assignat a la ciutat
        if not associacio:
            raise HTTPException(status_code=404, detail="Associació usuari-grup no trobada")

        # Obtenir dates del grup
        group = db.query(Group).filter(Group.id == request.group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Grup no trobat")
        # 5. Fer servir les dates del grup
        data_sortida = group.data_ini
        data_arribada = group.data_fi
        origin =  db.query(City).filter(City.name == associacio.origen).first()
        
        origin_iata = origin.airport
        destination =  db.query(City).filter(City.name == ciutat['ciutat']).first()
        destination_iata = destination.airport

        payload = {
            "query": {
                "market": "UK",
                "locale": "en-GB",
                "currency": "EUR",
                "query_legs": [
                    {
                        "origin_place_id": {"iata": origin_iata },
                        "destination_place_id": {"iata": destination_iata},
                        "date": {
                            "year": data_sortida.year,
                            "month": data_sortida.month,
                            "day": data_sortida.day
                        }
                    }
                ],
                "adults": 1,
                "cabin_class": "CABIN_CLASS_ECONOMY"
            }
        }

        headers = {
            "x-api-key": API_KEY
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(BASE_URL, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                #print(data)
                # Procesar resultados
                itineraries = data["content"]["results"]["itineraries"]
                legs = data["content"]["results"]["legs"]
                flights = []
                for itinerary_id, itinerary in itineraries.items():
                    for option in itinerary.get("pricingOptions", []):
                        price_milli = int(option["price"]["amount"])
                        price = price_milli / 1000
                        deep_link = option["items"][0]["deepLink"]

                        leg_id = itinerary["legIds"][0]
                        leg = legs[leg_id]

                        # Agafar el primer carrier
                        carrier_id = leg["operatingCarrierIds"][0]
                        company_name = data["content"]["results"]["carriers"][carrier_id]["name"]
                        dt_data_d = leg["departureDateTime"]
                        dt_data_a = leg["arrivalDateTime"]
                        
                        dte_d = datetime(
                            year=dt_data_d["year"],
                            month=dt_data_d["month"],
                            day=dt_data_d["day"],
                            hour=dt_data_d["hour"],
                            minute=dt_data_d["minute"],
                            second=dt_data_d["second"]
                        )
                        dte_a = datetime(
                            year=dt_data_a["year"],
                            month=dt_data_a["month"],
                            day=dt_data_a["day"],
                            hour=dt_data_a["hour"],
                            minute=dt_data_a["minute"],
                            second=dt_data_a["second"]
                        )

                        formatted_time_departure = dte_d.strftime("%I:%M %p")
                        formatted_time_arrival = dte_a.strftime("%I:%M %p")

                        flights.append({
                            "city": ciutat['ciutat'],
                            "image_path": f"/static/{ciutat['ciutat']}.jpg",
                            "id": itinerary_id,
                            "price": price,
                            "link": deep_link,
                            "departureDatetime": formatted_time_departure,
                            "arrivalDatetime": formatted_time_arrival,
                            "company": company_name,
                            "origin": data["content"]["results"]["places"][leg["originPlaceId"]]["iata"],
                            "destination": data["content"]["results"]["places"][leg["destinationPlaceId"]]["iata"],
                            "stops": leg["stopCount"]
                        })

                # Ordenar y devolver los 3 más baratos
                cheapest = sorted(flights, key=lambda x: x["price"])[:1]
                print(cheapest)
                return {"cheapest_flights": cheapest}

            except httpx.HTTPStatusError as e:
                raise HTTPException(status_code=response.status_code, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
   

def obtain_country(lat, lon):
    try:
        location = reverse((lat, lon), language='en')
        if location and "country" in location.raw["address"]:
            return location.raw["address"]["country"]
    except:
        pass
    return "Desconocido"

def obtain_airports_city(df, ciudad):
    resultados = df[df['en-GB'].str.contains(ciudad, case=False, na=False)][
        ['IATA', 'en-GB', 'latitude', 'longitude']
    ].copy()
    resultados["country"] = resultados.apply(
        lambda row: obtain_country(row["latitude"], row["longitude"]),
        axis=1
    )
    return resultados

@router.post("/airports")
def get_airports(request: CityRequest):
    result = obtain_airports_city(df, request.city)
    return result.to_dict(orient='records')



