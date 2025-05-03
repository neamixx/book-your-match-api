from fastapi import APIRouter, Depends, HTTPException, Cookie
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from .. import models, schemas
from ..schemas import *
from ..database import SessionLocal

router = APIRouter(prefix="/users", tags=["users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if the user already exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    # Create a new user
    db_user = models.User(name=user.name, email=user.email, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.password != user.password:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(key="email", value=user.email)
    return response


@router.get("/", response_model=list[User])
def get_users(db: Session = Depends(get_db)):
    #Get all users
    users = db.query(models.User).all()
    return users

@router.get("/me")
async def read_user(email: str = Cookie(None)):
    if email is None:
        raise HTTPException(status_code=401, detail="User not logged in")
    
    return {"email": email}


@router.post("/logout")
async def logout():
    return JSONResponse(content={"message": "Logout successful"}, cookies={"email": ""})

@router.post("/{id}/embedding")
async def update_embedding(id: int, request: EmbeddingRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.embedding is None:
        user.embedding = request.embedding
    else:
        print(user.embedding)
        print(request.embedding)
        
        for request_item in request.embedding:
            user_items = user.embedding
            if request_item in user_items:
                print("Updating existing embedding")
                user_items[request_item] = request.embedding[request_item]
            else:
                print("Adding new embedding")
                user_items[request_item] = request.embedding[request_item]
        user.embedding = user_items
        print(user.embedding)
        
    db.query(models.User).filter(models.User.id == id).update({"embedding": user.embedding})
    db.commit()
    db.refresh(user)

    return {"message": f"Embedding updated for city {id}"}

@router.get("/{id}")
def get_user(id: int, db: Session = Depends(get_db)):
    #Get user by id
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user