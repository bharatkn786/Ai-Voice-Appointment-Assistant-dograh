import json
from pathlib import Path

from app.database.connection import SessionLocal, Base, engine
from app.database.models import Doctor

Base.metadata.create_all(bind=engine)

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "doctors.json"
doctors = json.loads(DATA_FILE.read_text())

db = SessionLocal()
for d in doctors:
    existing = db.query(Doctor).filter(Doctor.name == d["name"]).first()
    if existing:
        for key, value in d.items():
            setattr(existing, key, value)
    else:
        db.add(Doctor(**d))
db.commit()
db.close()
print("Doctors synced successfully")