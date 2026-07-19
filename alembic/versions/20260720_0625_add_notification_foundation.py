"""add notification foundation

Revision ID: 20260720_0625
Revises: 20260720_0615
Create Date: 2026-07-20 06:25:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260720_0625"
down_revision: str | Sequence[str] | None = "20260720_0615"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "notification_templates",
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("channel", sa.String(length=50), nullable=False),
        sa.Column("subject_template", sa.String(length=255), nullable=True),
        sa.Column("body_template", sa.String(length=4000), nullable=False),
        sa.Column("variables_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "code", name="uq_notification_templates_tenant_code"),
    )
    op.create_index(op.f("ix_notification_templates_code"), "notification_templates", ["code"], unique=False)
    op.create_index(op.f("ix_notification_templates_tenant_id"), "notification_templates", ["tenant_id"], unique=False)

    op.create_table(
        "notifications",
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("template_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("source_module", sa.String(length=100), nullable=True),
        sa.Column("source_entity_type", sa.String(length=100), nullable=True),
        sa.Column("source_entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message", sa.String(length=4000), nullable=False),
        sa.Column("priority", sa.String(length=50), nullable=False, server_default="NORMAL"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="QUEUED"),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"]),
        sa.ForeignKeyConstraint(["template_id"], ["notification_templates.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notifications_priority"), "notifications", ["priority"], unique=False)
    op.create_index(op.f("ix_notifications_source_entity_id"), "notifications", ["source_entity_id"], unique=False)
    op.create_index(op.f("ix_notifications_source_module"), "notifications", ["source_module"], unique=False)
    op.create_index(op.f("ix_notifications_sppg_id"), "notifications", ["sppg_id"], unique=False)
    op.create_index(op.f("ix_notifications_status"), "notifications", ["status"], unique=False)
    op.create_index(op.f("ix_notifications_template_id"), "notifications", ["template_id"], unique=False)
    op.create_index(op.f("ix_notifications_tenant_id"), "notifications", ["tenant_id"], unique=False)

    op.create_table(
        "notification_recipients",
        sa.Column("notification_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("channel", sa.String(length=50), nullable=False),
        sa.Column("recipient_address", sa.String(length=255), nullable=True),
        sa.Column("delivery_status", sa.String(length=50), nullable=False, server_default="QUEUED"),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["notification_id"], ["notifications.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notification_recipients_channel"), "notification_recipients", ["channel"], unique=False)
    op.create_index(op.f("ix_notification_recipients_delivery_status"), "notification_recipients", ["delivery_status"], unique=False)
    op.create_index(op.f("ix_notification_recipients_notification_id"), "notification_recipients", ["notification_id"], unique=False)
    op.create_index(op.f("ix_notification_recipients_tenant_id"), "notification_recipients", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_notification_recipients_user_id"), "notification_recipients", ["user_id"], unique=False)

    op.create_table(
        "notification_deliveries",
        sa.Column("notification_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("recipient_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("channel", sa.String(length=50), nullable=False),
        sa.Column("provider_name", sa.String(length=100), nullable=True),
        sa.Column("provider_message_id", sa.String(length=255), nullable=True),
        sa.Column("attempt_no", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="QUEUED"),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failure_reason", sa.String(length=1000), nullable=True),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("response_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["notification_id"], ["notifications.id"]),
        sa.ForeignKeyConstraint(["recipient_id"], ["notification_recipients.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notification_deliveries_channel"), "notification_deliveries", ["channel"], unique=False)
    op.create_index(op.f("ix_notification_deliveries_notification_id"), "notification_deliveries", ["notification_id"], unique=False)
    op.create_index(op.f("ix_notification_deliveries_recipient_id"), "notification_deliveries", ["recipient_id"], unique=False)
    op.create_index(op.f("ix_notification_deliveries_status"), "notification_deliveries", ["status"], unique=False)
    op.create_index(op.f("ix_notification_deliveries_tenant_id"), "notification_deliveries", ["tenant_id"], unique=False)

    op.create_table(
        "notification_preferences",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("channel", sa.String(length=50), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("quiet_hours_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("config_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "user_id", "channel", name="uq_notification_preferences_tenant_user_channel"),
    )
    op.create_index(op.f("ix_notification_preferences_channel"), "notification_preferences", ["channel"], unique=False)
    op.create_index(op.f("ix_notification_preferences_tenant_id"), "notification_preferences", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_notification_preferences_user_id"), "notification_preferences", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_notification_preferences_user_id"), table_name="notification_preferences")
    op.drop_index(op.f("ix_notification_preferences_tenant_id"), table_name="notification_preferences")
    op.drop_index(op.f("ix_notification_preferences_channel"), table_name="notification_preferences")
    op.drop_table("notification_preferences")

    op.drop_index(op.f("ix_notification_deliveries_tenant_id"), table_name="notification_deliveries")
    op.drop_index(op.f("ix_notification_deliveries_status"), table_name="notification_deliveries")
    op.drop_index(op.f("ix_notification_deliveries_recipient_id"), table_name="notification_deliveries")
    op.drop_index(op.f("ix_notification_deliveries_notification_id"), table_name="notification_deliveries")
    op.drop_index(op.f("ix_notification_deliveries_channel"), table_name="notification_deliveries")
    op.drop_table("notification_deliveries")

    op.drop_index(op.f("ix_notification_recipients_user_id"), table_name="notification_recipients")
    op.drop_index(op.f("ix_notification_recipients_tenant_id"), table_name="notification_recipients")
    op.drop_index(op.f("ix_notification_recipients_notification_id"), table_name="notification_recipients")
    op.drop_index(op.f("ix_notification_recipients_delivery_status"), table_name="notification_recipients")
    op.drop_index(op.f("ix_notification_recipients_channel"), table_name="notification_recipients")
    op.drop_table("notification_recipients")

    op.drop_index(op.f("ix_notifications_tenant_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_template_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_status"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_sppg_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_source_module"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_source_entity_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_priority"), table_name="notifications")
    op.drop_table("notifications")

    op.drop_index(op.f("ix_notification_templates_tenant_id"), table_name="notification_templates")
    op.drop_index(op.f("ix_notification_templates_code"), table_name="notification_templates")
    op.drop_table("notification_templates")
