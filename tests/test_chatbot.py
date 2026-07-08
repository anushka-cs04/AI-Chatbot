import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app as app_module
from chatbot import get_response


class ChatbotTests(unittest.TestCase):
    @patch("chatbot.get_client")
    def test_get_response_returns_text(self, mock_get_client):
        mock_client = type("Client", (), {})()
        mock_client.models = type(
            "Models",
            (),
            {"generate_content": lambda *args, **kwargs: type("Response", (), {"text": "Hello from test"})()},
        )()
        mock_get_client.return_value = mock_client

        reply = get_response("Hello")

        self.assertEqual(reply, "Hello from test")

    def test_new_chat_is_temporary_until_first_message(self):
        with app_module.app.test_client() as client:
            new_chat_response = client.post("/new_chat")
            self.assertEqual(new_chat_response.status_code, 200)

            new_chat_data = new_chat_response.get_json()
            self.assertEqual(new_chat_data["chat"]["messages"], [])
            self.assertNotIn(new_chat_data["chat_id"], client.get("/history").get_json()["chats"])

            with patch("app.get_response", return_value="Saved reply"):
                send_response = client.post(
                    "/chat",
                    json={"message": "Hello there", "chat_id": new_chat_data["chat_id"]},
                )

            self.assertEqual(send_response.status_code, 200)
            history_data = client.get("/history").get_json()
            self.assertIn(new_chat_data["chat_id"], history_data["chats"])
            self.assertIsNone(history_data["temp_chat"])

    def test_delete_chat_switches_to_blank_draft(self):
        with app_module.app.test_client() as client:
            with patch("app.get_response", return_value="Saved reply"):
                create_response = client.post(
                    "/chat",
                    json={"message": "First message", "chat_id": None},
                )

            chat_id = create_response.get_json()["chat_id"]
            delete_response = client.post(f"/delete_chat/{chat_id}")
            self.assertEqual(delete_response.status_code, 200)

            history_data = client.get("/history").get_json()
            self.assertNotIn(chat_id, history_data["chats"])
            self.assertIn("temp_chat", history_data)
            self.assertEqual(history_data["temp_chat"]["messages"], [])


if __name__ == "__main__":
    unittest.main()
