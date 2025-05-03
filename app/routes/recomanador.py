from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, List
import numpy as np
from ..database import SessionLocal
from sqlalchemy.orm import Session
from ..models import *
from ..schemas import *


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Tags en ordre
TAGS = ["natura", "urbà", "platja", "història", "cultura", "gastronomia", "aventura", "relax", "tecnologia", "clima càlid"]

# Base de dades simple de ciutats (com vector)
CIUTATS = {
    "Barcelona": [0.6, 1.0, 0.9, 0.8, 0.9, 1.0, 0.4, 0.7, 0.6, 0.9],
    "Reykjavik": [1.0, 0.4, 0.1, 0.7, 0.5, 0.6, 0.9, 0.8, 0.3, 0.2],
    "Tokyo": [0.4, 1.0, 0.3, 0.7, 1.0, 1.0, 0.6, 0.4, 1.0, 0.6],
    "Lisboa": [0.7, 0.9, 0.9, 0.8, 0.9, 0.9, 0.5, 0.7, 0.5, 0.9],
    "Ljubljana": [1.0, 0.4, 0.2, 0.9, 0.8, 0.7, 0.3, 1.0, 0.3, 0.6]
}

# Models per validar entrada
# Moure aixo al models 
class PreferenciesUsuari(BaseModel):
    usuari: str
    preferencies: Dict[str, float]

@router.post("/recomanar")
def recomanar(input: GroupInput, db: Session = Depends(get_db)):
    # Obtenir usuaris del grup
    usuaris = db.query(User).filter(User.group_id == input.group_id).all()

    if not usuaris:
        raise HTTPException(status_code=404, detail="No s'han trobat usuaris per aquest grup.")

    # Agafar els emmbeddings de cada usuari
    vectors = []
    for user in usuaris:
       user_vector = [user.preferences.get(tag, 0) for tag in TAGS]
       vectors.append(user_vector)

    vector_global = np.mean(vectors, axis=0)

    # Obtenir ciutats de la base de dades
    ciutats = db.query(City).all()

    if not ciutats:
        raise HTTPException(status_code=404, detail="No s'han trobat ciutats a la base de dades.")

    # Calcular distància Manhattan i ordenar
    resultats = []
    for ciutat in ciutats:
        ciutat_vector = [ciutat.vector.get(tag, 0) for tag in TAGS]
        distancia = np.sum(np.abs(np.array(vector_global) - np.array(ciutat_vector)))
        resultats.append({"ciutat": ciutat.nom, "distancia": round(distancia, 4)})

    resultats.sort(key=lambda x: x["distancia"])
    return resultats[0]