from typing import List
from pydantic import BaseModel
from datetime import date

##USER

from typing import List, Dict
class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str
class User(UserBase):
    id: int

    class Config:
        orm_mode = True


##CARDS

class Choice(BaseModel):
    user_email: str
    card_id: int
    agreeded: bool

class FlightSearchRequest(BaseModel):
    group_id: int
    email: str

class AutoSuggestRequest(BaseModel):
    market: str
    locale: str
    searchTerm: str
    includedEntityTypes: list
    limit: int
    isDestination: bool

class UserInGroup(BaseModel):
    id: int
    name: str
    email: str
    class Config:
        orm_mode = True
class GroupS(BaseModel):
    id: int
    name: str
    description: str
    members: List[UserInGroup]
    
class GroupCreate(BaseModel):
    name: str
    description: str
    data_ini: date
    data_fi: date
    num_mem: int

class CardCreate(BaseModel):
    name: str

class GroupInput(BaseModel):
    group_id: int

class CityRequest(BaseModel):
    city: str
 
class CityCreate(BaseModel):
    name: str
    country: str
    airport: str
    image_url: str

class EmbeddingRequest(BaseModel):
    embedding: object