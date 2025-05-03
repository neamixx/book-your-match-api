from fastapi import FastAPI
from app.database import engine
from app import models
from app.routes import users, skyscanner, recomanador, group, card
from fastapi.middleware.cors import CORSMiddleware
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
image_path = os.path.abspath("./images")
app.mount("/static", StaticFiles(directory=image_path), name="static")

# Include routers
app.include_router(card.router)
app.include_router(users.router)
app.include_router(group.router)
app.include_router(recomanador.router)
app.include_router(skyscanner.router)