from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..schemas import *
from ..database import SessionLocal
from ..models import City

router = APIRouter(prefix="/city", tags=["cities"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#Create a new city
@router.post("/create")
def create_city(city: CityCreate, db: Session = Depends(get_db)):
    existing_city = db.query(City).filter(City.name == city.name).first()
    if existing_city:
        raise HTTPException(status_code=400, detail="City already exists")
    
    new_city = City(
        name=city.name,
        country=city.country,
        airport=city.airport
    )
    
    db.add(new_city)
    db.commit()
    db.refresh(new_city)
    
    return new_city

# Set the airport for a specific city
@router.post("/set-airport")
def set_airport(airport: str, city: str, db: Session = Depends(get_db)):
    city_db = db.query(City).filter(City.name == city).first() 
    if city_db is None:
        raise HTTPException(status_code=404, detail="City not found")
    city_db.airport = airport
    db.commit()
    db.refresh(city_db)
    return city_db

# Get all cities
@router.get("/all")
def get_cities(db: Session = Depends(get_db)):
    cities = db.query(City).all()
    if not cities:
        raise HTTPException(status_code=404, detail="No cities found")
    return cities

# Get a specific city by name
@router.get("/{name}")
def get_city(name: str, db: Session = Depends(get_db)):
    city = db.query(City).filter(City.name == name).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    return city

@router.post("/{city_name}/embedding")
async def update_embedding(city_name: str, request: EmbeddingRequest, db: Session = Depends(get_db)):
    city = db.query(City).filter(City.name == city_name).first()
    
    if not city:
        raise HTTPException(status_code=404, detail="City not found")

    if city.embedding is None:
        city.embedding = request.embedding
    else:
        print(city.embedding)
        print(request.embedding)
        
        for request_item in request.embedding:
            city_items = city.embedding
            if request_item in city_items:
                print("Updating existing embedding")
                city_items[request_item] = request.embedding[request_item]
            else:
                print("Adding new embedding")
                city_items[request_item] = request.embedding[request_item]
        city.embedding = city_items
        print(city.embedding)
        db.query(City).filter(City.name == city_name).update({"embedding": city.embedding})
        db.commit()
        db.refresh(city)

    return {"message": f"Embedding updated for city {city_name}"}
