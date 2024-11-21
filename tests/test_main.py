from unittest.mock import AsyncMock, patch

import pytest
from aiohttp import web

import main


class FakeAsyncOpen:
    """
    Custom async context manager to simulate file operations.

    :param content: Content to be returned by the read method.
    :param raise_error: Whether to raise an error when entering the context.
    """

    def __init__(self, content: str = "", raise_error: bool = False):
        self.content = content
        self.raise_error = raise_error

    async def __aenter__(self):
        if self.raise_error:
            raise Exception("File read error")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def read(self):
        """
        Simulate the `read` method of an async file object.

        :return: Content of the file.
        """
        if self.raise_error:
            raise Exception("File read error")
        return self.content


@pytest.mark.asyncio
@patch("main.aiofiles.open")
async def test_start_services_config_error(mock_open):
    """
    Test start_services function with a file read error.

    :param mock_open: Mocked aiofiles.open function.
    """
    mock_open.return_value = FakeAsyncOpen(raise_error=True)

    with pytest.raises(ValueError) as excinfo:
        await main.start_services("config.json", "events_file.json")

    assert "Error loading configuration: File read error" in str(excinfo.value)


@pytest.mark.asyncio
@patch("main.aiofiles.open")
async def test_start_services_invalid_config(mock_open):
    """
    Test start_services function with an invalid config file.

    :param mock_open: Mocked aiofiles.open function.
    """
    mock_open.return_value = FakeAsyncOpen(content="{}")

    with pytest.raises(ValueError) as excinfo:
        await main.start_services("config.json", "events_file.json")

    assert "Missing required config keys: endpoint, period" in str(
        excinfo.value
    )


@pytest.mark.asyncio
@patch("main.aiofiles.open")
@patch("main.consumer_init_app", new_callable=AsyncMock)
@patch("main.EventPropagator.run", new_callable=AsyncMock)
async def test_start_services_success(
    mock_run, mock_consumer_init_app, mock_open
):
    """
    Test start_services function with a valid config file.

    :param mock_open: Mocked aiofiles.open function.
    :param mock_consumer_init_app: Mocked consumer_init_app function.
    :param mock_run: Mocked EventPropagator.run method.
    """
    mock_open.return_value = FakeAsyncOpen(
        content='{"endpoint": "http://localhost:5000/event", "period": 5}'
    )
    mock_consumer_init_app.return_value = web.Application()

    consumer_runner, propagator = await main.start_services(
        "config.json", "events_file.json"
    )

    assert consumer_runner is not None
    assert propagator is not None

    await propagator.run()
    mock_run.assert_called_once()
    mock_consumer_init_app.assert_called_once()


@pytest.mark.asyncio
@patch("main.aiofiles.open")
async def test_start_services_missing_config_file(mock_open):
    """
    Test start_services function with a missing config file.

    :param mock_open: Mocked aiofiles.open function.
    """
    mock_open.side_effect = FileNotFoundError("Config file not found")

    with pytest.raises(ValueError) as excinfo:
        await main.start_services("config.json", "events_file.json")

    assert "Error loading configuration: Config file not found" in str(
        excinfo.value
    )


@pytest.mark.asyncio
@patch("main.aiofiles.open")
async def test_start_services_invalid_json(mock_open):
    """
    Test start_services function with invalid JSON in the config file.

    :param mock_open: Mocked aiofiles.open function.
    """
    mock_open.return_value = FakeAsyncOpen(content="{invalid_json}")

    with pytest.raises(ValueError) as excinfo:
        await main.start_services("config.json", "events_file.json")

    assert "Expecting property name enclosed" in str(excinfo.value)
