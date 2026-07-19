"""add budget and accounting foundation"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260720_0330"
down_revision = "20260720_0215"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=30), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=30), nullable=False),
        sa.Column("normal_balance", sa.String(length=10), nullable=False),
        sa.Column("allow_posting", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_accounts_tenant_id_tenants")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_accounts")),
        sa.UniqueConstraint("tenant_id", "code", name="uq_accounts_tenant_code"),
    )
    op.create_index("ix_accounts_code", "accounts", ["code"], unique=False)
    op.create_index("ix_accounts_tenant_id", "accounts", ["tenant_id"], unique=False)

    op.create_table(
        "journal_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entry_number", sa.String(length=50), nullable=False),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("reference", sa.String(length=255), nullable=True),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("source_module", sa.String(length=50), nullable=False),
        sa.Column("source_document_type", sa.String(length=50), nullable=False),
        sa.Column("source_document_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default=sa.text("'DRAFT'")),
        sa.Column("posted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("posted_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["posted_by"], ["users.id"], name=op.f("fk_journal_entries_posted_by_users")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_journal_entries_tenant_id_tenants")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_journal_entries")),
        sa.UniqueConstraint("tenant_id", "source_module", "source_document_type", "source_document_id", name="uq_journal_entries_tenant_source_document"),
    )
    op.create_index("ix_journal_entries_entry_number", "journal_entries", ["entry_number"], unique=False)
    op.create_index("ix_journal_entries_tenant_id", "journal_entries", ["tenant_id"], unique=False)

    op.create_table(
        "journal_lines",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("journal_entry_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("line_type", sa.String(length=10), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], name=op.f("fk_journal_lines_account_id_accounts")),
        sa.ForeignKeyConstraint(["journal_entry_id"], ["journal_entries.id"], name=op.f("fk_journal_lines_journal_entry_id_journal_entries")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_journal_lines_tenant_id_tenants")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_journal_lines")),
    )
    op.create_index("ix_journal_lines_account_id", "journal_lines", ["account_id"], unique=False)
    op.create_index("ix_journal_lines_journal_entry_id", "journal_lines", ["journal_entry_id"], unique=False)
    op.create_index("ix_journal_lines_tenant_id", "journal_lines", ["tenant_id"], unique=False)

    op.create_table(
        "budgets",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("budget_number", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("date_start", sa.Date(), nullable=False),
        sa.Column("date_end", sa.Date(), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("status", sa.String(length=30), nullable=False, server_default=sa.text("'DRAFT'")),
        sa.Column("approved_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["approved_by"], ["users.id"], name=op.f("fk_budgets_approved_by_users")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_budgets_tenant_id_tenants")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_budgets")),
        sa.UniqueConstraint("tenant_id", "budget_number", name="uq_budgets_tenant_budget_number"),
    )
    op.create_index("ix_budgets_budget_number", "budgets", ["budget_number"], unique=False)
    op.create_index("ix_budgets_tenant_id", "budgets", ["tenant_id"], unique=False)

    op.create_table(
        "budget_lines",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("budget_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("category_name", sa.String(length=100), nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("planned_amount", sa.Float(), nullable=False),
        sa.Column("revised_amount", sa.Float(), nullable=True),
        sa.Column("control_mode", sa.String(length=20), nullable=False, server_default=sa.text("'WARNING'")),
        sa.Column("tolerance_percentage", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("cached_reserved_amount", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("cached_committed_amount", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("cached_actual_amount", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], name=op.f("fk_budget_lines_account_id_accounts")),
        sa.ForeignKeyConstraint(["budget_id"], ["budgets.id"], name=op.f("fk_budget_lines_budget_id_budgets")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name=op.f("fk_budget_lines_tenant_id_tenants")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_budget_lines")),
    )
    op.create_index("ix_budget_lines_budget_id", "budget_lines", ["budget_id"], unique=False)
    op.create_index("ix_budget_lines_tenant_id", "budget_lines", ["tenant_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_budget_lines_tenant_id", table_name="budget_lines")
    op.drop_index("ix_budget_lines_budget_id", table_name="budget_lines")
    op.drop_table("budget_lines")

    op.drop_index("ix_budgets_tenant_id", table_name="budgets")
    op.drop_index("ix_budgets_budget_number", table_name="budgets")
    op.drop_table("budgets")

    op.drop_index("ix_journal_lines_tenant_id", table_name="journal_lines")
    op.drop_index("ix_journal_lines_journal_entry_id", table_name="journal_lines")
    op.drop_index("ix_journal_lines_account_id", table_name="journal_lines")
    op.drop_table("journal_lines")

    op.drop_index("ix_journal_entries_tenant_id", table_name="journal_entries")
    op.drop_index("ix_journal_entries_entry_number", table_name="journal_entries")
    op.drop_table("journal_entries")

    op.drop_index("ix_accounts_tenant_id", table_name="accounts")
    op.drop_index("ix_accounts_code", table_name="accounts")
    op.drop_table("accounts")
