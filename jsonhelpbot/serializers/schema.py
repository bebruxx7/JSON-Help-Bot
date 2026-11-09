from __future__ import annotations

SCHEMA_VERSION = 1

MEDIA_METHODS = {
    "photo": "send_photo",
    "video": "send_video",
    "animation": "send_animation",
    "audio": "send_audio",
    "voice": "send_voice",
    "document": "send_document",
    "sticker": "send_sticker",
    "video_note": "send_video_note",
}

EXTRA_TYPES = frozenset(
    {
        "location",
        "venue",
        "contact",
        "poll",
        "dice",
    }
)

SUPPORTED_TYPES = frozenset({"text", *MEDIA_METHODS, *EXTRA_TYPES})
