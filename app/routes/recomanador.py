from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, List
import numpy as np
from ..database import SessionLocal
from sqlalchemy.orm import Session
from ..models import User as DBUser, UserGroupAssociation, City
from ..schemas import User as UserSchema, GroupInput


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Tags en ordre
TAGS = ["natura", "urbà", "platja", "història", "cultura", "gastronomia", "aventura", "relax", "tecnologia", "clima càlid"]


# Models per validar entrada
# Moure aixo al models 
class PreferenciesUsuari(BaseModel):
    usuari: str
    preferencies: Dict[str, float]

@router.post("/recomanar")
def recomanar(input: GroupInput, db: Session = Depends(get_db)):
    # Obtenir usuaris del grup
    usuaris = db.query(DBUser).join(UserGroupAssociation).filter(UserGroupAssociation.group_id == input.group_id).all()

    if not usuaris:
        raise HTTPException(status_code=404, detail="No s'han trobat usuaris per aquest grup.")

    # Agafar els emmbeddings de cada usuari
    vectors = []
    for user in usuaris:
       user_vector = list(user.embedding.values())
       vectors.append(user_vector)

    vector_global = np.mean(vectors, axis=0)

    # Obtenir ciutats de la base de dades
    ciutats = db.query(City).all()

    if not ciutats:
        raise HTTPException(status_code=404, detail="No s'han trobat ciutats a la base de dades.")

    # Calcular distància Manhattan i ordenar
    resultats = []
    for ciutat in ciutats:
        ciutat_vector = list(ciutat.embedding.values())
        if len(ciutat_vector) != len(vector_global):
            continue  
        distancia = np.sum(np.abs(np.array(vector_global) - np.array(ciutat_vector)))
        resultats.append({"ciutat": ciutat.name, "distancia": round(distancia, 4)})

    if not resultats:
        raise HTTPException(status_code=500, detail="No s'ha pogut comparar cap ciutat. Comprova els embeddings.")
    resultats.sort(key=lambda x: x["distancia"])
    return resultats[0]