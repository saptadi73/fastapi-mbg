"""fix supplier invoice defaults

Revision ID: 20260720_0420
Revises: 20260720_0415
Create Date: 2026-07-20 04:20:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260720_0420"
down_revision: str | None = "20260720_0415"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("supplier_invoices", "id", server_default=sa.text("gen_random_uuid()"))
    op.alter_column("supplier_invoices", "created_at", server_default=sa.text("CURRENT_TIMESTAMP"))
    op.alter_column("supplier_invoices", "updated_at", server_default=sa.text("CURRENT_TIMESTAMP"))
    op.alter_column("supplier_invoice_lines", "id", server_default=sa.text("gen_random_uuid()"))
    op.alter_column("supplier_invoice_lines", "created_at", server_default=sa.text("CURRENT_TIMESTAMP"))
    op.alter_column("supplier_invoice_lines", "updated_at", server_default=sa.text("CURRENT_TIMESTAMP"))


def downgrade() -> None:
    op.alter_column("supplier_invoice_lines", "updated_at", server_default=None)
    op.alter_column("supplier_invoice_lines", "created_at", server_default=None)
    op.alter_column("supplier_invoice_lines", "id", server_default=None)
    op.alter_column("supplier_invoices", "updated_at", server_default=None)
    op.alter_column("supplier_invoices", "created_at", server_default=None)
    op.alter_column("supplier_invoices", "id", server_default=None)
