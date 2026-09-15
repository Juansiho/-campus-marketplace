"""
Configuración central de SQLAlchemy 2.0 para Campus Marketplace.

En producción se usa MySQL (según el requerimiento no funcional del
proyecto semestral). Para las pruebas de integración de esta guía se
usa SQLite en memoria, tal como pide el criterio de evaluación
("3 pruebas de integración pasando en CI/CD con BD en memoria").
"""
from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    """Clase base declarativa de la que heredan todas las entidades."""
    pass


def get_engine(url: str | None = None):
    """
    Crea el engine de SQLAlchemy.

    - Si se pasa `url` o existe la variable de entorno DATABASE_URL, se usa esa.
    - Si no, se usa MySQL local por defecto (ajustar credenciales según el equipo).
    """
    database_url = url or os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:root@localhost:3306/campus_marketplace",
    )
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, echo=False, future=True, connect_args=connect_args)


def get_session_factory(engine=None):
    engine = engine or get_engine()
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
