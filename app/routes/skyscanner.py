import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..schemas import FlightSearchRequest, AutoSuggestRequest, CityRequest
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

router = APIRouter(prefix="/skyscanner", tags=["skyscanner"])

df = pd.read_csv("iata_airports_and_locations_with_vibes.csv")

geolocator = Nominatim(user_agent="iata-airports-app")
reverse = RateLimiter(geolocator.reverse, min_delay_seconds=1)
# Should be in a .env file
# but for now, hardcoded
API_KEY = "sh969210162413250384813708759185"
BASE_URL = "https://partners.api.skyscanner.net/apiservices/v3/flights/live/search/create"


# Try to get just the top three results
# from the API
'''
@router.post("/search-flights")
async def search_flights(request: FlightSearchRequest):
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

            # Procesar resultados
            itineraries = data["content"]["results"]["itineraries"]
            flights = []

            for itinerary_id, itinerary in itineraries.items():
                for option in itinerary.get("pricingOptions", []):
                    price_milli = int(option["price"]["amount"])
                    price = price_milli / 1000
                    deep_link = option["items"][0]["deepLink"]
                    flights.append({
                        "id": itinerary_id,
                        "price": price,
                        "link": deep_link
                    })

            # Ordenar y devolver los 3 más baratos
            cheapest = sorted(flights, key=lambda x: x["price"])[:3]

            return {"cheapest_flights": cheapest}

        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=response.status_code, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

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



