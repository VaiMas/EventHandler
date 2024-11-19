from aiohttp import web
import aiosqlite
import json


async def init_db():
    async with aiosqlite.connect("events.db") as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                event_payload TEXT NOT NULL
            )
        ''')
        await db.commit()

async def handle_events(request):
    if not request.can_read_body:
        return web.Response(status=400)
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return web.Response(status=400)
    if (
        not isinstance(data, list)
        or not all(
            isinstance(item, dict)
            and isinstance(item.get('event_type'), str)
            and isinstance(item.get('event_payload'), str)
            for item in data
        )
        ):
        return web.Response(status=400)

    async with aiosqlite.connect('events.db') as db:
        for event in data:
            await db.execute('''
                INSERT INTO received_events (event_type, event_payload)
                VALUES (?, ?)
            ''', (event['event_type'], event['event_payload']))
        await db.commit()

    return web.json_response({"status": "success"}, status=200)

async def init_app():
    await init_db()
    app = web.Application()
    app.router.add_post('/event', handle_events)
    return app
