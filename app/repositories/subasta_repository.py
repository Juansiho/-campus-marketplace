from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import EstadoSubasta, Subasta


class SubastaRepository:
    """Repositorio CRUD para la entidad Subasta."""

    def __init__(self, session: Session):
        self.session = session

    def crear(self, articulo_id: int, fecha_cierre: datetime) -> Subasta:
        subasta = Subasta(articulo_id=articulo_id, fecha_cierre=fecha_cierre)
        self.session.add(subasta)
        self.session.commit()
        self.session.refresh(subasta)
        return subasta

    def obtener_por_id(self, subasta_id: int) -> Subasta | None:
        return self.session.get(Subasta, subasta_id)

    def listar_activas(self) -> list[Subasta]:
        stmt = select(Subasta).where(Subasta.estado == EstadoSubasta.ACTIVA)
        return list(self.session.scalars(stmt).all())

    def cerrar(self, subasta_id: int) -> Subasta | None:
        """Cierra la subasta (lo dispararía el scheduler concurrente al vencer el tiempo)."""
        subasta = self.obtener_por_id(subasta_id)
        if subasta is None:
            return None
        subasta.estado = EstadoSubasta.CERRADA
        self.session.commit()
        self.session.refresh(subasta)
        return subasta

    def cancelar(self, subasta_id: int) -> Subasta | None:
        subasta = self.obtener_por_id(subasta_id)
        if subasta is None:
            return None
        if subasta.pujas:
            raise ValueError("No se puede cancelar una subasta que ya recibió pujas")
        subasta.estado = EstadoSubasta.CANCELADA
        self.session.commit()
        self.session.refresh(subasta)
        return subasta

    def eliminar(self, subasta_id: int) -> bool:
        subasta = self.obtener_por_id(subasta_id)
        if subasta is None:
            return False
        self.session.delete(subasta)
        self.session.commit()
        return True
