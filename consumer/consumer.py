import json
import logging

import aiosqlite
from aiohttp import web


def setup_logging():
    """
    Set up logging configuration.
    """
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )


setup_logging()
logger = logging.getLogger(__name__)


async def init_db():
    """
    Initialize the database by creating the received_events table if it does
    not exist.
    """
    async with aiosqlite.connect("events.db") as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS received_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                event_payload TEXT NOT NULL
            )
        """
        )
        await db.commit()


async def handle_events(request):
    """
    Handle incoming events by saving them to the database.

    :param request: The incoming request object.
    :return: A JSON response indicating success or failure.
    """
    if not request.can_read_body:
        return web.json_response(
            {"error": "Request body is not readable"}, status=400
        )
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return web.json_response({"error": "Invalid JSON format"}, status=400)
    if not isinstance(data, list) or not all(
        isinstance(item, dict)
        and isinstance(item.get("event_type"), str)
        and isinstance(item.get("event_payload"), str)
        for item in data
    ):
        return web.json_response(
            {"error": "Invalid event data format"}, status=400
        )

    try:
        async with aiosqlite.connect("events.db") as db:
            for event in data:
                await db.execute(
                    """
                    INSERT INTO received_events (event_type, event_payload)
                    VALUES (?, ?)
                """,
                    (event["event_type"], event["event_payload"]),
                )
            await db.commit()
    except aiosqlite.DatabaseError as db_err:
        logger.error(f"Database error: {db_err}")
        return web.json_response(
            {"error": "Database operation failed"}, status=500
        )
    except Exception as e:
        logger.error(f"Error saving events to database: {e}")
        return web.json_response({"error": "Internal server error"}, status=500)

    return web.json_response({"status": "success"}, status=200)


async def init_app():
    """
    Initialize the web application and set up routes.

    :return: The initialized web application.
    """
    await init_db()
    app = web.Application()
    app.router.add_post("/event", handle_events)
    return app
