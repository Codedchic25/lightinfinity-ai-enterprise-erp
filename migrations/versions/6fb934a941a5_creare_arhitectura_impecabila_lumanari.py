"""creare_arhitectura_impecabila_lumanari

Revision ID: 6fb934a941a5
Revises:
Create Date: 2026-09-15 13:20:16.637319

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6fb934a941a5"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the initial enterprise database schema."""
    op.create_table(
        "ceara",
        sa.Column("id_ceara", sa.Integer(), nullable=False),
        sa.Column("nume_ceara", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id_ceara"),
    )
    op.create_index(
        op.f("ix_ceara_id_ceara"),
        "ceara",
        ["id_ceara"],
        unique=False,
    )

    op.create_table(
        "clienti",
        sa.Column("id_client", sa.Integer(), nullable=False),
        sa.Column("nume", sa.String(length=200), nullable=False),
        sa.Column("telefon", sa.String(length=20), nullable=True),
        sa.Column("email", sa.String(length=150), nullable=False),
        sa.Column("parola_hash", sa.String(length=250), nullable=True),
        sa.PrimaryKeyConstraint("id_client"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(
        op.f("ix_clienti_id_client"),
        "clienti",
        ["id_client"],
        unique=False,
    )

    op.create_table(
        "culori",
        sa.Column("id_culoare", sa.Integer(), nullable=False),
        sa.Column("nume_culoare", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id_culoare"),
    )
    op.create_index(
        op.f("ix_culori_id_culoare"),
        "culori",
        ["id_culoare"],
        unique=False,
    )

    op.create_table(
        "forme",
        sa.Column("id_forma", sa.Integer(), nullable=False),
        sa.Column("nume_forma", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id_forma"),
    )
    op.create_index(
        op.f("ix_forme_id_forma"),
        "forme",
        ["id_forma"],
        unique=False,
    )

    op.create_table(
        "materiale",
        sa.Column("id_material", sa.Integer(), nullable=False),
        sa.Column("nume_material", sa.String(length=200), nullable=False),
        sa.Column("unitate", sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint("id_material"),
    )
    op.create_index(
        op.f("ix_materiale_id_material"),
        "materiale",
        ["id_material"],
        unique=False,
    )

    op.create_table(
        "parfumuri",
        sa.Column("id_parfum", sa.Integer(), nullable=False),
        sa.Column("nume_parfum", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id_parfum"),
    )
    op.create_index(
        op.f("ix_parfumuri_id_parfum"),
        "parfumuri",
        ["id_parfum"],
        unique=False,
    )

    op.create_table(
        "sezoane",
        sa.Column("id_sezon", sa.Integer(), nullable=False),
        sa.Column("nume_sezon", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id_sezon"),
    )
    op.create_index(
        op.f("ix_sezoane_id_sezon"),
        "sezoane",
        ["id_sezon"],
        unique=False,
    )

    op.create_table(
        "comenzi",
        sa.Column("id_comanda", sa.Integer(), nullable=False),
        sa.Column("id_client", sa.Integer(), nullable=True),
        sa.Column("data_comanda", sa.Date(), nullable=True),
        sa.Column("total", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.ForeignKeyConstraint(["id_client"], ["clienti.id_client"]),
        sa.PrimaryKeyConstraint("id_comanda"),
    )
    op.create_index(
        op.f("ix_comenzi_id_comanda"),
        "comenzi",
        ["id_comanda"],
        unique=False,
    )

    op.create_table(
        "lumanari",
        sa.Column("id_lumanare", sa.Integer(), nullable=False),
        sa.Column("nume", sa.String(length=200), nullable=False),
        sa.Column("id_ceara", sa.Integer(), nullable=True),
        sa.Column("id_sezon", sa.Integer(), nullable=True),
        sa.Column("id_forma", sa.Integer(), nullable=True),
        sa.Column("id_parfum", sa.Integer(), nullable=True),
        sa.Column("id_culoare", sa.Integer(), nullable=True),
        sa.Column("pret", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("stoc", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["id_ceara"], ["ceara.id_ceara"]),
        sa.ForeignKeyConstraint(["id_culoare"], ["culori.id_culoare"]),
        sa.ForeignKeyConstraint(["id_forma"], ["forme.id_forma"]),
        sa.ForeignKeyConstraint(["id_parfum"], ["parfumuri.id_parfum"]),
        sa.ForeignKeyConstraint(["id_sezon"], ["sezoane.id_sezon"]),
        sa.PrimaryKeyConstraint("id_lumanare"),
    )
    op.create_index(
        op.f("ix_lumanari_id_lumanare"),
        "lumanari",
        ["id_lumanare"],
        unique=False,
    )

    op.create_table(
        "pivot_comanda_lumanare",
        sa.Column("id_pivot", sa.Integer(), nullable=False),
        sa.Column("id_comanda", sa.Integer(), nullable=True),
        sa.Column("id_lumanare", sa.Integer(), nullable=True),
        sa.Column("cantitate", sa.Integer(), nullable=False),
        sa.Column("pret_unitar", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.ForeignKeyConstraint(["id_comanda"], ["comenzi.id_comanda"]),
        sa.ForeignKeyConstraint(["id_lumanare"], ["lumanari.id_lumanare"]),
        sa.PrimaryKeyConstraint("id_pivot"),
    )
    op.create_index(
        op.f("ix_pivot_comanda_lumanare_id_pivot"),
        "pivot_comanda_lumanare",
        ["id_pivot"],
        unique=False,
    )

    op.create_table(
        "productie",
        sa.Column("id_productie", sa.Integer(), nullable=False),
        sa.Column("id_lumanare", sa.Integer(), nullable=True),
        sa.Column("data_productie", sa.Date(), nullable=True),
        sa.Column("cantitate", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["id_lumanare"], ["lumanari.id_lumanare"]),
        sa.PrimaryKeyConstraint("id_productie"),
    )
    op.create_index(
        op.f("ix_productie_id_productie"),
        "productie",
        ["id_productie"],
        unique=False,
    )

    op.create_table(
        "consum_materiale",
        sa.Column("id_consum", sa.Integer(), nullable=False),
        sa.Column("id_productie", sa.Integer(), nullable=True),
        sa.Column("id_material", sa.Integer(), nullable=True),
        sa.Column("cantitate_consumata", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.ForeignKeyConstraint(["id_material"], ["materiale.id_material"]),
        sa.ForeignKeyConstraint(["id_productie"], ["productie.id_productie"]),
        sa.PrimaryKeyConstraint("id_consum"),
    )
    op.create_index(
        op.f("ix_consum_materiale_id_consum"),
        "consum_materiale",
        ["id_consum"],
        unique=False,
    )


def downgrade() -> None:
    """Drop the initial enterprise database schema."""
    op.drop_index(op.f("ix_consum_materiale_id_consum"), table_name="consum_materiale")
    op.drop_table("consum_materiale")

    op.drop_index(op.f("ix_productie_id_productie"), table_name="productie")
    op.drop_table("productie")

    op.drop_index(op.f("ix_pivot_comanda_lumanare_id_pivot"), table_name="pivot_comanda_lumanare")
    op.drop_table("pivot_comanda_lumanare")

    op.drop_index(op.f("ix_lumanari_id_lumanare"), table_name="lumanari")
    op.drop_table("lumanari")

    op.drop_index(op.f("ix_comenzi_id_comanda"), table_name="comenzi")
    op.drop_table("comenzi")

    op.drop_index(op.f("ix_sezoane_id_sezon"), table_name="sezoane")
    op.drop_table("sezoane")

    op.drop_index(op.f("ix_parfumuri_id_parfum"), table_name="parfumuri")
    op.drop_table("parfumuri")

    op.drop_index(op.f("ix_materiale_id_material"), table_name="materiale")
    op.drop_table("materiale")

    op.drop_index(op.f("ix_forme_id_forma"), table_name="forme")
    op.drop_table("forme")

    op.drop_index(op.f("ix_culori_id_culoare"), table_name="culori")
    op.drop_table("culori")

    op.drop_index(op.f("ix_clienti_id_client"), table_name="clienti")
    op.drop_table("clienti")

    op.drop_index(op.f("ix_ceara_id_ceara"), table_name="ceara")
    op.drop_table("ceara")
