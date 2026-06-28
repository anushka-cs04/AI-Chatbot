import os
from dotenv import load_dotenv
from google import genai

# Load the API key from .env
load_dotenv()

# Create Gemini client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def get_response(user_message):
    response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=f"""
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
{user_message}
"""
)

    return response.text