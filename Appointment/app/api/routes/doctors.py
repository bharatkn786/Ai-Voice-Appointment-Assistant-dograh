from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.services.doctor_service import (
    get_all_doctors,
    get_doctor,
    search_doctors
)

router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.get("/search")
def search(
    name: str = None,
    specialty: str = None,
    location: str = None,
    db: Session = Depends(get_db)
):
    return search_doctors(db, name, specialty, location)


@router.get("/")
def doctors(db: Session = Depends(get_db)):
    return get_all_doctors(db)


@router.get("/{doctor_id}")
def doctor(doctor_id: int, db: Session = Depends(get_db)):
    return get_doctor(db, doctor_id)

