import json
import re

import httpx

from app.core.config.settings import Settings
from app.support.exceptions.base import BadRequestException, ServiceUnavailableException


class OpenAINL2SQLClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def is_configured(self) -> bool:
        return bool(
            self.settings.openai_enabled
            and self.settings.openai_api_key
            and self.settings.openai_nl2sql_model
        )

    async def translate_to_sql(
        self,
        *,
        question: str,
        schema_context: str,
        dialect: str,
        max_rows: int,
    ) -> dict:
        if not self.is_configured():
            raise ServiceUnavailableException(
                code="OPENAI_NL2SQL_NOT_CONFIGURED",
                message="Integrasi OpenAI NL2SQL belum dikonfigurasi pada .env.",
            )

        prompt = (
            f"{self.settings.openai_nl2sql_system_prompt}\n\n"
            f"Database dialect: {dialect}\n"
            f"Maximum rows when execution is requested: {max_rows}\n\n"
            f"Schema context:\n{schema_context}\n\n"
            f"Question:\n{question}\n\n"
            "Important rules:\n"
            "- SQL must be read-only.\n"
            "- Use only SELECT or WITH.\n"
            "- Do not invent tables or columns.\n"
            "- Return valid JSON only.\n"
        )
        payload = {
            "model": self.settings.openai_nl2sql_model,
            "input": prompt,
        }
        headers = {
            "Authorization": f"Bearer {self.settings.openai_api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=self.settings.openai_timeout_seconds) as client:
            response = await client.post(
                f"{self.settings.openai_base_url.rstrip('/')}/responses",
                headers=headers,
                json=payload,
            )
        response.raise_for_status()
        content = self._extract_text(response.json())
        parsed = self._extract_json(content)
        if "sql" not in parsed:
            raise BadRequestException(
                code="OPENAI_NL2SQL_INVALID_RESPONSE",
                message="Respons OpenAI NL2SQL tidak memiliki field sql.",
            )
        return parsed

    @staticmethod
    def _extract_text(payload: dict) -> str:
        output_text = payload.get("output_text")
        if isinstance(output_text, str) and output_text.strip():
            return output_text
        fragments: list[str] = []
        for item in payload.get("output", []):
            for content in item.get("content", []):
                if content.get("type") == "output_text" and isinstance(content.get("text"), str):
                    fragments.append(content["text"])
                elif isinstance(content.get("text"), str):
                    fragments.append(content["text"])
        return "\n".join(fragments).strip()

    @staticmethod
    def _extract_json(content: str) -> dict:
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise
