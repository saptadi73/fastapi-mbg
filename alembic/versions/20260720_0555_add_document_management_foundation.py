"""add document management foundation

Revision ID: 20260720_0555
Revises: 20260720_0545
Create Date: 2026-07-20 05:55:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260720_0555"
down_revision: str | None = "20260720_0545"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("document_number", sa.String(length=100), nullable=False),
        sa.Column("document_type", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column("owner_entity_type", sa.String(length=100), nullable=True),
        sa.Column("owner_entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_documents_tenant_id_tenants")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_documents")),
        sa.UniqueConstraint("tenant_id", "document_number", name="uq_documents_tenant_document_number"),
    )
    op.create_index(op.f("ix_documents_tenant_id"), "documents", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_documents_sppg_id"), "documents", ["sppg_id"], unique=False)
    op.create_index(op.f("ix_documents_document_number"), "documents", ["document_number"], unique=False)
    op.create_index(op.f("ix_documents_document_type"), "documents", ["document_type"], unique=False)
    op.create_index(op.f("ix_documents_owner_entity_type"), "documents", ["owner_entity_type"], unique=False)
    op.create_index(op.f("ix_documents_owner_entity_id"), "documents", ["owner_entity_id"], unique=False)

    op.create_table(
        "document_versions",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_mime_type", sa.String(length=120), nullable=True),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column("checksum_sha256", sa.String(length=128), nullable=True),
        sa.Column("storage_backend", sa.String(length=50), nullable=False, server_default="LOCAL"),
        sa.Column("object_key", sa.String(length=500), nullable=False),
        sa.Column("version_notes", sa.String(length=1000), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], name=op.f("fk_document_versions_document_id_documents")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_document_versions_tenant_id_tenants")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_document_versions")),
        sa.UniqueConstraint("document_id", "version_number", name="uq_document_versions_document_version_number"),
    )
    op.create_index(op.f("ix_document_versions_tenant_id"), "document_versions", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_document_versions_document_id"), "document_versions", ["document_id"], unique=False)

    op.create_table(
        "document_links",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("linked_entity_type", sa.String(length=100), nullable=False),
        sa.Column("linked_entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("relation_type", sa.String(length=50), nullable=False, server_default="ATTACHMENT"),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], name=op.f("fk_document_links_document_id_documents")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_document_links_tenant_id_tenants")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_document_links")),
        sa.UniqueConstraint("document_id", "linked_entity_type", "linked_entity_id", name="uq_document_links_document_entity"),
    )
    op.create_index(op.f("ix_document_links_tenant_id"), "document_links", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_document_links_document_id"), "document_links", ["document_id"], unique=False)
    op.create_index(op.f("ix_document_links_linked_entity_type"), "document_links", ["linked_entity_type"], unique=False)
    op.create_index(op.f("ix_document_links_linked_entity_id"), "document_links", ["linked_entity_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_document_links_linked_entity_id"), table_name="document_links")
    op.drop_index(op.f("ix_document_links_linked_entity_type"), table_name="document_links")
    op.drop_index(op.f("ix_document_links_document_id"), table_name="document_links")
    op.drop_index(op.f("ix_document_links_tenant_id"), table_name="document_links")
    op.drop_table("document_links")
    op.drop_index(op.f("ix_document_versions_document_id"), table_name="document_versions")
    op.drop_index(op.f("ix_document_versions_tenant_id"), table_name="document_versions")
    op.drop_table("document_versions")
    op.drop_index(op.f("ix_documents_owner_entity_id"), table_name="documents")
    op.drop_index(op.f("ix_documents_owner_entity_type"), table_name="documents")
    op.drop_index(op.f("ix_documents_document_type"), table_name="documents")
    op.drop_index(op.f("ix_documents_document_number"), table_name="documents")
    op.drop_index(op.f("ix_documents_sppg_id"), table_name="documents")
    op.drop_index(op.f("ix_documents_tenant_id"), table_name="documents")
    op.drop_table("documents")
