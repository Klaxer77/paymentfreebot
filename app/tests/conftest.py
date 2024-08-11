import asyncio
import pytest
from app.config import settings
from httpx import ASGITransport, AsyncClient
from app.main import app as fastapi_app
from app.utils.mock import mock_script

@pytest.fixture(scope='session', autouse=True)
async def setup_db():
    assert settings.MODE == 'TEST'
    await mock_script()
 
 
@pytest.mark.asyncio   
@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()
    
    
@pytest.fixture(scope='function')
async def ac():
    async with AsyncClient(transport=ASGITransport(fastapi_app), base_url='http://test') as ac:
        yield ac