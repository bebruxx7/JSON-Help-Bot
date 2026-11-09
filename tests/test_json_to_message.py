from __future__ import annotations

import pytest
from aiogram.types import MessageEntity, PhotoSize

from jsonhelpbot.serializers.json_to_message import PayloadError, build_send_call
from jsonhelpbot.serializers.message_to_json import message_to_dict
from tests.factories import make_message


def test_text_call():
    method, kwargs = build_send_call({"type": "text", "text": "Hello"})

    assert method == "send_message"
    assert kwargs == {"text": "Hello"}


def test_text_call_with_entities():
    method, kwargs = build_send_call(
        {
            "type": "text",
            "text": "Hello",
            "entities": [{"type": "bold", "offset": 0, "length": 5}],
        }
    )

    assert method == "send_message"
    assert isinstance(kwargs["entities"][0], MessageEntity)
    assert kwargs["entities"][0].type == "bold"


@pytest.mark.parametrize(
    ("media_type", "method_name"),
    [
        ("photo", "send_photo"),
        ("video", "send_video"),
        ("animation", "send_animation"),
        ("audio", "send_audio"),
        ("voice", "send_voice"),
        ("document", "send_document"),
        ("sticker", "send_sticker"),
        ("video_note", "send_video_note"),
    ],
)
def test_media_prefers_url(media_type, method_name):
    method, kwargs = build_send_call(
        {
            "type": media_type,
            "media": {
                "file_id": "file-id",
                "url": "https://example.com/file",
            },
        }
    )

    assert method == method_name
    assert kwargs[media_type] == "https://example.com/file"


def test_media_by_file_id_with_caption():
    method, kwargs = build_send_call(
        {
            "type": "photo",
            "caption": "A cat",
            "caption_entities": [{"type": "bold", "offset": 0, "length": 1}],
            "media": {"file_id": "photo-id"},
        }
    )

    assert method == "send_photo"
    assert kwargs["photo"] == "photo-id"
    assert kwargs["caption"] == "A cat"
    assert kwargs["caption_entities"][0].type == "bold"


def test_video_passes_dimensions():
    method, kwargs = build_send_call(
        {
            "type": "video",
            "media": {
                "file_id": "video-id",
                "width": 1920,
                "height": 1080,
                "duration": 30,
            },
        }
    )

    assert method == "send_video"
    assert kwargs["width"] == 1920
    assert kwargs["height"] == 1080
    assert kwargs["duration"] == 30


def test_audio_passes_metadata():
    method, kwargs = build_send_call(
        {
            "type": "audio",
            "media": {
                "file_id": "audio-id",
                "duration": 180,
                "performer": "Artist",
                "title": "Song",
            },
        }
    )

    assert method == "send_audio"
    assert kwargs["duration"] == 180
    assert kwargs["performer"] == "Artist"
    assert kwargs["title"] == "Song"


def test_sticker_passes_emoji():
    method, kwargs = build_send_call(
        {"type": "sticker", "media": {"file_id": "sticker-id", "emoji": "🙂"}}
    )

    assert method == "send_sticker"
    assert kwargs["emoji"] == "🙂"


def test_location_call():
    method, kwargs = build_send_call(
        {
            "type": "location",
            "location": {
                "latitude": 55.75,
                "longitude": 37.61,
                "horizontal_accuracy": 10.0,
            },
        }
    )

    assert method == "send_location"
    assert kwargs["latitude"] == 55.75
    assert kwargs["longitude"] == 37.61
    assert kwargs["horizontal_accuracy"] == 10.0


def test_venue_call():
    method, kwargs = build_send_call(
        {
            "type": "venue",
            "venue": {
                "title": "Red Square",
                "address": "Moscow",
                "location": {"latitude": 55.7539, "longitude": 37.6208},
            },
        }
    )

    assert method == "send_venue"
    assert kwargs["title"] == "Red Square"
    assert kwargs["address"] == "Moscow"
    assert kwargs["latitude"] == 55.7539


def test_contact_call():
    method, kwargs = build_send_call(
        {
            "type": "contact",
            "contact": {
                "phone_number": "+15550000000",
                "first_name": "Ivan",
                "last_name": "Petrov",
            },
        }
    )

    assert method == "send_contact"
    assert kwargs["phone_number"] == "+15550000000"
    assert kwargs["first_name"] == "Ivan"
    assert kwargs["last_name"] == "Petrov"


def test_poll_call():
    method, kwargs = build_send_call(
        {
            "type": "poll",
            "poll": {
                "question": "Walk?",
                "options": [{"text": "Yes"}, {"text": "No"}],
                "is_anonymous": True,
                "allows_multiple_answers": False,
            },
        }
    )

    assert method == "send_poll"
    assert kwargs["question"] == "Walk?"
    assert [option.text for option in kwargs["options"]] == ["Yes", "No"]
    assert kwargs["is_anonymous"] is True


def test_dice_call():
    method, kwargs = build_send_call({"type": "dice", "dice": {"emoji": "🎲"}})

    assert method == "send_dice"
    assert kwargs["emoji"] == "🎲"


def test_dice_without_emoji():
    method, kwargs = build_send_call({"type": "dice"})

    assert method == "send_dice"
    assert kwargs == {}


def test_round_trip_photo_message():
    message = make_message(
        photo=[
            PhotoSize(file_id="small", file_unique_id="small-u", width=90, height=90),
            PhotoSize(
                file_id="large",
                file_unique_id="large-u",
                width=800,
                height=600,
            ),
        ],
        caption="A cat",
    )

    payload = message_to_dict(message)
    method, kwargs = build_send_call(payload)

    assert method == "send_photo"
    assert kwargs["photo"] == "large"
    assert kwargs["caption"] == "A cat"


@pytest.mark.parametrize(
    ("payload", "match"),
    [
        ([], "object"),
        ({}, "type"),
        ({"type": "text"}, "text"),
        ({"type": "photo"}, "media"),
        ({"type": "photo", "media": {}}, "file_id"),
        ({"type": "location", "location": {}}, "latitude"),
        ({"type": "contact", "contact": {"first_name": "Ivan"}}, "phone_number"),
        ({"type": "poll", "poll": {"question": "Q?", "options": []}}, "two options"),
        ({"type": "unknown", "text": "Hello"}, "Unknown type"),
    ],
)
def test_invalid_payloads(payload, match):
    with pytest.raises(PayloadError, match=match):
        build_send_call(payload)
