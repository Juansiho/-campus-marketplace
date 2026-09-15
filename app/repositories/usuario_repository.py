from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Usuario


class UsuarioRepository:
    """Repositorio CRUD para la entidad Usuario."""

    def __init__(self, session: Session):
        self.session = session

    def crear(self, nombre_completo: str, email: str, password_hash: str) -> Usuario:
        usuario = Usuario(
            nombre_completo=nombre_completo, email=email, password_hash=password_hash
        )
        self.session.add(usuario)
        self.session.commit()
        self.session.refresh(usuario)
        return usuario

    def obtener_por_id(self, usuario_id: int) -> Usuario | None:
        return self.session.get(Usuario, usuario_id)

    def obtener_por_email(self, email: str) -> Usuario | None:
        stmt = select(Usuario).where(Usuario.email == email)
        return self.session.scalars(stmt).first()

    def listar(self) -> list[Usuario]:
        return list(self.session.scalars(select(Usuario)).all())

    def actualizar(self, usuario_id: int, **campos) -> Usuario | None:
        usuario = self.obtener_por_id(usuario_id)
        if usuario is None:
            return None
        for campo, valor in campos.items():
            setattr(usuario, campo, valor)
        self.session.commit()
        self.session.refresh(usuario)
        return usuario

    def eliminar(self, usuario_id: int) -> bool:
        usuario = self.obtener_por_id(usuario_id)
        if usuario is None:
            return False
        self.session.delete(usuario)
        self.session.commit()
        return True
