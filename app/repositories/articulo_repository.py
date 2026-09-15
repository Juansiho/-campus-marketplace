from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import Articulo


class ArticuloRepository:
    """Repositorio CRUD para la entidad Articulo."""

    def __init__(self, session: Session):
        self.session = session

    def crear(self, titulo: str, precio_base: float, vendedor_id: int, **extra) -> Articulo:
        articulo = Articulo(
            titulo=titulo, precio_base=precio_base, vendedor_id=vendedor_id, **extra
        )
        self.session.add(articulo)
        self.session.commit()
        self.session.refresh(articulo)
        return articulo

    def obtener_por_id(self, articulo_id: int) -> Articulo | None:
        return self.session.get(Articulo, articulo_id)

    def listar_por_vendedor(self, vendedor_id: int) -> list[Articulo]:
        """
        Trae los artículos de un vendedor junto con su vendedor y su subasta
        en UNA sola consulta (JOIN), evitando el problema N+1 que aparecería
        si se accediera a `articulo.vendedor` o `articulo.subasta` por cada
        fila de forma perezosa (lazy load).
        """
        stmt = (
            select(Articulo)
            .options(joinedload(Articulo.vendedor), joinedload(Articulo.subasta))
            .where(Articulo.vendedor_id == vendedor_id)
        )
        return list(self.session.scalars(stmt).unique().all())

    def listar(self) -> list[Articulo]:
        return list(self.session.scalars(select(Articulo)).all())

    def actualizar(self, articulo_id: int, **campos) -> Articulo | None:
        articulo = self.obtener_por_id(articulo_id)
        if articulo is None:
            return None
        for campo, valor in campos.items():
            setattr(articulo, campo, valor)
        self.session.commit()
        self.session.refresh(articulo)
        return articulo

    def eliminar(self, articulo_id: int) -> bool:
        articulo = self.obtener_por_id(articulo_id)
        if articulo is None:
            return False
        self.session.delete(articulo)
        self.session.commit()
        return True
