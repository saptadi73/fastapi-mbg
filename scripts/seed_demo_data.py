import asyncio
from datetime import date
from datetime import datetime
from datetime import timezone

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config.settings import get_settings
from app.core.security.password import hash_password
from app.modules.identity.models.user import User
from app.modules.identity.repositories.user_repository import UserRepository
from app.modules.inventory.repositories.inventory_balance_repository import InventoryBalanceRepository
from app.modules.inventory.repositories.inventory_transaction_repository import InventoryTransactionRepository
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
from app.modules.product.repositories.product_repository import ProductRepository
from app.modules.product.schemas.product_schema import ProductCreate
from app.modules.product.services.product_service import ProductService
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
            schools = await school_service.list_schools()
            if not schools:
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
                print(f"Sekolah dibuat: {school.id}")
            else:
                school = schools[0]
                print(f"Sekolah sudah ada: {school.id}")

            sppg_service = SppgService(SppgRepository(session), TenantRepository(session))
            sppg_list = await sppg_service.list_sppg()
            if not sppg_list:
                sppg = await sppg_service.create_sppg(
                    SppgCreate(
                        tenant_id=str(tenant.id),
                        code="SPPG-JKT-01",
                        name="SPPG Jakarta Pusat 01",
                        city="Jakarta Pusat",
                        latitude=-6.1754,
                        longitude=106.8272,
                    )
                )
                await session.commit()
                print(f"SPPG dibuat: {sppg.id}")
            else:
                sppg = sppg_list[0]
                print(f"SPPG sudah ada: {sppg.id}")

            warehouse_service = WarehouseService(
                WarehouseRepository(session),
                TenantRepository(session),
                SppgRepository(session),
            )
            warehouses = await warehouse_service.list_warehouses()
            if not warehouses:
                warehouse = await warehouse_service.create_warehouse(
                    WarehouseCreate(
                        tenant_id=str(tenant.id),
                        sppg_id=str(sppg.id),
                        code="WH-JKT-01",
                        name="Gudang Utama Jakarta Pusat",
                        warehouse_type="MAIN",
                        location="Area SPPG Jakarta Pusat 01",
                        is_active=True,
                    )
                )
                await session.commit()
                print(f"Warehouse dibuat: {warehouse.id}")
            else:
                warehouse = warehouses[0]
                print(f"Warehouse sudah ada: {warehouse.id}")

            beneficiary_service = BeneficiaryService(
                BeneficiaryRepository(session),
                TenantRepository(session),
                SchoolRepository(session),
            )
            beneficiaries = await beneficiary_service.list_beneficiaries()
            if not beneficiaries:
                beneficiary = await beneficiary_service.create_beneficiary(
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
                print(f"Beneficiary dibuat: {beneficiary.id}")
            else:
                print(f"Beneficiary sudah ada: {beneficiaries[0].id}")

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

            stock_service = StockService(
                InventoryTransactionRepository(session),
                InventoryBalanceRepository(session),
                TenantRepository(session),
                SppgRepository(session),
                ProductRepository(session),
                UomRepository(session),
                WarehouseRepository(session),
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
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
