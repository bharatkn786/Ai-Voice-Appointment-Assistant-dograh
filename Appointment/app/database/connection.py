from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import DATABASE_URL


engine = create_engine(
    DATABASE_URL.replace(
        "postgresql://",
        "postgresql+psycopg2://"
    ),
    pool_pre_ping=True,     # # Checks if the DB connection is alive before using it
    pool_recycle=1800       # # Recycles the connection after 30 minutes (1800 seconds)
)

Base = declarative_base()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)