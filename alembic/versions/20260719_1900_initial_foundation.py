"""initial foundation"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260719_1900"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.create_table(
        "tenants",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tenants")),
        sa.UniqueConstraint("code", name=op.f("uq_tenants_code")),
    )
    op.create_index(op.f("ix_tenants_code"), "tenants", ["code"], unique=False)

    op.create_table(
        "sppg",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("city", sa.String(length=120), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_sppg_tenant_id_tenants")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sppg")),
        sa.UniqueConstraint("tenant_id", "code", name="uq_sppg_tenant_code"),
    )
    op.create_index(op.f("ix_sppg_code"), "sppg", ["code"], unique=False)
    op.create_index("ix_sppg_tenant_id", "sppg", ["tenant_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_sppg_tenant_id", table_name="sppg")
    op.drop_index(op.f("ix_sppg_code"), table_name="sppg")
    op.drop_table("sppg")
    op.drop_index(op.f("ix_tenants_code"), table_name="tenants")
    op.drop_table("tenants")
