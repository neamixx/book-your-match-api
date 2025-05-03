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
