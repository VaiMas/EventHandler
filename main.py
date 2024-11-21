import argparse
import asyncio
import json
import logging

import aiofiles
from aiohttp import web

from consumer import init_app as consumer_init_app
from propagator import EventPropagator


def setup_logging():
    """
    Set up logging configuration.
    """
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )


setup_logging()
logger = logging.getLogger(__name__)


async def start_services(config_file, events_file):
    """
    Start the consumer and propagator services.

    :param config_file: Path to the configuration file.
    :param events_file: Path to the events file.
    """
    try:
        async with aiofiles.open(config_file, mode="r") as file:
            config = json.loads(await file.read())
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        raise ValueError(f"Error loading configuration: {e}")

    required_keys = ["endpoint", "period"]
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        raise ValueError(
            f"Missing required config keys: {', '.join(missing_keys)}"
        )

    endpoint = config.get("endpoint")
    period = config.get("period")

    if not endpoint or not period:
        raise ValueError("Config file must contain 'endpoint' and 'period'.")

    # Start consumer service
    consumer_app = await consumer_init_app()
    consumer_runner = web.AppRunner(consumer_app)
    await consumer_runner.setup()
    consumer_site = web.TCPSite(consumer_runner, "localhost", 5000)
    await consumer_site.start()

    # Start propagator service
    propagator = EventPropagator(
        events_file=events_file, endpoint=endpoint, period=period
    )
    return consumer_runner, propagator


async def shutdown(consumer_runner, propagator_task):
    """
    Shutdown the services gracefully.

    :param consumer_runner: The consumer runner.
    :param propagator_task: The propagator task.
    """
    try:
        await consumer_runner.cleanup()
        propagator_task.cancel()
        await propagator_task
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


async def run_services(config_file, events_file):
    """
    Run the services and handle graceful shutdown.
    """
    consumer_runner, propagator = await start_services(config_file, events_file)
    propagator_task = asyncio.create_task(propagator.run())

    try:
        await propagator_task
    except asyncio.CancelledError:
        logger.info("Propagator task cancelled")
    except Exception as e:
        logger.error(f"Error running propagator: {e}")
    finally:
        await shutdown(consumer_runner, propagator_task)


def main():
    """
    Main entry point for the script.
    """
    parser = argparse.ArgumentParser(
        description="Run the Event Propagator and Consumer services."
    )
    parser.add_argument(
        "--config",
        default="config.json",
        help="Path to the configuration file.",
    )
    parser.add_argument(
        "--events", default="events_file.json", help="Path to the events file."
    )
    args = parser.parse_args()

    try:
        asyncio.run(run_services(args.config, args.events))
    except Exception as e:
        logger.error(f"Error starting services: {e}")


if __name__ == "__main__":
    main()
