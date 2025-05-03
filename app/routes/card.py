from fastapi import APIRouter, File, UploadFile, Depends, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import HTTPException
from fastapi.responses import FileResponse


import random
import os
from os import listdir
from os.path import isfile, join
from pathlib import Path
from ..database import SessionLocal
from ..schemas import *
from ..models import Card

router = APIRouter(prefix="/card", tags=["cards"])

tittles = [
    "Playa",
    "Mojitos",
    "Ron",
    "Ski"
]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_random_image():
    image_path = os.path.abspath("./images")
    images = [ 
        f for f in listdir(image_path) if isfile(join(image_path, f))
    ]
    
    if len(images) < 1:
        return 'error'
    
    index = random.randrange(len(images) - 1)
    return images[index] 


@router.post("/create")
def create_card(
    name: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Comprovem si ja existeix una targeta amb el mateix nom
    existing_card = db.query(Card).filter(Card.image == file.filename).first()
    if existing_card:
        raise HTTPException(status_code=400, detail="Card already exists")

    # Guardem el fitxer a la carpeta local d’imatges
    image_path = os.path.abspath("./images")
    os.makedirs(image_path, exist_ok=True)  # Ens assegurem que la carpeta existeix
    file_location = f"{image_path}/{file.filename}"
    
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    # Creem la targeta a la base de dades
    db_card = Card(name=name, image=file.filename)
    db.add(db_card)
    db.commit()
    db.refresh(db_card)

    return db_card

# Define the GET endpoint for the /card route



# Define the POST endpoint for the /card route
@router.get("/card")
async def get_card():
    # Here you would typically process the card data (e.g., save to a database)
    image_path = Path(get_random_image())
    if image_path == 'error':
        return {"error in loading image"}

    index = random.randrange(len(tittles) - 1)
    
    return {"id": index, "tittle": tittles[index], "image": f"/static/{image_path}" }

@router.get("/cards")
async def get_cards(db: Session = Depends(get_db)):
    # Here you would typically process the card data (e.g., save to a database)
    #image_path = Path(get_random_image())
    cards = db.query(Card).all()
    if not cards:
        raise HTTPException(status_code=404, detail="No groups found")
    return cards
    
