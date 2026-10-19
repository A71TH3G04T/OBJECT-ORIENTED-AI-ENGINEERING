# Gemini Chatbot with Memory (OOP version)

A command line chatbot that remembers your last conversations, even after you close it and run it again. The whole thing lives in one class called `ChatSession`.

I wrote this while learning object oriented programming in Python. I wanted something real to practice on instead of a textbook example.

## How the memory works

The Gemini API doesn't remember anything between requests, so the bot has to do the remembering itself.

- Every message and reply is saved to a JSON file as soon as it happens.
- When the bot starts, it loads the last 5 exchanges from that file and hands them to Gemini as the starting history.
- That's why it can answer "what's my name?" on a fresh run.

## Using the class

```python
session = ChatSession(client, "gemini-3.6-flash", "chat_history.json", "You are a helpful assistant")
print(session.send("My name is Ali"))
```

The methods, in the order they get used:

- `load_history` reads the JSON file (an empty list if it's missing or broken)
- `build_past` turns the last few saved exchanges into Gemini messages
- `start_chat` creates the Gemini chat with that history loaded
- `send` sends one message, saves the exchange and returns the reply
- `add_exchange` and `save_history` do the saving

## Run it yourself

```
pip install google-genai python-dotenv
```

Put your Gemini API key in a file called `.env` next to `chat.py`:

```
GEMINI_API_KEY=your_key_here
```

Then:

```
python chat.py
```

Type `exit` to quit. The history file is created on the first run. It holds your actual conversations, so it's listed in `.gitignore` and isn't part of this repo.

## Bugs I hit while building it

These are the ones that taught me the most.

- `history[-5]` gives you one item. `history[-5:]` gives you the last five. It took me a while to see that one.
- If a class has two `__init__` methods, the second one silently replaces the first. No error, things just stop working.
- My first version replayed old messages by sending them to Gemini again and throwing away the answers. That costs extra API calls and doesn't restore anything. The fix was to build the history and pass it in when creating the chat.

## What I want to try next

- Combine this with function calling, so the bot can use tools and still remember
- Keep a summary of old chats instead of only the last 5 exchanges
