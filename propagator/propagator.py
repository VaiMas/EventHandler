import asyncio
import json
import logging
import random

import aiofiles
import httpx


def setup_logging():
    """
    Set up logging configuration.
    """
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )


setup_logging()
logger = logging.getLogger(__name__)


class EventPropagator:
    def __init__(self, events_file, endpoint, period):
        """
        Initialize the EventPropagator.

        :param events_file: Path to the events file.
        :param endpoint: Endpoint to send events to.
        :param period: Period between sending events.
        """
        self.events_file = events_file
        self.endpoint = endpoint
        self.period = period
        self.events = []

    async def load_events_from_file(self):
        """
        Load events from the specified file.
        """
        try:
            async with aiofiles.open(self.events_file, mode="r") as file:
                self.events = json.loads(await file.read())
        except Exception as e:
            logger.error(f"Error loading events: {e}")
            raise ValueError(f"Error loading events: {e}")

    async def send_event(self, event):
        """
        Send an event to the specified endpoint.

        :param event: Event to be sent.
        """
        if not isinstance(event.get("event_type"), str) or not isinstance(
            event.get("event_payload"), str
        ):
            logger.warning(f"Invalid event format: {event}")
            return

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.endpoint, json=[event])
                response.raise_for_status()
                if not response.text:
                    logger.warning(
                        f"Received empty response for event: {event}"
                    )
            except httpx.HTTPStatusError as e:
                logger.error(
                    f"HTTP error sending event: "
                    f"{e.response.status_code} - {e.response.text}"
                )
            except httpx.RequestError as e:
                logger.error(f"Request error sending event: {e}")
            except Exception as e:
                logger.error(f"Unexpected error sending event: {e}")

    async def event_loop(self):
        """
        Continuously send events at the specified period.
        """
        while True:
            event = random.choice(self.events)
            await self.send_event(event)
            await asyncio.sleep(self.period)

    async def run(self):
        """
        Load events from file and start the event loop.
        """
        await self.load_events_from_file()
        await self.event_loop()
