"""expand delivery distribution routes

Revision ID: 20260720_1015
Revises: 20260720_0905
Create Date: 2026-07-20 10:15:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260720_1015"
down_revision: str | Sequence[str] | None = "20260720_0905"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "delivery_routes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sppg_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("route_code", sa.String(length=100), nullable=False),
        sa.Column("route_name", sa.String(length=255), nullable=False),
        sa.Column("route_status", sa.String(length=30), nullable=False, server_default="PLANNED"),
        sa.Column("planned_departure", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_departure", sa.DateTime(timezone=True), nullable=True),
        sa.Column("planned_arrival", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_arrival", sa.DateTime(timezone=True), nullable=True),
        sa.Column("origin_gps", sa.String(length=120), nullable=True),
        sa.Column("destination_gps", sa.String(length=120), nullable=True),
        sa.Column("total_distance_km", sa.Float(), nullable=True),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["sppg_id"], ["sppg.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "route_code", name="uq_delivery_routes_tenant_route_code"),
    )
    op.create_index("ix_delivery_routes_tenant_id", "delivery_routes", ["tenant_id"], unique=False)
    op.create_index("ix_delivery_routes_sppg_id", "delivery_routes", ["sppg_id"], unique=False)
    op.create_index("ix_delivery_routes_route_code", "delivery_routes", ["route_code"], unique=False)

    op.add_column("delivery_orders", sa.Column("route_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key("fk_delivery_orders_route_id", "delivery_orders", "delivery_routes", ["route_id"], ["id"])
    op.create_index("ix_delivery_orders_route_id", "delivery_orders", ["route_id"], unique=False)

    op.create_table(
        "delivery_route_stops",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("route_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("delivery_order_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("school_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("stop_sequence", sa.Integer(), nullable=False),
        sa.Column("planned_arrival", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_arrival", sa.DateTime(timezone=True), nullable=True),
        sa.Column("planned_departure", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_departure", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="PLANNED"),
        sa.Column("recipient_name", sa.String(length=255), nullable=True),
        sa.Column("stop_gps", sa.String(length=120), nullable=True),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["route_id"], ["delivery_routes.id"]),
        sa.ForeignKeyConstraint(["delivery_order_id"], ["delivery_orders.id"]),
        sa.ForeignKeyConstraint(["school_id"], ["schools.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("route_id", "stop_sequence", name="uq_delivery_route_stops_route_sequence"),
    )
    op.create_index("ix_delivery_route_stops_tenant_id", "delivery_route_stops", ["tenant_id"], unique=False)
    op.create_index("ix_delivery_route_stops_route_id", "delivery_route_stops", ["route_id"], unique=False)
    op.create_index("ix_delivery_route_stops_delivery_order_id", "delivery_route_stops", ["delivery_order_id"], unique=False)
    op.create_index("ix_delivery_route_stops_school_id", "delivery_route_stops", ["school_id"], unique=False)

    op.create_table(
        "delivery_incidents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("delivery_order_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("route_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("route_stop_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("incident_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("severity", sa.String(length=30), nullable=False, server_default="MEDIUM"),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column("incident_gps", sa.String(length=120), nullable=True),
        sa.Column("temperature_celsius", sa.Float(), nullable=True),
        sa.Column("media_urls", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="OPEN"),
        sa.Column("resolution_notes", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["delivery_order_id"], ["delivery_orders.id"]),
        sa.ForeignKeyConstraint(["route_id"], ["delivery_routes.id"]),
        sa.ForeignKeyConstraint(["route_stop_id"], ["delivery_route_stops.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_delivery_incidents_tenant_id", "delivery_incidents", ["tenant_id"], unique=False)
    op.create_index("ix_delivery_incidents_delivery_order_id", "delivery_incidents", ["delivery_order_id"], unique=False)
    op.create_index("ix_delivery_incidents_route_id", "delivery_incidents", ["route_id"], unique=False)
    op.create_index("ix_delivery_incidents_route_stop_id", "delivery_incidents", ["route_stop_id"], unique=False)

    op.add_column("delivery_proofs", sa.Column("route_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("delivery_proofs", sa.Column("route_stop_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("delivery_proofs", sa.Column("condition_status", sa.String(length=50), nullable=True))
    op.add_column(
        "delivery_proofs",
        sa.Column("photo_urls", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
    )
    op.add_column("delivery_proofs", sa.Column("signature_name", sa.String(length=255), nullable=True))
    op.add_column("delivery_proofs", sa.Column("signature_url", sa.String(length=500), nullable=True))
    op.add_column("delivery_proofs", sa.Column("signature_signed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("delivery_proofs", sa.Column("incident_notes", sa.String(length=500), nullable=True))
    op.add_column(
        "delivery_proofs",
        sa.Column(
            "linked_incident_ids",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )
    op.create_foreign_key("fk_delivery_proofs_route_id", "delivery_proofs", "delivery_routes", ["route_id"], ["id"])
    op.create_foreign_key(
        "fk_delivery_proofs_route_stop_id",
        "delivery_proofs",
        "delivery_route_stops",
        ["route_stop_id"],
        ["id"],
    )
    op.create_index("ix_delivery_proofs_route_id", "delivery_proofs", ["route_id"], unique=False)
    op.create_index("ix_delivery_proofs_route_stop_id", "delivery_proofs", ["route_stop_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_delivery_proofs_route_stop_id", table_name="delivery_proofs")
    op.drop_index("ix_delivery_proofs_route_id", table_name="delivery_proofs")
    op.drop_constraint("fk_delivery_proofs_route_stop_id", "delivery_proofs", type_="foreignkey")
    op.drop_constraint("fk_delivery_proofs_route_id", "delivery_proofs", type_="foreignkey")
    op.drop_column("delivery_proofs", "linked_incident_ids")
    op.drop_column("delivery_proofs", "incident_notes")
    op.drop_column("delivery_proofs", "signature_signed_at")
    op.drop_column("delivery_proofs", "signature_url")
    op.drop_column("delivery_proofs", "signature_name")
    op.drop_column("delivery_proofs", "photo_urls")
    op.drop_column("delivery_proofs", "condition_status")
    op.drop_column("delivery_proofs", "route_stop_id")
    op.drop_column("delivery_proofs", "route_id")

    op.drop_index("ix_delivery_incidents_route_stop_id", table_name="delivery_incidents")
    op.drop_index("ix_delivery_incidents_route_id", table_name="delivery_incidents")
    op.drop_index("ix_delivery_incidents_delivery_order_id", table_name="delivery_incidents")
    op.drop_index("ix_delivery_incidents_tenant_id", table_name="delivery_incidents")
    op.drop_table("delivery_incidents")

    op.drop_index("ix_delivery_route_stops_school_id", table_name="delivery_route_stops")
    op.drop_index("ix_delivery_route_stops_delivery_order_id", table_name="delivery_route_stops")
    op.drop_index("ix_delivery_route_stops_route_id", table_name="delivery_route_stops")
    op.drop_index("ix_delivery_route_stops_tenant_id", table_name="delivery_route_stops")
    op.drop_table("delivery_route_stops")

    op.drop_index("ix_delivery_orders_route_id", table_name="delivery_orders")
    op.drop_constraint("fk_delivery_orders_route_id", "delivery_orders", type_="foreignkey")
    op.drop_column("delivery_orders", "route_id")

    op.drop_index("ix_delivery_routes_route_code", table_name="delivery_routes")
    op.drop_index("ix_delivery_routes_sppg_id", table_name="delivery_routes")
    op.drop_index("ix_delivery_routes_tenant_id", table_name="delivery_routes")
    op.drop_table("delivery_routes")
