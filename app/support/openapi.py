from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def register_openapi(app: FastAPI) -> None:
    def custom_openapi() -> dict:
        if app.openapi_schema:
            return app.openapi_schema

        schema = get_openapi(
            title=app.title,
            version="0.1.0",
            description=(
                "OpenAPI untuk ERP MBG FastAPI.\n\n"
                "Semua endpoint menggunakan envelope JSON standar.\n\n"
                "Success:\n"
                "- `success`: boolean\n"
                "- `code`: string stabil untuk frontend\n"
                "- `message`: string\n"
                "- `data`: object | array | null\n"
                "- `meta.timestamp`: ISO 8601 UTC\n"
                "- `meta.request_id`: UUID request\n\n"
                "Error:\n"
                "- `success`: false\n"
                "- `code`: string error stabil\n"
                "- `message`: string\n"
                "- `errors`: array detail error\n\n"
                "Autentikasi menggunakan Bearer JWT dari endpoint `/api/v1/identity/login`.\n"
                "Format date yang dipakai backend adalah `YYYY-MM-DD`, "
                "dan format datetime adalah ISO 8601, misalnya `2026-07-25T08:05:00Z`."
            ),
            routes=app.routes,
        )

        components = schema.setdefault("components", {})
        schemas = components.setdefault("schemas", {})
        responses = components.setdefault("responses", {})

        schemas["StandardSuccessEnvelope"] = {
            "type": "object",
            "properties": {
                "success": {"type": "boolean", "example": True},
                "code": {"type": "string", "example": "SOME_SUCCESS_CODE"},
                "message": {"type": "string", "example": "Operasi berhasil."},
                "data": {"nullable": True},
                "meta": {
                    "type": "object",
                    "properties": {
                        "timestamp": {"type": "string", "format": "date-time"},
                        "request_id": {"type": "string"},
                        "total": {"type": "integer"},
                    },
                },
            },
            "required": ["success", "code", "message", "data", "meta"],
        }
        schemas["StandardErrorEnvelope"] = {
            "type": "object",
            "properties": {
                "success": {"type": "boolean", "example": False},
                "code": {"type": "string", "example": "REQUEST_VALIDATION_ERROR"},
                "message": {"type": "string", "example": "Validasi request gagal."},
                "errors": {
                    "type": "array",
                    "items": {"type": "object"},
                },
                "meta": {
                    "type": "object",
                    "properties": {
                        "timestamp": {"type": "string", "format": "date-time"},
                        "request_id": {"type": "string"},
                    },
                },
            },
            "required": ["success", "code", "message", "errors", "meta"],
        }

        responses["AuthenticationRequired"] = {
            "description": "Bearer token wajib disertakan.",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/StandardErrorEnvelope"},
                    "example": {
                        "success": False,
                        "code": "AUTHENTICATION_REQUIRED",
                        "message": "Bearer token wajib disertakan.",
                        "errors": [],
                        "meta": {
                            "timestamp": "2026-07-19T14:28:44.668195+00:00",
                            "request_id": "uuid",
                        },
                    },
                }
            },
        }
        responses["InsufficientRole"] = {
            "description": "Role user tidak cukup.",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/StandardErrorEnvelope"},
                    "example": {
                        "success": False,
                        "code": "INSUFFICIENT_ROLE",
                        "message": "Role user tidak memiliki izin untuk aksi ini.",
                        "errors": [],
                        "meta": {
                            "timestamp": "2026-07-19T14:28:44.668195+00:00",
                            "request_id": "uuid",
                        },
                    },
                }
            },
        }
        responses["ValidationErrorEnvelope"] = {
            "description": "Payload request tidak valid.",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/StandardErrorEnvelope"},
                    "example": {
                        "success": False,
                        "code": "REQUEST_VALIDATION_ERROR",
                        "message": "Validasi request gagal.",
                        "errors": [{"field": "body.plan_date", "detail": "Input should be a valid date"}],
                        "meta": {
                            "timestamp": "2026-07-19T14:28:44.668195+00:00",
                            "request_id": "uuid",
                        },
                    },
                }
            },
        }
        responses["InternalServerErrorEnvelope"] = {
            "description": "Kesalahan internal server.",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/StandardErrorEnvelope"},
                    "example": {
                        "success": False,
                        "code": "INTERNAL_SERVER_ERROR",
                        "message": "Terjadi kesalahan internal pada server.",
                        "errors": [],
                        "meta": {
                            "timestamp": "2026-07-19T14:28:44.668195+00:00",
                            "request_id": "uuid",
                        },
                    },
                }
            },
        }

        for path_item in schema.get("paths", {}).values():
            for operation in path_item.values():
                if not isinstance(operation, dict):
                    continue
                op_responses = operation.setdefault("responses", {})
                op_responses.setdefault("401", {"$ref": "#/components/responses/AuthenticationRequired"})
                op_responses.setdefault("403", {"$ref": "#/components/responses/InsufficientRole"})
                op_responses.setdefault("422", {"$ref": "#/components/responses/ValidationErrorEnvelope"})
                op_responses.setdefault("500", {"$ref": "#/components/responses/InternalServerErrorEnvelope"})

        schema["tags"] = [
            {"name": "Health", "description": "Health check service dan database."},
            {"name": "Identity", "description": "Autentikasi JWT dan profil user aktif."},
            {"name": "Accounting", "description": "Accounts dan journal entries."},
            {"name": "Budget", "description": "Budget allocation, approval, dan availability."},
            {"name": "Tenant", "description": "Master tenant SaaS."},
            {"name": "SPPG", "description": "Master SPPG atau dapur operasional."},
            {"name": "Geography", "description": "Master sekolah dan titik layanan."},
            {"name": "Beneficiary", "description": "Master penerima manfaat."},
            {"name": "UoM", "description": "Unit of measure."},
            {"name": "Product", "description": "Master produk dan material."},
            {"name": "Recipe", "description": "Recipe dan komponen bahan."},
            {"name": "Meal Plan", "description": "Perencanaan menu, kebutuhan bahan, dan preview biaya."},
            {"name": "Inventory", "description": "Warehouse, ledger transaksi, dan saldo stok."},
            {"name": "Procurement", "description": "Purchase request dan goods receipt."},
            {"name": "Production", "description": "Production order, konsumsi bahan, dan cost sheet."},
            {"name": "Delivery", "description": "Delivery order dan proof of delivery."},
        ]

        app.openapi_schema = schema
        return app.openapi_schema

    app.openapi = custom_openapi
