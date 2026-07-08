import os
import uuid

from flask import Flask, jsonify, render_template, request, session

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - depends on environment
    def load_dotenv():
        return False

from chatbot import get_response

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "super-secret-nova-key-change-this-in-production")
Gemini_API_KEY = os.getenv("GEMINI_API_KEY")
print(f"Gemini API Key: {'Set' if Gemini_API_KEY else 'Not Set'}")

def create_chat(title="New Conversation", welcome_message=None):
    chat_id = str(uuid.uuid4())
    if welcome_message is None:
        welcome_message = (
            "Hello! I am Nova, your professional AI assistant. How can I collaborate with you today?"
        )

    session.setdefault("chats", {})[chat_id] = {
        "title": title,
        "messages": [{"sender": "bot", "text": welcome_message}],
    }
    session["active_chat"] = chat_id
    session.modified = True
    return chat_id


def create_temp_chat():
    chat_id = str(uuid.uuid4())
    session["temp_chat"] = {
        "id": chat_id,
        "title": "New Conversation",
        "messages": [],
    }
    session["active_chat"] = chat_id
    session.modified = True
    return chat_id


def discard_temp_chat():
    if "temp_chat" in session:
        session.pop("temp_chat", None)
        session.modified = True
    return True


def ensure_session_state():
    if "chats" not in session or not isinstance(session["chats"], dict):
        session["chats"] = {}

    if not session["chats"]:
        create_chat()
        return session["active_chat"]

    if "active_chat" not in session or session["active_chat"] not in session["chats"]:
        session["active_chat"] = next(iter(session["chats"].keys()))
        session.modified = True

    return session["active_chat"]


@app.route("/")
def home():
    ensure_session_state()
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"error": "Please enter a message before sending."}), 400

    chat_id = data.get("chat_id")
    temp_chat = session.get("temp_chat")
    is_temp_chat = bool(chat_id and temp_chat and temp_chat.get("id") == chat_id)

    if not chat_id:
        chat_id = ensure_session_state()
        is_temp_chat = False

    if is_temp_chat:
        temp_chat["messages"].append({"sender": "user", "text": user_message})
        if temp_chat.get("title") == "New Conversation":
            title = user_message[:28].strip()
            temp_chat["title"] = title + ("..." if len(user_message) > 28 else "")

        bot_reply = get_response(user_message)
        temp_chat["messages"].append({"sender": "bot", "text": bot_reply})

        session["chats"][chat_id] = {
            "title": temp_chat["title"],
            "messages": temp_chat["messages"],
        }
        session["active_chat"] = chat_id
        session.pop("temp_chat", None)
        session.modified = True

        return jsonify({
            "response": bot_reply,
            "chat_id": chat_id,
            "title": session["chats"][chat_id]["title"],
            "saved": True,
        })

    if chat_id not in session["chats"]:
        chat_id = create_chat()

    session["chats"][chat_id]["messages"].append({"sender": "user", "text": user_message})

    if session["chats"][chat_id]["title"] == "New Conversation":
        title = user_message[:28].strip()
        session["chats"][chat_id]["title"] = title + ("..." if len(user_message) > 28 else "")

    bot_reply = get_response(user_message)
    session["chats"][chat_id]["messages"].append({"sender": "bot", "text": bot_reply})
    session.modified = True

    return jsonify({
        "response": bot_reply,
        "chat_id": chat_id,
        "title": session["chats"][chat_id]["title"],
    })


@app.route("/history", methods=["GET"])
def get_history():
    ensure_session_state()
    return jsonify({
        "chats": session.get("chats", {}),
        "active_chat": session.get("active_chat"),
        "temp_chat": session.get("temp_chat"),
    })


@app.route("/select_chat/<chat_id>", methods=["POST"])
def select_chat(chat_id):
    temp_chat = session.get("temp_chat")
    if temp_chat and not temp_chat.get("messages"):
        discard_temp_chat()

    if "chats" in session and chat_id in session["chats"]:
        session["active_chat"] = chat_id
        session.modified = True
        return jsonify({"success": True, "chat": session["chats"][chat_id]})
    return jsonify({"error": "Chat not found"}), 404


@app.route("/new_chat", methods=["POST"])
def new_chat():
    discard_temp_chat()
    chat_id = create_temp_chat()
    return jsonify({
        "chat_id": chat_id,
        "chat": session["temp_chat"],
    })


@app.route("/discard_temp_chat", methods=["POST"])
def discard_chat():
    discard_temp_chat()
    return jsonify({"success": True})


@app.route("/delete_chat/<chat_id>", methods=["POST"])
def delete_chat(chat_id):
    chats = session.get("chats", {})
    if chat_id in chats:
        chats.pop(chat_id, None)
        session["chats"] = chats
        session.modified = True

    if session.get("active_chat") == chat_id:
        if "temp_chat" in session:
            session.pop("temp_chat", None)
        session["active_chat"] = None
        create_temp_chat()

    return jsonify({"success": True, "chat_id": chat_id})


if __name__ == "__main__":
    app.run(debug=True)