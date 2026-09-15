"""
Entidades mapeadas con SQLAlchemy 2.0 (estilo declarativo con `Mapped`).

Modelo Entidad-Relación (según el documento del proyecto semestral):
Usuario 1—N Articulo, Articulo 1—1 Subasta, Subasta 1—N Puja,
Usuario 1—N Puja, Subasta 1—N MetricaConcurrencia, Usuario 1—N Notificacion.

6 entidades en total (se pide un mínimo de 5).
"""
from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, String, Enum as SAEnum, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class EstadoSubasta(str, enum.Enum):
    ACTIVA = "ACTIVA"
    CERRADA = "CERRADA"
    CANCELADA = "CANCELADA"


class Usuario(Base):
    __tablename__ = "usuario"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre_completo: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    fecha_registro: Mapped[datetime] = mapped_column(server_default=func.now())

    articulos: Mapped[list["Articulo"]] = relationship(
        back_populates="vendedor", cascade="all, delete-orphan"
    )
    pujas: Mapped[list["Puja"]] = relationship(back_populates="postor")
    notificaciones: Mapped[list["Notificacion"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Usuario id={self.id} email={self.email!r}>"


class Articulo(Base):
    __tablename__ = "articulo"
    __table_args__ = (
        CheckConstraint("precio_base > 0", name="ck_articulo_precio_base_positivo"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(150), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(1000), nullable=True)
    precio_base: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    categoria: Mapped[str] = mapped_column(String(60), nullable=False, default="general")
    fecha_publicacion: Mapped[datetime] = mapped_column(server_default=func.now())

    vendedor_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"), nullable=False)
    vendedor: Mapped["Usuario"] = relationship(back_populates="articulos")

    subasta: Mapped["Subasta"] = relationship(
        back_populates="articulo", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Articulo id={self.id} titulo={self.titulo!r}>"


class Subasta(Base):
    __tablename__ = "subasta"

    id: Mapped[int] = mapped_column(primary_key=True)
    articulo_id: Mapped[int] = mapped_column(ForeignKey("articulo.id"), unique=True, nullable=False)
    fecha_inicio: Mapped[datetime] = mapped_column(server_default=func.now())
    fecha_cierre: Mapped[datetime] = mapped_column(nullable=False)
    estado: Mapped[EstadoSubasta] = mapped_column(
        SAEnum(EstadoSubasta), default=EstadoSubasta.ACTIVA, nullable=False
    )

    articulo: Mapped["Articulo"] = relationship(back_populates="subasta")
    pujas: Mapped[list["Puja"]] = relationship(
        back_populates="subasta", cascade="all, delete-orphan", order_by="Puja.monto.desc()"
    )
    metricas: Mapped[list["MetricaConcurrencia"]] = relationship(
        back_populates="subasta", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Subasta id={self.id} estado={self.estado}>"


class Puja(Base):
    __tablename__ = "puja"
    __table_args__ = (
        CheckConstraint("monto > 0", name="ck_puja_monto_positivo"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    subasta_id: Mapped[int] = mapped_column(ForeignKey("subasta.id"), nullable=False)
    postor_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"), nullable=False)
    monto: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    fecha: Mapped[datetime] = mapped_column(server_default=func.now())

    subasta: Mapped["Subasta"] = relationship(back_populates="pujas")
    postor: Mapped["Usuario"] = relationship(back_populates="pujas")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Puja id={self.id} monto={self.monto}>"


class Notificacion(Base):
    __tablename__ = "notificacion"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"), nullable=False)
    mensaje: Mapped[str] = mapped_column(String(300), nullable=False)
    leida: Mapped[bool] = mapped_column(default=False)
    fecha: Mapped[datetime] = mapped_column(server_default=func.now())

    usuario: Mapped["Usuario"] = relationship(back_populates="notificaciones")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Notificacion id={self.id} usuario_id={self.usuario_id}>"


class MetricaConcurrencia(Base):
    __tablename__ = "metrica_concurrencia"

    id: Mapped[int] = mapped_column(primary_key=True)
    subasta_id: Mapped[int] = mapped_column(ForeignKey("subasta.id"), nullable=False)
    pujas_por_segundo: Mapped[float] = mapped_column(Numeric(6, 2), default=0)
    conflictos_resueltos: Mapped[int] = mapped_column(default=0)
    fecha_registro: Mapped[datetime] = mapped_column(server_default=func.now())

    subasta: Mapped["Subasta"] = relationship(back_populates="metricas")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<MetricaConcurrencia subasta_id={self.subasta_id}>"
