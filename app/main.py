import logging

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import app.core.base as models
from app.db.connection import get_db

# Configurare Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Light Infinity AI - Backend Engine", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/products")
def get_catalog_products(db: Session = Depends(get_db)):  # noqa: B008
    try:
        products = db.query(models.Lumanare).all()
        return [
            {
                "id_lumanare": p.id_lumanare,
                "nume": p.nume,
                "pret": float(p.pret),
                "stoc": p.stoc,
            }
            for p in products
        ]
    except Exception as e:  # noqa: BLE001
        logger.error(f"Eroare /api/products: {e!s}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/materials")
def get_inventory_materials(db: Session = Depends(get_db)):  # noqa: B008
    try:
        materials = db.query(models.Material).all()
        return [
            {
                "id_material": m.id_material,
                "nume_material": m.nume_material,
                "unitate": m.unitate,
            }
            for m in materials
        ]
    except Exception as e:  # noqa: BLE001
        logger.error(f"Eroare /api/materials: {e!s}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/orders")
def get_all_orders(db: Session = Depends(get_db)):  # noqa: B008
    try:
        orders = db.query(models.Comanda).all()
        return [
            {
                "id_comanda": o.id_comanda,
                "id_client": o.id_client,
                "data_comanda": o.data_comanda.strftime("%Y-%m-%d") if o.data_comanda else None,
                "total": float(o.total),
            }
            for o in orders
        ]
    except Exception as e:  # noqa: BLE001
        logger.error(f"Eroare la citirea registrului de comenzi: {e!s}")
        raise HTTPException(status_code=500, detail=str(e))
