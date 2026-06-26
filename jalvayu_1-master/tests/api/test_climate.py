import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_create_climate_dataset(async_client: AsyncClient, db):
    # Mock authentication headers
    # response = await async_client.post(
    #     "/api/v1/climate/",
    #     json={
    #         "name": "IMD Gridded Rainfall",
    #         "description": "Daily rainfall",
    #         "source": "IMD",
    #         "source_url": "https://imd.gov.in"
    #     }
    # )
    # assert response.status_code == 201
    pass

async def test_list_climate_datasets(async_client: AsyncClient, db):
    # response = await async_client.get("/api/v1/climate/")
    # assert response.status_code == 200
    pass
