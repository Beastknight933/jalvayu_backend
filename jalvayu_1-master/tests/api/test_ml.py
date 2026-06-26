import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_register_model(async_client: AsyncClient, db):
    pass

async def test_trigger_training(async_client: AsyncClient, db):
    pass
