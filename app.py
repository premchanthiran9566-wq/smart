"""
app.py

Flask backend for the mobile-phone chatbot.
It receives a user message, sends it to the Gemini API together with the
system prompt from chatbot_config.py, and returns the model's reply.
"""

import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai

from chatbot_config import SYSTEM_PROMPT

# Load variables from the .env file (GEMINI_API_KEY)
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing. Please set it in your .env file."
    )

genai.configure(api_key=GEMINI_API_KEY)

# Create the model once with the system prompt attached, so every
# conversation automatically follows the mobile-phone-only rules.
model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    system_instruction=SYSTEM_PROMPT,
)

app = Flask(__name__)


@app.route("/")
def home():
    """Render the chat page."""
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """Receive a user message and return the Gemini model's reply."""
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "Please type a message before sending."}), 400

    try:
        response = model.generate_content(user_message)
        reply_text = response.text if response and response.text else (
            "Sorry, I could not generate a response. Please try again."
        )
    except Exception as error:
        reply_text = f"Something went wrong while contacting the AI service: {error}"

    return jsonify({"reply": reply_text})


if __name__ == "__main__":
    app.run(debug=True)
