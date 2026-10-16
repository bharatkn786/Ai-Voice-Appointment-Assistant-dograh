# from sqlalchemy.orm import Session

# from app.database.models import Doctor


# def get_all_doctors(db: Session):
#     return db.query(Doctor).all()


# def get_doctor(db: Session, doctor_id: int):
#     return db.query(Doctor).filter(Doctor.id == doctor_id).first()



# # handling the null situation
# def search_doctors(
#     db: Session,
#     name: str = None,
#     specialty: str = None,
#     location: str = None
# ):
#     if name == "null":
#         name = None

#     if specialty == "null":
#         specialty = None

#     if location == "null":
#         location = None

#     query = db.query(Doctor)

#     if name:
#         query = query.filter(
#             Doctor.name.ilike(f"%{name}%")
#         )

#     if specialty:
#         query = query.filter(
#             Doctor.specialty.ilike(f"%{specialty}%")
#         )

#     if location:
#         query = query.filter(
#             Doctor.location.ilike(f"%{location}%")
#         )

#     return query.all()






from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.models import Doctor

STRONG = 0.75   # clear match
CLOSE = 0.30    # similar, ask the caller to confirm

SEARCH_SQL = text(
    "SELECT * FROM search_doctors_fuzzy("
    "CAST(:n AS text), CAST(:s AS text), CAST(:l AS text))"
)


def pack(row, match):
    return {"id": row["id"], "name": row["name"], "specialty": row["specialty"],
            "location": row["location"], "available": row["available"], "match": match}


def get_all_doctors(db: Session):
    rows = db.execute(SEARCH_SQL, {"n": None, "s": None, "l": None}).mappings().all()
    return [pack(r, "all") for r in rows]


def get_doctor(db: Session, doctor_id: int):
    return db.query(Doctor).filter(Doctor.id == doctor_id).first()


def search_doctors(db: Session, name: str = None, specialty: str = None,
                   location: str = None):
    name, specialty, location = (None if v in (None, "", "null") else v
                                 for v in (name, specialty, location))
    rows = db.execute(SEARCH_SQL, {"n": name, "s": specialty, "l": location}).mappings().all()

    if not name:
        return [pack(r, "filter") for r in rows]

    best = rows[0]["score"] if rows else 0
    if best >= STRONG:
        return [pack(r, "strong") for r in rows if r["score"] >= max(STRONG, best - 0.1)]
    if best >= CLOSE:
        return [pack(r, "close") for r in rows[:3] if r["score"] >= CLOSE]
    if specialty or location:                 # not found with those filters, try name only
        return search_doctors(db, name)
    return []