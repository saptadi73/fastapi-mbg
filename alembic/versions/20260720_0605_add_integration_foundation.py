"""add integration foundation

Revision ID: 20260720_0605
Revises: 20260720_0555
Create Date: 2026-07-20 06:05:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260720_0605"
down_revision: str | None = "20260720_0555"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "external_systems",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("system_type", sa.String(length=100), nullable=False),
        sa.Column("base_url", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_external_systems_tenant_id_tenants")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_external_systems")),
        sa.UniqueConstraint("tenant_id", "code", name="uq_external_systems_tenant_code"),
    )
    op.create_index(op.f("ix_external_systems_tenant_id"), "external_systems", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_external_systems_code"), "external_systems", ["code"], unique=False)
    op.create_index(op.f("ix_external_systems_system_type"), "external_systems", ["system_type"], unique=False)

    op.create_table(
        "integration_credentials",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_system_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("credential_name", sa.String(length=100), nullable=False),
        sa.Column("credential_type", sa.String(length=50), nullable=False, server_default="API_KEY"),
        sa.Column("secret_masked", sa.String(length=255), nullable=True),
        sa.Column("config_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["external_system_id"], ["external_systems.id"], name=op.f("fk_integration_credentials_external_system_id_external_systems")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_integration_credentials_tenant_id_tenants")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_integration_credentials")),
        sa.UniqueConstraint("tenant_id", "external_system_id", "credential_name", name="uq_integration_credentials_tenant_system_name"),
    )
    op.create_index(op.f("ix_integration_credentials_tenant_id"), "integration_credentials", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_integration_credentials_external_system_id"), "integration_credentials", ["external_system_id"], unique=False)

    op.create_table(
        "sync_logs",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_system_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("direction", sa.String(length=20), nullable=False, server_default="OUTBOUND"),
        sa.Column("message_type", sa.String(length=100), nullable=False),
        sa.Column("entity_type", sa.String(length=100), nullable=True),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("external_reference", sa.String(length=255), nullable=True),
        sa.Column("idempotency_key", sa.String(length=150), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="PENDING"),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("response_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["external_system_id"], ["external_systems.id"], name=op.f("fk_sync_logs_external_system_id_external_systems")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_sync_logs_tenant_id_tenants")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sync_logs")),
        sa.UniqueConstraint("tenant_id", "external_system_id", "idempotency_key", name="uq_sync_logs_tenant_system_idempotency"),
    )
    op.create_index(op.f("ix_sync_logs_tenant_id"), "sync_logs", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_sync_logs_external_system_id"), "sync_logs", ["external_system_id"], unique=False)
    op.create_index(op.f("ix_sync_logs_idempotency_key"), "sync_logs", ["idempotency_key"], unique=False)
    op.create_index(op.f("ix_sync_logs_external_reference"), "sync_logs", ["external_reference"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_sync_logs_external_reference"), table_name="sync_logs")
    op.drop_index(op.f("ix_sync_logs_idempotency_key"), table_name="sync_logs")
    op.drop_index(op.f("ix_sync_logs_external_system_id"), table_name="sync_logs")
    op.drop_index(op.f("ix_sync_logs_tenant_id"), table_name="sync_logs")
    op.drop_table("sync_logs")
    op.drop_index(op.f("ix_integration_credentials_external_system_id"), table_name="integration_credentials")
    op.drop_index(op.f("ix_integration_credentials_tenant_id"), table_name="integration_credentials")
    op.drop_table("integration_credentials")
    op.drop_index(op.f("ix_external_systems_system_type"), table_name="external_systems")
    op.drop_index(op.f("ix_external_systems_code"), table_name="external_systems")
    op.drop_index(op.f("ix_external_systems_tenant_id"), table_name="external_systems")
    op.drop_table("external_systems")
