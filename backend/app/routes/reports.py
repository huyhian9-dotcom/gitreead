from __future__ import annotations

from fastapi import APIRouter

from app.models.schemas import AnalysisListItem
from app.storage import store

router = APIRouter(tags=["reports"])


@router.get("/reports", response_model=list[AnalysisListItem])
async def list_reports() -> list[AnalysisListItem]:
    return await store.list_analyses()
