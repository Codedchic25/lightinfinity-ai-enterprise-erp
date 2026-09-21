import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.base import (
    Ceara,
    Client,
    Comanda,
    ComandaLumanare,
    ConsumMateriale,
    Culoare,
    Forma,
    Lumanare,
    Material,
    Parfum,
    Productie,
    Sezon,
)
from app.db.connection import Base


@pytest.fixture
def db_session():
    """Create an isolated in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_lumanare_relations(db_session):
    """Verify candle creation and relationships with nomenclature tables."""
    ceara = Ceara(nume_ceara="Ceara de Soia Premium")
    sezon = Sezon(nume_sezon="Iarna")
    forma = Forma(nume_forma="Cilindrica")
    parfum = Parfum(nume_parfum="Lavanda")
    culoare = Culoare(nume_culoare="Alb")

    db_session.add_all([ceara, sezon, forma, parfum, culoare])
    db_session.flush()

    lumanare = Lumanare(
        nume="Lumanare Premium",
        id_ceara=ceara.id_ceara,
        id_sezon=sezon.id_sezon,
        id_forma=forma.id_forma,
        id_parfum=parfum.id_parfum,
        id_culoare=culoare.id_culoare,
        pret=35.00,
        stoc=10,
    )

    db_session.add(lumanare)
    db_session.commit()
    db_session.refresh(lumanare)

    assert lumanare.ceara.nume_ceara == "Ceara de Soia Premium"
    assert lumanare.sezon.nume_sezon == "Iarna"
    assert lumanare.forma.nume_forma == "Cilindrica"
    assert lumanare.parfum.nume_parfum == "Lavanda"
    assert lumanare.culoare.nume_culoare == "Alb"
    assert lumanare.stoc == 10
def test_comanda_relations(db_session):
    """Verify order relationships between client, order, and candle."""
    client = Client(
        nume="Client Test",
        email="client.test@example.com",
    )

    ceara = Ceara(nume_ceara="Ceara Test")
    sezon = Sezon(nume_sezon="Vara")
    forma = Forma(nume_forma="Rotunda")
    parfum = Parfum(nume_parfum="Vanilie")
    culoare = Culoare(nume_culoare="Albastru")

    db_session.add_all([
        client,
        ceara,
        sezon,
        forma,
        parfum,
        culoare,
    ])
    db_session.flush()

    lumanare = Lumanare(
        nume="Lumanare Test",
        id_ceara=ceara.id_ceara,
        id_sezon=sezon.id_sezon,
        id_forma=forma.id_forma,
        id_parfum=parfum.id_parfum,
        id_culoare=culoare.id_culoare,
        pret=50.00,
        stoc=20,
    )

    db_session.add(lumanare)
    db_session.flush()

    comanda = Comanda(
        id_client=client.id_client,
        total=100.00,
    )

    db_session.add(comanda)
    db_session.flush()

    articol = ComandaLumanare(
        id_comanda=comanda.id_comanda,
        id_lumanare=lumanare.id_lumanare,
        cantitate=2,
        pret_unitar=50.00,
    )

    db_session.add(articol)
    db_session.commit()
    db_session.refresh(comanda)

    assert comanda.client.nume == "Client Test"
    assert len(comanda.lumanari_comandate) == 1
    assert comanda.lumanari_comandate[0].lumanare.nume == "Lumanare Test"
    assert comanda.lumanari_comandate[0].cantitate == 2
    assert comanda.lumanari_comandate[0].pret_unitar == 50.00
def test_productie_materiale_relations(db_session):
    """Verify production relationships with candles and consumed materials."""
    ceara = Ceara(nume_ceara="Ceara Productie")
    sezon = Sezon(nume_sezon="Toamna")
    forma = Forma(nume_forma="Patrata")
    parfum = Parfum(nume_parfum="Scortisoara")
    culoare = Culoare(nume_culoare="Maro")

    db_session.add_all([
        ceara,
        sezon,
        forma,
        parfum,
        culoare,
    ])
    db_session.flush()

    lumanare = Lumanare(
        nume="Lumanare Productie",
        id_ceara=ceara.id_ceara,
        id_sezon=sezon.id_sezon,
        id_forma=forma.id_forma,
        id_parfum=parfum.id_parfum,
        id_culoare=culoare.id_culoare,
        pret=45.00,
        stoc=10,
    )

    material = Material(
        nume_material="Fitil Bumbac",
        unitate="buc",
    )

    db_session.add_all([lumanare, material])
    db_session.flush()

    productie = Productie(
        id_lumanare=lumanare.id_lumanare,
        cantitate=10,
    )

    db_session.add(productie)
    db_session.flush()

    consum = ConsumMateriale(
        id_productie=productie.id_productie,
        id_material=material.id_material,
        cantitate_consumata=10.00,
    )

    db_session.add(consum)
    db_session.commit()
    db_session.refresh(productie)

    assert productie.lumanare.nume == "Lumanare Productie"
    assert len(productie.materiale_consumate) == 1
    assert productie.materiale_consumate[0].material.nume_material == "Fitil Bumbac"
    assert productie.materiale_consumate[0].cantitate_consumata == 10.00
def test_lumanare_requires_name(db_session):
    """Verify that a candle without a name is rejected by the database."""
    ceara = Ceara(nume_ceara="Ceara Validare")
    sezon = Sezon(nume_sezon="Iarna")
    forma = Forma(nume_forma="Rotunda")
    parfum = Parfum(nume_parfum="Vanilie")
    culoare = Culoare(nume_culoare="Alb")

    db_session.add_all([
        ceara,
        sezon,
        forma,
        parfum,
        culoare,
    ])
    db_session.flush()

    lumanare = Lumanare(
        nume=None,
        id_ceara=ceara.id_ceara,
        id_sezon=sezon.id_sezon,
        id_forma=forma.id_forma,
        id_parfum=parfum.id_parfum,
        id_culoare=culoare.id_culoare,
        pret=30.00,
        stoc=5,
    )

    db_session.add(lumanare)

    with pytest.raises(Exception):
        db_session.commit()

    db_session.rollback()
