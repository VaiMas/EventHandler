import asyncio
import json
import random

import httpx
import aiofiles


class EventPropagator:
    def __init__(self, config_file=None, events_file=None,
                 endpoint=None, period=None):
        self.config_file = config_file
        self.events_file = events_file
        self.endpoint = endpoint
        self.period = period
        self.config = {}
        self.events = []

    async def load_config(self):
        if not self.config_file:
            raise ValueError("Config file not set")

        try:
            async with aiofiles.open(self.config_file, mode='r') as file:
                self.config = json.loads(await file.read())

        except Exception as e:
            raise ValueError(f"Error loading config: {e}")

    async def load_events_from_file(self):
        try:
            async with aiofiles.open(self.events_file, mode='r') as file:
                self.events = json.loads(await file.read())
        except Exception as e:
            raise ValueError(f"Error loading events: {e}")

    async def send_event(self, event):
        if (
            not isinstance(event.get('event_type'), str)
            or not isinstance(event.get('event_payload'), str)
        ):
            return

        async with httpx.AsyncClient() as client:
            try:
                await client.post(self.endpoint, json=[event])
            except httpx.HTTPStatusError as e:
                print(f"Error sending event: {e}")

    async def configure(self):
        await self.load_config()

        self.events_file = self.events_file or self.config.get('events_file')
        self.endpoint = self.endpoint or self.config.get('endpoint')
        self.period = self.period or self.config.get('period')

        if not self.events_file or not self.endpoint or not self.period:
            return False

        await self.load_events_from_db()
        return True

    async def event_loop(self):
        while True:
            event = random.choice(self.events)
            await self.send_event(event)
            await asyncio.sleep(self.period)

    async def run(self):
        if not await self.configure():
            return

        await self.event_loop()
