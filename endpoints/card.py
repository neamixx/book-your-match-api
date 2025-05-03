from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel

import random
import os
from os import listdir
from os.path import isfile, join
from pathlib import Path


def get_random_image():
    image_path = os.path.abspath("./images")
    images = [ 
        f for f in listdir(image_path) if isfile(join(image_path, f))
    ]
    
    if len(images) < 1:
        return 'error'
    
    index = random.randrange(len(images) - 1)
    return images[index] 

# Initialize the router
router = APIRouter()



# Define the GET endpoint for the /card route

tittles = [
    "Playa",
    "Mojitos",
    "Ron",
    "Ski"
]

# Define the POST endpoint for the /card route
@router.get("/card")
async def get_card():
    # Here you would typically process the card data (e.g., save to a database)
    image_path = Path(get_random_image())
    if image_path == 'error':
        return {"error in loading image"}

    index = random.randrange(len(tittles) - 1)
    
    return {"id": index, "tittle": tittles[index], "image": f"/static/{image_path}" }
