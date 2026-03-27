from __future__ import annotations

import asyncio

from app.models.schemas import AnalysisListItem, AnalysisResponse, StreamEvent


class AnalysisStore:
    def __init__(self) -> None:
        self._analyses: dict[str, AnalysisResponse] = {}
        self._events: dict[str, list[StreamEvent]] = {}
        self._lock = asyncio.Lock()

    async def reset(self) -> None:
        async with self._lock:
            self._analyses.clear()
            self._events.clear()

    async def create_analysis(self, analysis: AnalysisResponse) -> None:
        async with self._lock:
            self._analyses[analysis.id] = analysis
            self._events.setdefault(analysis.id, [])

    async def upsert_analysis(self, analysis: AnalysisResponse) -> None:
        async with self._lock:
            self._analyses[analysis.id] = analysis
            self._events.setdefault(analysis.id, [])

    async def get_analysis(self, analysis_id: str) -> AnalysisResponse | None:
        async with self._lock:
            return self._analyses.get(analysis_id)

    async def list_analyses(self) -> list[AnalysisListItem]:
        async with self._lock:
            items = [
                AnalysisListItem(
                    id=analysis.id,
                    repo_url=analysis.repo_url,
                    status=analysis.status,
                    score=analysis.score,
                    grade=analysis.grade,
                    created_at=analysis.created_at,
                )
                for analysis in self._analyses.values()
            ]
        return sorted(items, key=lambda item: item.created_at, reverse=True)

    async def append_event(self, analysis_id: str, event: StreamEvent) -> None:
        async with self._lock:
            self._events.setdefault(analysis_id, []).append(event)

    async def get_events_since(self, analysis_id: str, cursor: int) -> list[StreamEvent]:
        async with self._lock:
            return list(self._events.get(analysis_id, [])[cursor:])


store = AnalysisStore()
