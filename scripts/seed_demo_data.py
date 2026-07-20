import asyncio
from datetime import date
from datetime import datetime
from datetime import timezone
from uuid import UUID

from geoalchemy2.elements import WKTElement
from sqlalchemy import delete, or_, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config.settings import get_settings
from app.core.security.password import hash_password
from app.modules.delivery.models.delivery_order import DeliveryOrder
from app.modules.delivery.models.delivery_incident import DeliveryIncident
from app.modules.delivery.models.delivery_proof import DeliveryProof
from app.modules.delivery.models.delivery_route import DeliveryRoute
from app.modules.delivery.models.delivery_route_stop import DeliveryRouteStop
from app.modules.delivery.repositories.delivery_incident_repository import DeliveryIncidentRepository
from app.modules.delivery.repositories.delivery_order_repository import DeliveryOrderRepository
from app.modules.delivery.repositories.delivery_proof_repository import DeliveryProofRepository
from app.modules.delivery.repositories.delivery_route_repository import DeliveryRouteRepository
from app.modules.delivery.repositories.delivery_route_stop_repository import DeliveryRouteStopRepository
from app.modules.feedback.models.complaint import Complaint
from app.modules.feedback.models.feedback_item import FeedbackItem
from app.modules.feedback.models.feedback_submission import FeedbackSubmission
from app.modules.feedback.models.service_quality_score import ServiceQualityScore
from app.modules.fleet.models.driver import Driver
from app.modules.fleet.models.vehicle import Vehicle
from app.modules.fleet.models.vehicle_assignment import VehicleAssignment
from app.modules.fleet.models.vehicle_location import VehicleLocation
from app.modules.fleet.models.vehicle_maintenance import VehicleMaintenance
from app.modules.fleet.models.vehicle_type import VehicleType
from app.modules.identity.models.user import User
from app.modules.identity.repositories.user_repository import UserRepository
from app.modules.inventory.repositories.inventory_balance_repository import InventoryBalanceRepository
from app.modules.inventory.repositories.inventory_batch_repository import InventoryBatchRepository
from app.modules.inventory.repositories.inventory_transaction_repository import InventoryTransactionRepository
from app.modules.inventory.repositories.stock_location_repository import StockLocationRepository
from app.modules.inventory.repositories.warehouse_repository import WarehouseRepository
from app.modules.inventory.schemas.stock_schema import InventoryTransactionCreate
from app.modules.inventory.schemas.warehouse_schema import WarehouseCreate
from app.modules.inventory.services.stock_service import StockService
from app.modules.inventory.services.warehouse_service import WarehouseService
from app.modules.meal_plan.repositories.meal_plan_repository import MealPlanRepository
from app.modules.meal_plan.schemas.meal_plan_schema import MealPlanCreate
from app.modules.meal_plan.services.meal_plan_service import MealPlanService
from app.modules.geography.repositories.school_repository import SchoolRepository
from app.modules.geography.schemas.school_schema import SchoolCreate
from app.modules.geography.services.school_service import SchoolService
from app.modules.beneficiary.repositories.beneficiary_repository import BeneficiaryRepository
from app.modules.beneficiary.schemas.beneficiary_schema import BeneficiaryCreate
from app.modules.beneficiary.services.beneficiary_service import BeneficiaryService
from app.modules.gis.models.service_area import ServiceArea
from app.modules.gis.repositories.service_area_repository import ServiceAreaRepository
from app.modules.accounting.repositories.account_repository import AccountRepository
from app.modules.accounting.repositories.journal_entry_repository import JournalEntryRepository
from app.modules.accounting.repositories.journal_line_repository import JournalLineRepository
from app.modules.accounting.models.journal_entry import JournalEntry
from app.modules.accounting.models.journal_line import JournalLine
from app.modules.accounting.schemas.accounting_schema import AccountCreate, JournalEntryCreate
from app.modules.accounting.schemas.accounting_schema import JournalLineCreate
from app.modules.accounting.services.accounting_service import AccountingService
from app.modules.budget.repositories.budget_line_repository import BudgetLineRepository
from app.modules.budget.repositories.budget_repository import BudgetRepository
from app.modules.budget.schemas.budget_schema import BudgetCreate, BudgetLineCreate
from app.modules.budget.services.budget_service import BudgetService
from app.modules.product.repositories.product_repository import ProductRepository
from app.modules.product.schemas.product_schema import ProductCreate
from app.modules.product.services.product_service import ProductService
from app.modules.program.models.program import Program  # noqa: F401
from app.modules.production.models.production_order import ProductionOrder
from app.modules.production.repositories.production_order_repository import ProductionOrderRepository
from app.modules.funding.models.funding_source import FundingSource
from app.modules.funding.models.funding_agreement import FundingAgreement
from app.modules.funding.models.funding_disbursement import FundingDisbursement
from app.modules.funding.models.funding_repayment import FundingRepayment
from app.modules.government_claim.models.government_claim import GovernmentClaim
from app.modules.government_claim.models.government_claim_line import GovernmentClaimLine
from app.modules.government_claim.models.claim_payment import ClaimPayment
from app.modules.government_claim.models.claim_verification import ClaimVerification
from app.modules.recipe.repositories.recipe_repository import RecipeRepository
from app.modules.recipe.repositories.recipe_line_repository import RecipeLineRepository
from app.modules.recipe.schemas.recipe_schema import RecipeCreate
from app.modules.recipe.schemas.recipe_schema import RecipeLineCreate
from app.modules.recipe.services.recipe_service import RecipeService
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.sppg.schemas.sppg_schema import SppgCreate
from app.modules.sppg.services.sppg_service import SppgService
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.modules.tenant.schemas.tenant_schema import TenantCreate
from app.modules.tenant.services.tenant_service import TenantService
from app.modules.uom.repositories.uom_repository import UomRepository
from app.modules.uom.schemas.uom_schema import UomCreate
from app.modules.uom.services.uom_service import UomService


def _build_square_multipolygon_wkt(latitude: float, longitude: float, half_side_deg: float = 0.012) -> str:
    south = latitude - half_side_deg
    north = latitude + half_side_deg
    west = longitude - half_side_deg
    east = longitude + half_side_deg
    return (
        "MULTIPOLYGON("
        f"(({west} {south}, {east} {south}, {east} {north}, {west} {north}, {west} {south}))"
        ")"
    )


def _format_gps(latitude: float, longitude: float) -> str:
    return f"{latitude:.6f},{longitude:.6f}"


def _fleet_offset(base_value: float, unit_index: int, axis: str) -> float:
    multiplier = unit_index + 1
    if axis == "lat":
        return base_value + (0.0024 * multiplier)
    return base_value + (0.0017 * multiplier)


