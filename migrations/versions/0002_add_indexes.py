"""agrega índices de rendimiento sobre las FKs más consultadas

Revision ID: 0002_add_indexes
Revises: 0001_initial
Create Date: 2026-09-14
"""
from __future__ import annotations

from alembic import op

revision = "0002_add_indexes"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Acelera el historial de pujas por subasta y por usuario (evita full scan
    # en el join que resuelve el problema N+1 del repositorio de Puja).
    op.create_index("ix_puja_subasta_id", "puja", ["subasta_id"])
    op.create_index("ix_puja_postor_id", "puja", ["postor_id"])
    # Acelera "listar_por_vendedor" del repositorio de Articulo.
    op.create_index("ix_articulo_vendedor_id", "articulo", ["vendedor_id"])
    # Acelera el filtro de subastas activas que consulta el scheduler concurrente.
    op.create_index("ix_subasta_estado", "subasta", ["estado"])


def downgrade() -> None:
    op.drop_index("ix_subasta_estado", table_name="subasta")
    op.drop_index("ix_articulo_vendedor_id", table_name="articulo")
    op.drop_index("ix_puja_postor_id", table_name="puja")
    op.drop_index("ix_puja_subasta_id", table_name="puja")
