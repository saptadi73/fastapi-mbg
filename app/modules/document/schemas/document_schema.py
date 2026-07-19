from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DocumentCreate(BaseModel):
    tenant_id: str
    sppg_id: str | None = None
    document_type: str
    title: str
    description: str | None = None
    owner_entity_type: str | None = None
    owner_entity_id: str | None = None
    tags: list[str] = []


class DocumentVersionCreate(BaseModel):
    file_name: str
    file_mime_type: str | None = None
    file_size_bytes: int | None = None
    checksum_sha256: str | None = None
    storage_backend: str = "LOCAL"
    object_key: str
    version_notes: str | None = None
    metadata_json: dict = {}
    uploaded_at: datetime


class DocumentLinkCreate(BaseModel):
    linked_entity_type: str
    linked_entity_id: str
    relation_type: str = "ATTACHMENT"


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    sppg_id: UUID | None
    document_number: str
    document_type: str
    title: str
    description: str | None
    owner_entity_type: str | None
    owner_entity_id: UUID | None
    tags: list[str]
    is_active: bool


class DocumentVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    document_id: UUID
    version_number: int
    file_name: str
    file_mime_type: str | None
    file_size_bytes: int | None
    checksum_sha256: str | None
    storage_backend: str
    object_key: str
    version_notes: str | None
    metadata_json: dict
    uploaded_at: datetime


class DocumentLinkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    document_id: UUID
    linked_entity_type: str
    linked_entity_id: UUID
    relation_type: str


class DocumentBundleRead(BaseModel):
    document: DocumentRead
    versions: list[DocumentVersionRead]
    links: list[DocumentLinkRead]
