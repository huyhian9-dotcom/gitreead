from __future__ import annotations

from datetime import UTC, datetime, timedelta

import httpx
import pytest

from app.main import app
from app.models.schemas import AnalysisResponse, StreamEvent
from app.routes import analysis as analysis_routes
from app.storage import store


@pytest.mark.asyncio
async def test_health_endpoint_returns_ok() -> None:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_post_analyze_returns_accepted(monkeypatch: pytest.MonkeyPatch) -> None:
    tasks: list[object] = []

    def fake_spawn(coro: object) -> object:
        tasks.append(coro)
        close = getattr(coro, "close", None)
        if callable(close):
            close()
        return object()

    monkeypatch.setattr(analysis_routes, "spawn_analysis_job", fake_spawn)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/api/v1/analyze",
            json={"repo_url": "https://github.com/org/repo"},
        )

    assert response.status_code == 202
    payload = response.json()
    assert payload["status"] == "pending"
    analysis = await store.get_analysis(payload["id"])
    assert analysis is not None
    assert analysis.status == "pending"
    assert tasks


@pytest.mark.asyncio
async def test_get_analysis_returns_404_for_unknown_id() -> None:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get("/api/v1/analysis/missing")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_reports_are_sorted_descending() -> None:
    now = datetime.now(UTC)
    await store.create_analysis(
        AnalysisResponse(
            id="older",
            repo_url="https://github.com/org/older",
            status="completed",
            created_at=now - timedelta(minutes=5),
        )
    )
    await store.create_analysis(
        AnalysisResponse(
            id="newer",
            repo_url="https://github.com/org/newer",
            status="pending",
            created_at=now,
        )
    )

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get("/api/v1/reports")

    assert response.status_code == 200
    payload = response.json()
    assert [item["id"] for item in payload] == ["newer", "older"]


@pytest.mark.asyncio
async def test_stream_endpoint_emits_sse_events() -> None:
    analysis = AnalysisResponse(
        id="stream-id",
        repo_url="https://github.com/org/repo",
        status="completed",
        created_at=datetime.now(UTC),
    )
    await store.create_analysis(analysis)
    await store.append_event("stream-id", StreamEvent(event="status_update", data={"status": "fetching"}))
    await store.append_event(
        "stream-id",
        StreamEvent(event="criteria_complete", data={"criteria": "code_quality", "score": 80}),
    )
    await store.append_event(
        "stream-id",
        StreamEvent(event="analysis_complete", data={"score": 72, "grade": "B"}),
    )

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get("/api/v1/analysis/stream-id/stream")

    assert response.status_code == 200
    assert "event: status_update" in response.text
    assert '"status": "fetching"' in response.text
    assert "event: analysis_complete" in response.text


@pytest.mark.asyncio
async def test_run_analysis_job_updates_store_and_events(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeGraph:
        async def astream(self, state: dict[str, object], stream_mode: str = 'values'):
            assert stream_mode == 'values'
            yield {
                **state,
                'status': 'fetching',
            }
            yield {
                **state,
                'status': 'analyzing',
                'code_quality_analysis': {
                    'score': 80,
                    'strengths': ['Boa modularidade'],
                    'improvements': ['Reduzir acoplamento'],
                    'details': 'Detalhes',
                },
            }
            yield {
                **state,
                'status': 'completed',
                'final_score': 72,
                'grade': 'B',
                'summary': 'Resumo final.',
                'recommendations': ['Alta: melhorar testes'],
                'code_quality_analysis': {
                    'score': 80,
                    'strengths': ['Boa modularidade'],
                    'improvements': ['Reduzir acoplamento'],
                    'details': 'Detalhes',
                },
                'docs_analysis': {
                    'score': 60,
                    'strengths': [],
                    'improvements': ['Expandir README'],
                    'details': 'Detalhes',
                },
                'tests_analysis': {
                    'score': 50,
                    'strengths': [],
                    'improvements': ['Cobrir edge cases'],
                    'details': 'Detalhes',
                },
                'security_analysis': {
                    'score': 70,
                    'strengths': [],
                    'improvements': ['Revisar secrets'],
                    'details': 'Detalhes',
                },
                'structure_analysis': {
                    'score': 65,
                    'strengths': [],
                    'improvements': ['Organizar raiz'],
                    'details': 'Detalhes',
                },
            }

    monkeypatch.setattr(analysis_routes, 'analysis_graph', FakeGraph())

    await store.create_analysis(
        AnalysisResponse(
            id='job-id',
            repo_url='https://github.com/org/repo',
            status='pending',
            created_at=datetime.now(UTC),
        )
    )

    await analysis_routes.run_analysis_job(
        'job-id',
        analysis_routes.AnalysisRequest(repo_url='https://github.com/org/repo'),
    )

    analysis = await store.get_analysis('job-id')
    events = await store.get_events_since('job-id', 0)

    assert analysis is not None
    assert analysis.status == 'completed'
    assert analysis.score == 72
    assert analysis.grade == 'B'
    assert analysis.summary == 'Resumo final.'
    assert any(event.event == 'criteria_complete' for event in events)
    assert any(event.event == 'analysis_complete' for event in events)
