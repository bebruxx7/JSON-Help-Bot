from __future__ import annotations

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

EXTRA_KEYS = (
    "location",
    "venue",
    "contact",
    "poll",
    "dice",
)
