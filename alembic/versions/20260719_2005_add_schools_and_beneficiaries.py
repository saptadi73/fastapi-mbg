"""add schools and beneficiaries"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260719_2005"
down_revision = "20260719_1925"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "schools",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("school_level", sa.String(length=50), nullable=False),
        sa.Column("address", sa.String(length=500), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("student_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("active_beneficiary_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_schools_tenant_id_tenants")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_schools")),
        sa.UniqueConstraint("tenant_id", "code", name="uq_schools_tenant_code"),
    )
    op.create_index(op.f("ix_schools_code"), "schools", ["code"], unique=False)
    op.create_index("ix_schools_tenant_id", "schools", ["tenant_id"], unique=False)

    op.create_table(
        "beneficiaries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("school_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_reference", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("age_group", sa.String(length=50), nullable=False),
        sa.Column("gender", sa.String(length=20), nullable=True),
        sa.Column("dietary_restriction", sa.String(length=100), nullable=True),
        sa.Column("allergy_notes", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"], name=op.f("fk_beneficiaries_school_id_schools")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_beneficiaries_tenant_id_tenants")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_beneficiaries")),
        sa.UniqueConstraint(
            "tenant_id",
            "external_reference",
            name="uq_beneficiaries_tenant_external_reference",
        ),
    )
    op.create_index("ix_beneficiaries_tenant_id", "beneficiaries", ["tenant_id"], unique=False)
    op.create_index("ix_beneficiaries_school_id", "beneficiaries", ["school_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_beneficiaries_school_id", table_name="beneficiaries")
    op.drop_index("ix_beneficiaries_tenant_id", table_name="beneficiaries")
    op.drop_table("beneficiaries")
    op.drop_index("ix_schools_tenant_id", table_name="schools")
    op.drop_index(op.f("ix_schools_code"), table_name="schools")
    op.drop_table("schools")
