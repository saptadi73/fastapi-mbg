from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.asset.models.asset import Asset
from app.modules.asset.models.asset_assignment import AssetAssignment
from app.modules.asset.models.asset_category import AssetCategory
from app.modules.asset.models.asset_depreciation import AssetDepreciation


class AssetRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_categories(self, tenant_id: UUID | None = None) -> list[AssetCategory]:
        query = select(AssetCategory).order_by(AssetCategory.name)
        if tenant_id is not None:
            query = query.where(AssetCategory.tenant_id == tenant_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_category_by_id(self, category_id: UUID) -> AssetCategory | None:
        return await self.session.get(AssetCategory, category_id)

    async def get_category_by_tenant_code(self, tenant_id: UUID, code: str) -> AssetCategory | None:
        result = await self.session.execute(
            select(AssetCategory).where(AssetCategory.tenant_id == tenant_id, AssetCategory.code == code)
        )
        return result.scalar_one_or_none()

    async def add_category(self, category: AssetCategory) -> AssetCategory:
        self.session.add(category)
        await self.session.flush()
        await self.session.refresh(category)
        return category

    async def list_assets(self, tenant_id: UUID | None = None, sppg_id: UUID | None = None) -> list[Asset]:
        query = select(Asset).order_by(Asset.asset_code)
        if tenant_id is not None:
            query = query.where(Asset.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(Asset.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_asset_by_id(self, asset_id: UUID) -> Asset | None:
        return await self.session.get(Asset, asset_id)

    async def get_asset_by_id_and_scope(self, asset_id: UUID, tenant_id: UUID | None = None, sppg_id: UUID | None = None) -> Asset | None:
        query = select(Asset).where(Asset.id == asset_id)
        if tenant_id is not None:
            query = query.where(Asset.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(Asset.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_asset_by_tenant_code(self, tenant_id: UUID, asset_code: str) -> Asset | None:
        result = await self.session.execute(
            select(Asset).where(Asset.tenant_id == tenant_id, Asset.asset_code == asset_code)
        )
        return result.scalar_one_or_none()

    async def add_asset(self, asset: Asset) -> Asset:
        self.session.add(asset)
        await self.session.flush()
        await self.session.refresh(asset)
        return asset

    async def list_assignments(self, tenant_id: UUID | None = None, sppg_id: UUID | None = None) -> list[AssetAssignment]:
        query = select(AssetAssignment).order_by(AssetAssignment.assignment_date.desc(), AssetAssignment.created_at.desc())
        if tenant_id is not None:
            query = query.where(AssetAssignment.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(AssetAssignment.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_assignments_by_asset(self, asset_id: UUID) -> list[AssetAssignment]:
        result = await self.session.execute(
            select(AssetAssignment).where(AssetAssignment.asset_id == asset_id).order_by(
                AssetAssignment.assignment_date.desc(),
                AssetAssignment.created_at.desc(),
            )
        )
        return list(result.scalars().all())

    async def add_assignment(self, assignment: AssetAssignment) -> AssetAssignment:
        self.session.add(assignment)
        await self.session.flush()
        await self.session.refresh(assignment)
        return assignment

    async def list_depreciations(self, tenant_id: UUID | None = None, sppg_id: UUID | None = None) -> list[AssetDepreciation]:
        query = select(AssetDepreciation).order_by(AssetDepreciation.depreciation_date.desc(), AssetDepreciation.created_at.desc())
        if tenant_id is not None:
            query = query.where(AssetDepreciation.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(AssetDepreciation.sppg_id == sppg_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_depreciations_by_asset(self, asset_id: UUID) -> list[AssetDepreciation]:
        result = await self.session.execute(
            select(AssetDepreciation).where(AssetDepreciation.asset_id == asset_id).order_by(
                AssetDepreciation.depreciation_date.desc(),
                AssetDepreciation.created_at.desc(),
            )
        )
        return list(result.scalars().all())

    async def get_depreciation_by_asset_date(self, asset_id: UUID, depreciation_date) -> AssetDepreciation | None:
        result = await self.session.execute(
            select(AssetDepreciation).where(
                AssetDepreciation.asset_id == asset_id,
                AssetDepreciation.depreciation_date == depreciation_date,
            )
        )
        return result.scalar_one_or_none()

    async def add_depreciation(self, depreciation: AssetDepreciation) -> AssetDepreciation:
        self.session.add(depreciation)
        await self.session.flush()
        await self.session.refresh(depreciation)
        return depreciation
