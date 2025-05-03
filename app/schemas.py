from typing import List
from pydantic import BaseModel
from datetime import date
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

class FlightSearchRequest(BaseModel):
    market: str
    locale: str
    currency: str
    origin_iata: str
    destination_iata: str
    year: int
    month: int
    day: int
    adults: int
    cabin_class: str

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

class CardCreate(BaseModel):
    name: str

class CityRequest(BaseModel):
    city: str
 
