from fastapi import APIRouter, Depends, HTTPException, Cookie
from sqlalchemy.orm import Session
from ..schemas import *
from ..database import SessionLocal
from ..models import *

router = APIRouter(prefix="/groups", tags=["groups"])

# unirse per id
# Data anada data tornada nª persones

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Get all groups
@router.get("/")
def get_groups(db: Session = Depends(get_db)):
    
    groups = db.query(Group).join(UserGroupAssociation).all()
    if not groups:
        raise HTTPException(status_code=404, detail="No groups found")
    return groups

# Get a specific group by name
@router.post("/create")
def create_group(group: GroupCreate, email: str, ori: str, db: Session = Depends(get_db)):
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
        admin_id=user.id,
        data_ini=group.data_ini,
        data_fi=group.data_fi,
        num_mem=1,
    )

    db_group.members.append(UserGroupAssociation(user_id=user.id, origen=ori ,state="pendent"))
    
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    
    return db_group

# Get estat relacio
@router.get("/relation")
def get_relation(email: str, group_id: int, db: Session = Depends(get_db)):
    if not email:
        raise HTTPException(status_code=400, detail="Missing email")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    relation = db.query(UserGroupAssociation).filter_by(
        user_id=user.id,
        group_id=group_id
    ).first()

    if not relation:
        return {"relation": "not_member"}

    return {
        "user_id": relation.user_id,
        "group_id": relation.group_id,
        "origen": relation.origen,  # ex: app, web, etc.
        "state": relation.state  # ex: pendent, completat, etc.
    }


# Join a group
@router.post("/join")
def join_group(group_id: int, email: str, ori: str, db: Session = Depends(get_db)):
    if email is None:
        raise HTTPException(status_code=401, detail="User not logged in")

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    group = db.query(Group).filter(Group.id == group_id).first()
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")

    existing_association = db.query(UserGroupAssociation).filter(
        UserGroupAssociation.user_id == user.id,
        UserGroupAssociation.group_id == group.id
    ).first()

    if existing_association:
        raise HTTPException(status_code=400, detail="Already a member of this group")

    association = UserGroupAssociation(user_id=user.id, group_id=group.id, origen= ori, state= "pendent")
    db.add(association)
    group.num_mem += 1
    db.commit()
    
    return {"message": "Joined group successfully"}

# Get members of a group
@router.get("/{group_name}")
def get_members(group_name: str, db: Session = Depends(get_db)):
    group = db.query(Group).filter(Group.name == group_name).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    members = db.query(User).join(UserGroupAssociation).filter(
        UserGroupAssociation.group_id == group.id
    ).all()
    
    return members

# Get groups of a user
@router.get("/by-user/{email}")
def get_user_groups(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    groups = db.query(Group).join(UserGroupAssociation).filter(
        UserGroupAssociation.user_id == user.id
    ).all()
    
    return groups

