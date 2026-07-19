"""add workflow foundation

Revision ID: 20260720_0535
Revises: 20260720_0525
Create Date: 2026-07-20 05:35:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260720_0535"
down_revision: str | None = "20260720_0525"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "workflow_definitions",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("document_type", sa.String(length=100), nullable=False),
        sa.Column("initial_state", sa.String(length=50), nullable=False, server_default="DRAFT"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_workflow_definitions_tenant_id_tenants")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_workflow_definitions")),
        sa.UniqueConstraint("tenant_id", "document_type", "code", name="uq_workflow_definitions_tenant_document_code"),
    )
    op.create_index(op.f("ix_workflow_definitions_tenant_id"), "workflow_definitions", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_workflow_definitions_document_type"), "workflow_definitions", ["document_type"], unique=False)

    op.create_table(
        "workflow_transitions",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workflow_definition_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("from_state", sa.String(length=50), nullable=False),
        sa.Column("action_name", sa.String(length=50), nullable=False),
        sa.Column("to_state", sa.String(length=50), nullable=False),
        sa.Column("allowed_role", sa.String(length=100), nullable=True),
        sa.Column("requires_approval", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_workflow_transitions_tenant_id_tenants")),
        sa.ForeignKeyConstraint(
            ["workflow_definition_id"],
            ["workflow_definitions.id"],
            name=op.f("fk_workflow_transitions_workflow_definition_id_workflow_definitions"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_workflow_transitions")),
        sa.UniqueConstraint(
            "workflow_definition_id",
            "from_state",
            "action_name",
            name="uq_workflow_transitions_definition_state_action",
        ),
    )
    op.create_index(op.f("ix_workflow_transitions_tenant_id"), "workflow_transitions", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_workflow_transitions_workflow_definition_id"), "workflow_transitions", ["workflow_definition_id"], unique=False)

    op.create_table(
        "workflow_instances",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workflow_definition_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_type", sa.String(length=100), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("current_state", sa.String(length=50), nullable=False),
        sa.Column("last_action", sa.String(length=50), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_workflow_instances_tenant_id_tenants")),
        sa.ForeignKeyConstraint(
            ["workflow_definition_id"],
            ["workflow_definitions.id"],
            name=op.f("fk_workflow_instances_workflow_definition_id_workflow_definitions"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_workflow_instances")),
        sa.UniqueConstraint("tenant_id", "document_type", "document_id", name="uq_workflow_instances_tenant_document"),
    )
    op.create_index(op.f("ix_workflow_instances_tenant_id"), "workflow_instances", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_workflow_instances_workflow_definition_id"), "workflow_instances", ["workflow_definition_id"], unique=False)
    op.create_index(op.f("ix_workflow_instances_document_type"), "workflow_instances", ["document_type"], unique=False)
    op.create_index(op.f("ix_workflow_instances_document_id"), "workflow_instances", ["document_id"], unique=False)

    op.create_table(
        "workflow_history",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workflow_instance_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("from_state", sa.String(length=50), nullable=True),
        sa.Column("action_name", sa.String(length=50), nullable=False),
        sa.Column("to_state", sa.String(length=50), nullable=False),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("actor_name", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], name=op.f("fk_workflow_history_actor_user_id_users")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_workflow_history_tenant_id_tenants")),
        sa.ForeignKeyConstraint(
            ["workflow_instance_id"],
            ["workflow_instances.id"],
            name=op.f("fk_workflow_history_workflow_instance_id_workflow_instances"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_workflow_history")),
    )
    op.create_index(op.f("ix_workflow_history_tenant_id"), "workflow_history", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_workflow_history_workflow_instance_id"), "workflow_history", ["workflow_instance_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_workflow_history_workflow_instance_id"), table_name="workflow_history")
    op.drop_index(op.f("ix_workflow_history_tenant_id"), table_name="workflow_history")
    op.drop_table("workflow_history")
    op.drop_index(op.f("ix_workflow_instances_document_id"), table_name="workflow_instances")
    op.drop_index(op.f("ix_workflow_instances_document_type"), table_name="workflow_instances")
    op.drop_index(op.f("ix_workflow_instances_workflow_definition_id"), table_name="workflow_instances")
    op.drop_index(op.f("ix_workflow_instances_tenant_id"), table_name="workflow_instances")
    op.drop_table("workflow_instances")
    op.drop_index(op.f("ix_workflow_transitions_workflow_definition_id"), table_name="workflow_transitions")
    op.drop_index(op.f("ix_workflow_transitions_tenant_id"), table_name="workflow_transitions")
    op.drop_table("workflow_transitions")
    op.drop_index(op.f("ix_workflow_definitions_document_type"), table_name="workflow_definitions")
    op.drop_index(op.f("ix_workflow_definitions_tenant_id"), table_name="workflow_definitions")
    op.drop_table("workflow_definitions")
