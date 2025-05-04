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

from ..models import *
from ..schemas import Choice, EmbeddingRequest

router = APIRouter(prefix="", tags=["cards"])

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
    db_card = Card(name=name, image=file.filename, embedding={
        "temperature": 0.5,
        "demography": 0.5,
        "night-life": 0.5,
        "beach": 0.5,
        "price": 0.5,
        "mountain": 0.5,
        "nature": 0.5
    })
    db.add(db_card)
    db.commit()
    db.refresh(db_card)

    return db_card

# Define the GET endpoint for the /card route



# Define the POST endpoint for the /card route
@router.get("/card")
async def get_card(db: Session = Depends(get_db)):
    # Here you would typically process the card data (e.g., save to a database)
    id = random.randrange(0, 20)
    card = db.query(Card).filter(Card.id == id).first()
    image_path = Path(get_random_image())
    if image_path == 'error':
        return {"error in loading image"}

    index = random.randrange(len(tittles) - 1)
    
    return {"id": id, "tittle": card.name, "image": f"/static/{card.image}" }

@router.get("/cards")
async def get_cards(db: Session = Depends(get_db)):
    # Here you would typically process the card data (e.g., save to a database)
    #image_path = Path(get_random_image())
    cards = db.query(Card).all()
    if not cards:
        raise HTTPException(status_code=404, detail="No groups found")
    return cards


def adjust_user_embedding(user_embedding: object, card_embedding: object, agreeded: bool):
    adjusted = user_embedding.copy()
    print(adjusted)
    if user_embedding == None or card_embedding == None:
        return None
    else:
        for card_key, card_value in card_embedding.items():
            if card_key in user_embedding:
                k = 0.15
                if not agreeded:
                    k = -k                    
                adjusted[card_key] = max(min( user_embedding[card_key] + card_value * k, 1.0), 0.0)
                
        print(adjusted)
        return adjusted
    

@router.post("/card")
async def alter_algorithm(choice: Choice, db: Session = Depends(get_db)):
    usr = db.query(User).filter(User.email == choice.user_email).first()
    crd = db.query(Card).filter(Card.id == choice.card_id).first()
    print(crd.image)
    adjusted_embedding = adjust_user_embedding(usr.embedding, crd.embedding, choice.agreeded)
    if adjusted_embedding != None: 
        usr.embedding = adjusted_embedding
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="User or Card not found")


@router.post("/{id}/embedding")
async def update_embedding(id: int, request: EmbeddingRequest, db: Session = Depends(get_db)):
    card = db.query(Card).filter(Card.id == id).first()
    
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    if card.embedding is None:
        card.embedding = request.embedding
    else:
        print(card.embedding)
        print(request.embedding)
        
        for request_item in request.embedding:
            card_items = card.embedding
            if request_item in card_items:
                print("Updating existing embedding")
                card_items[request_item] = request.embedding[request_item]
            else:
                print("Adding new embedding")
                card_items[request_item] = request.embedding[request_item]
        card.embedding = card_items
        print(card.embedding)
    db.query(Card).filter(Card.id == id).update({"embedding": card.embedding})
    db.commit()
    db.refresh(card)

    return {"message": f"Embedding updated for card {id}"}
