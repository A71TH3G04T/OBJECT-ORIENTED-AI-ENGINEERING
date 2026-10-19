import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv


class ChatSession:
    """Holds one conversation: its history, its file, and its Gemini chat object."""

    def __init__(self, client, model, history_file, system_instruction):
        self.client = client
        self.model = model
        self.history_file = history_file
        self.system_instruction = system_instruction
        self.history = []
        self.load_history()
        self.start_chat()

    def load_history(self):
        """Read the JSON file into self.history. Empty list if missing or corrupted."""
        if os.path.exists(self.history_file):
            with open(self.history_file, "r", encoding="utf-8") as file:
                try:
                    self.history = json.load(file)
                except json.JSONDecodeError:
                    self.history = []

    def save_history(self):
        """Write self.history back to the JSON file."""
        with open(self.history_file, "w", encoding="utf-8") as file:
            json.dump(self.history, file, ensure_ascii=False, indent=4)

    def add_exchange(self, user_msg, ai_msg):
        """Record one back-and-forth, then save straight away."""
        self.history.append({"User": user_msg, "Ai": ai_msg})
        self.save_history()

    def build_past(self, limit=5):
        """Turn the last few saved exchanges into Gemini Content objects."""
        past = []
        for entry in self.history[-limit:]:
            user_msg = entry.get("User")
            ai_msg = entry.get("Ai")
            if not user_msg or not ai_msg:
                continue
            past.append(types.Content(role="user", parts=[types.Part(text=user_msg)]))
            past.append(types.Content(role="model", parts=[types.Part(text=ai_msg)]))
        return past

    def start_chat(self):
        """Create the Gemini chat object, pre-loaded with past conversation."""
        self.chat = self.client.chats.create(
            model=self.model,
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction
            ),
            history=self.build_past()
        )

    def send(self, user_msg):
        """Send one message, save the exchange, return the reply text."""
        response = self.chat.send_message(user_msg)
        reply = response.text
        self.add_exchange(user_msg, reply)
        return reply


# ---------------- the app ----------------
if __name__ == "__main__":

    SYSTEM_INSTRUCTION = "You are a helpful, clear and respectful AI assistant."
    MODEL = "gemini-3.6-flash"
    HISTORY_FILE = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "chat_history.json"
    )

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY missing - is .env a FILE in this folder?")

    client = genai.Client(api_key=api_key)
    session = ChatSession(client, MODEL, HISTORY_FILE, SYSTEM_INSTRUCTION)

    print(f"Loaded {len(session.history)} past exchanges. Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")

        if user_input.strip().lower() == "exit":
            print("Bye Ali.")
            break

        if not user_input.strip():
            continue

        try:
            print("AI:", session.send(user_input), "\n")
        except Exception as error:
            print("Request failed:", type(error).__name__, "-", error, "\n")