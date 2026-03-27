from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from app.agents.graph import build_analysis_graph
from app.agents.nodes.reporter import build_criteria_dict
from app.models.schemas import AnalysisRequest, AnalysisResponse, CriteriaResult, StreamEvent
from app.models.state import RepoAnalysisState
from app.storage import store

router = APIRouter(tags=["analysis"])
analysis_graph = build_analysis_graph()
TERMINAL_STATUSES = {"completed", "failed"}


def spawn_analysis_job(coro: object) -> asyncio.Task[object]:
    return asyncio.create_task(coro)  # type: ignore[arg-type]


def _criteria_models_from_state(state: RepoAnalysisState) -> dict[str, CriteriaResult] | None:
    criteria = build_criteria_dict(state)
    if not criteria:
        return None
    return {
        name: CriteriaResult.model_validate(payload)
        for name, payload in criteria.items()
    }


async def _update_analysis_from_state(analysis_id: str, state: RepoAnalysisState) -> AnalysisResponse:
    current = await store.get_analysis(analysis_id)
    if current is None:
        raise KeyError(f"Unknown analysis id {analysis_id}")

    criteria = _criteria_models_from_state(state)
    updated = current.model_copy(
        update={
            "status": state.get("status", current.status),
            "score": state.get("final_score", current.score),
            "grade": state.get("grade", current.grade),
            "summary": state.get("summary", current.summary),
            "criteria": criteria or current.criteria,
            "recommendations": state.get("recommendations", current.recommendations),
            "completed_at": (
                datetime.now(UTC)
                if state.get("status") == "completed"
                else current.completed_at
            ),
            "error": "; ".join(state.get("errors", [])) or current.error,
        }
    )
    await store.upsert_analysis(updated)
    return updated


async def _append_status_event(analysis_id: str, status_value: str) -> None:
    await store.append_event(
        analysis_id,
        StreamEvent(event="status_update", data={"status": status_value}),
    )


async def _emit_state_events(
    analysis_id: str,
    previous_state: RepoAnalysisState,
    new_state: RepoAnalysisState,
) -> None:
    previous_status = previous_state.get("status")
    current_status = new_state.get("status")
    if current_status and current_status != previous_status:
        await _append_status_event(analysis_id, current_status)

    field_mapping = {
        "code_quality": "code_quality_analysis",
        "docs": "docs_analysis",
        "tests": "tests_analysis",
        "security": "security_analysis",
        "structure": "structure_analysis",
    }
    for criteria_name, field_name in field_mapping.items():
        previous_payload = previous_state.get(field_name)
        current_payload = new_state.get(field_name)
        if current_payload and not previous_payload:
            await store.append_event(
                analysis_id,
                StreamEvent(
                    event="criteria_complete",
                    data={
                        "criteria": criteria_name,
                        "score": current_payload.get("score", 0),
                    },
                ),
            )

    if current_status == "completed" and previous_status != "completed":
        await store.append_event(
            analysis_id,
            StreamEvent(
                event="analysis_complete",
                data={
                    "score": new_state.get("final_score", 0),
                    "grade": new_state.get("grade", "F"),
                },
            ),
        )


async def run_analysis_job(analysis_id: str, request: AnalysisRequest) -> None:
    state: RepoAnalysisState = {
        "analysis_id": analysis_id,
        "repo_url": request.repo_url,
        "branch": request.branch,
        "repo_metadata": {},
        "file_tree": [],
        "selected_files": [],
        "file_contents": {},
        "language_stats": {},
        "dependencies": [],
        "code_quality_analysis": {},
        "docs_analysis": {},
        "tests_analysis": {},
        "security_analysis": {},
        "structure_analysis": {},
        "final_score": 0.0,
        "grade": "F",
        "summary": "",
        "recommendations": [],
        "report": {},
        "errors": [],
        "status": "pending",
    }

    previous_state = state
    try:
        async for snapshot in analysis_graph.astream(state, stream_mode="values"):
            await _emit_state_events(analysis_id, previous_state, snapshot)
            await _update_analysis_from_state(analysis_id, snapshot)
            previous_state = snapshot
    except Exception as exc:
        failed_state: RepoAnalysisState = {
            **previous_state,
            "status": "failed",
            "errors": [*previous_state.get("errors", []), f"analysis execution failed: {exc}"],
            "final_score": 0.0,
            "grade": "F",
        }
        await _append_status_event(analysis_id, "failed")
        await _update_analysis_from_state(analysis_id, failed_state)


@router.post("/analyze", status_code=status.HTTP_202_ACCEPTED)
async def analyze_repository(payload: AnalysisRequest) -> dict[str, str]:
    analysis_id = str(uuid4())
    now = datetime.now(UTC)
    analysis = AnalysisResponse(
        id=analysis_id,
        repo_url=payload.repo_url,
        status="pending",
        created_at=now,
    )
    await store.create_analysis(analysis)
    await _append_status_event(analysis_id, "pending")
    spawn_analysis_job(run_analysis_job(analysis_id, payload))
    return {"id": analysis_id, "status": "pending"}


@router.get("/analysis/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(analysis_id: str) -> AnalysisResponse:
    analysis = await store.get_analysis(analysis_id)
    if analysis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")
    return analysis


@router.get("/analysis/{analysis_id}/stream")
async def stream_analysis(analysis_id: str) -> StreamingResponse:
    if await store.get_analysis(analysis_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")

    async def event_generator():
        cursor = 0
        while True:
            events = await store.get_events_since(analysis_id, cursor)
            for event in events:
                cursor += 1
                yield f"event: {event.event}\ndata: {json.dumps(event.data)}\n\n"

            analysis = await store.get_analysis(analysis_id)
            if analysis and analysis.status in TERMINAL_STATUSES and not events:
                break

            await asyncio.sleep(0.25)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
