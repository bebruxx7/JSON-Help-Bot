START_TEXT = """JSON helper is online.

Send a regular message and I will reply with its JSON representation.
Send JSON as text or a .json file with a "type" field and I will build a message from it.

Commands:
/help — how it works
/json — JSON of the message you reply to"""

HELP_TEXT = """How to use

1. Message -> JSON
Send text, photo, video, audio, voice, document, sticker, animation, video note, location, venue, contact, poll or dice. The bot will return JSON.
If the JSON does not fit into one message, the bot sends a message_<id>.json file.

2. JSON -> message
Send JSON as text or as a .json file. At minimum you need "type" and the data for that type, for example:
{"type": "text", "text": "Hello"}

Types: text, photo, video, animation, audio, voice, document, sticker, video_note, location, venue, contact, poll, dice.

3. Media
Media in JSON is either a file_id (valid only for this bot) or a url.
Example: {"type": "photo", "media": {"url": "https://example.com/cat.jpg"}}
Use "caption" for captions.

4. Commands
/json — reply to a message to get its JSON
/help — this help

Limitations: keyboards and buttons are not transferred; a dice is rolled anew;
a poll is created anew without old votes."""
