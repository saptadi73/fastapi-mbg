import asyncio
from datetime import date

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config.settings import get_settings
from app.core.security.password import hash_password
from app.modules.beneficiary.repositories.beneficiary_repository import BeneficiaryRepository
from app.modules.beneficiary.schemas.beneficiary_schema import BeneficiaryCreate
from app.modules.beneficiary.services.beneficiary_service import BeneficiaryService
from app.modules.geography.repositories.school_repository import SchoolRepository
from app.modules.geography.schemas.school_schema import SchoolCreate
from app.modules.geography.services.school_service import SchoolService
from app.modules.identity.models.user import User
from app.modules.identity.repositories.user_repository import UserRepository
from app.modules.meal_plan.repositories.meal_plan_repository import MealPlanRepository
from app.modules.meal_plan.schemas.meal_plan_schema import MealPlanCreate
from app.modules.meal_plan.services.meal_plan_service import MealPlanService
from app.modules.product.repositories.product_repository import ProductRepository
from app.modules.product.schemas.product_schema import ProductCreate
from app.modules.product.services.product_service import ProductService
from app.modules.recipe.repositories.recipe_line_repository import RecipeLineRepository
from app.modules.recipe.repositories.recipe_repository import RecipeRepository
from app.modules.recipe.schemas.recipe_schema import RecipeCreate, RecipeLineCreate
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


async def _seed_test_data() -> None:
    settings = get_settings()
    engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)
    try:
        async with session_factory() as session:
            tenant_service = TenantService(TenantRepository(session))
            tenants = await tenant_service.list_tenants()
            if tenants:
                tenant = tenants[0]
            else:
                tenant = await tenant_service.create_tenant(
                    TenantCreate(code="MBG-DEMO", name="Tenant Demo MBG")
                )
                await session.commit()

            user_repository = UserRepository(session)
            if await user_repository.get_by_email("operator@example.com") is None:
                await user_repository.add(
                    User(
                        tenant_id=tenant.id,
                        active_sppg_id=None,
                        full_name="Demo Operator MBG",
                        email="operator@example.com",
                        password_hash=hash_password("mbg12345"),
                        role_names=["super_admin"],
                        is_active=True,
                    )
                )
                await session.commit()

            if await user_repository.get_by_email("viewer@example.com") is None:
                await user_repository.add(
                    User(
                        tenant_id=tenant.id,
                        active_sppg_id=None,
                        full_name="Demo Viewer MBG",
                        email="viewer@example.com",
                        password_hash=hash_password("viewer123"),
                        role_names=["viewer"],
                        is_active=True,
                    )
                )
                await session.commit()

            uom_service = UomService(UomRepository(session), TenantRepository(session))
            uoms = await uom_service.list_uoms()
            if uoms:
                uom = uoms[0]
            else:
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

            product_service = ProductService(
                ProductRepository(session),
                TenantRepository(session),
                UomRepository(session),
            )
            products = await product_service.list_products()
            if products:
                product = products[0]
            else:
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

            recipe_service = RecipeService(
                RecipeRepository(session),
                RecipeLineRepository(session),
                TenantRepository(session),
                ProductRepository(session),
                UomRepository(session),
            )
            recipes = await recipe_service.list_recipes()
            if recipes:
                recipe = recipes[0]
            else:
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

            if not await recipe_service.list_recipe_lines(recipe.id):
                await recipe_service.create_recipe_line(
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

            school_service = SchoolService(SchoolRepository(session), TenantRepository(session))
            schools = await school_service.list_schools()
            if schools:
                school = schools[0]
            else:
                school = await school_service.create_school(
                    SchoolCreate(
                        tenant_id=str(tenant.id),
                        code="SCH-JKT-01",
                        name="SDN Jakarta Pusat 01",
                        school_level="SD",
                        address="Jl. Merdeka No. 1, Jakarta Pusat",
                        latitude=-6.1702,
                        longitude=106.8283,
                        student_count=320,
                    )
                )
                await session.commit()

            sppg_service = SppgService(SppgRepository(session), TenantRepository(session))
            sppg_items = await sppg_service.list_sppg()
            if sppg_items:
                sppg = sppg_items[0]
            else:
                sppg = await sppg_service.create_sppg(
                    SppgCreate(
                        tenant_id=str(tenant.id),
                        code="SPPG-JKT-01",
                        name="SPPG Jakarta Pusat 01",
                        address="Jl. Cikini Raya No. 10, Jakarta Pusat",
                        province="DKI Jakarta",
                        city="Jakarta Pusat",
                        district="Menteng",
                        village="Cikini",
                        latitude=-6.1754,
                        longitude=106.8272,
                        service_radius_meter=5000,
                        timezone="Asia/Jakarta",
                    )
                )
                await session.commit()

            operator_user = await user_repository.get_by_email("operator@example.com")
            viewer_user = await user_repository.get_by_email("viewer@example.com")
            if operator_user is not None and operator_user.active_sppg_id != sppg.id:
                operator_user.active_sppg_id = sppg.id
            if viewer_user is not None and viewer_user.active_sppg_id != sppg.id:
                viewer_user.active_sppg_id = sppg.id
            if operator_user is not None:
                await user_repository.add_sppg_access(operator_user.id, tenant.id, sppg.id)
            if viewer_user is not None:
                await user_repository.add_sppg_access(viewer_user.id, tenant.id, sppg.id)
            await session.commit()

            beneficiary_service = BeneficiaryService(
                BeneficiaryRepository(session),
                TenantRepository(session),
                SchoolRepository(session),
            )
            if not await beneficiary_service.list_beneficiaries():
                await beneficiary_service.create_beneficiary(
                    BeneficiaryCreate(
                        tenant_id=str(tenant.id),
                        school_id=str(school.id),
                        external_reference="BEN-SCH-JKT-0001",
                        category="student",
                        age_group="7-12",
                        gender="female",
                        dietary_restriction=None,
                        allergy_notes=None,
                        is_active=True,
                    )
                )
                await session.commit()

            meal_plan_service = MealPlanService(
                MealPlanRepository(session),
                TenantRepository(session),
                SppgRepository(session),
                RecipeRepository(session),
                RecipeLineRepository(session),
                ProductRepository(session),
            )
            if not await meal_plan_service.list_meal_plans():
                await meal_plan_service.create_meal_plan(
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
    finally:
        await engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def seed_test_data() -> None:
    asyncio.run(_seed_test_data())
