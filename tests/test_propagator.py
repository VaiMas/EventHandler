import asyncio
import json
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from propagator.propagator import EventPropagator


@pytest.fixture
def event_propagator():
    """
    Fixture to create an EventPropagator instance for testing.
    """
    return EventPropagator(
        events_file="test_events.json",
        endpoint="http://localhost:5000/event",
        period=1,
    )


@pytest.mark.asyncio
async def test_load_events(event_propagator, mocker):
    """
    Test loading events from the events file.
    """
    mock_open = mocker.patch("aiofiles.open", new_callable=MagicMock)
    mock_open.return_value.__aenter__.return_value.read = AsyncMock(
        return_value=json.dumps(
            [{"event_type": "message", "event_payload": "hello"}]
        )
    )

    await event_propagator.load_events_from_file()
    assert event_propagator.events == [
        {"event_type": "message", "event_payload": "hello"}
    ]


@pytest.mark.asyncio
async def test_send_event_success(event_propagator, mocker):
    """
    Test successful sending of an event.
    """
    mock_post = mocker.patch("httpx.AsyncClient.post", new_callable=AsyncMock)
    mock_post.return_value.status_code = 200

    event = {"event_type": "message", "event_payload": "hello"}
    await event_propagator.send_event(event)
    mock_post.assert_called_once_with(
        "http://localhost:5000/event", json=[event]
    )


@pytest.mark.asyncio
async def test_send_event_failure(event_propagator, mocker):
    """
    Test sending an event with a failure.
    """
    mock_post = mocker.patch("httpx.AsyncClient.post", new_callable=AsyncMock)
    mock_post.side_effect = httpx.RequestError("Request failed")

    event = {"event_type": "message", "event_payload": "hello"}
    await event_propagator.send_event(event)
    mock_post.assert_called_once_with(
        "http://localhost:5000/event", json=[event]
    )


@pytest.mark.asyncio
async def test_event_loop(event_propagator, mocker):
    """
    Test the event loop for sending events periodically.
    """
    mock_send_event = mocker.patch.object(
        event_propagator, "send_event", new_callable=AsyncMock
    )
    mock_sleep = mocker.patch("asyncio.sleep", new_callable=AsyncMock)

    event_propagator.events = [
        {"event_type": "message", "event_payload": "hello"}
    ]

    async def stop_event_loop(*args, **kwargs):
        """
        Stop the loop after the first iteration by raising CancelledError.
        """
        raise asyncio.CancelledError

    mock_sleep.side_effect = stop_event_loop

    with pytest.raises(asyncio.CancelledError):
        await event_propagator.event_loop()

    mock_send_event.assert_called_once()


@pytest.mark.asyncio
async def test_send_event_invalid_format(event_propagator, mocker):
    """
    Test sending an event with an invalid format.
    """
    mock_post = mocker.patch("httpx.AsyncClient.post", new_callable=AsyncMock)

    event = {"event_type": 123, "event_payload": {}}
    await event_propagator.send_event(event)
    mock_post.assert_not_called()


@pytest.mark.asyncio
async def test_load_events_empty_file(event_propagator, mocker):
    """
    Test loading events from an empty events file.
    """
    mock_open = mocker.patch("aiofiles.open", new_callable=MagicMock)
    mock_open.return_value.__aenter__.return_value.read = AsyncMock(
        return_value="[]"
    )

    await event_propagator.load_events_from_file()
    assert event_propagator.events == []


@pytest.mark.asyncio
async def test_send_event_unexpected_error(event_propagator, mocker):
    """
    Test sending an event with an unexpected error.
    """
    mock_post = mocker.patch("httpx.AsyncClient.post", new_callable=AsyncMock)
    mock_post.side_effect = Exception("Unexpected error")

    event = {"event_type": "message", "event_payload": "hello"}
    await event_propagator.send_event(event)
    mock_post.assert_called_once_with(
        "http://localhost:5000/event", json=[event]
    )
