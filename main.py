import asyncio
import json
import aiofiles
from aiohttp import web
from consumer.consumer import init_app as consumer_init_app
from propagator.propagator import EventPropagator
import argparse


async def start_services(config_file, events_file):
    consumer_app = await consumer_init_app()
    consumer_runner = web.AppRunner(consumer_app)
    await consumer_runner.setup()
    consumer_site = web.TCPSite(consumer_runner, 'localhost', 8080)
    await consumer_site.start()

    propagator = EventPropagator(config_file=config_file, events_file=events_file)
    await propagator.run()

def main():
    parser = argparse.ArgumentParser(description="Run the Event Propagator and Consumer services.")
    parser.add_argument("--config", default="config.json", help="Path to the configuration file.")
    parser.add_argument("--events", default="events_file.json", help="Path to the events file.")
    args = parser.parse_args()

    asyncio.run(start_services(args.config, args.events))

if __name__ == '__main__':
    main()