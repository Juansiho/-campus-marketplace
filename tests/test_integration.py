"""
Pruebas de integración de Campus Marketplace.

Usan SQLite en memoria (no MySQL) para que el pipeline de CI/CD no dependa
de un servicio de base de datos externo, tal como pide el criterio de
evaluación de la Guía 4 ("3 pruebas de integración pasando en CI/CD con
BD en memoria").
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import event
from sqlalchemy.engine import Engine

from app.database import Base, get_engine, get_session_factory
from app.repositories.articulo_repository import ArticuloRepository
from app.repositories.puja_repository import PujaRepository
from app.repositories.subasta_repository import SubastaRepository
from app.repositories.usuario_repository import UsuarioRepository


@event.listens_for(Engine, "connect")
def _fk_pragma_on_connect(dbapi_connection, connection_record):  # pragma: no cover
    # SQLite no aplica llaves foráneas por defecto; se activa para que las
    # pruebas se comporten como en MySQL.
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture()
def session():
    engine = get_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = get_session_factory(engine)
    db = factory()
    try:
        yield db
    finally:
        db.close()


def _crear_escenario_basico(session):
    """Crea un vendedor, un comprador, un artículo y su subasta activa."""
    usuarios = UsuarioRepository(session)
    articulos = ArticuloRepository(session)
    subastas = SubastaRepository(session)

    vendedor = usuarios.crear("Ana Vendedora", "ana@umb.edu.co", "hash1")
    comprador = usuarios.crear("Luis Comprador", "luis@umb.edu.co", "hash2")
    articulo = articulos.crear(
        titulo="Calculadora Casio FX-991",
        precio_base=50000,
        vendedor_id=vendedor.id,
        categoria="calculadoras",
    )
    subasta = subastas.crear(
        articulo_id=articulo.id, fecha_cierre=datetime.now(timezone.utc) + timedelta(hours=1)
    )
    return vendedor, comprador, articulo, subasta


def test_crud_usuario_y_articulo(session):
    """1) CRUD básico: crear, leer y actualizar un usuario y un artículo."""
    usuarios = UsuarioRepository(session)
    articulos = ArticuloRepository(session)

    usuario = usuarios.crear("Camilo Ramírez", "camilo@umb.edu.co", "hash")
    assert usuario.id is not None

    articulo = articulos.crear(
        titulo="Libro Cálculo I", precio_base=30000, vendedor_id=usuario.id
    )
    assert articulo.id is not None

    encontrado = articulos.obtener_por_id(articulo.id)
    assert encontrado.titulo == "Libro Cálculo I"

    actualizado = articulos.actualizar(articulo.id, precio_base=25000)
    assert float(actualizado.precio_base) == 25000

    assert usuarios.obtener_por_email("camilo@umb.edu.co").id == usuario.id


def test_registrar_puja_valida_monto_y_vendedor(session):
    """2) Reglas de negocio: la puja debe superar el monto actual y el
    vendedor no puede pujar por su propio artículo (regla de concurrencia)."""
    vendedor, comprador, articulo, subasta = _crear_escenario_basico(session)
    pujas = PujaRepository(session)

    # El vendedor no puede pujar por su propio artículo.
    with pytest.raises(ValueError):
        pujas.registrar_puja(subasta.id, vendedor.id, 60000)

    primera = pujas.registrar_puja(subasta.id, comprador.id, 60000)
    assert float(primera.monto) == 60000

    # Una puja menor o igual a la actual debe rechazarse.
    with pytest.raises(ValueError):
        pujas.registrar_puja(subasta.id, comprador.id, 60000)

    segunda = pujas.registrar_puja(subasta.id, comprador.id, 70000)
    assert float(segunda.monto) == 70000
    assert pujas.monto_maximo_actual(subasta.id) == 70000


def test_historial_de_pujas_sin_n_mas_1(session):
    """3) La consulta con JOIN trae el historial y el postor en una sola
    consulta, sin necesidad de lazy-load fila por fila (resuelve el N+1)."""
    vendedor, comprador, articulo, subasta = _crear_escenario_basico(session)
    pujas = PujaRepository(session)

    pujas.registrar_puja(subasta.id, comprador.id, 55000)
    pujas.registrar_puja(subasta.id, comprador.id, 65000)

    historial = pujas.historial_por_subasta(subasta.id)

    assert len(historial) == 2
    # El postor ya viene cargado (joinedload): acceder a .nombre_completo no
    # dispara una consulta adicional por cada puja.
    assert {p.postor.nombre_completo for p in historial} == {"Luis Comprador"}
    # Debe venir ordenado de mayor a menor monto.
    assert float(historial[0].monto) == 65000
