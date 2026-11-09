from __future__ import annotations

from aiogram.types import MessageEntity, PhotoSize, Update

from jsonhelpbot.serializers.message_to_json import message_to_dict, update_to_dict
from tests.factories import make_message

TEXT_UPDATE = {
    "update_id": 938481316,
    "message": {
        "message_id": 3174559,
        "from": {
            "id": 1356971297,
            "is_bot": False,
            "first_name": "BebruxX",
            "username": "reset_data",
            "language_code": "ru",
            "is_premium": True,
        },
        "chat": {
            "id": 1356971297,
            "first_name": "BebruxX",
            "username": "reset_data",
            "type": "private",
        },
        "date": 1794260253,
        "text": "Hello from Telegram",
        "entities": [
            {
                "type": "custom_emoji",
                "offset": 0,
                "length": 5,
                "custom_emoji_id": "5192670170157423644",
            }
        ],
    },
}

FORWARDED_UPDATE = {
    "update_id": 938481317,
    "message": {
        "message_id": 3174560,
        "from": {
            "id": 1356971297,
            "is_bot": False,
            "first_name": "BebruxX",
            "username": "reset_data",
            "language_code": "ru",
            "is_premium": True,
        },
        "chat": {
            "id": 1356971297,
            "first_name": "BebruxX",
            "username": "reset_data",
            "type": "private",
        },
        "date": 1794260253,
        "forward_origin": {
            "type": "user",
            "sender_user": {
                "id": 888888888,
                "is_bot": True,
                "first_name": "123123",
                "username": "123123_userbot",
            },
            "date": 1794259728,
        },
        "forward_from": {
            "id": 888888888,
            "is_bot": True,
            "first_name": "123123",
            "username": "123123_userbot",
        },
        "forward_date": 1794259728,
        "text": "lallallaalaaaaaa",
        "entities": [
            {
                "type": "custom_emoji",
                "offset": 5,
                "length": 2,
                "custom_emoji_id": "5192670170157423644",
            }
        ],
    },
}


def test_text_update_is_raw_telegram_json():
    update = Update.model_validate(TEXT_UPDATE)

    assert update_to_dict(update) == TEXT_UPDATE


def test_forwarded_update_keeps_forward_fields():
    update = Update.model_validate(FORWARDED_UPDATE)

    assert update_to_dict(update) == FORWARDED_UPDATE


def test_bare_message_has_no_update_wrapper():
    message = make_message(
        text="Hello",
        entities=[MessageEntity(type="bold", offset=0, length=5)],
    )

    payload = message_to_dict(message)

    assert "update_id" not in payload
    assert "schema" not in payload
    assert "type" not in payload
    assert payload["message_id"] == 1
    assert payload["date"] == 1704110400
    assert payload["text"] == "Hello"
    assert payload["entities"] == [{"type": "bold", "offset": 0, "length": 5}]
    assert payload["from"] == {
        "id": 100,
        "is_bot": False,
        "first_name": "Tester",
        "username": "tester",
    }
    assert payload["chat"] == {"id": 100, "type": "private", "first_name": "Tester"}


def test_photo_message_is_raw():
    message = make_message(
        photo=[
            PhotoSize(file_id="small", file_unique_id="small-u", width=90, height=90),
            PhotoSize(
                file_id="large",
                file_unique_id="large-u",
                width=800,
                height=600,
                file_size=1234,
            ),
        ],
        caption="A cat",
        caption_entities=[MessageEntity(type="italic", offset=0, length=5)],
    )

    payload = message_to_dict(message)

    assert payload["photo"] == [
        {"file_id": "small", "file_unique_id": "small-u", "width": 90, "height": 90},
        {
            "file_id": "large",
            "file_unique_id": "large-u",
            "width": 800,
            "height": 600,
            "file_size": 1234,
        },
    ]
    assert payload["caption"] == "A cat"
    assert payload["caption_entities"] == [
        {"type": "italic", "offset": 0, "length": 5}
    ]


def test_none_fields_are_not_serialized():
    message = make_message(text="Hello")

    payload = message_to_dict(message)

    assert "photo" not in payload
    assert "caption" not in payload
    assert "forward_origin" not in payload
