from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, List
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

router = APIRouter()

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
class PreferenciesUsuari(BaseModel):
    usuari: str
    preferencies: Dict[str, float]

@router.post("/recomanar")
def recomanar(usuaris: List[PreferenciesUsuari]):
    vectors = []

    for u in usuaris:
        v = [u.preferencies.get(tag, 0) for tag in TAGS]
        vectors.append(v)

    vector_global = np.mean(vectors, axis=0)

    resultats = []
    for ciutat, v in CIUTATS.items():
        score = cosine_similarity([vector_global], [v])[0][0]
        resultats.append({"ciutat": ciutat, "score": round(score, 4)})

    resultats.sort(key=lambda x: x["score"], reverse=True)
    return resultats[0]
