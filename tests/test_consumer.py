from unittest import mock

from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from consumer import init_app


class TestConsumer(AioHTTPTestCase):
    async def get_application(self):
        return await init_app()

    @unittest_run_loop
    async def test_handle_event_success(self):
        """
        Test handling events successfully.
        """
        data = [{"event_type": "type1", "event_payload": "payload1"}]
        resp = await self.client.post(
            "/event", json=data, headers={"Content-Type": "application/json"}
        )
        assert resp.status == 200
        json_resp = await resp.json()
        assert json_resp["status"] == "success"

    @unittest_run_loop
    async def test_handle_event_invalid_content_type(self):
        """
        Test handling events with invalid content type.
        """
        data = "Invalid content type"
        resp = await self.client.post(
            "/event", data=data, headers={"Content-Type": "text/plain"}
        )
        assert resp.status == 400
        json_resp = await resp.json()
        assert json_resp == {"error": "Invalid JSON format"}

    @unittest_run_loop
    async def test_handle_event_invalid_json_format(self):
        """
        Test handling events with invalid JSON format.
        """
        data = '{"event_type": "type1", "event_payload": "payload1"'
        resp = await self.client.post(
            "/event", data=data, headers={"Content-Type": "application/json"}
        )
        assert resp.status == 400
        json_resp = await resp.json()
        assert json_resp == {"error": "Invalid JSON format"}

    @unittest_run_loop
    async def test_handle_event_missing_fields(self):
        """
        Test handling events with missing fields.
        """
        data = [{"event_type": "type1"}]  # Missing 'event_payload'
        resp = await self.client.post(
            "/event", json=data, headers={"Content-Type": "application/json"}
        )
        assert resp.status == 400
        json_resp = await resp.json()
        assert json_resp == {"error": "Invalid event data format"}

    @unittest_run_loop
    async def test_handle_event_internal_server_error(self):
        """
        Test handling events with an internal server error.
        """
        with mock.patch(
            "aiosqlite.connect", side_effect=Exception("Database error")
        ):
            data = [{"event_type": "type1", "event_payload": "payload1"}]
            resp = await self.client.post(
                "/event",
                json=data,
                headers={"Content-Type": "application/json"},
            )
            assert resp.status == 500
            json_resp = await resp.json()
            assert json_resp == {"error": "Internal server error"}

    @unittest_run_loop
    async def test_handle_event_request_body_not_readable(self):
        """
        Test handling events with non-readable request body.
        """
        with mock.patch.object(
            web.Request,
            "can_read_body",
            new_callable=mock.PropertyMock,
            return_value=False,
        ):
            resp = await self.client.post(
                "/event", json={}, headers={"Content-Type": "application/json"}
            )
            assert resp.status == 400
            json_resp = await resp.json()
            assert json_resp == {"error": "Request body is not readable"}

    @unittest_run_loop
    async def test_handle_event_invalid_data_logging(self):
        """
        Test handling events with invalid data format.
        """
        data = [{"event_type": "type1", "event_payload": 123}]
        resp = await self.client.post(
            "/event", json=data, headers={"Content-Type": "application/json"}
        )
        assert resp.status == 400
        json_resp = await resp.json()
        assert json_resp == {"error": "Invalid event data format"}

    @unittest_run_loop
    async def test_handle_event_invalid_json_logging(self):
        """
        Test handling events with invalid JSON format.
        """
        data = '{"event_type": "type1", "event_payload": "payload1"'
        resp = await self.client.post(
            "/event", data=data, headers={"Content-Type": "application/json"}
        )
        assert resp.status == 400
        json_resp = await resp.json()
        assert json_resp == {"error": "Invalid JSON format"}
