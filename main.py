from fastapi import FastAPI
from app.database import engine
from app import models
from app.routes import auth, skyscanner, recomanador, group
from fastapi.middleware.cors import CORSMiddleware
from endpoints.card import router as card_router
from fastapi.staticfiles import StaticFiles

import os


models.Base.metadata.create_all(bind=engine)



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(recomanador.router)

app.include_router(group.router)
app.include_router(card_router)
    
image_path = os.path.abspath("./images")

app.mount("/static", StaticFiles(directory=image_path), name="static")