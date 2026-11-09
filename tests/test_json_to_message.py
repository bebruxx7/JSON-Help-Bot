from __future__ import annotations

import pytest
from aiogram.types import MessageEntity, PhotoSize

from jsonhelpbot.serializers.json_to_message import PayloadError, build_send_call
from jsonhelpbot.serializers.message_to_json import message_to_dict
from tests.factories import make_message


def test_text_from_update():
    payload = {
        "update_id": 1,
        "message": {
            "message_id": 10,
            "date": 1700000000,
            "chat": {"id": 1, "type": "private"},
            "from": {"id": 1, "is_bot": False, "first_name": "A"},
            "text": "Hello",
            "entities": [{"type": "bold", "offset": 0, "length": 5}],
        },
    }

    method, kwargs = build_send_call(payload)

    assert method == "send_message"
    assert kwargs["text"] == "Hello"
    assert isinstance(kwargs["entities"][0], MessageEntity)
    assert kwargs["entities"][0].type == "bold"


def test_text_from_bare_message():
    method, kwargs = build_send_call({"text": "Hello"})

    assert method == "send_message"
    assert kwargs == {"text": "Hello"}


@pytest.mark.parametrize(
    ("payload", "method_name", "media_key"),
    [
        ({"photo": [{"file_id": "id"}]}, "send_photo", "photo"),
        ({"video": {"file_id": "id"}}, "send_video", "video"),
        ({"animation": {"file_id": "id"}}, "send_animation", "animation"),
        ({"audio": {"file_id": "id"}}, "send_audio", "audio"),
        ({"voice": {"file_id": "id"}}, "send_voice", "voice"),
        ({"document": {"file_id": "id"}}, "send_document", "document"),
        ({"sticker": {"file_id": "id"}}, "send_sticker", "sticker"),
        ({"video_note": {"file_id": "id"}}, "send_video_note", "video_note"),
    ],
)
def test_media_by_file_id(payload, method_name, media_key):
    method, kwargs = build_send_call(payload)

    assert method == method_name
    assert kwargs[media_key] == "id"


def test_photo_selects_largest_size():
    payload = {
        "photo": [
            {"file_id": "small", "file_unique_id": "s", "width": 90, "height": 90},
            {"file_id": "large", "file_unique_id": "l", "width": 800, "height": 600},
        ]
    }

    method, kwargs = build_send_call(payload)

    assert method == "send_photo"
    assert kwargs["photo"] == "large"


def test_media_url_override():
    payload = {
        "photo": {"file_id": "id", "url": "https://example.com/cat.jpg"},
        "caption": "A cat",
    }

    method, kwargs = build_send_call(payload)

    assert method == "send_photo"
    assert kwargs["photo"] == "https://example.com/cat.jpg"
    assert kwargs["caption"] == "A cat"


def test_media_caption_entities():
    payload = {
        "video": {"file_id": "video-id"},
        "caption": "A cat",
        "caption_entities": [{"type": "bold", "offset": 0, "length": 1}],
    }

    method, kwargs = build_send_call(payload)

    assert method == "send_video"
    assert kwargs["caption"] == "A cat"
    assert kwargs["caption_entities"][0].type == "bold"


def test_video_passes_dimensions():
    payload = {
        "video": {
            "file_id": "video-id",
            "width": 1920,
            "height": 1080,
            "duration": 30,
        }
    }

    method, kwargs = build_send_call(payload)

    assert method == "send_video"
    assert kwargs["width"] == 1920
    assert kwargs["height"] == 1080
    assert kwargs["duration"] == 30


def test_audio_passes_metadata():
    payload = {
        "audio": {
            "file_id": "audio-id",
            "duration": 180,
            "performer": "Artist",
            "title": "Song",
        }
    }

    method, kwargs = build_send_call(payload)

    assert method == "send_audio"
    assert kwargs["duration"] == 180
    assert kwargs["performer"] == "Artist"
    assert kwargs["title"] == "Song"


def test_sticker_passes_emoji():
    method, kwargs = build_send_call(
        {"sticker": {"file_id": "sticker-id", "emoji": "🙂"}}
    )

    assert method == "send_sticker"
    assert kwargs["emoji"] == "🙂"


def test_location_call():
    method, kwargs = build_send_call(
        {
            "location": {
                "latitude": 55.75,
                "longitude": 37.61,
                "horizontal_accuracy": 10.0,
            }
        }
    )

    assert method == "send_location"
    assert kwargs["latitude"] == 55.75
    assert kwargs["longitude"] == 37.61
    assert kwargs["horizontal_accuracy"] == 10.0


def test_venue_call():
    method, kwargs = build_send_call(
        {
            "venue": {
                "title": "Red Square",
                "address": "Moscow",
                "location": {"latitude": 55.7539, "longitude": 37.6208},
            }
        }
    )

    assert method == "send_venue"
    assert kwargs["title"] == "Red Square"
    assert kwargs["address"] == "Moscow"
    assert kwargs["latitude"] == 55.7539


def test_contact_call():
    method, kwargs = build_send_call(
        {
            "contact": {
                "phone_number": "+15550000000",
                "first_name": "Ivan",
                "last_name": "Petrov",
            }
        }
    )

    assert method == "send_contact"
    assert kwargs["phone_number"] == "+15550000000"
    assert kwargs["first_name"] == "Ivan"
    assert kwargs["last_name"] == "Petrov"


def test_poll_call():
    method, kwargs = build_send_call(
        {
            "poll": {
                "question": "Walk?",
                "options": [{"text": "Yes"}, {"text": "No"}],
                "is_anonymous": True,
                "allows_multiple_answers": False,
            }
        }
    )

    assert method == "send_poll"
    assert kwargs["question"] == "Walk?"
    assert [option.text for option in kwargs["options"]] == ["Yes", "No"]
    assert kwargs["is_anonymous"] is True


def test_dice_call():
    method, kwargs = build_send_call({"dice": {"emoji": "🎲", "value": 4}})

    assert method == "send_dice"
    assert kwargs["emoji"] == "🎲"


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
        ({"update_id": 1}, "message"),
        ({"message": {"message_id": 1}}, "supported content"),
        ({"photo": []}, "file_id"),
        ({"photo": {}}, "file_id"),
        ({"location": {}}, "latitude"),
        ({"contact": {"first_name": "A"}}, "phone_number"),
        ({"poll": {"question": "Q?", "options": []}}, "two options"),
    ],
)
def test_invalid_payloads(payload, match):
    with pytest.raises(PayloadError, match=match):
        build_send_call(payload)
