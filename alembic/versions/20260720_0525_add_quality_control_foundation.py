"""add quality control foundation

Revision ID: 20260720_0525
Revises: 20260720_0515
Create Date: 2026-07-20 05:25:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260720_0525"
down_revision: str | None = "20260720_0515"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "qc_inspections",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("inspection_number", sa.String(length=100), nullable=False),
        sa.Column("inspection_type", sa.String(length=50), nullable=False, server_default="PRODUCTION"),
        sa.Column("stage", sa.String(length=50), nullable=False, server_default="PRODUCTION_OUTPUT"),
        sa.Column("reference_type", sa.String(length=50), nullable=False),
        sa.Column("reference_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("inspection_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("inspector_name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="DRAFT"),
        sa.Column("overall_result", sa.String(length=30), nullable=True),
        sa.Column("is_mandatory_for_release", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"], name=op.f("fk_qc_inspections_sppg_id_sppg")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_qc_inspections_tenant_id_tenants")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_qc_inspections")),
        sa.UniqueConstraint("tenant_id", "inspection_number", name="uq_qc_inspections_tenant_number"),
    )
    op.create_index(op.f("ix_qc_inspections_tenant_id"), "qc_inspections", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_qc_inspections_sppg_id"), "qc_inspections", ["sppg_id"], unique=False)
    op.create_index(op.f("ix_qc_inspections_inspection_number"), "qc_inspections", ["inspection_number"], unique=False)
    op.create_index(op.f("ix_qc_inspections_reference_id"), "qc_inspections", ["reference_id"], unique=False)

    op.create_table(
        "qc_inspection_lines",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("inspection_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("parameter_name", sa.String(length=255), nullable=False),
        sa.Column("expected_value", sa.String(length=255), nullable=True),
        sa.Column("actual_value", sa.String(length=255), nullable=True),
        sa.Column("result_status", sa.String(length=20), nullable=False, server_default="PASS"),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["inspection_id"], ["qc_inspections.id"], name=op.f("fk_qc_inspection_lines_inspection_id_qc_inspections")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_qc_inspection_lines_tenant_id_tenants")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_qc_inspection_lines")),
    )
    op.create_index(op.f("ix_qc_inspection_lines_tenant_id"), "qc_inspection_lines", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_qc_inspection_lines_inspection_id"), "qc_inspection_lines", ["inspection_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_qc_inspection_lines_inspection_id"), table_name="qc_inspection_lines")
    op.drop_index(op.f("ix_qc_inspection_lines_tenant_id"), table_name="qc_inspection_lines")
    op.drop_table("qc_inspection_lines")
    op.drop_index(op.f("ix_qc_inspections_reference_id"), table_name="qc_inspections")
    op.drop_index(op.f("ix_qc_inspections_inspection_number"), table_name="qc_inspections")
    op.drop_index(op.f("ix_qc_inspections_sppg_id"), table_name="qc_inspections")
    op.drop_index(op.f("ix_qc_inspections_tenant_id"), table_name="qc_inspections")
    op.drop_table("qc_inspections")
