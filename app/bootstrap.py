from collections.abc import Iterable
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config.settings import Settings, get_settings
from app.core.database.session import close_database, initialize_database
from app.core.tenancy.middleware import TenantContextMiddleware
from app.modules.ai.manifest import manifest as ai_manifest
from app.modules.accounting.manifest import manifest as accounting_manifest
from app.modules.asset.manifest import manifest as asset_manifest
from app.modules.audit.manifest import manifest as audit_manifest
from app.modules.beneficiary.manifest import manifest as beneficiary_manifest
from app.modules.budget.manifest import manifest as budget_manifest
from app.modules.costing.manifest import manifest as costing_manifest
from app.modules.delivery.manifest import manifest as delivery_manifest
from app.modules.document.manifest import manifest as document_manifest
from app.modules.feedback.manifest import manifest as feedback_manifest
from app.modules.fleet.manifest import manifest as fleet_manifest
from app.modules.funding.manifest import manifest as funding_manifest
from app.modules.geography.manifest import manifest as geography_manifest
from app.modules.gis.manifest import manifest as gis_manifest
from app.modules.government_claim.manifest import manifest as government_claim_manifest
from app.modules.health.manifest import manifest as health_manifest
from app.modules.identity.manifest import manifest as identity_manifest
from app.modules.integration.manifest import manifest as integration_manifest
from app.modules.inventory.manifest import manifest as inventory_manifest
from app.modules.manifest import ModuleManifest
from app.modules.meal_plan.manifest import manifest as meal_plan_manifest
from app.modules.notification.manifest import manifest as notification_manifest
from app.modules.platform_ops.manifest import manifest as platform_ops_manifest
from app.modules.program.manifest import manifest as program_manifest
from app.modules.product.manifest import manifest as product_manifest
from app.modules.production.manifest import manifest as production_manifest
from app.modules.procurement.manifest import manifest as procurement_manifest
from app.modules.quality.manifest import manifest as quality_manifest
from app.modules.recipe.manifest import manifest as recipe_manifest
from app.modules.reporting.manifest import manifest as reporting_manifest
from app.modules.sppg.manifest import manifest as sppg_manifest
from app.modules.tenant.manifest import manifest as tenant_manifest
from app.modules.uom.manifest import manifest as uom_manifest
from app.modules.workflow.manifest import manifest as workflow_manifest
from app.modules.workforce.manifest import manifest as workforce_manifest
from app.support.exceptions.handlers import register_exception_handlers
from app.support.middleware.cors import register_cors
from app.support.middleware.request_id import register_request_id
from app.support.middleware.timing import register_timing_middleware
from app.support.openapi import register_openapi


def get_module_manifests() -> Iterable[ModuleManifest]:
    return (
        health_manifest,
        identity_manifest,
        ai_manifest,
        audit_manifest,
        accounting_manifest,
        asset_manifest,
        budget_manifest,
        tenant_manifest,
        sppg_manifest,
        geography_manifest,
        gis_manifest,
        beneficiary_manifest,
        costing_manifest,
        delivery_manifest,
        document_manifest,
        feedback_manifest,
        fleet_manifest,
        funding_manifest,
        government_claim_manifest,
        integration_manifest,
        inventory_manifest,
        platform_ops_manifest,
        program_manifest,
        notification_manifest,
        quality_manifest,
        reporting_manifest,
        uom_manifest,
        workflow_manifest,
        workforce_manifest,
        product_manifest,
        production_manifest,
        procurement_manifest,
        recipe_manifest,
        meal_plan_manifest,
    )


def register_modules(app: FastAPI) -> None:
    for module in get_module_manifests():
        app.include_router(module.router, prefix=module.prefix, tags=module.tags)


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    await initialize_database(settings)
    try:
        yield
    finally:
        await close_database()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        debug=settings.app_debug,
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    register_request_id(app)
    register_timing_middleware(app)
    app.add_middleware(TenantContextMiddleware)
    register_cors(app, settings)
    register_exception_handlers(app)
    register_modules(app)
    register_openapi(app)

    return app
