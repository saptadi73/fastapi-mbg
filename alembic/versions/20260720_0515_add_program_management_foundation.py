"""add program management foundation

Revision ID: 20260720_0515
Revises: 20260720_0505
Create Date: 2026-07-20 05:15:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260720_0515"
down_revision: str | None = "20260720_0505"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "programs",
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column("program_type", sa.String(length=50), nullable=False, server_default="PUBLIC"),
        sa.Column("funding_source_name", sa.String(length=255), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="DRAFT"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_programs")),
    )
    op.create_index(op.f("ix_programs_code"), "programs", ["code"], unique=True)

    op.create_table(
        "program_periods",
        sa.Column("program_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("date_start", sa.Date(), nullable=False),
        sa.Column("date_end", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="DRAFT"),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["program_id"], ["programs.id"], name=op.f("fk_program_periods_program_id_programs")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_program_periods")),
        sa.UniqueConstraint("program_id", "code", name="uq_program_periods_program_code"),
    )
    op.create_index(op.f("ix_program_periods_program_id"), "program_periods", ["program_id"], unique=False)

    op.create_table(
        "program_tenants",
        sa.Column("program_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["program_id"], ["programs.id"], name=op.f("fk_program_tenants_program_id_programs")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_program_tenants_tenant_id_tenants")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_program_tenants")),
        sa.UniqueConstraint("program_id", "tenant_id", name="uq_program_tenants_program_tenant"),
    )
    op.create_index(op.f("ix_program_tenants_program_id"), "program_tenants", ["program_id"], unique=False)
    op.create_index(op.f("ix_program_tenants_tenant_id"), "program_tenants", ["tenant_id"], unique=False)

    op.create_table(
        "program_sppg",
        sa.Column("program_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["program_id"], ["programs.id"], name=op.f("fk_program_sppg_program_id_programs")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_program_sppg_tenant_id_tenants")),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"], name=op.f("fk_program_sppg_sppg_id_sppg")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_program_sppg")),
        sa.UniqueConstraint("program_id", "sppg_id", name="uq_program_sppg_program_sppg"),
    )
    op.create_index(op.f("ix_program_sppg_program_id"), "program_sppg", ["program_id"], unique=False)
    op.create_index(op.f("ix_program_sppg_tenant_id"), "program_sppg", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_program_sppg_sppg_id"), "program_sppg", ["sppg_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_program_sppg_sppg_id"), table_name="program_sppg")
    op.drop_index(op.f("ix_program_sppg_tenant_id"), table_name="program_sppg")
    op.drop_index(op.f("ix_program_sppg_program_id"), table_name="program_sppg")
    op.drop_table("program_sppg")
    op.drop_index(op.f("ix_program_tenants_tenant_id"), table_name="program_tenants")
    op.drop_index(op.f("ix_program_tenants_program_id"), table_name="program_tenants")
    op.drop_table("program_tenants")
    op.drop_index(op.f("ix_program_periods_program_id"), table_name="program_periods")
    op.drop_table("program_periods")
    op.drop_index(op.f("ix_programs_code"), table_name="programs")
    op.drop_table("programs")
