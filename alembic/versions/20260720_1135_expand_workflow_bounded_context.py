"""expand workflow bounded context

Revision ID: 20260720_1135
Revises: 20260720_1115
Create Date: 2026-07-20 11:35:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260720_1135"
down_revision: str | Sequence[str] | None = "20260720_1115"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "workflow_versions",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workflow_definition_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="DRAFT"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["workflow_definition_id"], ["workflow_definitions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workflow_definition_id", "version_number", name="uq_workflow_versions_definition_number"),
    )
    op.create_index("ix_workflow_versions_tenant_id", "workflow_versions", ["tenant_id"], unique=False)
    op.create_index("ix_workflow_versions_workflow_definition_id", "workflow_versions", ["workflow_definition_id"], unique=False)

    op.create_table(
        "workflow_states",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workflow_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("state_code", sa.String(length=50), nullable=False),
        sa.Column("state_name", sa.String(length=255), nullable=False),
        sa.Column("sequence_number", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("is_initial", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_terminal", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("sla_hours", sa.Integer(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["workflow_version_id"], ["workflow_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workflow_version_id", "state_code", name="uq_workflow_states_version_code"),
    )
    op.create_index("ix_workflow_states_tenant_id", "workflow_states", ["tenant_id"], unique=False)
    op.create_index("ix_workflow_states_workflow_version_id", "workflow_states", ["workflow_version_id"], unique=False)

    op.create_table(
        "workflow_actions",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workflow_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action_code", sa.String(length=50), nullable=False),
        sa.Column("action_name", sa.String(length=255), nullable=False),
        sa.Column("allowed_role", sa.String(length=100), nullable=True),
        sa.Column("requires_approval", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["workflow_version_id"], ["workflow_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workflow_version_id", "action_code", name="uq_workflow_actions_version_code"),
    )
    op.create_index("ix_workflow_actions_tenant_id", "workflow_actions", ["tenant_id"], unique=False)
    op.create_index("ix_workflow_actions_workflow_version_id", "workflow_actions", ["workflow_version_id"], unique=False)

    op.add_column("workflow_instances", sa.Column("workflow_version_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key("fk_workflow_instances_version_id", "workflow_instances", "workflow_versions", ["workflow_version_id"], ["id"])
    op.create_index("ix_workflow_instances_workflow_version_id", "workflow_instances", ["workflow_version_id"], unique=False)

    op.create_table(
        "approval_requests",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workflow_instance_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("requested_state", sa.String(length=50), nullable=False),
        sa.Column("requested_action", sa.String(length=50), nullable=False),
        sa.Column("requested_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("requested_by_name", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="PENDING"),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["workflow_instance_id"], ["workflow_instances.id"]),
        sa.ForeignKeyConstraint(["requested_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_approval_requests_tenant_id", "approval_requests", ["tenant_id"], unique=False)
    op.create_index("ix_approval_requests_workflow_instance_id", "approval_requests", ["workflow_instance_id"], unique=False)

    op.create_table(
        "approval_decisions",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("approval_request_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("decision", sa.String(length=30), nullable=False),
        sa.Column("decision_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("decision_by_name", sa.String(length=255), nullable=True),
        sa.Column("decision_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["approval_request_id"], ["approval_requests.id"]),
        sa.ForeignKeyConstraint(["decision_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_approval_decisions_tenant_id", "approval_decisions", ["tenant_id"], unique=False)
    op.create_index("ix_approval_decisions_approval_request_id", "approval_decisions", ["approval_request_id"], unique=False)

    op.add_column("workflow_history", sa.Column("approval_request_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key("fk_workflow_history_approval_request_id", "workflow_history", "approval_requests", ["approval_request_id"], ["id"])
    op.create_index("ix_workflow_history_approval_request_id", "workflow_history", ["approval_request_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_workflow_history_approval_request_id", table_name="workflow_history")
    op.drop_constraint("fk_workflow_history_approval_request_id", "workflow_history", type_="foreignkey")
    op.drop_column("workflow_history", "approval_request_id")

    op.drop_index("ix_approval_decisions_approval_request_id", table_name="approval_decisions")
    op.drop_index("ix_approval_decisions_tenant_id", table_name="approval_decisions")
    op.drop_table("approval_decisions")

    op.drop_index("ix_approval_requests_workflow_instance_id", table_name="approval_requests")
    op.drop_index("ix_approval_requests_tenant_id", table_name="approval_requests")
    op.drop_table("approval_requests")

    op.drop_index("ix_workflow_instances_workflow_version_id", table_name="workflow_instances")
    op.drop_constraint("fk_workflow_instances_version_id", "workflow_instances", type_="foreignkey")
    op.drop_column("workflow_instances", "workflow_version_id")

    op.drop_index("ix_workflow_actions_workflow_version_id", table_name="workflow_actions")
    op.drop_index("ix_workflow_actions_tenant_id", table_name="workflow_actions")
    op.drop_table("workflow_actions")

    op.drop_index("ix_workflow_states_workflow_version_id", table_name="workflow_states")
    op.drop_index("ix_workflow_states_tenant_id", table_name="workflow_states")
    op.drop_table("workflow_states")

    op.drop_index("ix_workflow_versions_workflow_definition_id", table_name="workflow_versions")
    op.drop_index("ix_workflow_versions_tenant_id", table_name="workflow_versions")
    op.drop_table("workflow_versions")
