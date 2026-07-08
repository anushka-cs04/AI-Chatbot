import os

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - depends on environment
    def load_dotenv():
        return False

try:
    from google import genai
except ImportError:  # pragma: no cover - depends on environment
    genai = None

load_dotenv()


def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or genai is None:
        return None
    return genai.Client(api_key=api_key)


def build_prompt(user_message):
    cleaned = " ".join((user_message or "").split())
    return f"""
You are Nova AI, a professional AI assistant.

Always format your responses nicely.

Rules:
- Keep paragraphs short (2-3 lines maximum).
- Use blank lines between paragraphs.
- Use bullet points whenever appropriate.
- Use headings for different sections.
- Never write one huge paragraph.
- Make responses clean and easy to read.
- If the answer is long, divide it into sections.

User Question:
{cleaned}
""".strip()


def get_response(user_message):
    if not user_message or not str(user_message).strip():
        return "Please enter a message so I can help you."

    client = get_client()
    if client is None:
        return (
            "I’m ready to help, but the Gemini API key is not configured yet. "
            "Please add GEMINI_API_KEY to your environment and try again."
        )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=build_prompt(user_message),
        )
        return (response.text or "I’m here and ready to help.").strip()
    except Exception:
        return "I’m having trouble reaching the assistant right now. Please try again in a moment."