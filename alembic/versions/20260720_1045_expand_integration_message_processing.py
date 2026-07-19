"""expand integration message processing

Revision ID: 20260720_1045
Revises: 20260720_1015
Create Date: 2026-07-20 10:45:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260720_1045"
down_revision: str | Sequence[str] | None = "20260720_1015"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "webhook_subscriptions",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_system_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subscription_name", sa.String(length=120), nullable=False),
        sa.Column("event_type", sa.String(length=120), nullable=False),
        sa.Column("endpoint_path", sa.String(length=255), nullable=False),
        sa.Column("signing_secret_masked", sa.String(length=255), nullable=True),
        sa.Column("headers_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("last_received_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["external_system_id"], ["external_systems.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "external_system_id", "subscription_name", name="uq_webhook_subscriptions_tenant_system_name"),
    )
    op.create_index("ix_webhook_subscriptions_tenant_id", "webhook_subscriptions", ["tenant_id"], unique=False)
    op.create_index("ix_webhook_subscriptions_external_system_id", "webhook_subscriptions", ["external_system_id"], unique=False)
    op.create_index("ix_webhook_subscriptions_event_type", "webhook_subscriptions", ["event_type"], unique=False)

    op.create_table(
        "data_mappings",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_system_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mapping_name", sa.String(length=120), nullable=False),
        sa.Column("source_entity", sa.String(length=120), nullable=False),
        sa.Column("target_entity", sa.String(length=120), nullable=False),
        sa.Column("direction", sa.String(length=20), nullable=False, server_default="BIDIRECTIONAL"),
        sa.Column("mapping_config_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["external_system_id"], ["external_systems.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "external_system_id", "mapping_name", name="uq_data_mappings_tenant_system_name"),
    )
    op.create_index("ix_data_mappings_tenant_id", "data_mappings", ["tenant_id"], unique=False)
    op.create_index("ix_data_mappings_external_system_id", "data_mappings", ["external_system_id"], unique=False)

    op.create_table(
        "sync_jobs",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_system_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_name", sa.String(length=120), nullable=False),
        sa.Column("direction", sa.String(length=20), nullable=False, server_default="OUTBOUND"),
        sa.Column("trigger_mode", sa.String(length=30), nullable=False, server_default="MANUAL"),
        sa.Column("entity_type", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="READY"),
        sa.Column("schedule_expression", sa.String(length=120), nullable=True),
        sa.Column("filter_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_success_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["external_system_id"], ["external_systems.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "external_system_id", "job_name", name="uq_sync_jobs_tenant_system_job"),
    )
    op.create_index("ix_sync_jobs_tenant_id", "sync_jobs", ["tenant_id"], unique=False)
    op.create_index("ix_sync_jobs_external_system_id", "sync_jobs", ["external_system_id"], unique=False)

    op.create_table(
        "inbound_messages",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_system_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("webhook_subscription_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("message_type", sa.String(length=120), nullable=False),
        sa.Column("external_reference", sa.String(length=255), nullable=True),
        sa.Column("idempotency_key", sa.String(length=150), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="RECEIVED"),
        sa.Column("headers_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["external_system_id"], ["external_systems.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["webhook_subscription_id"], ["webhook_subscriptions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "external_system_id", "idempotency_key", name="uq_inbound_messages_tenant_system_idempotency"),
    )
    op.create_index("ix_inbound_messages_tenant_id", "inbound_messages", ["tenant_id"], unique=False)
    op.create_index("ix_inbound_messages_external_system_id", "inbound_messages", ["external_system_id"], unique=False)
    op.create_index("ix_inbound_messages_webhook_subscription_id", "inbound_messages", ["webhook_subscription_id"], unique=False)
    op.create_index("ix_inbound_messages_external_reference", "inbound_messages", ["external_reference"], unique=False)
    op.create_index("ix_inbound_messages_idempotency_key", "inbound_messages", ["idempotency_key"], unique=False)

    op.create_table(
        "outbound_messages",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_system_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sync_job_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("message_type", sa.String(length=120), nullable=False),
        sa.Column("entity_type", sa.String(length=120), nullable=True),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("external_reference", sa.String(length=255), nullable=True),
        sa.Column("idempotency_key", sa.String(length=150), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="QUEUED"),
        sa.Column("destination_url", sa.String(length=500), nullable=True),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("response_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("queued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["external_system_id"], ["external_systems.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["sync_job_id"], ["sync_jobs.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "external_system_id", "idempotency_key", name="uq_outbound_messages_tenant_system_idempotency"),
    )
    op.create_index("ix_outbound_messages_tenant_id", "outbound_messages", ["tenant_id"], unique=False)
    op.create_index("ix_outbound_messages_external_system_id", "outbound_messages", ["external_system_id"], unique=False)
    op.create_index("ix_outbound_messages_sync_job_id", "outbound_messages", ["sync_job_id"], unique=False)
    op.create_index("ix_outbound_messages_external_reference", "outbound_messages", ["external_reference"], unique=False)
    op.create_index("ix_outbound_messages_idempotency_key", "outbound_messages", ["idempotency_key"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_outbound_messages_idempotency_key", table_name="outbound_messages")
    op.drop_index("ix_outbound_messages_external_reference", table_name="outbound_messages")
    op.drop_index("ix_outbound_messages_sync_job_id", table_name="outbound_messages")
    op.drop_index("ix_outbound_messages_external_system_id", table_name="outbound_messages")
    op.drop_index("ix_outbound_messages_tenant_id", table_name="outbound_messages")
    op.drop_table("outbound_messages")

    op.drop_index("ix_inbound_messages_idempotency_key", table_name="inbound_messages")
    op.drop_index("ix_inbound_messages_external_reference", table_name="inbound_messages")
    op.drop_index("ix_inbound_messages_webhook_subscription_id", table_name="inbound_messages")
    op.drop_index("ix_inbound_messages_external_system_id", table_name="inbound_messages")
    op.drop_index("ix_inbound_messages_tenant_id", table_name="inbound_messages")
    op.drop_table("inbound_messages")

    op.drop_index("ix_sync_jobs_external_system_id", table_name="sync_jobs")
    op.drop_index("ix_sync_jobs_tenant_id", table_name="sync_jobs")
    op.drop_table("sync_jobs")

    op.drop_index("ix_data_mappings_external_system_id", table_name="data_mappings")
    op.drop_index("ix_data_mappings_tenant_id", table_name="data_mappings")
    op.drop_table("data_mappings")

    op.drop_index("ix_webhook_subscriptions_event_type", table_name="webhook_subscriptions")
    op.drop_index("ix_webhook_subscriptions_external_system_id", table_name="webhook_subscriptions")
    op.drop_index("ix_webhook_subscriptions_tenant_id", table_name="webhook_subscriptions")
    op.drop_table("webhook_subscriptions")
