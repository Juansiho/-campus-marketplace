from __future__ import annotations

from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload

from app.models import EstadoSubasta, Puja, Subasta


class PujaRepository:
    """Repositorio CRUD para la entidad Puja."""

    def __init__(self, session: Session):
        self.session = session

    def registrar_puja(self, subasta_id: int, postor_id: int, monto: float) -> Puja:
        """
        Registra una puja de forma atómica: bloquea la fila de la subasta
        (SELECT ... FOR UPDATE en MySQL) para que dos pujas concurrentes
        no lean el mismo "monto actual" y ambas crean que ganaron.
        """
        subasta = (
            self.session.execute(
                select(Subasta).where(Subasta.id == subasta_id).with_for_update()
            )
            .scalars()
            .first()
        )
        if subasta is None:
            raise ValueError("Subasta no encontrada")
        if subasta.estado != EstadoSubasta.ACTIVA:
            raise ValueError("La subasta no está activa")
        if subasta.articulo.vendedor_id == postor_id:
            raise ValueError("El vendedor no puede pujar por su propio artículo")

        monto_actual = self.monto_maximo_actual(subasta_id) or float(subasta.articulo.precio_base)
        if monto <= monto_actual:
            raise ValueError(f"La puja debe superar el monto actual ({monto_actual})")

        puja = Puja(subasta_id=subasta_id, postor_id=postor_id, monto=monto)
        self.session.add(puja)
        self.session.commit()
        self.session.refresh(puja)
        return puja

    def monto_maximo_actual(self, subasta_id: int) -> float | None:
        stmt = select(func.max(Puja.monto)).where(Puja.subasta_id == subasta_id)
        return self.session.scalar(stmt)

    def historial_por_subasta(self, subasta_id: int) -> list[Puja]:
        """
        Trae el historial de pujas de una subasta con el postor ya cargado
        (JOIN), evitando el N+1 de acceder a `puja.postor` fila por fila.
        """
        stmt = (
            select(Puja)
            .options(joinedload(Puja.postor))
            .where(Puja.subasta_id == subasta_id)
            .order_by(Puja.monto.desc())
        )
        return list(self.session.scalars(stmt).unique().all())

    def historial_por_usuario(self, usuario_id: int) -> list[Puja]:
        stmt = (
            select(Puja)
            .options(joinedload(Puja.subasta))
            .where(Puja.postor_id == usuario_id)
            .order_by(Puja.fecha.desc())
        )
        return list(self.session.scalars(stmt).unique().all())

    def eliminar(self, puja_id: int) -> bool:
        puja = self.session.get(Puja, puja_id)
        if puja is None:
            return False
        self.session.delete(puja)
        self.session.commit()
        return True
