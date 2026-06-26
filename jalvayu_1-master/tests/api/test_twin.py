import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_get_twin_state(async_client: AsyncClient, db):
    pass

async def test_trigger_simulation(async_client: AsyncClient, db):
    pass
