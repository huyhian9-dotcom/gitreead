from __future__ import annotations

import json
import re
from typing import Any, TypeVar

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field, ValidationError

from app.config import get_settings

MODEL_NAME = "claude-sonnet-4-20250514"

T = TypeVar("T", bound=BaseModel)


class AnalysisPayload(BaseModel):
    score: float = Field(ge=0, le=100)
    strengths: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)
    details: str = ""


class ReportPayload(BaseModel):
    summary: str
    recommendations: list[str] = Field(default_factory=list)


def _extract_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text")
                if text:
                    parts.append(str(text))
            else:
                text = getattr(item, "text", None)
                if text:
                    parts.append(str(text))
        return "\n".join(parts)
    return str(content)


def _extract_json_object(text: str) -> str:
    fenced = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        return fenced.group(1)
    inline = re.search(r"(\{.*\})", text, re.DOTALL)
    if inline:
        return inline.group(1)
    raise ValueError("No JSON object found in model response")


async def _invoke_json_model(
    system_prompt: str,
    user_prompt: str,
    schema: type[T],
    fallback: T,
) -> T:
    settings = get_settings()
    if not settings.ANTHROPIC_API_KEY:
        return fallback

    from langchain_anthropic import ChatAnthropic

    llm = ChatAnthropic(
        model=MODEL_NAME,
        anthropic_api_key=settings.ANTHROPIC_API_KEY,
        temperature=0,
        max_tokens=1800,
    )

    try:
        response = await llm.ainvoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]
        )
        raw_text = _extract_text(response.content)
        payload = json.loads(_extract_json_object(raw_text))
        return schema.model_validate(payload)
    except (json.JSONDecodeError, ValidationError, ValueError, TypeError):
        return fallback
    except Exception:
        return fallback


async def run_analysis_prompt(
    system_prompt: str,
    user_prompt: str,
    fallback: dict[str, Any],
) -> dict[str, Any]:
    payload = await _invoke_json_model(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        schema=AnalysisPayload,
        fallback=AnalysisPayload.model_validate(fallback),
    )
    return payload.model_dump()


async def run_report_prompt(
    system_prompt: str,
    user_prompt: str,
    fallback: dict[str, Any],
) -> dict[str, Any]:
    payload = await _invoke_json_model(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        schema=ReportPayload,
        fallback=ReportPayload.model_validate(fallback),
    )
    return payload.model_dump()
