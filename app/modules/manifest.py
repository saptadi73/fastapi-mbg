from dataclasses import dataclass

from fastapi import APIRouter


@dataclass(frozen=True)
class ModuleManifest:
    name: str
    prefix: str
    tags: list[str]
    router: APIRouter
