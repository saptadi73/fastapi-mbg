from datetime import datetime
from uuid import UUID

from app.core.tenancy.context import get_current_sppg, get_current_tenant
from app.core.tenancy.write_scope import enforce_sppg_write_scope, enforce_tenant_write_scope
from app.modules.document.models.document import Document
from app.modules.document.models.document_link import DocumentLink
from app.modules.document.models.document_version import DocumentVersion
from app.modules.document.repositories.document_repository import DocumentRepository
from app.modules.document.schemas.document_schema import DocumentCreate, DocumentLinkCreate, DocumentVersionCreate
from app.modules.sppg.repositories.sppg_repository import SppgRepository
from app.modules.tenant.repositories.tenant_repository import TenantRepository
from app.support.exceptions.base import BadRequestException, ConflictException, NotFoundException


class DocumentService:
    def __init__(
        self,
        repository: DocumentRepository,
        tenant_repository: TenantRepository,
        sppg_repository: SppgRepository,
    ) -> None:
        self.repository = repository
        self.tenant_repository = tenant_repository
        self.sppg_repository = sppg_repository

    def _parse_scope_uuid(self, value: str | None, code: str, message: str) -> UUID | None:
        if value is None:
            return None
        try:
            return UUID(value)
        except ValueError as exc:
            raise BadRequestException(code=code, message=message) from exc

    def _get_scope(self) -> tuple[UUID | None, UUID | None]:
        return (
            self._parse_scope_uuid(get_current_tenant(), "INVALID_TENANT_CONTEXT", "Header X-Tenant-ID tidak valid."),
            self._parse_scope_uuid(get_current_sppg(), "INVALID_SPPG_CONTEXT", "Header X-SPPG-ID tidak valid."),
        )

    async def list_documents(self) -> list[Document]:
        tenant_id, sppg_id = self._get_scope()
        return await self.repository.list_documents(tenant_id=tenant_id, sppg_id=sppg_id)

    async def get_document_bundle(self, document_id: UUID) -> dict:
        tenant_id, sppg_id = self._get_scope()
        document = await self.repository.get_document_by_id(document_id)
        if document is None:
            raise NotFoundException(code="DOCUMENT_NOT_FOUND", message="Dokumen tidak ditemukan.")
        if tenant_id is not None and document.tenant_id != tenant_id:
            raise NotFoundException(code="DOCUMENT_NOT_FOUND", message="Dokumen tidak ditemukan.")
        if sppg_id is not None and document.sppg_id not in {None, sppg_id}:
            raise NotFoundException(code="DOCUMENT_NOT_FOUND", message="Dokumen tidak ditemukan.")
        return {
            "document": document,
            "versions": await self.repository.list_versions(document.id),
            "links": await self.repository.list_links(document.id),
        }

    async def create_document(self, payload: DocumentCreate) -> Document:
        tenant_id = UUID(payload.tenant_id)
        sppg_id = UUID(payload.sppg_id) if payload.sppg_id else None
        owner_entity_id = UUID(payload.owner_entity_id) if payload.owner_entity_id else None
        enforce_tenant_write_scope(tenant_id)
        if sppg_id is not None:
            enforce_sppg_write_scope(sppg_id)
        if await self.tenant_repository.get_by_id(tenant_id) is None:
            raise NotFoundException(code="TENANT_NOT_FOUND", message="Tenant dokumen tidak ditemukan.")
        if sppg_id is not None:
            sppg = await self.sppg_repository.get_by_id(sppg_id)
            if sppg is None or sppg.tenant_id != tenant_id:
                raise NotFoundException(code="SPPG_NOT_FOUND", message="SPPG dokumen tidak ditemukan.")
        next_number = await self.repository.count_by_tenant(tenant_id) + 1
        return await self.repository.add_document(
            Document(
                tenant_id=tenant_id,
                sppg_id=sppg_id,
                document_number=f"DOC-{datetime.now().strftime('%Y%m%d')}-{next_number:04d}",
                document_type=payload.document_type,
                title=payload.title,
                description=payload.description,
                owner_entity_type=payload.owner_entity_type,
                owner_entity_id=owner_entity_id,
                tags=payload.tags,
                is_active=True,
            )
        )

    async def add_version(self, document_id: UUID, payload: DocumentVersionCreate) -> DocumentVersion:
        bundle = await self.get_document_bundle(document_id)
        document = bundle["document"]
        versions = bundle["versions"]
        if not payload.object_key.strip():
            raise BadRequestException(code="DOCUMENT_OBJECT_KEY_REQUIRED", message="object_key wajib diisi.")
        return await self.repository.add_version(
            DocumentVersion(
                tenant_id=document.tenant_id,
                document_id=document.id,
                version_number=(versions[0].version_number + 1) if versions else 1,
                file_name=payload.file_name,
                file_mime_type=payload.file_mime_type,
                file_size_bytes=payload.file_size_bytes,
                checksum_sha256=payload.checksum_sha256,
                storage_backend=payload.storage_backend,
                object_key=payload.object_key,
                version_notes=payload.version_notes,
                metadata_json=payload.metadata_json,
                uploaded_at=payload.uploaded_at,
            )
        )

    async def add_link(self, document_id: UUID, payload: DocumentLinkCreate) -> DocumentLink:
        bundle = await self.get_document_bundle(document_id)
        document = bundle["document"]
        linked_entity_id = UUID(payload.linked_entity_id)
        existing = await self.repository.get_link(document.id, payload.linked_entity_type, linked_entity_id)
        if existing is not None:
            raise ConflictException(code="DOCUMENT_LINK_ALREADY_EXISTS", message="Link dokumen sudah ada.")
        return await self.repository.add_link(
            DocumentLink(
                tenant_id=document.tenant_id,
                document_id=document.id,
                linked_entity_type=payload.linked_entity_type,
                linked_entity_id=linked_entity_id,
                relation_type=payload.relation_type,
            )
        )
