import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..schemas import FlightSearchRequest, AutoSuggestRequest

router = APIRouter(prefix="/skyscanner", tags=["skyscanner"])

API_KEY = "sh969210162413250384813708759185"
BASE_URL = "https://partners.api.skyscanner.net/apiservices/v3/flights/live/search/create"


# Try to get just the top three results
# from the API
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