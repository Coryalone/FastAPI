from typing import List
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel

from sqlalchemy import create_engine, Column, Integer, String, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session

# подключение к БД

SQLALCHEMY_DATABASE_URL = "sqlite:///./meetups.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# описание таблицы
class Meetups(Base):
    __tablename__ = "meetups"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    finished_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    members = Column(String)


# описание сериализаторов
class MeetGuy(BaseModel):
    id: int
    name: str
    created_at: datetime
    finished_at: datetime
    members: str

    class Config:
        orm_mode = True


class TryIt(BaseModel):
    id: int

    class Config:
        orm_mode = True


class CreateMeet(BaseModel):
    name: str
    members: str
    created_at: datetime
    finished_at: datetime


class UpdateMeet(BaseModel):
    name: str
    created_at: datetime
    finished_at: datetime
    members: str


# связываение объектов питона и данных в таблице sql
Base.metadata.create_all(bind=engine)


# описание сервисов
def service_get_meet_by_id(db: Session, meet_id: int):
    return db.query(Meetups).filter(Meetups.id == meet_id).first()


def service_get_meets(db: Session, skip: int, limit: int):
    return db.query(Meetups).offset(skip).limit(limit).all()


def service_update_data(db: Session, meet_id: int, meet: UpdateMeet):
    upd = service_get_meet_by_id(db=db, meet_id=meet_id)
    upd.name = meet.name
    upd.created_at = meet.created_at
    upd.finished_at = meet.finished_at
    upd.members = meet.members
    db.commit()
    db.refresh(upd)
    return upd


def service_create_meet(db: Session, meet: CreateMeet):
    db_meets = Meetups(name=meet.name, created_at=meet.created_at, finished_at=meet.finished_at, members=meet.members)
    db.add(db_meets)
    db.commit()
    db.refresh(db_meets)
    return db_meets


def service_delete_meet(db: Session, meet_id: int):
    db.query(Meetups).filter(Meetups.id == meet_id).delete()
    db.commit()


app = FastAPI()


# Создание зависимойстей (на каждый запрос создается своя сессия)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# описаниее api

@app.get("/meets/", response_model=List[MeetGuy])
def get_meets(skip: int, limit: int, db: Session = Depends(get_db)):
    users = service_get_meets(db, skip=skip, limit=limit)
    return users


@app.get("/meets/{meet_id}", response_model=MeetGuy)
def get_meets_by_id(meet_id: int, db: Session = Depends(get_db)):
    db_user = service_get_meet_by_id(db, meet_id=meet_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/meets/", response_model=TryIt)
def create_meet(meet: CreateMeet, db: Session = Depends(get_db)):
    return service_create_meet(db=db, meet=meet)


@app.put("/meets/", response_model=MeetGuy)
def update_meet(meet_id: int, meet: UpdateMeet, db: Session = Depends(get_db)):
    return service_update_data(db=db, meet_id=meet_id, meet=meet)


@app.delete("/meets/{meet_id}")
def delete_this_meet(meet_id: int, db: Session = Depends(get_db)):
    service_delete_meet(db=db, meet_id=meet_id)
    return {'Message': 'Success'}
