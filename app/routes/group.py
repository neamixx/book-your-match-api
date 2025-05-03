from fastapi import APIRouter, Depends, HTTPException, Cookie
from sqlalchemy.orm import Session
from ..schemas import *
from ..database import SessionLocal
from ..models import *

router = APIRouter(prefix="/groups", tags=["groups"])
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()


@router.get("/")
def get_groups(db: Session = Depends(get_db)):
    
    groups = db.query(Group).join(UserGroupAssociation).all()
    if not groups:
        raise HTTPException(status_code=404, detail="No groups found")
    return groups

@router.post("/create")
def create_group(group: GroupCreate, email: str, db: Session = Depends(get_db)):
    if email is None:
        raise HTTPException(status_code=401, detail="User not logged in")

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    existing_group = db.query(Group).filter(Group.name == group.name).first()
    if existing_group:
        raise HTTPException(status_code=400, detail="Group already exists")
    
    db_group = Group(
        name=group.name,
        description=group.description,
        admin_id=user.id 
    )

    db_group.members.append(UserGroupAssociation(user_id=user.id))
    
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    
    return db_group


@router.post("/join")
def join_group(group_name: str, email: str, db: Session = Depends(get_db)):
    if email is None:
        raise HTTPException(status_code=401, detail="User not logged in")

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    group = db.query(Group).filter(Group.name == group_name).first()
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")

    existing_association = db.query(UserGroupAssociation).filter(
        UserGroupAssociation.user_id == user.id,
        UserGroupAssociation.group_id == group.id
    ).first()

    if existing_association:
        raise HTTPException(status_code=400, detail="Already a member of this group")

    association = UserGroupAssociation(user_id=user.id, group_id=group.id)
    db.add(association)
    db.commit()
    
    return {"message": "Joined group successfully"}

@router.get("/{group_name}")
def get_members(group_name: str, db: Session = Depends(get_db)):
    group = db.query(Group).filter(Group.name == group_name).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    members = db.query(User).join(UserGroupAssociation).filter(
        UserGroupAssociation.group_id == group.id
    ).all()
    
    return members