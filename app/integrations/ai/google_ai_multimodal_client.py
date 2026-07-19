import base64

import httpx

from app.core.config.settings import Settings
from app.support.exceptions.base import BadRequestException, ServiceUnavailableException


class GoogleAIMultimodalClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def is_configured(self) -> bool:
        return bool(
            self.settings.google_ai_enabled
            and self.settings.google_ai_api_key
            and self.settings.google_ai_media_model
        )

    async def analyze_media(
        self,
        *,
        prompt: str,
        mime_type: str,
        source_url: str | None = None,
        base64_data: str | None = None,
    ) -> dict:
        if not self.is_configured():
            raise ServiceUnavailableException(
                code="GOOGLE_AI_NOT_CONFIGURED",
                message="Integrasi Google AI belum dikonfigurasi pada .env.",
            )
        media_b64 = base64_data
        if media_b64 is None and source_url is not None:
            media_b64 = await self._download_as_base64(source_url)
        if not media_b64:
            raise BadRequestException(
                code="AI_MEDIA_SOURCE_REQUIRED",
                message="Sumber media wajib berupa source_url atau base64_data.",
            )
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {"inline_data": {"mime_type": mime_type, "data": media_b64}},
                    ]
                }
            ]
        }
        async with httpx.AsyncClient(timeout=self.settings.google_ai_timeout_seconds) as client:
            response = await client.post(
                f"{self.settings.google_ai_base_url.rstrip('/')}/models/{self.settings.google_ai_media_model}:generateContent",
                params={"key": self.settings.google_ai_api_key},
                json=payload,
            )
        response.raise_for_status()
        result = response.json()
        text_parts: list[str] = []
        for candidate in result.get("candidates", []):
            for part in candidate.get("content", {}).get("parts", []):
                if isinstance(part.get("text"), str):
                    text_parts.append(part["text"])
        return {
            "provider": "google_ai",
            "model": self.settings.google_ai_media_model,
            "analysis_text": "\n".join(text_parts).strip(),
            "raw_response": result,
        }

    async def _download_as_base64(self, source_url: str) -> str:
        max_bytes = self.settings.google_ai_media_max_download_mb * 1024 * 1024
        async with httpx.AsyncClient(timeout=self.settings.google_ai_timeout_seconds) as client:
            response = await client.get(source_url)
        response.raise_for_status()
        data = response.content
        if len(data) > max_bytes:
            raise BadRequestException(
                code="AI_MEDIA_FILE_TOO_LARGE",
                message="Ukuran file media melebihi batas konfigurasi.",
            )
        return base64.b64encode(data).decode("utf-8")
