# pyrefly: ignore [missing-import]

from app.database.connection import Base
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey,Boolean
from sqlalchemy.sql import func

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    specialty = Column(String, nullable=False)
    location = Column(String, nullable=False)
    available = Column(Boolean, default=True)
    calendar_id = Column(String, nullable=True)



class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    patient_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)      # text, not int
    date = Column(Date, nullable=False)
    time = Column(String, nullable=False)
    event_id = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    status = Column(String, nullable=False, default="booked", server_default="booked")
    cancelled_at = Column(DateTime, nullable=True)
    reference = Column(String, nullable=True)