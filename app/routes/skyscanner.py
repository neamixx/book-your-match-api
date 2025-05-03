import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..schemas import FlightSearchRequest, AutoSuggestRequest
from datetime import datetime
from ..database import SessionLocal
router = APIRouter(prefix="/skyscanner", tags=["skyscanner"])

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

            return {"cheapest_flights": cheapest}

        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=response.status_code, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))