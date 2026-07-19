from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.document.models.document import Document
from app.modules.document.models.document_link import DocumentLink
from app.modules.document.models.document_version import DocumentVersion


class DocumentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_documents(
        self,
        *,
        tenant_id: UUID | None = None,
        sppg_id: UUID | None = None,
        owner_entity_type: str | None = None,
        owner_entity_id: UUID | None = None,
    ) -> list[Document]:
        query = select(Document).order_by(Document.created_at.desc())
        if tenant_id is not None:
            query = query.where(Document.tenant_id == tenant_id)
        if sppg_id is not None:
            query = query.where(Document.sppg_id == sppg_id)
        if owner_entity_type is not None:
            query = query.where(Document.owner_entity_type == owner_entity_type)
        if owner_entity_id is not None:
            query = query.where(Document.owner_entity_id == owner_entity_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_document_by_id(self, document_id: UUID) -> Document | None:
        return await self.session.get(Document, document_id)

    async def add_document(self, document: Document) -> Document:
        self.session.add(document)
        await self.session.flush()
        await self.session.refresh(document)
        return document

    async def count_by_tenant(self, tenant_id: UUID) -> int:
        result = await self.session.execute(select(Document.id).where(Document.tenant_id == tenant_id))
        return len(list(result.scalars().all()))

    async def list_versions(self, document_id: UUID) -> list[DocumentVersion]:
        result = await self.session.execute(
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .order_by(DocumentVersion.version_number.desc())
        )
        return list(result.scalars().all())

    async def add_version(self, version: DocumentVersion) -> DocumentVersion:
        self.session.add(version)
        await self.session.flush()
        await self.session.refresh(version)
        return version

    async def list_links(self, document_id: UUID) -> list[DocumentLink]:
        result = await self.session.execute(
            select(DocumentLink)
            .where(DocumentLink.document_id == document_id)
            .order_by(DocumentLink.created_at)
        )
        return list(result.scalars().all())

    async def add_link(self, link: DocumentLink) -> DocumentLink:
        self.session.add(link)
        await self.session.flush()
        await self.session.refresh(link)
        return link

    async def get_link(self, document_id: UUID, linked_entity_type: str, linked_entity_id: UUID) -> DocumentLink | None:
        result = await self.session.execute(
            select(DocumentLink).where(
                DocumentLink.document_id == document_id,
                DocumentLink.linked_entity_type == linked_entity_type,
                DocumentLink.linked_entity_id == linked_entity_id,
            )
        )
        return result.scalar_one_or_none()
