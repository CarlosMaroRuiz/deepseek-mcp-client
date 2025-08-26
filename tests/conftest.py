import pytest

def pytest_configure(config):
    config.addinivalue_line("markers", "asyncio: mark test as an asyncio test")

# Limit to only asyncio backend to avoid trio errors
pytest.anyio_backends = ["asyncio"]