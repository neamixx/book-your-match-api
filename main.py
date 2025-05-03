from fastapi import FastAPI
from app.database import engine
from app import models
from app.routes import auth, skyscanner

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router)
app.include_router(recomanador.router)