async def main() -> None:
    settings = get_settings()
    engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)

    try:
        async with session_factory() as session:
            tenant_service = TenantService(TenantRepository(session))
            tenants = await tenant_service.list_tenants()
            if not tenants:
                tenant = await tenant_service.create_tenant(
                    TenantCreate(code="MBG-DEMO", name="Tenant Demo MBG")
                )
                await session.commit()
                print(f"Tenant dibuat: {tenant.id}")
            else:
                tenant = tenants[0]
                print(f"Tenant sudah ada: {tenant.id}")

            user_repository = UserRepository(session)
            user = await user_repository.get_by_email("operator@example.com")
            if user is None:
                user = await user_repository.add(
                    User(
                        tenant_id=tenant.id,
                        full_name="Demo Operator MBG",
                        email="operator@example.com",
                        password_hash=hash_password("mbg12345"),
                        role_names=["super_admin"],
                        is_active=True,
                    )
                )
                await session.commit()
                print(f"User dibuat: {user.id} email=operator@example.com password=mbg12345")
            else:
                print(f"User sudah ada: {user.id} email=operator@example.com")

            viewer_user = await user_repository.get_by_email("viewer@example.com")
            if viewer_user is None:
                viewer_user = await user_repository.add(
                    User(
                        tenant_id=tenant.id,
                        full_name="Demo Viewer MBG",
                        email="viewer@example.com",
                        password_hash=hash_password("viewer123"),
                        role_names=["viewer"],
                        is_active=True,
                    )
                )
                await session.commit()
                print(f"User dibuat: {viewer_user.id} email=viewer@example.com password=viewer123")
            else:
                print(f"User sudah ada: {viewer_user.id} email=viewer@example.com")

            uom_service = UomService(UomRepository(session), TenantRepository(session))
            uoms = await uom_service.list_uoms()
            if not uoms:
                uom = await uom_service.create_uom(
                    UomCreate(
                        tenant_id=str(tenant.id),
                        code="PORTION",
                        name="Portion",
                        symbol="portion",
                        dimension="UNIT",
                        factor_to_base=1.0,
                    )
                )
                await session.commit()
                print(f"UoM dibuat: {uom.id}")
            else:
                uom = uoms[0]
                print(f"UoM sudah ada: {uom.id}")

            product_service = ProductService(
                ProductRepository(session),
                TenantRepository(session),
                UomRepository(session),
            )
            products = await product_service.list_products()
            if not products:
                product = await product_service.create_product(
                    ProductCreate(
                        tenant_id=str(tenant.id),
                        code="MENU-NASI-AYAM",
                        name="Menu Nasi Ayam",
                        product_type="MENU_COMPONENT",
                        stock_uom_id=str(uom.id),
                        standard_cost=15000,
                    )
                )
                await session.commit()
                print(f"Produk dibuat: {product.id}")
            else:
                product = products[0]
                print(f"Produk sudah ada: {product.id}")

            recipe_service = RecipeService(
                RecipeRepository(session),
                RecipeLineRepository(session),
                TenantRepository(session),
                ProductRepository(session),
                UomRepository(session),
            )
            recipes = await recipe_service.list_recipes()
            if not recipes:
                recipe = await recipe_service.create_recipe(
                    RecipeCreate(
                        tenant_id=str(tenant.id),
                        product_id=str(product.id),
                        code="REC-NASI-AYAM-01",
                        name="Recipe Nasi Ayam 100 Porsi",
                        version=1,
                        output_quantity=100,
                        output_uom_id=str(uom.id),
                        effective_from=date(2026, 7, 19),
                        status="APPROVED",
                    )
                )
                await session.commit()
                print(f"Recipe dibuat: {recipe.id}")
            else:
                recipe = recipes[0]
                print(f"Recipe sudah ada: {recipe.id}")

            ingredient_products = await product_service.list_products()
            ingredient = next((item for item in ingredient_products if item.code == "MAT-BERAS"), None)
            if ingredient is None:
                ingredient = await product_service.create_product(
                    ProductCreate(
                        tenant_id=str(tenant.id),
                        code="MAT-BERAS",
                        name="Beras",
                        product_type="MATERIAL",
                        stock_uom_id=str(uom.id),
                        standard_cost=12000,
                    )
                )
                await session.commit()
                print(f"Produk bahan dibuat: {ingredient.id}")
            else:
                print(f"Produk bahan sudah ada: {ingredient.id}")

            recipe_lines = await recipe_service.list_recipe_lines(recipe.id)
            if not recipe_lines:
                recipe_line = await recipe_service.create_recipe_line(
                    recipe.id,
                    RecipeLineCreate(
                        tenant_id=str(tenant.id),
                        component_product_id=str(ingredient.id),
                        quantity=100,
                        uom_id=str(uom.id),
                        waste_percentage=10,
                        sequence=1,
                    ),
                )
                await session.commit()
                print(f"Recipe line dibuat: {recipe_line.id}")
            else:
                print(f"Recipe line sudah ada: {recipe_lines[0].id}")

            school_service = SchoolService(SchoolRepository(session), TenantRepository(session))
            school_seed = [
                {
                    "code": "SCH-JKT-01",
                    "name": "SDN Jakarta Pusat 01",
                    "school_level": "SD",
                    "address": "Jl. Merdeka No. 1, Jakarta Pusat",
                    "latitude": -6.1702,
                    "longitude": 106.8283,
                    "student_count": 320,
                },
                {
                    "code": "SCH-JKT-02",
                    "name": "SDN Cikini 02",
                    "school_level": "SD",
                    "address": "Jl. Cikini Kecil No. 12, Menteng",
                    "latitude": -6.1882,
                    "longitude": 106.8405,
                    "student_count": 280,
                },
                {
                    "code": "SCH-JKT-03",
                    "name": "SMPN Gondangdia 01",
                    "school_level": "SMP",
                    "address": "Jl. RP Soeroso No. 8, Menteng",
                    "latitude": -6.1864,
                    "longitude": 106.8327,
                    "student_count": 540,
                },
                {
                    "code": "SCH-JKT-04",
                    "name": "SDN Senen 03",
                    "school_level": "SD",
                    "address": "Jl. Kramat Raya No. 90, Senen",
                    "latitude": -6.1829,
                    "longitude": 106.8454,
                    "student_count": 350,
                },
                {
                    "code": "SCH-JKT-05",
                    "name": "SDN Kemayoran 01",
                    "school_level": "SD",
                    "address": "Jl. Garuda No. 5, Kemayoran",
                    "latitude": -6.1588,
                    "longitude": 106.8526,
                    "student_count": 310,
                },
                {
                    "code": "SCH-JKT-06",
                    "name": "SMPN Gunung Sahari 02",
                    "school_level": "SMP",
                    "address": "Jl. Industri Raya No. 14, Gunung Sahari",
                    "latitude": -6.1575,
                    "longitude": 106.8459,
                    "student_count": 500,
                },
                {
                    "code": "SCH-JKT-07",
                    "name": "SDN Sunter 01",
                    "school_level": "SD",
                    "address": "Jl. Danau Sunter Utara No. 21, Sunter",
                    "latitude": -6.1392,
                    "longitude": 106.8684,
                    "student_count": 330,
                },
                {
                    "code": "SCH-JKT-08",
                    "name": "SMAN Tanjung Priok 01",
                    "school_level": "SMA",
                    "address": "Jl. Enggano No. 7, Tanjung Priok",
                    "latitude": -6.1108,
                    "longitude": 106.8869,
                    "student_count": 760,
                },
                {
                    "code": "SCH-JKT-09",
                    "name": "SDN Tebet 01",
                    "school_level": "SD",
                    "address": "Jl. Tebet Barat Dalam No. 9, Tebet",
                    "latitude": -6.2297,
                    "longitude": 106.8493,
                    "student_count": 340,
                },
                {
                    "code": "SCH-JKT-10",
                    "name": "SMPN Manggarai 01",
                    "school_level": "SMP",
                    "address": "Jl. Minangkabau Timur No. 11, Manggarai",
                    "latitude": -6.2096,
                    "longitude": 106.8482,
                    "student_count": 520,
                },
                {
                    "code": "SCH-JKT-11",
                    "name": "SDN Pancoran 02",
                    "school_level": "SD",
                    "address": "Jl. Raya Pasar Minggu No. 44, Pancoran",
                    "latitude": -6.2446,
                    "longitude": 106.8427,
                    "student_count": 305,
                },
                {
                    "code": "SCH-JKT-12",
                    "name": "SDN Kalibata 03",
                    "school_level": "SD",
                    "address": "Jl. Kalibata Timur No. 18, Pancoran",
                    "latitude": -6.2562,
                    "longitude": 106.8488,
                    "student_count": 295,
                },
                {
                    "code": "SCH-JKT-13",
                    "name": "SDN Palmerah 01",
                    "school_level": "SD",
                    "address": "Jl. Palmerah Barat No. 15, Palmerah",
                    "latitude": -6.2058,
                    "longitude": 106.7924,
                    "student_count": 315,
                },
                {
                    "code": "SCH-JKT-14",
                    "name": "SMPN Slipi 02",
                    "school_level": "SMP",
                    "address": "Jl. Anggrek Neli Murni No. 7, Slipi",
                    "latitude": -6.2021,
                    "longitude": 106.8018,
                    "student_count": 510,
                },
                {
                    "code": "SCH-JKT-15",
                    "name": "SDN Kota Bambu 03",
                    "school_level": "SD",
                    "address": "Jl. Kota Bambu Utara No. 21, Palmerah",
                    "latitude": -6.1914,
                    "longitude": 106.7991,
                    "student_count": 288,
                },
                {
                    "code": "SCH-JKT-16",
                    "name": "SDN Kembangan 01",
                    "school_level": "SD",
                    "address": "Jl. Kembang Elok No. 12, Kembangan",
                    "latitude": -6.1868,
                    "longitude": 106.7421,
                    "student_count": 305,
                },
                {
                    "code": "SCH-JKT-17",
                    "name": "SMPN Meruya 01",
                    "school_level": "SMP",
                    "address": "Jl. Meruya Selatan No. 18, Meruya",
                    "latitude": -6.1977,
                    "longitude": 106.7389,
                    "student_count": 495,
                },
                {
                    "code": "SCH-JKT-18",
                    "name": "SDN Joglo 02",
                    "school_level": "SD",
                    "address": "Jl. H. Saaba No. 4, Joglo",
                    "latitude": -6.2145,
                    "longitude": 106.7364,
                    "student_count": 276,
                },
                {
                    "code": "SCH-JKT-19",
                    "name": "SDN Cakung 01",
                    "school_level": "SD",
                    "address": "Jl. Raya Bekasi KM 23 No. 9, Cakung",
                    "latitude": -6.1814,
                    "longitude": 106.9395,
                    "student_count": 322,
                },
                {
                    "code": "SCH-JKT-20",
                    "name": "SMPN Ujung Menteng 02",
                    "school_level": "SMP",
                    "address": "Jl. Ujung Menteng Raya No. 16, Cakung",
                    "latitude": -6.1886,
                    "longitude": 106.9582,
                    "student_count": 540,
                },
                {
                    "code": "SCH-JKT-21",
                    "name": "SDN Penggilingan 03",
                    "school_level": "SD",
                    "address": "Jl. Penggilingan Baru No. 11, Cakung",
                    "latitude": -6.1961,
                    "longitude": 106.9307,
                    "student_count": 298,
                },
                {
                    "code": "SCH-JKT-22",
                    "name": "SDN Pasar Minggu 01",
                    "school_level": "SD",
                    "address": "Jl. Raya Ragunan No. 18, Pasar Minggu",
                    "latitude": -6.2847,
                    "longitude": 106.8423,
                    "student_count": 314,
                },
                {
                    "code": "SCH-JKT-23",
                    "name": "SMPN Jati Padang 01",
                    "school_level": "SMP",
                    "address": "Jl. Jati Padang Raya No. 13, Pasar Minggu",
                    "latitude": -6.2868,
                    "longitude": 106.8312,
                    "student_count": 505,
                },
                {
                    "code": "SCH-JKT-24",
                    "name": "SDN Pejaten Timur 02",
                    "school_level": "SD",
                    "address": "Jl. Pejaten Timur No. 27, Pasar Minggu",
                    "latitude": -6.2765,
                    "longitude": 106.8429,
                    "student_count": 287,
                },
            ]
            existing_schools = {item.code: item for item in await school_service.list_schools()}
            school_map = dict(existing_schools)
            for school_payload in school_seed:
                if school_payload["code"] in school_map:
                    print(f"Sekolah sudah ada: {school_payload['code']}")
                    continue
                created_school = await school_service.create_school(
                    SchoolCreate(tenant_id=str(tenant.id), **school_payload)
                )
                await session.commit()
                school_map[created_school.code] = created_school
                print(f"Sekolah dibuat: {created_school.code} -> {created_school.id}")
            school = school_map["SCH-JKT-01"]

            sppg_service = SppgService(SppgRepository(session), TenantRepository(session))
            sppg_seed = [
                {
                    "code": "SPPG-JKT-01",
                    "name": "SPPG Jakarta Pusat 01",
                    "address": "Jl. Cikini Raya No. 10, Jakarta Pusat",
                    "province": "DKI Jakarta",
                    "city": "Jakarta Pusat",
                    "district": "Menteng",
                    "village": "Cikini",
                    "latitude": -6.1754,
                    "longitude": 106.8272,
                    "service_radius_meter": 5000,
                    "timezone": "Asia/Jakarta",
                },
                {
                    "code": "SPPG-JKT-02",
                    "name": "SPPG Kemayoran 01",
                    "address": "Jl. Benyamin Sueb No. 3, Kemayoran",
                    "province": "DKI Jakarta",
                    "city": "Jakarta Pusat",
                    "district": "Kemayoran",
                    "village": "Kebon Kosong",
                    "latitude": -6.1569,
                    "longitude": 106.8462,
                    "service_radius_meter": 4500,
                    "timezone": "Asia/Jakarta",
                },
                {
                    "code": "SPPG-JKT-03",
                    "name": "SPPG Sunter 01",
                    "address": "Jl. Danau Sunter Selatan No. 28, Jakarta Utara",
                    "province": "DKI Jakarta",
                    "city": "Jakarta Utara",
                    "district": "Tanjung Priok",
                    "village": "Sunter Agung",
                    "latitude": -6.1338,
                    "longitude": 106.8662,
                    "service_radius_meter": 4800,
                    "timezone": "Asia/Jakarta",
                },
                {
                    "code": "SPPG-JKT-04",
                    "name": "SPPG Tebet 01",
                    "address": "Jl. Tebet Timur Raya No. 19, Jakarta Selatan",
                    "province": "DKI Jakarta",
                    "city": "Jakarta Selatan",
                    "district": "Tebet",
                    "village": "Tebet Timur",
                    "latitude": -6.2272,
                    "longitude": 106.8524,
                    "service_radius_meter": 5200,
                    "timezone": "Asia/Jakarta",
                },
                {
                    "code": "SPPG-JKT-05",
                    "name": "SPPG Palmerah 01",
                    "address": "Jl. Palmerah Utara No. 24, Jakarta Barat",
                    "province": "DKI Jakarta",
                    "city": "Jakarta Barat",
                    "district": "Palmerah",
                    "village": "Palmerah",
                    "latitude": -6.2013,
                    "longitude": 106.7962,
                    "service_radius_meter": 4300,
                    "timezone": "Asia/Jakarta",
                },
                {
                    "code": "SPPG-JKT-06",
                    "name": "SPPG Kembangan 01",
                    "address": "Jl. Kembangan Raya No. 41, Jakarta Barat",
                    "province": "DKI Jakarta",
                    "city": "Jakarta Barat",
                    "district": "Kembangan",
                    "village": "Kembangan Selatan",
                    "latitude": -6.1912,
                    "longitude": 106.7469,
                    "service_radius_meter": 4700,
                    "timezone": "Asia/Jakarta",
                },
                {
                    "code": "SPPG-JKT-07",
                    "name": "SPPG Cakung 01",
                    "address": "Jl. Raya Penggilingan No. 20, Jakarta Timur",
                    "province": "DKI Jakarta",
                    "city": "Jakarta Timur",
                    "district": "Cakung",
                    "village": "Penggilingan",
                    "latitude": -6.1872,
                    "longitude": 106.9403,
                    "service_radius_meter": 5600,
                    "timezone": "Asia/Jakarta",
                },
                {
                    "code": "SPPG-JKT-08",
                    "name": "SPPG Pasar Minggu 01",
                    "address": "Jl. Ragunan No. 36, Jakarta Selatan",
                    "province": "DKI Jakarta",
                    "city": "Jakarta Selatan",
                    "district": "Pasar Minggu",
                    "village": "Jati Padang",
                    "latitude": -6.2826,
                    "longitude": 106.8384,
                    "service_radius_meter": 5400,
                    "timezone": "Asia/Jakarta",
                },
            ]
            existing_sppg = {item.code: item for item in await sppg_service.list_sppg()}
            sppg_map = dict(existing_sppg)
            for sppg_payload in sppg_seed:
                if sppg_payload["code"] in sppg_map:
                    print(f"SPPG sudah ada: {sppg_payload['code']}")
                    continue
                created_sppg = await sppg_service.create_sppg(
                    SppgCreate(tenant_id=str(tenant.id), **sppg_payload)
                )
                await session.commit()
                sppg_map[created_sppg.code] = created_sppg
                print(f"SPPG dibuat: {created_sppg.code} -> {created_sppg.id}")
            sppg = sppg_map["SPPG-JKT-01"]

            service_area_repository = ServiceAreaRepository(session)
            service_areas = await service_area_repository.list_all(tenant.id)
            service_area_sppg_ids = {area.sppg_id for area in service_areas}
            for sppg_item in sppg_map.values():
                if sppg_item.id in service_area_sppg_ids:
                    print(f"Service area sudah ada untuk: {sppg_item.code}")
                    continue
                service_area = await service_area_repository.add(
                    ServiceArea(
                        tenant_id=tenant.id,
                        sppg_id=sppg_item.id,
                        name=f"Area Layanan {sppg_item.name}",
                        boundary=WKTElement(
                            _build_square_multipolygon_wkt(sppg_item.latitude, sppg_item.longitude),
                            srid=4326,
                        ),
                        valid_from=date(2026, 7, 20),
                        valid_to=None,
                    )
                )
                await session.commit()
                print(f"Service area dibuat: {sppg_item.code} -> {service_area.id}")

            warehouse_service = WarehouseService(
                WarehouseRepository(session),
                TenantRepository(session),
                SppgRepository(session),
            )
            warehouse_seed = [
                ("WH-JKT-01", "Gudang Utama Jakarta Pusat", "Area SPPG Jakarta Pusat 01", "SPPG-JKT-01"),
                ("WH-JKT-02", "Gudang Kemayoran", "Area SPPG Kemayoran 01", "SPPG-JKT-02"),
                ("WH-JKT-03", "Gudang Sunter", "Area SPPG Sunter 01", "SPPG-JKT-03"),
                ("WH-JKT-04", "Gudang Tebet", "Area SPPG Tebet 01", "SPPG-JKT-04"),
                ("WH-JKT-05", "Gudang Palmerah", "Area SPPG Palmerah 01", "SPPG-JKT-05"),
                ("WH-JKT-06", "Gudang Kembangan", "Area SPPG Kembangan 01", "SPPG-JKT-06"),
                ("WH-JKT-07", "Gudang Cakung", "Area SPPG Cakung 01", "SPPG-JKT-07"),
                ("WH-JKT-08", "Gudang Pasar Minggu", "Area SPPG Pasar Minggu 01", "SPPG-JKT-08"),
            ]
            existing_warehouses = {item.code: item for item in await warehouse_service.list_warehouses()}
            for warehouse_code, warehouse_name, warehouse_location, warehouse_sppg_code in warehouse_seed:
                if warehouse_code in existing_warehouses:
                    print(f"Warehouse sudah ada: {warehouse_code}")
                    continue
                created_warehouse = await warehouse_service.create_warehouse(
                    WarehouseCreate(
                        tenant_id=str(tenant.id),
                        sppg_id=str(sppg_map[warehouse_sppg_code].id),
                        code=warehouse_code,
                        name=warehouse_name,
                        warehouse_type="MAIN",
                        location=warehouse_location,
                        is_active=True,
                    )
                )
                await session.commit()
                existing_warehouses[created_warehouse.code] = created_warehouse
                print(f"Warehouse dibuat: {created_warehouse.code} -> {created_warehouse.id}")
            warehouse = existing_warehouses["WH-JKT-01"]

            user.active_sppg_id = sppg.id
            viewer_user.active_sppg_id = sppg.id
            for sppg_item in sppg_map.values():
                await user_repository.add_sppg_access(user.id, tenant.id, sppg_item.id)
                await user_repository.add_sppg_access(viewer_user.id, tenant.id, sppg_item.id)
            await session.commit()
            print(f"Akses SPPG user demo dipastikan untuk {len(sppg_map)} dapur.")

            beneficiary_service = BeneficiaryService(
                BeneficiaryRepository(session),
                TenantRepository(session),
                SchoolRepository(session),
            )
            existing_beneficiaries = {
                item.external_reference: item for item in await beneficiary_service.list_beneficiaries()
            }
            school_beneficiary_targets = {
                "SCH-JKT-01": 24,
                "SCH-JKT-02": 20,
                "SCH-JKT-03": 28,
                "SCH-JKT-04": 18,
                "SCH-JKT-05": 18,
                "SCH-JKT-06": 22,
                "SCH-JKT-07": 18,
                "SCH-JKT-08": 26,
                "SCH-JKT-09": 20,
                "SCH-JKT-10": 22,
                "SCH-JKT-11": 16,
                "SCH-JKT-12": 16,
                "SCH-JKT-13": 18,
                "SCH-JKT-14": 22,
                "SCH-JKT-15": 16,
                "SCH-JKT-16": 18,
                "SCH-JKT-17": 22,
                "SCH-JKT-18": 16,
                "SCH-JKT-19": 18,
                "SCH-JKT-20": 24,
                "SCH-JKT-21": 16,
                "SCH-JKT-22": 18,
                "SCH-JKT-23": 22,
                "SCH-JKT-24": 16,
            }
            created_beneficiary_count = 0
            for school_code, beneficiary_target in school_beneficiary_targets.items():
                school_item = school_map[school_code]
                for index in range(1, beneficiary_target + 1):
                    external_reference = f"BEN-{school_code}-{index:03d}"
                    if external_reference in existing_beneficiaries:
                        continue
                    beneficiary = await beneficiary_service.create_beneficiary(
                        BeneficiaryCreate(
                            tenant_id=str(tenant.id),
                            school_id=str(school_item.id),
                            external_reference=external_reference,
                            category="student",
                            age_group="7-12" if school_item.school_level == "SD" else "13-18",
                            gender="female" if index % 2 == 0 else "male",
                            dietary_restriction="vegetarian" if index % 17 == 0 else None,
                            allergy_notes="alergi telur" if index % 19 == 0 else None,
                            is_active=True,
                        )
                    )
                    existing_beneficiaries[external_reference] = beneficiary
                    created_beneficiary_count += 1
                await session.commit()
            if created_beneficiary_count:
                print(f"Beneficiary tambahan dibuat: {created_beneficiary_count}")
            else:
                print(f"Beneficiary sudah mencukupi: {len(existing_beneficiaries)} data")

            meal_plan_service = MealPlanService(
                MealPlanRepository(session),
                TenantRepository(session),
                SppgRepository(session),
                RecipeRepository(session),
                RecipeLineRepository(session),
                ProductRepository(session),
            )
            meal_plans = await meal_plan_service.list_meal_plans()
            if not meal_plans:
                meal_plan = await meal_plan_service.create_meal_plan(
                    MealPlanCreate(
                        tenant_id=str(tenant.id),
                        sppg_id=str(sppg.id),
                        recipe_id=str(recipe.id),
                        plan_date=date(2026, 7, 20),
                        meal_type="LUNCH",
                        status="DRAFT",
                        planned_portions=320,
                        budget_cost_per_portion=15000,
                        notes="Meal plan demo untuk SDN Jakarta Pusat 01",
                    )
                )
                await session.commit()
                print(f"Meal plan dibuat: {meal_plan.id}")
            else:
                print(f"Meal plan sudah ada: {meal_plans[0].id}")

            existing_meal_plan_keys = {
                (str(item.sppg_id), item.plan_date.isoformat(), item.meal_type) for item in await meal_plan_service.list_meal_plans()
            }
            sppg_meal_plan_seed = [
                ("SPPG-JKT-02", date(2026, 7, 20), 290, "Distribusi aktif Kemayoran hari ini"),
                ("SPPG-JKT-03", date(2026, 7, 20), 360, "Distribusi aktif Sunter hari ini"),
                ("SPPG-JKT-04", date(2026, 7, 20), 340, "Distribusi aktif Tebet hari ini"),
                ("SPPG-JKT-05", date(2026, 7, 20), 330, "Distribusi aktif Palmerah hari ini"),
                ("SPPG-JKT-06", date(2026, 7, 20), 318, "Distribusi aktif Kembangan hari ini"),
                ("SPPG-JKT-07", date(2026, 7, 20), 346, "Distribusi aktif Cakung hari ini"),
                ("SPPG-JKT-08", date(2026, 7, 20), 334, "Distribusi aktif Pasar Minggu hari ini"),
                ("SPPG-JKT-01", date(2026, 7, 21), 320, "Distribusi cluster Menteng dan Senen"),
                ("SPPG-JKT-02", date(2026, 7, 21), 290, "Distribusi cluster Kemayoran"),
                ("SPPG-JKT-03", date(2026, 7, 21), 360, "Distribusi cluster Sunter dan Tanjung Priok"),
                ("SPPG-JKT-04", date(2026, 7, 21), 340, "Distribusi cluster Tebet dan Pancoran"),
                ("SPPG-JKT-05", date(2026, 7, 21), 330, "Distribusi cluster Palmerah dan Slipi"),
                ("SPPG-JKT-06", date(2026, 7, 21), 318, "Distribusi cluster Kembangan dan Meruya"),
                ("SPPG-JKT-07", date(2026, 7, 21), 346, "Distribusi cluster Cakung dan Penggilingan"),
                ("SPPG-JKT-08", date(2026, 7, 21), 334, "Distribusi cluster Pasar Minggu dan Pejaten"),
            ]
            created_meal_plan_count = 0
            for sppg_code, plan_date, planned_portions, notes in sppg_meal_plan_seed:
                sppg_item = sppg_map[sppg_code]
                meal_plan_key = (str(sppg_item.id), plan_date.isoformat(), "LUNCH")
                if meal_plan_key in existing_meal_plan_keys:
                    continue
                await meal_plan_service.create_meal_plan(
                    MealPlanCreate(
                        tenant_id=str(tenant.id),
                        sppg_id=str(sppg_item.id),
                        recipe_id=str(recipe.id),
                        plan_date=plan_date,
                        meal_type="LUNCH",
                        status="DRAFT",
                        planned_portions=planned_portions,
                        budget_cost_per_portion=15000,
                        notes=notes,
                    )
                )
                await session.commit()
                created_meal_plan_count += 1
            if created_meal_plan_count:
                print(f"Meal plan tambahan dibuat: {created_meal_plan_count}")
            else:
                print("Meal plan tambahan sudah tersedia.")

            meal_plan_repository = MealPlanRepository(session)
            production_order_repository = ProductionOrderRepository(session)
            delivery_order_repository = DeliveryOrderRepository(session)
            delivery_incident_repository = DeliveryIncidentRepository(session)
            delivery_route_repository = DeliveryRouteRepository(session)
            delivery_route_stop_repository = DeliveryRouteStopRepository(session)
            delivery_proof_repository = DeliveryProofRepository(session)

            meal_plans_by_scope = {
                (item.sppg_id, item.plan_date.isoformat()): item for item in await meal_plan_repository.list_all(tenant.id)
            }
            existing_production_orders = {
                item.production_number: item for item in await production_order_repository.list_all(tenant.id)
            }
            production_seed = [
                ("PO-DEMO-JKT01-20260720", "SPPG-JKT-01", "2026-07-20", 320, 320, 318, 2),
                ("PO-DEMO-JKT01-20260721", "SPPG-JKT-01", "2026-07-21", 320, 320, 320, 0),
                ("PO-DEMO-JKT02-20260721", "SPPG-JKT-02", "2026-07-20", 290, 288, 286, 2),
                ("PO-DEMO-JKT03-20260721", "SPPG-JKT-03", "2026-07-20", 360, 355, 352, 3),
                ("PO-DEMO-JKT04-20260721", "SPPG-JKT-04", "2026-07-20", 340, 338, 336, 2),
                ("PO-DEMO-JKT05-20260721", "SPPG-JKT-05", "2026-07-20", 330, 328, 326, 2),
                ("PO-DEMO-JKT06-20260721", "SPPG-JKT-06", "2026-07-20", 318, 316, 314, 2),
                ("PO-DEMO-JKT07-20260721", "SPPG-JKT-07", "2026-07-20", 346, 343, 340, 3),
                ("PO-DEMO-JKT08-20260721", "SPPG-JKT-08", "2026-07-20", 334, 332, 330, 2),
            ]
            created_production_count = 0
            updated_production_count = 0
            for production_number, sppg_code, production_date_raw, planned, actual, accepted, rejected in production_seed:
                meal_plan = meal_plans_by_scope.get((sppg_map[sppg_code].id, production_date_raw))
                if meal_plan is None:
                    continue
                production_date = date.fromisoformat(production_date_raw)
                production_order = existing_production_orders.get(production_number)
                if production_order is None:
                    production_order = await production_order_repository.add(
                        ProductionOrder(
                            tenant_id=tenant.id,
                            sppg_id=sppg_map[sppg_code].id,
                            meal_plan_id=meal_plan.id,
                            production_number=production_number,
                            production_date=production_date,
                            status="COMPLETED",
                            planned_portions=planned,
                            actual_portions=actual,
                            accepted_portions=accepted,
                            rejected_portions=rejected,
                            started_at=datetime(production_date.year, production_date.month, production_date.day, 2, 0, tzinfo=timezone.utc),
                            completed_at=datetime(production_date.year, production_date.month, production_date.day, 4, 30, tzinfo=timezone.utc),
                            actual_total_cost=float(accepted * 15000),
                            actual_cost_per_portion=15000.0,
                        )
                    )
                    created_production_count += 1
                else:
                    production_order.sppg_id = sppg_map[sppg_code].id
                    production_order.meal_plan_id = meal_plan.id
                    production_order.production_date = production_date
                    production_order.status = "COMPLETED"
                    production_order.planned_portions = planned
                    production_order.actual_portions = actual
                    production_order.accepted_portions = accepted
                    production_order.rejected_portions = rejected
                    production_order.started_at = datetime(
                        production_date.year, production_date.month, production_date.day, 2, 0, tzinfo=timezone.utc
                    )
                    production_order.completed_at = datetime(
                        production_date.year, production_date.month, production_date.day, 4, 30, tzinfo=timezone.utc
                    )
                    production_order.actual_total_cost = float(accepted * 15000)
                    production_order.actual_cost_per_portion = 15000.0
                    updated_production_count += 1
                await session.commit()
                existing_production_orders[production_order.production_number] = production_order
            if created_production_count:
                print(f"Production order demo dibuat: {created_production_count}")
            elif updated_production_count == 0:
                print("Production order demo sudah tersedia.")
            if updated_production_count:
                print(f"Production order demo diperbarui: {updated_production_count}")

            existing_delivery_orders = {
                item.delivery_number: item for item in await delivery_order_repository.list_all(tenant.id)
            }
            delivery_seed = [
                ("DO-DEMO-JKT01-001", "PO-DEMO-JKT01-20260720", "SPPG-JKT-01", "SCH-JKT-01", 318, 318, 0, "RECEIVED", "2026-07-20T03:30:00+00:00", "2026-07-20T04:15:00+00:00", "Ibu Rina"),
                ("DO-DEMO-JKT01-002", "PO-DEMO-JKT01-20260720", "SPPG-JKT-01", "SCH-JKT-04", 160, 158, 2, "PARTIALLY_RECEIVED", "2026-07-20T03:45:00+00:00", "2026-07-20T04:35:00+00:00", "Pak Dedi"),
                ("DO-DEMO-JKT01-003", "PO-DEMO-JKT01-20260721", "SPPG-JKT-01", "SCH-JKT-02", 150, None, None, "IN_TRANSIT", "2026-07-21T03:30:00+00:00", "2026-07-21T04:20:00+00:00", "Ibu Maya"),
                ("DO-DEMO-JKT01-004", "PO-DEMO-JKT01-20260721", "SPPG-JKT-01", "SCH-JKT-03", 170, None, None, "LOADING", "2026-07-21T03:50:00+00:00", "2026-07-21T04:40:00+00:00", "Pak Arif"),
                ("DO-DEMO-JKT02-001", "PO-DEMO-JKT02-20260721", "SPPG-JKT-02", "SCH-JKT-05", 140, 140, 0, "RECEIVED", "2026-07-20T03:40:00+00:00", "2026-07-20T04:25:00+00:00", "Ibu Wati"),
                ("DO-DEMO-JKT02-002", "PO-DEMO-JKT02-20260721", "SPPG-JKT-02", "SCH-JKT-06", 146, 144, 2, "PARTIALLY_RECEIVED", "2026-07-20T03:55:00+00:00", "2026-07-20T04:50:00+00:00", "Pak Yoga"),
                ("DO-DEMO-JKT03-001", "PO-DEMO-JKT03-20260721", "SPPG-JKT-03", "SCH-JKT-07", 160, 160, 0, "RECEIVED", "2026-07-20T03:20:00+00:00", "2026-07-20T04:05:00+00:00", "Ibu Nia"),
                ("DO-DEMO-JKT03-002", "PO-DEMO-JKT03-20260721", "SPPG-JKT-03", "SCH-JKT-08", 192, 192, 0, "RECEIVED", "2026-07-20T03:40:00+00:00", "2026-07-20T04:40:00+00:00", "Pak Rudi"),
                ("DO-DEMO-JKT04-001", "PO-DEMO-JKT04-20260721", "SPPG-JKT-04", "SCH-JKT-09", 160, 160, 0, "RECEIVED", "2026-07-20T03:25:00+00:00", "2026-07-20T04:10:00+00:00", "Ibu Sinta"),
                ("DO-DEMO-JKT04-002", "PO-DEMO-JKT04-20260721", "SPPG-JKT-04", "SCH-JKT-10", 176, 176, 0, "RECEIVED", "2026-07-20T03:50:00+00:00", "2026-07-20T04:50:00+00:00", "Pak Fajar"),
                ("DO-DEMO-JKT05-001", "PO-DEMO-JKT05-20260721", "SPPG-JKT-05", "SCH-JKT-13", 110, 110, 0, "RECEIVED", "2026-07-20T03:15:00+00:00", "2026-07-20T04:00:00+00:00", "Ibu Wulan"),
                ("DO-DEMO-JKT05-002", "PO-DEMO-JKT05-20260721", "SPPG-JKT-05", "SCH-JKT-14", 108, 106, 2, "PARTIALLY_RECEIVED", "2026-07-20T03:35:00+00:00", "2026-07-20T04:20:00+00:00", "Pak Hendra"),
                ("DO-DEMO-JKT05-003", "PO-DEMO-JKT05-20260721", "SPPG-JKT-05", "SCH-JKT-15", 108, 108, 0, "RECEIVED", "2026-07-20T03:55:00+00:00", "2026-07-20T04:45:00+00:00", "Ibu Sari"),
                ("DO-DEMO-JKT06-001", "PO-DEMO-JKT06-20260721", "SPPG-JKT-06", "SCH-JKT-16", 104, 104, 0, "RECEIVED", "2026-07-20T03:20:00+00:00", "2026-07-20T04:10:00+00:00", "Pak Rahmat"),
                ("DO-DEMO-JKT06-002", "PO-DEMO-JKT06-20260721", "SPPG-JKT-06", "SCH-JKT-17", 106, 104, 2, "PARTIALLY_RECEIVED", "2026-07-20T03:40:00+00:00", "2026-07-20T04:35:00+00:00", "Ibu Lina"),
                ("DO-DEMO-JKT06-003", "PO-DEMO-JKT06-20260721", "SPPG-JKT-06", "SCH-JKT-18", 108, 106, 2, "PARTIALLY_RECEIVED", "2026-07-20T04:00:00+00:00", "2026-07-20T04:55:00+00:00", "Pak Yusuf"),
                ("DO-DEMO-JKT07-001", "PO-DEMO-JKT07-20260721", "SPPG-JKT-07", "SCH-JKT-19", 112, 112, 0, "RECEIVED", "2026-07-20T03:10:00+00:00", "2026-07-20T04:05:00+00:00", "Ibu Melati"),
                ("DO-DEMO-JKT07-002", "PO-DEMO-JKT07-20260721", "SPPG-JKT-07", "SCH-JKT-20", 116, 114, 2, "PARTIALLY_RECEIVED", "2026-07-20T03:35:00+00:00", "2026-07-20T04:30:00+00:00", "Pak Tono"),
                ("DO-DEMO-JKT07-003", "PO-DEMO-JKT07-20260721", "SPPG-JKT-07", "SCH-JKT-21", 112, 112, 0, "RECEIVED", "2026-07-20T04:00:00+00:00", "2026-07-20T05:00:00+00:00", "Ibu Kartika"),
                ("DO-DEMO-JKT08-001", "PO-DEMO-JKT08-20260721", "SPPG-JKT-08", "SCH-JKT-22", 110, 110, 0, "RECEIVED", "2026-07-20T03:25:00+00:00", "2026-07-20T04:15:00+00:00", "Pak Damar"),
                ("DO-DEMO-JKT08-002", "PO-DEMO-JKT08-20260721", "SPPG-JKT-08", "SCH-JKT-23", 112, 110, 2, "PARTIALLY_RECEIVED", "2026-07-20T03:50:00+00:00", "2026-07-20T04:40:00+00:00", "Ibu Ratri"),
                ("DO-DEMO-JKT08-003", "PO-DEMO-JKT08-20260721", "SPPG-JKT-08", "SCH-JKT-24", 112, 110, 2, "PARTIALLY_RECEIVED", "2026-07-20T04:10:00+00:00", "2026-07-20T05:05:00+00:00", "Pak Bimo"),
            ]
            created_delivery_count = 0
            updated_delivery_count = 0
            for (
                delivery_number,
                production_number,
                sppg_code,
                school_code,
                shipped_portions,
                received_portions,
                rejected_portions,
                status,
                planned_departure_raw,
                planned_arrival_raw,
                receiver_name,
            ) in delivery_seed:
                production_order = existing_production_orders.get(production_number)
                school_item = school_map.get(school_code)
                if production_order is None or school_item is None:
                    continue
                planned_departure = datetime.fromisoformat(planned_departure_raw)
                planned_arrival = datetime.fromisoformat(planned_arrival_raw)
                actual_departure = planned_departure if status in {"IN_TRANSIT", "LOADING", "ARRIVED", "RECEIVED", "PARTIALLY_RECEIVED"} else None
                actual_arrival = planned_arrival if status in {"RECEIVED", "PARTIALLY_RECEIVED"} else None
                delivery_order = existing_delivery_orders.get(delivery_number)
                if delivery_order is None:
                    delivery_order = await delivery_order_repository.add(
                        DeliveryOrder(
                            tenant_id=tenant.id,
                            sppg_id=sppg_map[sppg_code].id,
                            production_order_id=production_order.id,
                            route_id=None,
                            school_id=school_item.id,
                            delivery_number=delivery_number,
                            planned_departure=planned_departure,
                            actual_departure=actual_departure,
                            planned_arrival=planned_arrival,
                            actual_arrival=actual_arrival,
                            planned_portions=shipped_portions,
                            shipped_portions=shipped_portions,
                            received_portions=received_portions,
                            rejected_portions=rejected_portions,
                            status=status,
                            receiver_name=receiver_name,
                            receiver_gps=_format_gps(school_item.latitude, school_item.longitude) if actual_arrival else None,
                        )
                    )
                    created_delivery_count += 1
                else:
                    delivery_order.sppg_id = sppg_map[sppg_code].id
                    delivery_order.production_order_id = production_order.id
                    delivery_order.school_id = school_item.id
                    delivery_order.planned_departure = planned_departure
                    delivery_order.actual_departure = actual_departure
                    delivery_order.planned_arrival = planned_arrival
                    delivery_order.actual_arrival = actual_arrival
                    delivery_order.planned_portions = shipped_portions
                    delivery_order.shipped_portions = shipped_portions
                    delivery_order.received_portions = received_portions
                    delivery_order.rejected_portions = rejected_portions
                    delivery_order.status = status
                    delivery_order.receiver_name = receiver_name
                    delivery_order.receiver_gps = _format_gps(school_item.latitude, school_item.longitude) if actual_arrival else None
                    updated_delivery_count += 1
                await session.commit()
                existing_delivery_orders[delivery_order.delivery_number] = delivery_order
            if created_delivery_count:
                print(f"Delivery order demo dibuat: {created_delivery_count}")
            elif updated_delivery_count == 0:
                print("Delivery order demo sudah tersedia.")
            if updated_delivery_count:
                print(f"Delivery order demo diperbarui: {updated_delivery_count}")

            existing_routes = {item.route_code: item for item in await delivery_route_repository.list_all(tenant.id)}
            route_seed = [
                (
                    "RT-DEMO-JKT01-20260720",
                    "SPPG-JKT-01",
                    "Rute Menteng Pagi",
                    "2026-07-20T03:20:00+00:00",
                    "2026-07-20T04:45:00+00:00",
                    "ARRIVED",
                    ["DO-DEMO-JKT01-001", "DO-DEMO-JKT01-002"],
                ),
                (
                    "RT-DEMO-JKT01-20260721",
                    "SPPG-JKT-01",
                    "Rute Menteng Besok",
                    "2026-07-21T03:20:00+00:00",
                    "2026-07-21T04:50:00+00:00",
                    "PLANNED",
                    ["DO-DEMO-JKT01-003", "DO-DEMO-JKT01-004"],
                ),
                (
                    "RT-DEMO-JKT02-20260721",
                    "SPPG-JKT-02",
                    "Rute Kemayoran Besok",
                    "2026-07-21T03:30:00+00:00",
                    "2026-07-21T05:00:00+00:00",
                    "PLANNED",
                    ["DO-DEMO-JKT02-001", "DO-DEMO-JKT02-002"],
                ),
                (
                    "RT-DEMO-JKT03-20260721",
                    "SPPG-JKT-03",
                    "Rute Sunter Besok",
                    "2026-07-21T03:10:00+00:00",
                    "2026-07-21T04:50:00+00:00",
                    "PLANNED",
                    ["DO-DEMO-JKT03-001", "DO-DEMO-JKT03-002"],
                ),
                (
                    "RT-DEMO-JKT04-20260721",
                    "SPPG-JKT-04",
                    "Rute Tebet Besok",
                    "2026-07-21T03:15:00+00:00",
                    "2026-07-21T05:00:00+00:00",
                    "PLANNED",
                    ["DO-DEMO-JKT04-001", "DO-DEMO-JKT04-002"],
                ),
                (
                    "RT-DEMO-JKT05-20260720",
                    "SPPG-JKT-05",
                    "Rute Palmerah Hari Ini",
                    "2026-07-20T03:05:00+00:00",
                    "2026-07-20T04:50:00+00:00",
                    "ARRIVED",
                    ["DO-DEMO-JKT05-001", "DO-DEMO-JKT05-002", "DO-DEMO-JKT05-003"],
                ),
                (
                    "RT-DEMO-JKT06-20260720",
                    "SPPG-JKT-06",
                    "Rute Kembangan Hari Ini",
                    "2026-07-20T03:10:00+00:00",
                    "2026-07-20T05:00:00+00:00",
                    "ARRIVED",
                    ["DO-DEMO-JKT06-001", "DO-DEMO-JKT06-002", "DO-DEMO-JKT06-003"],
                ),
                (
                    "RT-DEMO-JKT07-20260720",
                    "SPPG-JKT-07",
                    "Rute Cakung Hari Ini",
                    "2026-07-20T03:00:00+00:00",
                    "2026-07-20T05:10:00+00:00",
                    "ARRIVED",
                    ["DO-DEMO-JKT07-001", "DO-DEMO-JKT07-002", "DO-DEMO-JKT07-003"],
                ),
                (
                    "RT-DEMO-JKT08-20260720",
                    "SPPG-JKT-08",
                    "Rute Pasar Minggu Hari Ini",
                    "2026-07-20T03:15:00+00:00",
                    "2026-07-20T05:10:00+00:00",
                    "ARRIVED",
                    ["DO-DEMO-JKT08-001", "DO-DEMO-JKT08-002", "DO-DEMO-JKT08-003"],
                ),
            ]
            created_route_count = 0
            for route_code, sppg_code, route_name, depart_raw, arrive_raw, route_status, delivery_numbers in route_seed:
                if route_code in existing_routes:
                    continue
                sppg_item = sppg_map[sppg_code]
                delivery_items = [existing_delivery_orders[number] for number in delivery_numbers if number in existing_delivery_orders]
                if not delivery_items:
                    continue
                last_school = next((school_map[code] for code in school_map if school_map[code].id == delivery_items[-1].school_id), None)
                route = await delivery_route_repository.add(
                    DeliveryRoute(
                        tenant_id=tenant.id,
                        sppg_id=sppg_item.id,
                        route_code=route_code,
                        route_name=route_name,
                        route_status=route_status,
                        planned_departure=datetime.fromisoformat(depart_raw),
                        actual_departure=datetime.fromisoformat(depart_raw) if route_status == "ARRIVED" else None,
                        planned_arrival=datetime.fromisoformat(arrive_raw),
                        actual_arrival=datetime.fromisoformat(arrive_raw) if route_status == "ARRIVED" else None,
                        origin_gps=_format_gps(sppg_item.latitude, sppg_item.longitude),
                        destination_gps=_format_gps(last_school.latitude, last_school.longitude) if last_school else None,
                        total_distance_km=None,
                        notes=f"Rute demo {route_name}",
                    )
                )
                for sequence, delivery_item in enumerate(delivery_items, start=1):
                    school_item = next(item for item in school_map.values() if item.id == delivery_item.school_id)
                    await delivery_route_stop_repository.add(
                        DeliveryRouteStop(
                            tenant_id=tenant.id,
                            route_id=route.id,
                            delivery_order_id=delivery_item.id,
                            school_id=school_item.id,
                            stop_sequence=sequence,
                            planned_arrival=delivery_item.planned_arrival,
                            actual_arrival=delivery_item.actual_arrival,
                            planned_departure=delivery_item.planned_arrival,
                            actual_departure=delivery_item.actual_arrival,
                            status=delivery_item.status,
                            recipient_name=delivery_item.receiver_name,
                            stop_gps=_format_gps(school_item.latitude, school_item.longitude),
                            notes=f"Stop demo untuk {school_item.name}",
                        )
                    )
                    delivery_item.route_id = route.id
                await session.commit()
                existing_routes[route.route_code] = route
                created_route_count += 1
            if created_route_count:
                print(f"Route delivery demo dibuat: {created_route_count}")
            else:
                print("Route delivery demo sudah tersedia.")

            existing_proof_delivery_ids = {
                proof.delivery_order_id
                for proof in (await session.execute(select(DeliveryProof).where(DeliveryProof.tenant_id == tenant.id))).scalars().all()
            }
            proof_seed = [
                ("DO-DEMO-JKT01-001", "2026-07-20T04:16:00+00:00", 318, 0, "GOOD", "Diterima lengkap dan hangat."),
                ("DO-DEMO-JKT01-002", "2026-07-20T04:37:00+00:00", 158, 2, "MINOR_ISSUE", "Dua porsi rusak ringan saat bongkar."),
                ("DO-DEMO-JKT05-001", "2026-07-20T04:02:00+00:00", 110, 0, "GOOD", "Palmerah diterima sesuai jadwal."),
                ("DO-DEMO-JKT06-002", "2026-07-20T04:38:00+00:00", 104, 2, "MINOR_ISSUE", "Dua boks penyok ringan saat turun."),
                ("DO-DEMO-JKT07-002", "2026-07-20T04:33:00+00:00", 114, 2, "MINOR_ISSUE", "Terdapat dua porsi cadangan rusak ringan."),
                ("DO-DEMO-JKT08-001", "2026-07-20T04:17:00+00:00", 110, 0, "GOOD", "Distribusi Pasar Minggu diterima lengkap."),
            ]
            created_proof_count = 0
            route_stops_by_delivery_id = {
                stop.delivery_order_id: stop
                for route in existing_routes.values()
                for stop in await delivery_route_stop_repository.list_by_route(route.id)
            }
            for delivery_number, received_at_raw, received_portions, rejected_portions, condition_status, condition_notes in proof_seed:
                delivery_item = existing_delivery_orders.get(delivery_number)
                if delivery_item is None or delivery_item.id in existing_proof_delivery_ids:
                    continue
                stop = route_stops_by_delivery_id.get(delivery_item.id)
                proof = await delivery_proof_repository.add(
                    DeliveryProof(
                        tenant_id=tenant.id,
                        delivery_order_id=delivery_item.id,
                        route_id=delivery_item.route_id,
                        route_stop_id=stop.id if stop else None,
                        received_at=datetime.fromisoformat(received_at_raw),
                        receiver_name=delivery_item.receiver_name or "Penerima Demo",
                        receiver_gps=delivery_item.receiver_gps,
                        received_portions=received_portions,
                        rejected_portions=rejected_portions,
                        temperature_celsius=56.5,
                        condition_status=condition_status,
                        condition_notes=condition_notes,
                        photo_urls=[],
                        signature_name=delivery_item.receiver_name,
                        signature_url=None,
                        signature_signed_at=datetime.fromisoformat(received_at_raw),
                        incident_notes=None,
                        linked_incident_ids=[],
                    )
                )
                await session.commit()
                existing_proof_delivery_ids.add(proof.delivery_order_id)
                created_proof_count += 1
            if created_proof_count:
                print(f"Proof delivery demo dibuat: {created_proof_count}")
            else:
                print("Proof delivery demo sudah tersedia.")

            existing_incident_titles = {
                incident.title
                for incident in (
                    await session.execute(select(DeliveryIncident).where(DeliveryIncident.tenant_id == tenant.id))
                ).scalars().all()
            }
            incident_seed = [
                (
                    "DO-DEMO-JKT01-002",
                    "Kemasan sudut basah",
                    "QUALITY",
                    "MEDIUM",
                    "2026-07-20T04:28:00+00:00",
                    "Dua paket pada stop kedua mengalami kebasahan ringan saat bongkar.",
                    "RESOLVED",
                    "Driver mengganti kemasan cadangan di lokasi.",
                ),
                (
                    "DO-DEMO-JKT03-001",
                    "Lalu lintas padat jalur Sunter",
                    "DELAY",
                    "LOW",
                    "2026-07-21T03:55:00+00:00",
                    "Estimasi keterlambatan 10 menit karena kepadatan akses keluar dapur.",
                    "OPEN",
                    None,
                ),
                (
                    "DO-DEMO-JKT04-001",
                    "Akses bongkar sempit di Tebet",
                    "ACCESS",
                    "LOW",
                    "2026-07-20T03:58:00+00:00",
                    "Kendaraan perlu parkir ulang karena akses gerbang sekolah sedang padat.",
                    "RESOLVED",
                    "Koordinasi ulang titik bongkar dengan petugas sekolah.",
                ),
                (
                    "DO-DEMO-JKT02-002",
                    "Antrian lift barang Kemayoran",
                    "DELAY",
                    "MEDIUM",
                    "2026-07-21T04:18:00+00:00",
                    "Distribusi ke sekolah lantai atas tertunda karena lift layanan dipakai bersama.",
                    "OPEN",
                    None,
                ),
                (
                    "DO-DEMO-JKT05-002",
                    "Kemacetan Slipi menjelang sekolah",
                    "DELAY",
                    "LOW",
                    "2026-07-20T03:52:00+00:00",
                    "Laju kendaraan melambat di akses Slipi sehingga satu stop mundur beberapa menit.",
                    "RESOLVED",
                    "Driver dialihkan ke akses samping untuk percepatan bongkar.",
                ),
                (
                    "DO-DEMO-JKT07-002",
                    "Palet geser saat bongkar Cakung",
                    "HANDLING",
                    "MEDIUM",
                    "2026-07-20T04:20:00+00:00",
                    "Satu palet bergeser ketika proses penurunan sehingga perlu pengecekan ulang kemasan.",
                    "RESOLVED",
                    "Tim bongkar menata ulang palet dan mengganti dua kemasan cadangan.",
                ),
                (
                    "DO-DEMO-JKT08-003",
                    "Akses parkir sempit Pejaten",
                    "ACCESS",
                    "LOW",
                    "2026-07-20T04:42:00+00:00",
                    "Kendaraan harus antre singkat karena area parkir sekolah dipakai penjemputan.",
                    "RESOLVED",
                    "Petugas sekolah membuka titik bongkar alternatif.",
                ),
            ]
            created_incident_count = 0
            for (
                delivery_number,
                title,
                category,
                severity,
                incident_time_raw,
                description,
                status,
                resolution_notes,
            ) in incident_seed:
                if title in existing_incident_titles:
                    continue
                delivery_item = existing_delivery_orders.get(delivery_number)
                if delivery_item is None:
                    continue
                stop = route_stops_by_delivery_id.get(delivery_item.id)
                incident = await delivery_incident_repository.add(
                    DeliveryIncident(
                        tenant_id=tenant.id,
                        delivery_order_id=delivery_item.id,
                        route_id=delivery_item.route_id,
                        route_stop_id=stop.id if stop else None,
                        incident_time=datetime.fromisoformat(incident_time_raw),
                        category=category,
                        severity=severity,
                        title=title,
                        description=description,
                        incident_gps=delivery_item.receiver_gps if delivery_item.receiver_gps else (stop.stop_gps if stop else None),
                        temperature_celsius=55.0 if category == "QUALITY" else None,
                        media_urls=[],
                        status=status,
                        resolution_notes=resolution_notes,
                    )
                )
                await session.commit()
                existing_incident_titles.add(incident.title)
                created_incident_count += 1
            if created_incident_count:
                print(f"Incident delivery demo dibuat: {created_incident_count}")
            else:
                print("Incident delivery demo sudah tersedia.")

            legacy_vehicle_types = list(
                (
                    await session.execute(
                        select(VehicleType).where(
                            VehicleType.tenant_id == tenant.id,
                            VehicleType.code.like("VAN-%"),
                            VehicleType.code != "VAN-COLD",
                        )
                    )
                ).scalars().all()
            )
            legacy_vehicles = list(
                (
                    await session.execute(
                        select(Vehicle).where(
                            Vehicle.tenant_id == tenant.id,
                            Vehicle.vehicle_code.like("VH-%"),
                            ~Vehicle.vehicle_code.like("VH-JKT%"),
                        )
                    )
                ).scalars().all()
            )
            legacy_drivers = list(
                (
                    await session.execute(
                        select(Driver).where(
                            Driver.tenant_id == tenant.id,
                            or_(
                                Driver.driver_code.like("DRV-JKT__"),
                                Driver.driver_code.like("DRV-%"),
                            ),
                            ~Driver.driver_code.like("DRV-JKT__-__"),
                        )
                    )
                ).scalars().all()
            )
            legacy_vehicle_ids = [item.id for item in legacy_vehicles]
            legacy_driver_ids = [item.id for item in legacy_drivers]
            legacy_vehicle_type_ids = [item.id for item in legacy_vehicle_types]
            if legacy_vehicle_ids:
                await session.execute(delete(VehicleLocation).where(VehicleLocation.vehicle_id.in_(legacy_vehicle_ids)))
                await session.execute(delete(VehicleAssignment).where(VehicleAssignment.vehicle_id.in_(legacy_vehicle_ids)))
                await session.execute(delete(VehicleMaintenance).where(VehicleMaintenance.vehicle_id.in_(legacy_vehicle_ids)))
                await session.execute(delete(Vehicle).where(Vehicle.id.in_(legacy_vehicle_ids)))
            if legacy_driver_ids:
                await session.execute(delete(Driver).where(Driver.id.in_(legacy_driver_ids)))
            if legacy_vehicle_type_ids:
                await session.execute(delete(VehicleType).where(VehicleType.id.in_(legacy_vehicle_type_ids)))
            if legacy_vehicle_ids or legacy_driver_ids or legacy_vehicle_type_ids:
                await session.commit()
                print(
                    "Fleet demo lama dibersihkan: "
                    f"{len(legacy_vehicle_types)} vehicle type, "
                    f"{len(legacy_vehicles)} vehicle, "
                    f"{len(legacy_drivers)} driver."
                )

            vehicle_type_seed = [
                ("VAN-COLD", "Van Pendingin", "Van berpendingin untuk distribusi menu siap saji", 1200, 850.0, True),
                ("BOX-MED", "Box Truck Medium", "Truk box medium untuk distribusi multi sekolah", 2200, 1800.0, False),
                ("PICKUP-FAST", "Pickup Cepat", "Pickup kecil untuk rute pendek dan suplai cadangan", 600, 650.0, False),
            ]
            existing_vehicle_types = {
                item.code: item
                for item in (
                    await session.execute(select(VehicleType).where(VehicleType.tenant_id == tenant.id))
                ).scalars().all()
            }
            created_vehicle_type_count = 0
            for code, name, description, capacity_portions, capacity_kg, temperature_controlled in vehicle_type_seed:
                vehicle_type = existing_vehicle_types.get(code)
                if vehicle_type is None:
                    vehicle_type = VehicleType(
                        tenant_id=tenant.id,
                        code=code,
                        name=name,
                        description=description,
                        capacity_portions=capacity_portions,
                        capacity_kg=capacity_kg,
                        temperature_controlled=temperature_controlled,
                        is_active=True,
                    )
                    session.add(vehicle_type)
                    created_vehicle_type_count += 1
                else:
                    vehicle_type.name = name
                    vehicle_type.description = description
                    vehicle_type.capacity_portions = capacity_portions
                    vehicle_type.capacity_kg = capacity_kg
                    vehicle_type.temperature_controlled = temperature_controlled
                    vehicle_type.is_active = True
                await session.commit()
                existing_vehicle_types[code] = vehicle_type
            if created_vehicle_type_count:
                print(f"Vehicle type demo dibuat: {created_vehicle_type_count}")
            else:
                print("Vehicle type demo sudah tersedia.")

            vehicle_profiles = [
                ("VAN-COLD", "OWNED", "Toyota", "HiAce", 2024, 1000, "DIESEL", "IN_TRANSIT", "Unit distribusi utama"),
                ("BOX-MED", "OWNED", "Isuzu", "Elf Box", 2023, 1800, "DIESEL", "READY", "Unit rute sekolah padat"),
                ("PICKUP-FAST", "OWNED", "Suzuki", "Carry Box", 2024, 550, "BENSIN", "READY", "Unit pengiriman cepat"),
                ("VAN-COLD", "LEASED", "Mitsubishi", "L300 Cooler", 2022, 920, "DIESEL", "IN_TRANSIT", "Unit cadangan dingin"),
                ("BOX-MED", "OWNED", "Hino", "Dutro Box", 2021, 1900, "DIESEL", "MAINTENANCE", "Unit heavy load"),
            ]
            vehicle_seed: list[tuple[str, str, str, str, str, str, str, int, int, str, str, str]] = []
            for sppg_index in range(1, 9):
                sppg_code = f"SPPG-JKT-{sppg_index:02d}"
                for unit_index, profile in enumerate(vehicle_profiles, start=1):
                    (
                        vehicle_type_code,
                        ownership_status,
                        brand_name,
                        model_name,
                        manufacture_year,
                        capacity_portions,
                        fuel_type,
                        status,
                        note_prefix,
                    ) = profile
                    vehicle_seed.append(
                        (
                            f"VH-JKT{sppg_index:02d}-{unit_index:02d}",
                            f"B {2100 + ((sppg_index - 1) * 10) + unit_index} MBG",
                            sppg_code,
                            vehicle_type_code,
                            ownership_status,
                            brand_name,
                            model_name,
                            manufacture_year,
                            capacity_portions,
                            fuel_type,
                            status,
                            f"{note_prefix} {sppg_map[sppg_code].name}",
                        )
                    )
            existing_vehicles = {
                item.vehicle_code: item
                for item in (
                    await session.execute(select(Vehicle).where(Vehicle.tenant_id == tenant.id))
                ).scalars().all()
            }
            created_vehicle_count = 0
            for (
                vehicle_code,
                plate_number,
                sppg_code,
                vehicle_type_code,
                ownership_status,
                brand_name,
                model_name,
                manufacture_year,
                capacity_portions,
                fuel_type,
                status,
                notes,
            ) in vehicle_seed:
                vehicle = existing_vehicles.get(vehicle_code)
                if vehicle is None:
                    vehicle = Vehicle(
                        tenant_id=tenant.id,
                        home_sppg_id=sppg_map[sppg_code].id,
                        vehicle_type_id=existing_vehicle_types[vehicle_type_code].id,
                        vehicle_code=vehicle_code,
                        plate_number=plate_number,
                        ownership_status=ownership_status,
                        brand_name=brand_name,
                        model_name=model_name,
                        manufacture_year=manufacture_year,
                        capacity_portions=capacity_portions,
                        fuel_type=fuel_type,
                        status=status,
                        is_active=True,
                        notes=notes,
                    )
                    session.add(vehicle)
                    created_vehicle_count += 1
                else:
                    vehicle.home_sppg_id = sppg_map[sppg_code].id
                    vehicle.vehicle_type_id = existing_vehicle_types[vehicle_type_code].id
                    vehicle.plate_number = plate_number
                    vehicle.ownership_status = ownership_status
                    vehicle.brand_name = brand_name
                    vehicle.model_name = model_name
                    vehicle.manufacture_year = manufacture_year
                    vehicle.capacity_portions = capacity_portions
                    vehicle.fuel_type = fuel_type
                    vehicle.status = status
                    vehicle.is_active = True
                    vehicle.notes = notes
                await session.commit()
                existing_vehicles[vehicle_code] = vehicle
            if created_vehicle_count:
                print(f"Vehicle demo dibuat: {created_vehicle_count}")
            else:
                print("Vehicle demo sudah tersedia.")

            first_names = ["Agus", "Rudi", "Maya", "Fajar", "Wulan", "Rahmat", "Tono", "Damar", "Siti", "Bima"]
            last_names = ["Santoso", "Hartono", "Lestari", "Nugroho", "Sari", "Hidayat", "Prasetyo", "Wijaya", "Permata", "Saputra"]
            license_types = ["B1", "B2", "A", "B1", "B2"]
            driver_seed: list[tuple[str, str, str, str, str, date, str, str]] = []
            for sppg_index in range(1, 9):
                for unit_index in range(1, 6):
                    seed_index = sppg_index + unit_index - 2
                    first_name = first_names[seed_index % len(first_names)]
                    last_name = last_names[(seed_index + unit_index) % len(last_names)]
                    license_type = license_types[(unit_index - 1) % len(license_types)]
                    driver_seed.append(
                        (
                            f"DRV-JKT{sppg_index:02d}-{unit_index:02d}",
                            f"{first_name} {last_name}",
                            f"081210{sppg_index:02d}{unit_index:02d}00",
                            f"SIM{license_type}-{sppg_index:02d}{unit_index:02d}26",
                            license_type,
                            date(2027, min(12, unit_index + 7), min(28, 10 + sppg_index)),
                            "ACTIVE",
                            f"Driver unit {unit_index} untuk {sppg_map[f'SPPG-JKT-{sppg_index:02d}'].name}",
                        )
                    )
            existing_drivers = {
                item.driver_code: item
                for item in (
                    await session.execute(select(Driver).where(Driver.tenant_id == tenant.id))
                ).scalars().all()
            }
            created_driver_count = 0
            for driver_code, full_name, phone_number, license_number, license_type, license_expiry_date, status, notes in driver_seed:
                driver = existing_drivers.get(driver_code)
                if driver is None:
                    driver = Driver(
                        tenant_id=tenant.id,
                        driver_code=driver_code,
                        full_name=full_name,
                        phone_number=phone_number,
                        license_number=license_number,
                        license_type=license_type,
                        license_expiry_date=license_expiry_date,
                        status=status,
                        is_active=True,
                        notes=notes,
                    )
                    session.add(driver)
                    created_driver_count += 1
                else:
                    driver.full_name = full_name
                    driver.phone_number = phone_number
                    driver.license_number = license_number
                    driver.license_type = license_type
                    driver.license_expiry_date = license_expiry_date
                    driver.status = status
                    driver.is_active = True
                    driver.notes = notes
                await session.commit()
                existing_drivers[driver_code] = driver
            if created_driver_count:
                print(f"Driver demo dibuat: {created_driver_count}")
            else:
                print("Driver demo sudah tersedia.")

            demo_vehicle_ids = [vehicle.id for code, vehicle in existing_vehicles.items() if code.startswith("VH-JKT")]
            if demo_vehicle_ids:
                await session.execute(delete(VehicleLocation).where(VehicleLocation.vehicle_id.in_(demo_vehicle_ids)))
                await session.execute(delete(VehicleAssignment).where(VehicleAssignment.vehicle_id.in_(demo_vehicle_ids)))
                await session.execute(delete(VehicleMaintenance).where(VehicleMaintenance.vehicle_id.in_(demo_vehicle_ids)))
                await session.commit()

            assignment_roles = ["DELIVERY", "DISTRIBUTION", "BACKUP", "SUPPLY", "DELIVERY"]
            assignment_seed: list[tuple[str, str, str, date, date | None, str, str, str]] = []
            for sppg_index in range(1, 9):
                sppg_code = f"SPPG-JKT-{sppg_index:02d}"
                for unit_index in range(1, 6):
                    vehicle_code = f"VH-JKT{sppg_index:02d}-{unit_index:02d}"
                    driver_code = f"DRV-JKT{sppg_index:02d}-{unit_index:02d}"
                    vehicle_status = existing_vehicles[vehicle_code].status
                    assignment_seed.append(
                        (
                            vehicle_code,
                            sppg_code,
                            driver_code,
                            date(2026, 7, 20),
                            None,
                            assignment_roles[unit_index - 1],
                            "ASSIGNED" if vehicle_status != "MAINTENANCE" else "STANDBY",
                            f"Assignment unit {unit_index} untuk operasi {sppg_map[sppg_code].district or sppg_map[sppg_code].city}",
                        )
                    )
            existing_assignment_keys = {
                (item.vehicle_id, item.assignment_date, item.assignment_role): item
                for item in (
                    await session.execute(select(VehicleAssignment).where(VehicleAssignment.tenant_id == tenant.id))
                ).scalars().all()
            }
            created_assignment_count = 0
            for vehicle_code, sppg_code, driver_code, assignment_date, end_date, assignment_role, status, notes in assignment_seed:
                vehicle = existing_vehicles[vehicle_code]
                driver = existing_drivers[driver_code]
                assignment_key = (vehicle.id, assignment_date, assignment_role)
                assignment = existing_assignment_keys.get(assignment_key)
                if assignment is None:
                    assignment = VehicleAssignment(
                        tenant_id=tenant.id,
                        sppg_id=sppg_map[sppg_code].id,
                        vehicle_id=vehicle.id,
                        driver_id=driver.id,
                        assignment_date=assignment_date,
                        end_date=end_date,
                        assignment_role=assignment_role,
                        status=status,
                        is_active=True,
                        notes=notes,
                    )
                    session.add(assignment)
                    created_assignment_count += 1
                else:
                    assignment.sppg_id = sppg_map[sppg_code].id
                    assignment.driver_id = driver.id
                    assignment.end_date = end_date
                    assignment.status = status
                    assignment.is_active = True
                    assignment.notes = notes
                await session.commit()
                existing_assignment_keys[assignment_key] = assignment
            if created_assignment_count:
                print(f"Vehicle assignment demo dibuat: {created_assignment_count}")
            else:
                print("Vehicle assignment demo sudah tersedia.")

            maintenance_seed = [
                ("VH-JKT01-05", "SPPG-JKT-01", date(2026, 7, 19), "BRAKE_CHECK", 28640.0, 780000.0, "Bengkel Armada Pusat", "SCHEDULED", "Pengecekan rem unit cadangan."),
                ("VH-JKT03-05", "SPPG-JKT-03", date(2026, 7, 18), "PREVENTIVE_SERVICE", 48210.0, 1850000.0, "Bengkel Armada Utara", "COMPLETED", "Servis berkala sebelum distribusi puncak."),
                ("VH-JKT05-03", "SPPG-JKT-05", date(2026, 7, 19), "TIRE_REPLACEMENT", 22140.0, 950000.0, "Ban Palmerah Jaya", "COMPLETED", "Penggantian dua ban belakang."),
                ("VH-JKT06-05", "SPPG-JKT-06", date(2026, 7, 20), "COOLING_CHECK", 15330.0, 425000.0, "Cold Chain Service", "SCHEDULED", "Pemeriksaan pendingin sebelum rute panjang."),
                ("VH-JKT08-02", "SPPG-JKT-08", date(2026, 7, 17), "OIL_CHANGE", 19750.0, 650000.0, "Pasar Minggu Diesel Hub", "COMPLETED", "Ganti oli selesai sebelum siklus akhir pekan."),
            ]
            existing_maintenance_keys = {
                (item.vehicle_id, item.maintenance_date, item.maintenance_type): item
                for item in (
                    await session.execute(select(VehicleMaintenance).where(VehicleMaintenance.tenant_id == tenant.id))
                ).scalars().all()
            }
            created_maintenance_count = 0
            for vehicle_code, sppg_code, maintenance_date, maintenance_type, odometer_km, cost_amount, vendor_name, status, notes in maintenance_seed:
                vehicle = existing_vehicles[vehicle_code]
                maintenance_key = (vehicle.id, maintenance_date, maintenance_type)
                maintenance = existing_maintenance_keys.get(maintenance_key)
                if maintenance is None:
                    maintenance = VehicleMaintenance(
                        tenant_id=tenant.id,
                        sppg_id=sppg_map[sppg_code].id,
                        vehicle_id=vehicle.id,
                        maintenance_date=maintenance_date,
                        maintenance_type=maintenance_type,
                        odometer_km=odometer_km,
                        cost_amount=cost_amount,
                        vendor_name=vendor_name,
                        status=status,
                        notes=notes,
                    )
                    session.add(maintenance)
                    created_maintenance_count += 1
                else:
                    maintenance.sppg_id = sppg_map[sppg_code].id
                    maintenance.odometer_km = odometer_km
                    maintenance.cost_amount = cost_amount
                    maintenance.vendor_name = vendor_name
                    maintenance.status = status
                    maintenance.notes = notes
                await session.commit()
                existing_maintenance_keys[maintenance_key] = maintenance
            if created_maintenance_count:
                print(f"Vehicle maintenance demo dibuat: {created_maintenance_count}")
            else:
                print("Vehicle maintenance demo sudah tersedia.")

            existing_location_keys = {
                (item.vehicle_id, item.recorded_at.isoformat(), item.event_type): item
                for item in (
                    await session.execute(select(VehicleLocation).where(VehicleLocation.tenant_id == tenant.id))
                ).scalars().all()
            }
            created_location_count = 0
            for sppg_index in range(1, 9):
                sppg_code = f"SPPG-JKT-{sppg_index:02d}"
                sppg = sppg_map[sppg_code]
                for unit_index in range(1, 6):
                    vehicle_code = f"VH-JKT{sppg_index:02d}-{unit_index:02d}"
                    driver_code = f"DRV-JKT{sppg_index:02d}-{unit_index:02d}"
                    vehicle = existing_vehicles[vehicle_code]
                    assignment = existing_assignment_keys[(vehicle.id, date(2026, 7, 20), assignment_roles[unit_index - 1])]
                    base_lat = _fleet_offset(sppg.latitude, unit_index, "lat")
                    base_lon = _fleet_offset(sppg.longitude, unit_index, "lon")
                    location_points = [
                        (
                            datetime(2026, 7, 20, 6, 45 + unit_index, tzinfo=timezone.utc),
                            base_lat - 0.0012,
                            base_lon - 0.0011,
                            0.0,
                            15.0 * unit_index,
                            7.0,
                            True,
                            "LOADING",
                            "START_SHIFT",
                            "seed_demo",
                            f"Area dapur {sppg.name}",
                            f"Check-in awal {driver_code}",
                        ),
                        (
                            datetime(2026, 7, 20, 7, 20 + unit_index, tzinfo=timezone.utc),
                            base_lat,
                            base_lon,
                            34.0 + (unit_index * 2),
                            42.0 * unit_index,
                            9.5,
                            True,
                            "IN_TRANSIT",
                            "GPS_PING",
                            "seed_demo",
                            f"Koridor distribusi {sppg.city}",
                            f"Perjalanan aktif {vehicle_code}",
                        ),
                        (
                            datetime(2026, 7, 20, 8, 5 + unit_index, tzinfo=timezone.utc),
                            base_lat + 0.0014,
                            base_lon + 0.0010,
                            12.0 if unit_index != 5 else 0.0,
                            65.0 * unit_index,
                            6.0,
                            unit_index != 5,
                            "ARRIVED" if unit_index != 5 else "MAINTENANCE",
                            "ARRIVAL" if unit_index != 5 else "SERVICE_STOP",
                            "seed_demo",
                            f"Titik layanan {unit_index} {sppg.district or sppg.city}",
                            "Posisi terakhir demo untuk frontend map",
                        ),
                    ]
                    for (
                        recorded_at,
                        latitude,
                        longitude,
                        speed_kph,
                        heading_degree,
                        accuracy_meter,
                        engine_on,
                        movement_status,
                        event_type,
                        source,
                        address_label,
                        notes,
                    ) in location_points:
                        location_key = (vehicle.id, recorded_at.isoformat(), event_type)
                        location = existing_location_keys.get(location_key)
                        if location is None:
                            location = VehicleLocation(
                                tenant_id=tenant.id,
                                sppg_id=sppg.id,
                                vehicle_id=vehicle.id,
                                assignment_id=assignment.id,
                                recorded_at=recorded_at,
                                latitude=latitude,
                                longitude=longitude,
                                location=WKTElement(f"POINT({longitude} {latitude})", srid=4326),
                                speed_kph=speed_kph,
                                heading_degree=heading_degree,
                                accuracy_meter=accuracy_meter,
                                engine_on=engine_on,
                                movement_status=movement_status,
                                event_type=event_type,
                                source=source,
                                address_label=address_label,
                                notes=notes,
                            )
                            session.add(location)
                            created_location_count += 1
                        else:
                            location.sppg_id = sppg.id
                            location.assignment_id = assignment.id
                            location.latitude = latitude
                            location.longitude = longitude
                            location.location = WKTElement(f"POINT({longitude} {latitude})", srid=4326)
                            location.speed_kph = speed_kph
                            location.heading_degree = heading_degree
                            location.accuracy_meter = accuracy_meter
                            location.engine_on = engine_on
                            location.movement_status = movement_status
                            location.source = source
                            location.address_label = address_label
                            location.notes = notes
                        await session.commit()
                        existing_location_keys[location_key] = location
            if created_location_count:
                print(f"Vehicle location demo dibuat: {created_location_count}")
            else:
                print("Vehicle location demo sudah tersedia.")

            existing_submission_keys = {
                (
                    submission.sppg_id,
                    submission.school_id,
                    submission.feedback_date.isoformat(),
                    submission.respondent_name,
                )
                for submission in (
                    await session.execute(select(FeedbackSubmission).where(FeedbackSubmission.tenant_id == tenant.id))
                ).scalars().all()
            }
            feedback_seed = [
                ("SPPG-JKT-01", "SCH-JKT-01", "2026-07-18", "Ibu Rina", "Kepala Sekolah", 92.0, 98.0, 6.0, 90.0, 91.0, "Porsi sesuai dan anak-anak suka menu hari ini."),
                ("SPPG-JKT-01", "SCH-JKT-04", "2026-07-19", "Pak Dedi", "Koordinator UKS", 84.0, 94.0, 9.0, 82.0, 85.0, "Secara umum baik, namun bongkar muat perlu lebih rapi."),
                ("SPPG-JKT-02", "SCH-JKT-05", "2026-07-19", "Ibu Wati", "Guru Piket", 88.0, 96.0, 5.0, 87.0, 88.0, "Distribusi tepat waktu dan suhu makanan masih bagus."),
                ("SPPG-JKT-03", "SCH-JKT-07", "2026-07-20", "Ibu Nia", "Wakil Kepala Sekolah", 81.0, 90.0, 12.0, 76.0, 80.0, "Ada sedikit keterlambatan, tetapi kualitas makanan masih diterima."),
                ("SPPG-JKT-04", "SCH-JKT-09", "2026-07-20", "Ibu Sinta", "Guru Kelas", 90.0, 97.0, 4.0, 89.0, 90.0, "Pelayanan konsisten dan komunikasi driver sangat baik."),
                ("SPPG-JKT-01", "SCH-JKT-02", "2026-07-20", "Ibu Maya", "Guru Piket", 89.0, 97.0, 5.0, 88.0, 87.0, "Anak-anak menerima menu dengan baik dan distribusi rapi."),
                ("SPPG-JKT-01", "SCH-JKT-03", "2026-07-20", "Pak Arif", "Wakil Kurikulum", 86.0, 95.0, 7.0, 84.0, 85.0, "Pelayanan baik, hanya perlu sedikit percepatan saat jam sibuk."),
                ("SPPG-JKT-02", "SCH-JKT-06", "2026-07-20", "Pak Yoga", "Kepala TU", 82.0, 92.0, 10.0, 79.0, 81.0, "Distribusi masih aman, tetapi perlu perbaikan waktu serah terima."),
                ("SPPG-JKT-03", "SCH-JKT-08", "2026-07-20", "Pak Rudi", "Wakasek Sarpras", 80.0, 89.0, 13.0, 75.0, 79.0, "Keterlambatan kecil mempengaruhi jadwal istirahat siswa."),
                ("SPPG-JKT-04", "SCH-JKT-10", "2026-07-20", "Pak Fajar", "Guru Olahraga", 87.0, 95.0, 6.0, 86.0, 88.0, "Kualitas makanan baik dan suhu masih terjaga."),
                ("SPPG-JKT-04", "SCH-JKT-11", "2026-07-19", "Bu Lestari", "Guru Kelas", 85.0, 93.0, 8.0, 83.0, 84.0, "Distribusi cukup baik, namun kemasan perlu lebih kokoh."),
                ("SPPG-JKT-04", "SCH-JKT-12", "2026-07-19", "Pak Hendra", "Koordinator UKS", 88.0, 96.0, 5.0, 86.0, 87.0, "Pelayanan konsisten dan responsif."),
            ]
            created_feedback_count = 0
            created_feedback_item_count = 0
            feedback_submissions_by_key: dict[tuple[UUID, UUID, str, str], FeedbackSubmission] = {}
            for (
                sppg_code,
                school_code,
                feedback_date_raw,
                respondent_name,
                respondent_role,
                overall_rating,
                acceptance_rate,
                food_waste_portions,
                delivery_timeliness_rating,
                temperature_rating,
                comment_text,
            ) in feedback_seed:
                sppg_item = sppg_map[sppg_code]
                school_item = school_map[school_code]
                key = (sppg_item.id, school_item.id, feedback_date_raw, respondent_name)
                if key in existing_submission_keys:
                    continue
                related_delivery = next(
                    (
                        order for order in existing_delivery_orders.values()
                        if order.sppg_id == sppg_item.id and order.school_id == school_item.id
                    ),
                    None,
                )
                related_meal_plan = next(
                    (
                        item for item in meal_plans_by_scope.values()
                        if item.sppg_id == sppg_item.id and item.plan_date.isoformat() >= feedback_date_raw
                    ),
                    None,
                )
                submission = FeedbackSubmission(
                    tenant_id=tenant.id,
                    sppg_id=sppg_item.id,
                    school_id=school_item.id,
                    meal_plan_id=related_meal_plan.id if related_meal_plan else None,
                    delivery_order_id=related_delivery.id if related_delivery else None,
                    feedback_date=date.fromisoformat(feedback_date_raw),
                    source_type="SCHOOL",
                    respondent_name=respondent_name,
                    respondent_role=respondent_role,
                    overall_rating=overall_rating,
                    acceptance_rate=acceptance_rate,
                    food_waste_portions=food_waste_portions,
                    delivery_timeliness_rating=delivery_timeliness_rating,
                    temperature_rating=temperature_rating,
                    comment_text=comment_text,
                    status="SUBMITTED",
                )
                session.add(submission)
                await session.flush()
                feedback_submissions_by_key[key] = submission
                existing_submission_keys.add(key)
                created_feedback_count += 1
                feedback_items = [
                    ("TASTE", "taste_score", overall_rating, "POSITIVE" if overall_rating >= 85 else "NEUTRAL", "Rasa makanan diterima baik."),
                    ("DELIVERY", "timeliness", delivery_timeliness_rating, "POSITIVE" if delivery_timeliness_rating >= 85 else "NEUTRAL", "Ketepatan pengiriman sesuai ekspektasi."),
                    ("TEMPERATURE", "temperature", temperature_rating, "POSITIVE" if temperature_rating >= 85 else "NEUTRAL", "Suhu makanan saat diterima cukup baik."),
                ]
                for item_type, metric_name, score, sentiment, item_comment in feedback_items:
                    session.add(
                        FeedbackItem(
                            tenant_id=tenant.id,
                            feedback_submission_id=submission.id,
                            item_type=item_type,
                            metric_name=metric_name,
                            score=score,
                            sentiment=sentiment,
                            comment_text=item_comment,
                        )
                    )
                    created_feedback_item_count += 1
                await session.commit()
            if created_feedback_count:
                print(f"Feedback submission demo dibuat: {created_feedback_count}")
                print(f"Feedback item demo dibuat: {created_feedback_item_count}")
            else:
                print("Feedback submission demo sudah tersedia.")

            existing_complaint_texts = {
                complaint.complaint_text
                for complaint in (
                    await session.execute(select(Complaint).where(Complaint.tenant_id == tenant.id))
                ).scalars().all()
            }
            complaint_seed = [
                (
                    "SPPG-JKT-01",
                    "SCH-JKT-04",
                    "2026-07-19",
                    "TEMPERATURE",
                    "MEDIUM",
                    "Sebagian makanan pada batch kedua mulai kurang hangat saat tiba.",
                    "RESOLVED",
                    "2026-07-19T10:30:00+00:00",
                    "Koordinasi ulang urutan bongkar dan penutup termal.",
                    "Pak Dedi",
                ),
                (
                    "SPPG-JKT-03",
                    "SCH-JKT-07",
                    "2026-07-20",
                    "DELIVERY_DELAY",
                    "LOW",
                    "Pengiriman datang lewat sekitar 10 menit dari jadwal.",
                    "OPEN",
                    None,
                    "Masih dalam pemantauan untuk jadwal besok.",
                    "Ibu Nia",
                ),
                (
                    "SPPG-JKT-02",
                    "SCH-JKT-06",
                    "2026-07-20",
                    "DELIVERY_DELAY",
                    "MEDIUM",
                    "Serah terima terlambat karena antrian akses bongkar di gedung sekolah.",
                    "OPEN",
                    None,
                    "Butuh penyesuaian slot kedatangan kendaraan.",
                    "Pak Yoga",
                ),
                (
                    "SPPG-JKT-04",
                    "SCH-JKT-11",
                    "2026-07-19",
                    "PACKAGING",
                    "LOW",
                    "Beberapa kemasan luar tampak penyok meski isi masih layak.",
                    "RESOLVED",
                    "2026-07-19T11:00:00+00:00",
                    "Vendor kemasan diminta mengganti batch berikutnya.",
                    "Bu Lestari",
                ),
            ]
            created_complaint_count = 0
            submissions_index = {
                (submission.sppg_id, submission.school_id, submission.respondent_name, submission.feedback_date.isoformat()): submission
                for submission in (
                    await session.execute(select(FeedbackSubmission).where(FeedbackSubmission.tenant_id == tenant.id))
                ).scalars().all()
            }
            for (
                sppg_code,
                school_code,
                complaint_date_raw,
                category,
                severity,
                complaint_text,
                resolution_status,
                resolved_at_raw,
                notes,
                respondent_name,
            ) in complaint_seed:
                if complaint_text in existing_complaint_texts:
                    continue
                sppg_item = sppg_map[sppg_code]
                school_item = school_map[school_code]
                feedback_submission = submissions_index.get(
                    (sppg_item.id, school_item.id, respondent_name, complaint_date_raw)
                )
                complaint = Complaint(
                    tenant_id=tenant.id,
                    sppg_id=sppg_item.id,
                    feedback_submission_id=feedback_submission.id if feedback_submission else None,
                    complaint_date=datetime.fromisoformat(f"{complaint_date_raw}T09:15:00"),
                    category=category,
                    severity=severity,
                    complaint_text=complaint_text,
                    resolution_status=resolution_status,
                    resolved_at=datetime.fromisoformat(resolved_at_raw.replace("+00:00", "")) if resolved_at_raw else None,
                    notes=notes,
                )
                session.add(complaint)
                await session.commit()
                existing_complaint_texts.add(complaint.complaint_text)
                created_complaint_count += 1
            if created_complaint_count:
                print(f"Complaint demo dibuat: {created_complaint_count}")
            else:
                print("Complaint demo sudah tersedia.")

            existing_score_keys = {
                (score.sppg_id, score.score_date.isoformat())
                for score in (
                    await session.execute(select(ServiceQualityScore).where(ServiceQualityScore.tenant_id == tenant.id))
                ).scalars().all()
            }
            score_seed = [
                ("SPPG-JKT-01", "2026-07-18", 96.0, 88.0, 90.0, 91.0, 92.0, 90.0, 96.0, "Kinerja stabil akhir pekan."),
                ("SPPG-JKT-01", "2026-07-19", 92.0, 84.0, 82.0, 85.0, 88.0, 88.0, 82.0, "Ada isu minor pada handling batch kedua."),
                ("SPPG-JKT-02", "2026-07-19", 95.0, 90.0, 89.0, 90.0, 89.0, 88.0, 94.0, "Layanan cukup konsisten."),
                ("SPPG-JKT-03", "2026-07-20", 90.0, 80.0, 78.0, 81.0, 84.0, 83.0, 80.0, "Butuh perbaikan ketepatan waktu distribusi."),
                ("SPPG-JKT-04", "2026-07-20", 97.0, 92.0, 90.0, 91.0, 93.0, 92.0, 97.0, "Pelayanan paling stabil untuk awal pekan."),
                ("SPPG-JKT-01", "2026-07-20", 94.0, 89.0, 87.0, 88.0, 90.0, 90.0, 90.0, "Distribusi pusat kota tetap kuat dengan isu minor terkontrol."),
                ("SPPG-JKT-02", "2026-07-20", 91.0, 85.0, 81.0, 84.0, 86.0, 87.0, 83.0, "Cluster Kemayoran cukup baik, namun lead time perlu dipangkas."),
                ("SPPG-JKT-03", "2026-07-19", 89.0, 82.0, 80.0, 81.0, 83.0, 84.0, 82.0, "Kinerja cukup, tetapi pengiriman utara mulai padat."),
                ("SPPG-JKT-04", "2026-07-19", 93.0, 87.0, 85.0, 86.0, 88.0, 89.0, 90.0, "Area selatan stabil dan complaint relatif rendah."),
            ]
            created_score_count = 0
            for (
                sppg_code,
                score_date_raw,
                acceptance_score,
                waste_score,
                delivery_score,
                temperature_score,
                taste_score,
                nutrition_score,
                complaint_score,
                notes,
            ) in score_seed:
                sppg_item = sppg_map[sppg_code]
                key = (sppg_item.id, score_date_raw)
                if key in existing_score_keys:
                    continue
                parts = [
                    acceptance_score,
                    waste_score,
                    delivery_score,
                    temperature_score,
                    taste_score,
                    nutrition_score,
                    complaint_score,
                ]
                total_score = round(sum(parts) / len(parts), 6)
                session.add(
                    ServiceQualityScore(
                        tenant_id=tenant.id,
                        sppg_id=sppg_item.id,
                        score_date=date.fromisoformat(score_date_raw),
                        acceptance_score=acceptance_score,
                        waste_score=waste_score,
                        delivery_score=delivery_score,
                        temperature_score=temperature_score,
                        taste_score=taste_score,
                        nutrition_score=nutrition_score,
                        complaint_score=complaint_score,
                        total_score=total_score,
                        score_status="CALCULATED",
                        notes=notes,
                    )
                )
                await session.commit()
                existing_score_keys.add(key)
                created_score_count += 1
            if created_score_count:
                print(f"Service quality score demo dibuat: {created_score_count}")
            else:
                print("Service quality score demo sudah tersedia.")

            stock_service = StockService(
                InventoryTransactionRepository(session),
                InventoryBalanceRepository(session),
                TenantRepository(session),
                SppgRepository(session),
                ProductRepository(session),
                UomRepository(session),
                WarehouseRepository(session),
                StockLocationRepository(session),
                InventoryBatchRepository(session),
            )
            transactions = await stock_service.list_transactions()
            if not transactions:
                transaction = await stock_service.create_transaction(
                    InventoryTransactionCreate(
                        tenant_id=str(tenant.id),
                        sppg_id=str(sppg.id),
                        transaction_type="RECEIPT",
                        reference_type="SEEDING",
                        reference_id=None,
                        product_id=str(ingredient.id),
                        destination_warehouse_id=str(warehouse.id),
                        quantity=500,
                        uom_id=str(uom.id),
                        unit_cost=12000,
                        transaction_at=datetime.now(timezone.utc),
                        notes="Initial stock seeding",
                    ),
                    user,
                )
                await session.commit()
                print(f"Inventory transaction dibuat: {transaction.id}")
            else:
                print(f"Inventory transaction sudah ada: {transactions[0].id}")

            accounting_service = AccountingService(
                AccountRepository(session),
                JournalEntryRepository(session),
                JournalLineRepository(session),
                TenantRepository(session),
            )
            accounts = await accounting_service.list_accounts()
            if not accounts:
                cash_account = await accounting_service.create_account(
                    AccountCreate(
                        tenant_id=str(tenant.id),
                        code="110000",
                        name="Kas dan Bank",
                        category="ASSET",
                        normal_balance="DEBIT",
                    )
                )
                expense_account = await accounting_service.create_account(
                    AccountCreate(
                        tenant_id=str(tenant.id),
                        code="510000",
                        name="Biaya Bahan",
                        category="COST_OF_SERVICE",
                        normal_balance="DEBIT",
                    )
                )
                inventory_account = await accounting_service.create_account(
                    AccountCreate(
                        tenant_id=str(tenant.id),
                        code="130000",
                        name="Persediaan Bahan",
                        category="ASSET",
                        normal_balance="DEBIT",
                    )
                )
                grni_account = await accounting_service.create_account(
                    AccountCreate(
                        tenant_id=str(tenant.id),
                        code="240000",
                        name="Barang Diterima Belum Ditagih",
                        category="LIABILITY",
                        normal_balance="CREDIT",
                    )
                )
                await session.commit()
                print(f"Accounts dibuat: {cash_account.id}, {expense_account.id}, {inventory_account.id}, {grni_account.id}")
            else:
                cash_account = accounts[0]
                expense_account = accounts[min(1, len(accounts) - 1)]
                print(f"Accounts sudah ada: {cash_account.id}")

            account_repository = AccountRepository(session)
            account_map = {account.code: account for account in await account_repository.list_all(tenant.id)}
            supplemental_account_seed = [
                ("120500", "Piutang Klaim Pemerintah", "ASSET", "DEBIT"),
                ("230500", "Utang Pendanaan Investor", "LIABILITY", "CREDIT"),
                ("410000", "Pendapatan Klaim Pemerintah", "INCOME", "CREDIT"),
                ("520000", "Biaya Distribusi", "COST_OF_SERVICE", "DEBIT"),
                ("530000", "Biaya Operasional Dapur", "EXPENSE", "DEBIT"),
            ]
            created_account_codes: list[str] = []
            for code, name, category, normal_balance in supplemental_account_seed:
                if code in account_map:
                    continue
                created_account = await accounting_service.create_account(
                    AccountCreate(
                        tenant_id=str(tenant.id),
                        code=code,
                        name=name,
                        category=category,
                        normal_balance=normal_balance,
                    )
                )
                await session.commit()
                account_map[created_account.code] = created_account
                created_account_codes.append(created_account.code)
            if created_account_codes:
                print(f"Accounts tambahan dibuat: {', '.join(created_account_codes)}")
            else:
                print("Accounts tambahan sudah tersedia.")

            budget_service = BudgetService(
                BudgetRepository(session),
                BudgetLineRepository(session),
                TenantRepository(session),
                AccountRepository(session),
            )
            budgets = await budget_service.list_budgets()
            if not budgets:
                budget_bundle = await budget_service.create_budget(
                    BudgetCreate(
                        tenant_id=str(tenant.id),
                        name="Budget Operasional Juli 2026",
                        date_start=date(2026, 7, 1),
                        date_end=date(2026, 7, 31),
                        notes="Budget demo operasional",
                        lines=[
                            BudgetLineCreate(
                                category_name="BAHAN_BAKU",
                                account_id=str(expense_account.id),
                                planned_amount=50000000,
                                control_mode="WARNING",
                            )
                        ],
                    )
                )
                await session.commit()
                print(f"Budget dibuat: {budget_bundle['budget'].id}")
            else:
                print(f"Budget sudah ada: {budgets[0].id}")

            existing_claim_numbers = {
                item.claim_number
                for item in (
                    await session.execute(select(GovernmentClaim).where(GovernmentClaim.tenant_id == tenant.id))
                ).scalars().all()
            }
            existing_claim_payment_refs = {
                item.payment_reference
                for item in (
                    await session.execute(select(ClaimPayment).where(ClaimPayment.tenant_id == tenant.id))
                ).scalars().all()
                if item.payment_reference
            }
            existing_source_codes = {
                item.code
                for item in (
                    await session.execute(select(FundingSource).where(FundingSource.tenant_id == tenant.id))
                ).scalars().all()
            }
            existing_agreement_notes = {
                item.notes
                for item in (
                    await session.execute(select(FundingAgreement).where(FundingAgreement.tenant_id == tenant.id))
                ).scalars().all()
                if item.notes
            }
            existing_disbursement_refs = {
                item.reference_number
                for item in (
                    await session.execute(select(FundingDisbursement).where(FundingDisbursement.tenant_id == tenant.id))
                ).scalars().all()
                if item.reference_number
            }
            existing_repayment_refs = {
                item.payment_reference
                for item in (
                    await session.execute(select(FundingRepayment).where(FundingRepayment.tenant_id == tenant.id))
                ).scalars().all()
                if item.payment_reference
            }
            existing_journal_numbers = {
                item.entry_number
                for item in (
                    await session.execute(select(JournalEntry).where(JournalEntry.tenant_id == tenant.id))
                ).scalars().all()
            }
            existing_verification_keys = {
                (item.claim_id, str(item.verification_date), item.verifier_name)
                for item in (
                    await session.execute(select(ClaimVerification).where(ClaimVerification.tenant_id == tenant.id))
                ).scalars().all()
            }

            async def build_posted_journal_entry(
                *,
                entry_number: str,
                entry_date: date,
                reference: str,
                description: str,
                source_module: str,
                source_document_type: str,
                debit_account_code: str,
                credit_account_code: str,
                amount: float,
                ) -> JournalEntry:
                journal_entry = JournalEntry(
                    tenant_id=tenant.id,
                    entry_number=entry_number,
                    entry_date=entry_date,
                    reference=reference,
                    description=description,
                    source_module=source_module,
                    source_document_type=source_document_type,
                    source_document_id=None,
                    status="POSTED",
                    posted_at=datetime(entry_date.year, entry_date.month, entry_date.day, 12, 0, tzinfo=timezone.utc),
                    posted_by=user.id,
                )
                session.add(journal_entry)
                await session.flush()
                debit_account = account_map[debit_account_code]
                credit_account = account_map[credit_account_code]
                session.add(
                    JournalLine(
                        tenant_id=tenant.id,
                        journal_entry_id=journal_entry.id,
                        account_id=debit_account.id,
                        line_type="DEBIT",
                        amount=amount,
                        description=description,
                    )
                )
                session.add(
                    JournalLine(
                        tenant_id=tenant.id,
                        journal_entry_id=journal_entry.id,
                        account_id=credit_account.id,
                        line_type="CREDIT",
                        amount=amount,
                        description=description,
                    )
                )
                return journal_entry

            finance_cash_journal_seed = [
                ("JE-DEMO-OPS-001", date(2026, 7, 18), "OPS-DEL-001", "Biaya distribusi cluster Menteng", "delivery", "delivery_expense", "520000", "110000", 3500000.0),
                ("JE-DEMO-OPS-002", date(2026, 7, 19), "OPS-KIT-001", "Biaya operasional dapur harian", "operations", "kitchen_expense", "530000", "110000", 2250000.0),
                ("JE-DEMO-OPS-003", date(2026, 7, 20), "OPS-MAT-001", "Pembayaran bahan baku aktual", "procurement", "supplier_payment", "510000", "110000", 4800000.0),
            ]
            created_cash_journal_count = 0
            for (
                entry_number,
                entry_date,
                reference,
                description,
                source_module,
                source_document_type,
                debit_account_code,
                credit_account_code,
                amount,
            ) in finance_cash_journal_seed:
                if entry_number in existing_journal_numbers:
                    continue
                await build_posted_journal_entry(
                    entry_number=entry_number,
                    entry_date=entry_date,
                    reference=reference,
                    description=description,
                    source_module=source_module,
                    source_document_type=source_document_type,
                    debit_account_code=debit_account_code,
                    credit_account_code=credit_account_code,
                    amount=amount,
                )
                await session.commit()
                existing_journal_numbers.add(entry_number)
                created_cash_journal_count += 1
            if created_cash_journal_count:
                print(f"Journal cash flow demo dibuat: {created_cash_journal_count}")
            else:
                print("Journal cash flow demo sudah tersedia.")

            actualized = await budget_service.actualize_budget_by_account(
                tenant_id=tenant.id,
                account_id=account_map["510000"].id,
                amount=4800000.0,
                actual_date=date(2026, 7, 20),
            )
            if actualized:
                await session.commit()
                print(f"Budget actualization demo diperbarui untuk {len(actualized)} line.")

            funding_source_seed = [
                {
                    "code": "INVESTOR-ALPHA",
                    "source_type": "INVESTOR_WORKING_CAPITAL",
                    "name": "Investor Alpha Working Capital",
                    "party_name": "PT Alpha Kapital",
                    "contract_number": "INV-ALPHA-2026-01",
                    "start_date": date(2026, 5, 1),
                    "end_date": date(2027, 4, 30),
                    "status": "ACTIVE",
                    "notes": "Sumber pendanaan investor utama untuk modal kerja dapur.",
                }
            ]
            bridge_demo_sources = list(
                (
                    await session.execute(
                        select(FundingSource).where(
                            FundingSource.tenant_id == tenant.id,
                            FundingSource.name == "Investor Bridge Fund Demo",
                        )
                    )
                ).scalars().all()
            )
            if bridge_demo_sources:
                bridge_source_ids = [item.id for item in bridge_demo_sources]
                bridge_agreements = list(
                    (
                        await session.execute(
                            select(FundingAgreement).where(FundingAgreement.funding_source_id.in_(bridge_source_ids))
                        )
                    ).scalars().all()
                )
                bridge_agreement_ids = [item.id for item in bridge_agreements]
                bridge_disbursements = list(
                    (
                        await session.execute(
                            select(FundingDisbursement).where(FundingDisbursement.agreement_id.in_(bridge_agreement_ids))
                        )
                    ).scalars().all()
                ) if bridge_agreement_ids else []
                bridge_repayments = list(
                    (
                        await session.execute(
                            select(FundingRepayment).where(FundingRepayment.agreement_id.in_(bridge_agreement_ids))
                        )
                    ).scalars().all()
                ) if bridge_agreement_ids else []
                cleanup_journal_entry_ids = {
                    item.journal_entry_id for item in bridge_disbursements + bridge_repayments if item.journal_entry_id is not None
                }
                if bridge_agreement_ids:
                    await session.execute(delete(FundingRepayment).where(FundingRepayment.agreement_id.in_(bridge_agreement_ids)))
                    await session.execute(delete(FundingDisbursement).where(FundingDisbursement.agreement_id.in_(bridge_agreement_ids)))
                    await session.flush()
                if cleanup_journal_entry_ids:
                    await session.execute(delete(JournalLine).where(JournalLine.journal_entry_id.in_(cleanup_journal_entry_ids)))
                    await session.execute(delete(JournalEntry).where(JournalEntry.id.in_(cleanup_journal_entry_ids)))
                    await session.flush()
                if bridge_agreement_ids:
                    await session.execute(delete(FundingAgreement).where(FundingAgreement.id.in_(bridge_agreement_ids)))
                await session.execute(delete(FundingSource).where(FundingSource.id.in_(bridge_source_ids)))
                await session.commit()
                print(
                    "Funding demo lama dibersihkan: "
                    f"{len(bridge_demo_sources)} source, "
                    f"{len(bridge_agreements)} agreement, "
                    f"{len(bridge_disbursements)} disbursement, "
                    f"{len(bridge_repayments)} repayment."
                )
            funding_source_map: dict[str, FundingSource] = {
                item.code: item
                for item in (
                    await session.execute(select(FundingSource).where(FundingSource.tenant_id == tenant.id))
                ).scalars().all()
            }
            created_funding_source_count = 0
            updated_funding_source_count = 0
            for funding_source_payload in funding_source_seed:
                funding_source = funding_source_map.get(funding_source_payload["code"])
                if funding_source is None:
                    funding_source = FundingSource(tenant_id=tenant.id, **funding_source_payload)
                    session.add(funding_source)
                    created_funding_source_count += 1
                else:
                    for field_name, field_value in funding_source_payload.items():
                        setattr(funding_source, field_name, field_value)
                    updated_funding_source_count += 1
                await session.commit()
                funding_source_map[funding_source.code] = funding_source
            if created_funding_source_count:
                print(f"Funding source demo dibuat: {created_funding_source_count}")
            elif updated_funding_source_count == 0:
                print("Funding source demo sudah tersedia.")
            if updated_funding_source_count:
                print(f"Funding source demo diperbarui: {updated_funding_source_count}")

            funding_agreement_seed = [
                {
                    "source_code": "INVESTOR-ALPHA",
                    "agreement_type": "MURABAHA_WORKING_CAPITAL",
                    "principal_amount": 120000000.0,
                    "margin_method": "PERCENTAGE",
                    "margin_rate": 12.0,
                    "fixed_margin_amount": None,
                    "disbursement_schedule": {"frequency": "MONTHLY", "months": ["2026-06", "2026-07"]},
                    "repayment_terms": {"method": "MONTHLY_INSTALLMENT", "tenor_months": 6},
                    "status": "ACTIVE",
                    "notes": "AGREEMENT-DEMO-ALPHA-2026",
                }
            ]
            funding_agreement_map: dict[str, FundingAgreement] = {
                item.notes: item
                for item in (
                    await session.execute(select(FundingAgreement).where(FundingAgreement.tenant_id == tenant.id))
                ).scalars().all()
                if item.notes
            }
            created_agreement_count = 0
            updated_agreement_count = 0
            for agreement_payload in funding_agreement_seed:
                agreement_key = agreement_payload["notes"]
                funding_source = funding_source_map[agreement_payload["source_code"]]
                agreement = funding_agreement_map.get(agreement_key)
                if agreement is None:
                    agreement = FundingAgreement(
                        tenant_id=tenant.id,
                        funding_source_id=funding_source.id,
                        agreement_type=agreement_payload["agreement_type"],
                        principal_amount=agreement_payload["principal_amount"],
                        margin_method=agreement_payload["margin_method"],
                        margin_rate=agreement_payload["margin_rate"],
                        fixed_margin_amount=agreement_payload["fixed_margin_amount"],
                        disbursement_schedule=agreement_payload["disbursement_schedule"],
                        repayment_terms=agreement_payload["repayment_terms"],
                        status=agreement_payload["status"],
                        notes=agreement_key,
                    )
                    session.add(agreement)
                    created_agreement_count += 1
                else:
                    agreement.funding_source_id = funding_source.id
                    agreement.agreement_type = agreement_payload["agreement_type"]
                    agreement.principal_amount = agreement_payload["principal_amount"]
                    agreement.margin_method = agreement_payload["margin_method"]
                    agreement.margin_rate = agreement_payload["margin_rate"]
                    agreement.fixed_margin_amount = agreement_payload["fixed_margin_amount"]
                    agreement.disbursement_schedule = agreement_payload["disbursement_schedule"]
                    agreement.repayment_terms = agreement_payload["repayment_terms"]
                    agreement.status = agreement_payload["status"]
                    agreement.notes = agreement_key
                    updated_agreement_count += 1
                await session.commit()
                funding_agreement_map[agreement_key] = agreement
            if created_agreement_count:
                print(f"Funding agreement demo dibuat: {created_agreement_count}")
            elif updated_agreement_count == 0:
                print("Funding agreement demo sudah tersedia.")
            if updated_agreement_count:
                print(f"Funding agreement demo diperbarui: {updated_agreement_count}")

            agreement = funding_agreement_map["AGREEMENT-DEMO-ALPHA-2026"]
            funding_disbursement_seed = [
                ("FDB-DEMO-001", "JE-DEMO-FUND-DISB-001", date(2026, 6, 10), "SPPG-JKT-01", 30000000.0, "Pencairan modal kerja Menteng"),
                ("FDB-DEMO-002", "JE-DEMO-FUND-DISB-002", date(2026, 6, 15), "SPPG-JKT-02", 22000000.0, "Pencairan modal kerja Kemayoran"),
                ("FDB-DEMO-003", "JE-DEMO-FUND-DISB-003", date(2026, 6, 18), "SPPG-JKT-03", 26000000.0, "Pencairan modal kerja Sunter"),
                ("FDB-DEMO-004", "JE-DEMO-FUND-DISB-004", date(2026, 6, 20), "SPPG-JKT-04", 18000000.0, "Pencairan modal kerja Tebet"),
            ]
            created_disbursement_count = 0
            for reference_number, entry_number, disbursement_date, sppg_code, amount, notes in funding_disbursement_seed:
                if reference_number in existing_disbursement_refs:
                    continue
                if entry_number not in existing_journal_numbers:
                    await build_posted_journal_entry(
                        entry_number=entry_number,
                        entry_date=disbursement_date,
                        reference=reference_number,
                        description=f"Disbursement investor {sppg_code}",
                        source_module="funding",
                        source_document_type="funding_disbursement",
                        debit_account_code="110000",
                        credit_account_code="230500",
                        amount=amount,
                    )
                    await session.flush()
                journal_entry = (
                    await session.execute(select(JournalEntry).where(JournalEntry.tenant_id == tenant.id, JournalEntry.entry_number == entry_number))
                ).scalar_one()
                session.add(
                    FundingDisbursement(
                        tenant_id=tenant.id,
                        agreement_id=agreement.id,
                        sppg_id=sppg_map[sppg_code].id,
                        journal_entry_id=journal_entry.id,
                        disbursement_date=disbursement_date,
                        amount=amount,
                        bank_account_id=account_map["110000"].id,
                        reference_number=reference_number,
                        status="POSTED",
                        notes=notes,
                    )
                )
                await session.commit()
                existing_disbursement_refs.add(reference_number)
                existing_journal_numbers.add(entry_number)
                created_disbursement_count += 1
            if created_disbursement_count:
                print(f"Funding disbursement demo dibuat: {created_disbursement_count}")
            else:
                print("Funding disbursement demo sudah tersedia.")

            funding_repayment_seed = [
                ("FRP-DEMO-001", "JE-DEMO-FUND-REPAY-001", date(2026, 7, 18), 12000000.0, 1200000.0, 0.0, "Angsuran investor periode Juli batch 1"),
                ("FRP-DEMO-002", "JE-DEMO-FUND-REPAY-002", date(2026, 7, 20), 8000000.0, 900000.0, 100000.0, "Angsuran investor periode Juli batch 2"),
            ]
            created_repayment_count = 0
            for payment_reference, entry_number, repayment_date, principal_amount, margin_amount, penalty_amount, notes in funding_repayment_seed:
                if payment_reference in existing_repayment_refs:
                    continue
                total_cash_out = principal_amount + margin_amount + penalty_amount
                if entry_number not in existing_journal_numbers:
                    await build_posted_journal_entry(
                        entry_number=entry_number,
                        entry_date=repayment_date,
                        reference=payment_reference,
                        description="Pembayaran angsuran investor",
                        source_module="funding",
                        source_document_type="funding_repayment",
                        debit_account_code="230500",
                        credit_account_code="110000",
                        amount=total_cash_out,
                    )
                    await session.flush()
                journal_entry = (
                    await session.execute(select(JournalEntry).where(JournalEntry.tenant_id == tenant.id, JournalEntry.entry_number == entry_number))
                ).scalar_one()
                session.add(
                    FundingRepayment(
                        tenant_id=tenant.id,
                        agreement_id=agreement.id,
                        journal_entry_id=journal_entry.id,
                        repayment_date=repayment_date,
                        principal_amount=principal_amount,
                        margin_amount=margin_amount,
                        penalty_amount=penalty_amount,
                        payment_reference=payment_reference,
                        status="POSTED",
                        notes=notes,
                    )
                )
                await session.commit()
                existing_repayment_refs.add(payment_reference)
                existing_journal_numbers.add(entry_number)
                created_repayment_count += 1
            if created_repayment_count:
                print(f"Funding repayment demo dibuat: {created_repayment_count}")
            else:
                print("Funding repayment demo sudah tersedia.")

            government_claim_seed = [
                ("CLM-DEMO-JKT01-202605", "SPPG-JKT-01", date(2026, 5, 1), date(2026, 5, 31), "VERIFIED", 318, 4770000.0, 4700000.0, 0.0, date(2026, 6, 1), date(2026, 6, 5), None, "Claim lama masih outstanding sebagian penuh."),
                ("CLM-DEMO-JKT02-202606", "SPPG-JKT-02", date(2026, 6, 1), date(2026, 6, 30), "VERIFIED", 286, 4290000.0, 4250000.0, 2000000.0, date(2026, 6, 30), date(2026, 7, 2), date(2026, 7, 12), "Claim Juni dibayar sebagian."),
                ("CLM-DEMO-JKT01-202607", "SPPG-JKT-01", date(2026, 7, 1), date(2026, 7, 20), "VERIFIED", 318, 4770000.0, 4740000.0, 1500000.0, date(2026, 7, 18), date(2026, 7, 19), date(2026, 7, 20), "Claim Juli Menteng sudah terverifikasi dan dibayar sebagian."),
                ("CLM-DEMO-JKT02-202607", "SPPG-JKT-02", date(2026, 7, 1), date(2026, 7, 20), "VERIFIED", 286, 4290000.0, 4260000.0, 0.0, date(2026, 7, 18), date(2026, 7, 19), None, "Claim Juli Kemayoran sudah terverifikasi dan menunggu pembayaran."),
                ("CLM-DEMO-JKT03-202607", "SPPG-JKT-03", date(2026, 7, 1), date(2026, 7, 20), "SUBMITTED", 352, 5280000.0, None, 0.0, date(2026, 7, 19), None, None, "Claim Juli menunggu verifikasi."),
                ("CLM-DEMO-JKT04-202607", "SPPG-JKT-04", date(2026, 7, 1), date(2026, 7, 20), "PAID", 336, 5040000.0, 5000000.0, 5000000.0, date(2026, 7, 18), date(2026, 7, 19), date(2026, 7, 20), "Claim Juli sudah cair penuh."),
            ]
            created_claim_count = 0
            updated_claim_count = 0
            claim_map: dict[str, GovernmentClaim] = {
                item.claim_number: item
                for item in (
                    await session.execute(select(GovernmentClaim).where(GovernmentClaim.tenant_id == tenant.id))
                ).scalars().all()
            }
            existing_claim_line_claim_ids = {
                item.claim_id
                for item in (
                    await session.execute(select(GovernmentClaimLine).where(GovernmentClaimLine.tenant_id == tenant.id))
                ).scalars().all()
            }
            production_by_sppg_code = {}
            for code, sppg_item in sppg_map.items():
                scoped_orders = [item for item in existing_production_orders.values() if item.sppg_id == sppg_item.id]
                if not scoped_orders:
                    continue
                scoped_orders.sort(
                    key=lambda item: (
                        0 if item.production_date <= date(2026, 7, 20) else 1,
                        abs((item.production_date - date(2026, 7, 20)).days),
                        item.production_number,
                    )
                )
                production_by_sppg_code[code] = scoped_orders[0]
            delivery_by_sppg_code = {}
            for code, sppg_item in sppg_map.items():
                scoped_deliveries = [item for item in existing_delivery_orders.values() if item.sppg_id == sppg_item.id]
                if not scoped_deliveries:
                    continue
                scoped_deliveries.sort(
                    key=lambda item: (
                        0 if item.planned_departure.date() <= date(2026, 7, 20) else 1,
                        abs((item.planned_departure.date() - date(2026, 7, 20)).days),
                        item.delivery_number,
                    )
                )
                delivery_by_sppg_code[code] = scoped_deliveries[0]
            for (
                claim_number,
                sppg_code,
                period_start,
                period_end,
                status,
                total_portions,
                claimed_amount,
                approved_amount,
                paid_amount,
                submitted_at,
                verified_at,
                paid_at,
                notes,
            ) in government_claim_seed:
                claim = claim_map.get(claim_number)
                if claim is None:
                    claim = GovernmentClaim(
                        tenant_id=tenant.id,
                        sppg_id=sppg_map[sppg_code].id,
                        program_id=None,
                        claim_number=claim_number,
                        period_start=period_start,
                        period_end=period_end,
                        claim_type="ACTUAL_COST",
                        status=status,
                        total_portions=total_portions,
                        claimed_amount=claimed_amount,
                        approved_amount=approved_amount,
                        paid_amount=paid_amount,
                        notes=notes,
                        submitted_at=submitted_at,
                        verified_at=verified_at,
                        paid_at=paid_at,
                        is_active=True,
                    )
                    session.add(claim)
                    created_claim_count += 1
                else:
                    claim.sppg_id = sppg_map[sppg_code].id
                    claim.period_start = period_start
                    claim.period_end = period_end
                    claim.status = status
                    claim.total_portions = total_portions
                    claim.claimed_amount = claimed_amount
                    claim.approved_amount = approved_amount
                    claim.paid_amount = paid_amount
                    claim.notes = notes
                    claim.submitted_at = submitted_at
                    claim.verified_at = verified_at
                    claim.paid_at = paid_at
                    claim.is_active = True
                    updated_claim_count += 1
                await session.flush()
                linked_delivery = delivery_by_sppg_code.get(sppg_code)
                linked_production = production_by_sppg_code.get(sppg_code)
                if claim.id not in existing_claim_line_claim_ids:
                    session.add(
                        GovernmentClaimLine(
                            tenant_id=tenant.id,
                            claim_id=claim.id,
                            delivery_order_id=linked_delivery.id if linked_delivery else None,
                            production_order_id=linked_production.id if linked_production else None,
                            line_type="DELIVERY_ACTUAL_COST",
                            description=f"Biaya aktual distribusi {sppg_code}",
                            portions=total_portions,
                            unit_cost=round(claimed_amount / total_portions, 6) if total_portions > 0 else 0.0,
                            line_amount=claimed_amount,
                        )
                    )
                    existing_claim_line_claim_ids.add(claim.id)
                if approved_amount is not None and verified_at is not None:
                    verification_key = (claim.id, str(verified_at), "Verifier Demo")
                    if verification_key not in existing_verification_keys:
                        session.add(
                            ClaimVerification(
                                tenant_id=tenant.id,
                                claim_id=claim.id,
                                verification_date=verified_at,
                                verification_status="APPROVED",
                                verified_amount=approved_amount,
                                verifier_name="Verifier Demo",
                                notes=f"Verifikasi demo untuk {claim_number}",
                            )
                        )
                        existing_verification_keys.add(verification_key)
                await session.commit()
                claim_map[claim.claim_number] = claim
            if created_claim_count:
                print(f"Government claim demo dibuat: {created_claim_count}")
            elif updated_claim_count == 0:
                print("Government claim demo sudah tersedia.")
            if updated_claim_count:
                print(f"Government claim demo diperbarui: {updated_claim_count}")

            claim_payment_seed = [
                ("CLM-DEMO-JKT02-202606", "PAY-CLM-DEMO-001", "JE-DEMO-CLAIM-PAY-001", date(2026, 7, 12), 2000000.0),
                ("CLM-DEMO-JKT01-202607", "PAY-CLM-DEMO-003", "JE-DEMO-CLAIM-PAY-003", date(2026, 7, 20), 1500000.0),
                ("CLM-DEMO-JKT04-202607", "PAY-CLM-DEMO-002", "JE-DEMO-CLAIM-PAY-002", date(2026, 7, 20), 5000000.0),
            ]
            created_claim_payment_count = 0
            for claim_number, payment_reference, entry_number, payment_date, amount in claim_payment_seed:
                if payment_reference in existing_claim_payment_refs:
                    continue
                claim = claim_map.get(claim_number)
                if claim is None:
                    continue
                if entry_number not in existing_journal_numbers:
                    await build_posted_journal_entry(
                        entry_number=entry_number,
                        entry_date=payment_date,
                        reference=payment_reference,
                        description=f"Penerimaan pembayaran claim {claim_number}",
                        source_module="government_claim",
                        source_document_type="claim_payment",
                        debit_account_code="110000",
                        credit_account_code="120500",
                        amount=amount,
                    )
                    await session.flush()
                journal_entry = (
                    await session.execute(select(JournalEntry).where(JournalEntry.tenant_id == tenant.id, JournalEntry.entry_number == entry_number))
                ).scalar_one()
                session.add(
                    ClaimPayment(
                        tenant_id=tenant.id,
                        claim_id=claim.id,
                        journal_entry_id=journal_entry.id,
                        payment_date=payment_date,
                        payment_reference=payment_reference,
                        amount=amount,
                        notes=f"Pembayaran demo untuk {claim_number}",
                    )
                )
                await session.commit()
                existing_claim_payment_refs.add(payment_reference)
                existing_journal_numbers.add(entry_number)
                created_claim_payment_count += 1
            if created_claim_payment_count:
                print(f"Claim payment demo dibuat: {created_claim_payment_count}")
            else:
                print("Claim payment demo sudah tersedia.")

            print(
                "Ringkasan seed demo: "
                f"{len(sppg_map)} SPPG, "
                f"{len(school_map)} sekolah, "
                f"{len(existing_beneficiaries)} beneficiary, "
                f"{len(await service_area_repository.list_all(tenant.id))} service area, "
                f"{len(await delivery_order_repository.list_all(tenant.id))} delivery order, "
                f"{len(await delivery_route_repository.list_all(tenant.id))} route, "
                f"{len((await session.execute(select(FeedbackSubmission).where(FeedbackSubmission.tenant_id == tenant.id))).scalars().all())} feedback submission, "
                f"{len((await session.execute(select(GovernmentClaim).where(GovernmentClaim.tenant_id == tenant.id))).scalars().all())} government claim, "
                f"{len((await session.execute(select(FundingDisbursement).where(FundingDisbursement.tenant_id == tenant.id))).scalars().all())} funding disbursement."
            )
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
