"""creación inicial de tablas (Usuario, Articulo, Subasta, Puja, Notificacion, MetricaConcurrencia)

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-14
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "usuario",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("nombre_completo", sa.String(120), nullable=False),
        sa.Column("email", sa.String(150), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("fecha_registro", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "articulo",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("titulo", sa.String(150), nullable=False),
        sa.Column("descripcion", sa.String(1000), nullable=True),
        sa.Column("precio_base", sa.Numeric(10, 2), nullable=False),
        sa.Column("categoria", sa.String(60), nullable=False, server_default="general"),
        sa.Column("fecha_publicacion", sa.DateTime, server_default=sa.func.now()),
        sa.Column("vendedor_id", sa.Integer, sa.ForeignKey("usuario.id"), nullable=False),
        sa.CheckConstraint("precio_base > 0", name="ck_articulo_precio_base_positivo"),
    )

    op.create_table(
        "subasta",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("articulo_id", sa.Integer, sa.ForeignKey("articulo.id"), nullable=False, unique=True),
        sa.Column("fecha_inicio", sa.DateTime, server_default=sa.func.now()),
        sa.Column("fecha_cierre", sa.DateTime, nullable=False),
        sa.Column(
            "estado",
            sa.Enum("ACTIVA", "CERRADA", "CANCELADA", name="estadosubasta"),
            nullable=False,
            server_default="ACTIVA",
        ),
    )

    op.create_table(
        "puja",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("subasta_id", sa.Integer, sa.ForeignKey("subasta.id"), nullable=False),
        sa.Column("postor_id", sa.Integer, sa.ForeignKey("usuario.id"), nullable=False),
        sa.Column("monto", sa.Numeric(10, 2), nullable=False),
        sa.Column("fecha", sa.DateTime, server_default=sa.func.now()),
        sa.CheckConstraint("monto > 0", name="ck_puja_monto_positivo"),
    )

    op.create_table(
        "notificacion",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("usuario_id", sa.Integer, sa.ForeignKey("usuario.id"), nullable=False),
        sa.Column("mensaje", sa.String(300), nullable=False),
        sa.Column("leida", sa.Boolean, server_default=sa.false()),
        sa.Column("fecha", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "metrica_concurrencia",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("subasta_id", sa.Integer, sa.ForeignKey("subasta.id"), nullable=False),
        sa.Column("pujas_por_segundo", sa.Numeric(6, 2), server_default="0"),
        sa.Column("conflictos_resueltos", sa.Integer, server_default="0"),
        sa.Column("fecha_registro", sa.DateTime, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("metrica_concurrencia")
    op.drop_table("notificacion")
    op.drop_table("puja")
    op.drop_table("subasta")
    op.drop_table("articulo")
    op.drop_table("usuario")
