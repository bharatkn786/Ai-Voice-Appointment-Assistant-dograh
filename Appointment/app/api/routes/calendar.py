import secrets
from datetime import date as date_type

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.database.models import Booking
from app.services.doctor_service import get_doctor
from app.services.google_calendar_service import get_slots, book

router = APIRouter(prefix="/calendar", tags=["Calendar"])


class SlotReq(BaseModel):
    doctor_id: int
    date: date_type


class BookReq(BaseModel):
    doctor_id: int
    date: date_type
    time: str
    patient_name: str
    phone: str | None = None



TEST_PHONE = "1234567890"


def resolve_phone(phone: str | None) -> str:
    return phone or TEST_PHONE


def get_calendar(db: Session, doctor_id: int):
    doc = get_doctor(db, doctor_id)
    if not doc:
        return None, {"ok": False, "error": "doctor_not_found"}
    if not doc.available:
        return None, {"ok": False, "error": "doctor_unavailable", "name": doc.name}
    if not doc.calendar_id:
        return None, {"ok": False, "error": "no_calendar_for_doctor"}
    return doc, None


@router.post("/available-slots")
def available_slots(r: SlotReq, db: Session = Depends(get_db)):
    doc, err = get_calendar(db, r.doctor_id)
    if err:
        return err
    return {"ok": True, "doctor_id": doc.id, "name": doc.name,
            "date": r.date, "slots": get_slots(doc.calendar_id, r.date)}


@router.post("/book-slot")
def book_slot(r: BookReq, db: Session = Depends(get_db)):

    phone = resolve_phone(r.phone)

    doc, err = get_calendar(db, r.doctor_id)

    if err:
        return err

    result = book(
        doc.calendar_id,
        r.date,
        r.time,
        r.patient_name,
        phone
    )

    if result.get("ok"):
        result["doctor"] = doc.name

        try:
            ref = str(secrets.randbelow(900) + 100)

            db.add(
                Booking(
                    doctor_id=doc.id,
                    patient_name=r.patient_name,
                    phone=phone,
                    date=r.date,
                    time=r.time,
                    event_id=result["event_id"],
                    reference=ref,
                )
            )

            db.commit()

            result["booking_reference"] = ref
            result["booking_reference_spoken"] = " ".join(ref)

        except Exception as e:
            db.rollback()
            print("DB save failed:", e)

    return result