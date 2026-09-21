import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Mecanism de siguranță (Fallback) dacă lipsește .env sau cheia de Cloud
if not DATABASE_URL:
    print("⚠️ DATABASE_URL nu a fost găsit în .env! Se folosește baza de date locală SQLite: local_erp.db")
    DATABASE_URL = "sqlite:///local_erp.db"

# Formatare corectă pentru driverul PostgreSQL dacă este cazul
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

# Configurăm motorul bazei de date în funcție de tipul acesteia
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        pool_recycle=1800,
        echo=False,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
