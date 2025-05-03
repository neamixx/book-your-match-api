from typing import List, Optional
from sqlalchemy import Date, ForeignKey
from datetime import date
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship

class Base(DeclarativeBase):
    pass
class UserGroupAssociation(Base):
    __tablename__ = "user_group_association"
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("group.id"), primary_key=True)
    origen: Mapped[str] = mapped_column()
    state: Mapped[str] = mapped_column()
    # Relacions
    group: Mapped["Group"] = relationship("Group", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="groups")


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()
    groups: Mapped[List[UserGroupAssociation]] = relationship(
        "UserGroupAssociation", back_populates="user"
    )
    card_votes: Mapped[List["CardUserGroupAssociation"]] = relationship("CardUserGroupAssociation", back_populates="user")



class Group(Base):
    __tablename__ = "group"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    admin_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), nullable=True
    )
    description: Mapped[str] = mapped_column()
    data_ini: Mapped[date] = mapped_column(Date(), nullable=False)
    data_fi: Mapped[date] = mapped_column(Date(), nullable=False)
    num_mem: Mapped[int] = mapped_column()
    members: Mapped[List[UserGroupAssociation]] = relationship(
        "UserGroupAssociation", back_populates="group"
    )
    card_votes: Mapped[List["CardUserGroupAssociation"]] = relationship("CardUserGroupAssociation", back_populates="group")


class CardUserGroupAssociation(Base):
    __tablename__ = "card_user_group_association"
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("group.id"), primary_key=True)
    card_id: Mapped[int] = mapped_column(ForeignKey("card.id"), primary_key=True)
    value : Mapped[int] = mapped_column()

     # Relacions
    user: Mapped["User"] = relationship("User", back_populates="card_votes")
    group: Mapped["Group"] = relationship("Group", back_populates="card_votes")
    card: Mapped["Card"] = relationship("Card", back_populates="votes")

class Card(Base):
    __tablename__ = "card"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    image: Mapped[str] = mapped_column()
    votes: Mapped[List["CardUserGroupAssociation"]] = relationship("CardUserGroupAssociation", back_populates="card")

class City(Base):
    __tablename__ = "city"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    latitude: Mapped[float] = mapped_column()
    longitude: Mapped[float] = mapped_column()