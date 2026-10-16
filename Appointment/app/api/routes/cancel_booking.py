import re
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.database.models import Booking, Doctor
from app.services.google_calendar_service import cancel

router = APIRouter(prefix="/bookings", tags=["Bookings"])
TZ = ZoneInfo("Asia/Kolkata")


def last10(phone):
    return re.sub(r"\D", "", phone or "")[-10:]


class PhoneReq(BaseModel):
    phone: str | None = None


class CancelReq(BaseModel):
    booking_id: int
    phone: str | None = None
    reference: str | None = None


def upcoming_rows(db: Session, phone):
    key = last10(phone)
    if len(key) < 10:
        return None
    now = datetime.now(TZ)
    rows = (db.query(Booking, Doctor)
              .join(Doctor, Doctor.id == Booking.doctor_id)
              .filter(Booking.status == "booked", Booking.phone.like(f"%{key}"))
              .order_by(Booking.date, Booking.time).all())
    return [(b, d) for b, d in rows
            if (b.date, b.time) > (now.date(), now.strftime("%H:%M"))]


TEST_PHONE = "1234567890"


def resolve_phone(phone: str | None) -> str:            ## beacuse to test the webcall
    return phone or TEST_PHONE

@router.post("/upcoming")
def upcoming(r: PhoneReq, db: Session = Depends(get_db)):

    phone = resolve_phone(r.phone)          

    rows = upcoming_rows(db, phone)

    if rows is None:
        return {"ok": False, "error": "phone_unavailable"}

    return {
        "ok": True,
        "bookings": [
            {
                "booking_id": b.id,
                "doctor": d.name,
                "specialty": d.specialty,
                "date": b.date.isoformat(),
                "time": b.time,
                "patient_name": b.patient_name
            }
            for b, d in rows[:3]
        ]
    }


@router.post("/cancel")
def cancel_booking(r: CancelReq, db: Session = Depends(get_db)):

    phone = resolve_phone(r.phone)                   # for webcall   

    rows = upcoming_rows(db, phone)

    if rows is None:
        return {"ok": False, "error": "phone_unavailable"}

    match = next(((b, d) for b, d in rows if b.id == r.booking_id), None)
    if not match:
        return {"ok": False, "error": "booking_not_found"}
    b, d = match

    given = re.sub(r"\D", "", r.reference or "")
    if b.reference and given != b.reference:
        return {"ok": False, "error": "wrong_appointment_number"}

    if b.event_id and d.calendar_id:
        res = cancel(d.calendar_id, b.event_id)
        if not res["ok"]:
            return res
    b.status = "cancelled"
    b.cancelled_at = func.now()
    db.commit()
    return {"ok": True, "cancelled": {"doctor": d.name,
            "date": b.date.isoformat(), "time": b.time}}