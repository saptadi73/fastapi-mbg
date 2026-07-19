"""add asset foundation

Revision ID: 20260720_0725
Revises: 20260720_0715
Create Date: 2026-07-19 07:25:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260720_0725"
down_revision: str | Sequence[str] | None = "20260720_0715"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "asset_categories",
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("asset_account_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("depreciation_expense_account_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("accumulated_depreciation_account_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("useful_life_months", sa.Integer(), nullable=True),
        sa.Column("depreciation_method", sa.String(length=50), nullable=False, server_default="STRAIGHT_LINE"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["accumulated_depreciation_account_id"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["asset_account_id"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["depreciation_expense_account_id"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "code", name="uq_asset_categories_tenant_code"),
    )
    op.create_index(op.f("ix_asset_categories_accumulated_depreciation_account_id"), "asset_categories", ["accumulated_depreciation_account_id"], unique=False)
    op.create_index(op.f("ix_asset_categories_asset_account_id"), "asset_categories", ["asset_account_id"], unique=False)
    op.create_index(op.f("ix_asset_categories_code"), "asset_categories", ["code"], unique=False)
    op.create_index(op.f("ix_asset_categories_depreciation_expense_account_id"), "asset_categories", ["depreciation_expense_account_id"], unique=False)
    op.create_index(op.f("ix_asset_categories_tenant_id"), "asset_categories", ["tenant_id"], unique=False)

    op.create_table(
        "assets",
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("asset_category_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("asset_code", sa.String(length=100), nullable=False),
        sa.Column("asset_name", sa.String(length=255), nullable=False),
        sa.Column("acquisition_date", sa.Date(), nullable=False),
        sa.Column("acquisition_cost", sa.Float(), nullable=False, server_default="0"),
        sa.Column("residual_value", sa.Float(), nullable=False, server_default="0"),
        sa.Column("useful_life_months", sa.Integer(), nullable=True),
        sa.Column("depreciation_method", sa.String(length=50), nullable=False, server_default="STRAIGHT_LINE"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="ACTIVE"),
        sa.Column("serial_number", sa.String(length=100), nullable=True),
        sa.Column("condition_status", sa.String(length=50), nullable=True),
        sa.Column("location_name", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["asset_category_id"], ["asset_categories.id"]),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "asset_code", name="uq_assets_tenant_asset_code"),
    )
    op.create_index(op.f("ix_assets_acquisition_date"), "assets", ["acquisition_date"], unique=False)
    op.create_index(op.f("ix_assets_asset_category_id"), "assets", ["asset_category_id"], unique=False)
    op.create_index(op.f("ix_assets_asset_code"), "assets", ["asset_code"], unique=False)
    op.create_index(op.f("ix_assets_sppg_id"), "assets", ["sppg_id"], unique=False)
    op.create_index(op.f("ix_assets_status"), "assets", ["status"], unique=False)
    op.create_index(op.f("ix_assets_tenant_id"), "assets", ["tenant_id"], unique=False)

    op.create_table(
        "asset_assignments",
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("assigned_to_name", sa.String(length=255), nullable=True),
        sa.Column("assignment_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("assignment_role", sa.String(length=50), nullable=False, server_default="OPERATIONAL"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="ASSIGNED"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"]),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_asset_assignments_asset_id"), "asset_assignments", ["asset_id"], unique=False)
    op.create_index(op.f("ix_asset_assignments_assignment_date"), "asset_assignments", ["assignment_date"], unique=False)
    op.create_index(op.f("ix_asset_assignments_sppg_id"), "asset_assignments", ["sppg_id"], unique=False)
    op.create_index(op.f("ix_asset_assignments_status"), "asset_assignments", ["status"], unique=False)
    op.create_index(op.f("ix_asset_assignments_tenant_id"), "asset_assignments", ["tenant_id"], unique=False)

    op.create_table(
        "asset_depreciations",
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("journal_entry_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("depreciation_date", sa.Date(), nullable=False),
        sa.Column("depreciation_amount", sa.Float(), nullable=False, server_default="0"),
        sa.Column("accumulated_depreciation_amount", sa.Float(), nullable=False, server_default="0"),
        sa.Column("book_value_after", sa.Float(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="POSTED"),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"]),
        sa.ForeignKeyConstraint(["journal_entry_id"], ["journal_entries.id"]),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("asset_id", "depreciation_date", name="uq_asset_depreciation_asset_date"),
    )
    op.create_index(op.f("ix_asset_depreciations_asset_id"), "asset_depreciations", ["asset_id"], unique=False)
    op.create_index(op.f("ix_asset_depreciations_depreciation_date"), "asset_depreciations", ["depreciation_date"], unique=False)
    op.create_index(op.f("ix_asset_depreciations_journal_entry_id"), "asset_depreciations", ["journal_entry_id"], unique=False)
    op.create_index(op.f("ix_asset_depreciations_sppg_id"), "asset_depreciations", ["sppg_id"], unique=False)
    op.create_index(op.f("ix_asset_depreciations_status"), "asset_depreciations", ["status"], unique=False)
    op.create_index(op.f("ix_asset_depreciations_tenant_id"), "asset_depreciations", ["tenant_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_asset_depreciations_tenant_id"), table_name="asset_depreciations")
    op.drop_index(op.f("ix_asset_depreciations_status"), table_name="asset_depreciations")
    op.drop_index(op.f("ix_asset_depreciations_sppg_id"), table_name="asset_depreciations")
    op.drop_index(op.f("ix_asset_depreciations_journal_entry_id"), table_name="asset_depreciations")
    op.drop_index(op.f("ix_asset_depreciations_depreciation_date"), table_name="asset_depreciations")
    op.drop_index(op.f("ix_asset_depreciations_asset_id"), table_name="asset_depreciations")
    op.drop_table("asset_depreciations")
    op.drop_index(op.f("ix_asset_assignments_tenant_id"), table_name="asset_assignments")
    op.drop_index(op.f("ix_asset_assignments_status"), table_name="asset_assignments")
    op.drop_index(op.f("ix_asset_assignments_sppg_id"), table_name="asset_assignments")
    op.drop_index(op.f("ix_asset_assignments_assignment_date"), table_name="asset_assignments")
    op.drop_index(op.f("ix_asset_assignments_asset_id"), table_name="asset_assignments")
    op.drop_table("asset_assignments")
    op.drop_index(op.f("ix_assets_tenant_id"), table_name="assets")
    op.drop_index(op.f("ix_assets_status"), table_name="assets")
    op.drop_index(op.f("ix_assets_sppg_id"), table_name="assets")
    op.drop_index(op.f("ix_assets_asset_code"), table_name="assets")
    op.drop_index(op.f("ix_assets_asset_category_id"), table_name="assets")
    op.drop_index(op.f("ix_assets_acquisition_date"), table_name="assets")
    op.drop_table("assets")
    op.drop_index(op.f("ix_asset_categories_tenant_id"), table_name="asset_categories")
    op.drop_index(op.f("ix_asset_categories_depreciation_expense_account_id"), table_name="asset_categories")
    op.drop_index(op.f("ix_asset_categories_code"), table_name="asset_categories")
    op.drop_index(op.f("ix_asset_categories_asset_account_id"), table_name="asset_categories")
    op.drop_index(op.f("ix_asset_categories_accumulated_depreciation_account_id"), table_name="asset_categories")
    op.drop_table("asset_categories")
