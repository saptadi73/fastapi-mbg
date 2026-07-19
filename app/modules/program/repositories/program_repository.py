from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.program.models.program import Program
from app.modules.program.models.program_period import ProgramPeriod
from app.modules.program.models.program_sppg import ProgramSppg
from app.modules.program.models.program_tenant import ProgramTenant


class ProgramRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_programs(self, tenant_id: UUID | None = None, sppg_id: UUID | None = None) -> list[Program]:
        query = select(Program).order_by(Program.name)
        if tenant_id is not None:
            query = query.where(
                Program.id.in_(
                    select(ProgramTenant.program_id).where(ProgramTenant.tenant_id == tenant_id)
                )
            )
        if sppg_id is not None:
            query = query.where(
                Program.id.in_(
                    select(ProgramSppg.program_id).where(ProgramSppg.sppg_id == sppg_id)
                )
            )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_program_by_id(self, program_id: UUID) -> Program | None:
        return await self.session.get(Program, program_id)

    async def get_program_by_code(self, code: str) -> Program | None:
        result = await self.session.execute(select(Program).where(Program.code == code))
        return result.scalar_one_or_none()

    async def add_program(self, program: Program) -> Program:
        self.session.add(program)
        await self.session.flush()
        await self.session.refresh(program)
        return program

    async def list_periods(self, program_id: UUID) -> list[ProgramPeriod]:
        result = await self.session.execute(
            select(ProgramPeriod).where(ProgramPeriod.program_id == program_id).order_by(ProgramPeriod.date_start)
        )
        return list(result.scalars().all())

    async def get_period_by_program_and_code(self, program_id: UUID, code: str) -> ProgramPeriod | None:
        result = await self.session.execute(
            select(ProgramPeriod).where(ProgramPeriod.program_id == program_id, ProgramPeriod.code == code)
        )
        return result.scalar_one_or_none()

    async def add_period(self, period: ProgramPeriod) -> ProgramPeriod:
        self.session.add(period)
        await self.session.flush()
        await self.session.refresh(period)
        return period

    async def list_tenant_assignments(self, program_id: UUID) -> list[ProgramTenant]:
        result = await self.session.execute(
            select(ProgramTenant).where(ProgramTenant.program_id == program_id).order_by(ProgramTenant.created_at)
        )
        return list(result.scalars().all())

    async def get_program_tenant(self, program_id: UUID, tenant_id: UUID) -> ProgramTenant | None:
        result = await self.session.execute(
            select(ProgramTenant).where(
                ProgramTenant.program_id == program_id,
                ProgramTenant.tenant_id == tenant_id,
            )
        )
        return result.scalar_one_or_none()

    async def add_program_tenant(self, assignment: ProgramTenant) -> ProgramTenant:
        self.session.add(assignment)
        await self.session.flush()
        await self.session.refresh(assignment)
        return assignment

    async def list_sppg_assignments(self, program_id: UUID) -> list[ProgramSppg]:
        result = await self.session.execute(
            select(ProgramSppg).where(ProgramSppg.program_id == program_id).order_by(ProgramSppg.created_at)
        )
        return list(result.scalars().all())

    async def get_program_sppg(self, program_id: UUID, sppg_id: UUID) -> ProgramSppg | None:
        result = await self.session.execute(
            select(ProgramSppg).where(
                ProgramSppg.program_id == program_id,
                ProgramSppg.sppg_id == sppg_id,
            )
        )
        return result.scalar_one_or_none()

    async def add_program_sppg(self, assignment: ProgramSppg) -> ProgramSppg:
        self.session.add(assignment)
        await self.session.flush()
        await self.session.refresh(assignment)
        return assignment
