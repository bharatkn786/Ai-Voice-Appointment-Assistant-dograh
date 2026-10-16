from fastapi import FastAPI,Request
from sqlalchemy import text

from app.database.connection import engine, Base
from app.database.models import Doctor
from app.api.routes.doctors import router as doctors_router

from app.api.routes.calendar import router as calendar_router
from app.api.routes.cancel_booking import router as bookings_router


from pydantic import BaseModel

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(doctors_router)

app.include_router(bookings_router)
app.include_router(calendar_router)

@app.get("/")
def root():
    return {"message": "Appointment API is running"}


@app.get("/db-test")
def db_test():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))

        return {
            "database": "connected",
            "result": result.scalar()
            
        }


class CallerIn(BaseModel):
    caller_number: str

@app.post("/test-caller")
def test_caller(body: CallerIn):
    print("CALLER NUMBER:", body.caller_number)
    return {"success": True, "caller_number": body.caller_number}