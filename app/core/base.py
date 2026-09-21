from datetime import date

from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.db.connection import Base

# ==========================================
# 1. NOMENCLATOARE (Exact cum le cere seed.py)
# ==========================================


class Ceara(Base):
    __tablename__ = "ceara"
    id_ceara = Column(Integer, primary_key=True, index=True)
    nume_ceara = Column(String(100), nullable=False)

    lumanari = relationship("Lumanare", back_populates="ceara")


class Sezon(Base):
    __tablename__ = "sezoane"
    id_sezon = Column(Integer, primary_key=True, index=True)
    nume_sezon = Column(String(100), nullable=False)

    lumanari = relationship("Lumanare", back_populates="sezon")


class Forma(Base):
    __tablename__ = "forme"
    id_forma = Column(Integer, primary_key=True, index=True)
    nume_forma = Column(String(100), nullable=False)

    lumanari = relationship("Lumanare", back_populates="forma")


class Parfum(Base):
    __tablename__ = "parfumuri"
    id_parfum = Column(Integer, primary_key=True, index=True)
    nume_parfum = Column(String(100), nullable=False)

    lumanari = relationship("Lumanare", back_populates="parfum")


class Culoare(Base):
    __tablename__ = "culori"
    id_culoare = Column(Integer, primary_key=True, index=True)
    nume_culoare = Column(String(100), nullable=False)

    lumanari = relationship("Lumanare", back_populates="culoare")


# ==========================================
# 2. CATALOG PRODUSE
# ==========================================


class Lumanare(Base):
    __tablename__ = "lumanari"
    id_lumanare = Column(Integer, primary_key=True, index=True)
    nume = Column(String(200), nullable=False)
    id_ceara = Column(Integer, ForeignKey("ceara.id_ceara"))
    id_sezon = Column(Integer, ForeignKey("sezoane.id_sezon"))
    id_forma = Column(Integer, ForeignKey("forme.id_forma"))
    id_parfum = Column(Integer, ForeignKey("parfumuri.id_parfum"))
    id_culoare = Column(Integer, ForeignKey("culori.id_culoare"))
    pret = Column(Numeric(10, 2), nullable=False)
    stoc = Column(Integer, default=0)

    ceara = relationship("Ceara", back_populates="lumanari")
    sezon = relationship("Sezon", back_populates="lumanari")
    forma = relationship("Forma", back_populates="lumanari")
    parfum = relationship("Parfum", back_populates="lumanari")
    culoare = relationship("Culoare", back_populates="lumanari")

    comenzi_asociate = relationship("ComandaLumanare", back_populates="lumanare")
    productii = relationship("Productie", back_populates="lumanare")


# ==========================================
# 3. CRM & COMUNZI
# ==========================================


class Client(Base):
    __tablename__ = "clienti"
    id_client = Column(Integer, primary_key=True, index=True)
    nume = Column(String(200), nullable=False)
    telefon = Column(String(20), nullable=True)
    email = Column(String(150), nullable=False, unique=True)  # Am adăugat unique=True pentru siguranță
    parola_hash = Column(String(250), nullable=True)  # 🔒 AICI ESTE COLOANA NOUĂ PENTRU PAROLĂ

    comenzi = relationship("Comanda", back_populates="client")


class Comanda(Base):
    __tablename__ = "comenzi"
    id_comanda = Column(Integer, primary_key=True, index=True)
    id_client = Column(Integer, ForeignKey("clienti.id_client"))
    data_comanda = Column(Date, default=date.today)
    total = Column(Numeric(10, 2), nullable=False)

    client = relationship("Client", back_populates="comenzi")
    lumanari_comandate = relationship("ComandaLumanare", back_populates="comanda")


class ComandaLumanare(Base):
    __tablename__ = "pivot_comanda_lumanare"
    id_pivot = Column(Integer, primary_key=True, index=True)
    id_comanda = Column(Integer, ForeignKey("comenzi.id_comanda"))
    id_lumanare = Column(Integer, ForeignKey("lumanari.id_lumanare"))
    cantitate = Column(Integer, nullable=False)
    pret_unitar = Column(Numeric(10, 2), nullable=False)

    comanda = relationship("Comanda", back_populates="lumanari_comandate")
    lumanare = relationship("Lumanare", back_populates="comenzi_asociate")


# ==========================================
# 4. LOGISTICĂ & OPERAȚIUNI ERP
# ==========================================


class Material(Base):
    __tablename__ = "materiale"
    id_material = Column(Integer, primary_key=True, index=True)
    nume_material = Column(String(200), nullable=False)
    unitate = Column(String(20), nullable=False)

    consumuri = relationship("ConsumMateriale", back_populates="material")


class Productie(Base):
    __tablename__ = "productie"
    id_productie = Column(Integer, primary_key=True, index=True)
    id_lumanare = Column(Integer, ForeignKey("lumanari.id_lumanare"))
    data_productie = Column(Date, default=date.today)
    cantitate = Column(Integer, nullable=False)

    lumanare = relationship("Lumanare", back_populates="productii")
    materiale_consumate = relationship("ConsumMateriale", back_populates="productie")


class ConsumMateriale(Base):
    __tablename__ = "consum_materiale"
    id_consum = Column(Integer, primary_key=True, index=True)
    id_productie = Column(Integer, ForeignKey("productie.id_productie"))
    id_material = Column(Integer, ForeignKey("materiale.id_material"))
    cantitate_consumata = Column(Numeric(10, 2), nullable=False)

    productie = relationship("Productie", back_populates="materiale_consumate")
    material = relationship("Material", back_populates="consumuri")
