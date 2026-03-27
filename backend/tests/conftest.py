from __future__ import annotations

import pytest

from app.storage import store


@pytest.fixture(autouse=True)
async def reset_store() -> None:
    await store.reset()
    yield
    await store.reset()
