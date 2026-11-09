START_TEXT = """JSON helper is online.

Send any message and I will reply with the raw Telegram update as JSON.
Send a Telegram update (or just a message object) as text or a .json file and I will send the message from it.

Commands:
/help — how it works
/json — raw JSON of the message you reply to"""

HELP_TEXT = """How to use

1. Message -> JSON
Send text, photo, video, audio, voice, document, sticker, animation, video note, location, venue, contact, poll or dice. The bot replies with the raw Telegram update JSON, including update_id, from, chat, date, forward fields and entities.
If the JSON does not fit into one message, the bot sends a message_<id>.json file.

2. JSON -> message
Send a Telegram update JSON (with a "message" object) or a bare message object, as text or as a .json file. The bot detects the content type from the message fields.

Examples:
{"text": "Hello"}
{"message": {"message_id": 1, "date": 1700000000, "chat": {"id": 1, "type": "private"}, "text": "Hello"}}

3. Media
Use the media objects from Telegram JSON. A file_id works only in this bot; you may replace it with a direct url:
{"photo": {"url": "https://example.com/cat.jpg"}, "caption": "A cat"}

4. Commands
/json — reply to a message to get its raw JSON (without update_id)
/help — this help

Limitations: keyboards and buttons are not transferred; a dice is rolled anew;
a poll is created anew without old votes."""
