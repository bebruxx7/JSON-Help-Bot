from __future__ import annotations

from datetime import datetime
from typing import Any

from aiogram.types import Message, MessageEntity

from jsonhelpbot.serializers.schema import SCHEMA_VERSION
from jsonhelpbot.utils.json_tools import dumps

_FILE_FIELDS = (
    "file_name",
    "mime_type",
    "file_size",
    "width",
    "height",
    "duration",
    "length",
    "title",
    "performer",
    "emoji",
    "is_animated",
    "is_video",
    "set_name",
)

_VENUE_FIELDS = (
    "foursquare_id",
    "foursquare_type",
    "google_place_id",
    "google_place_type",
)

_POLL_FIELDS = (
    "correct_option_id",
    "explanation",
    "open_period",
    "close_date",
)


def content_type_of(message: Message) -> str:
    value = message.content_type
    return value.value if hasattr(value, "value") else str(value)


def message_to_dict(message: Message) -> dict[str, Any]:
    content_type = content_type_of(message)
    payload: dict[str, Any] = {
        "schema": SCHEMA_VERSION,
        "type": content_type,
        "message_id": message.message_id,
        "date": _iso(message.date),
        "chat": _chat(message.chat),
    }
    from_user = _user(message.from_user)
    if from_user is not None:
        payload["from"] = from_user
    if message.reply_to_message is not None:
        payload["reply_to_message_id"] = message.reply_to_message.message_id
    if message.edit_date is not None:
        payload["edit_date"] = _iso(message.edit_date)
    if message.text is not None:
        payload["text"] = message.text
    if message.caption is not None:
        payload["caption"] = message.caption
    entities = _entities(message.entities)
    if entities:
        payload["entities"] = entities
    caption_entities = _entities(message.caption_entities)
    if caption_entities:
        payload["caption_entities"] = caption_entities
    media = _media(message)
    if media is not None:
        payload["media"] = media
    if message.location is not None:
        payload["location"] = _location(message.location)
    if message.venue is not None:
        payload["venue"] = _venue(message.venue)
    if message.contact is not None:
        payload["contact"] = _contact(message.contact)
    if message.poll is not None:
        payload["poll"] = _poll(message.poll)
    if message.dice is not None:
        payload["dice"] = {"emoji": message.dice.emoji, "value": message.dice.value}
    return payload


def message_to_json(message: Message) -> str:
    return dumps(message_to_dict(message))


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _user(user) -> dict[str, Any] | None:
    if user is None:
        return None
    data: dict[str, Any] = {
        "id": user.id,
        "is_bot": user.is_bot,
        "first_name": user.first_name,
    }
    if user.last_name is not None:
        data["last_name"] = user.last_name
    if user.username is not None:
        data["username"] = user.username
    if getattr(user, "language_code", None) is not None:
        data["language_code"] = user.language_code
    return data


def _chat(chat) -> dict[str, Any]:
    data: dict[str, Any] = {"id": chat.id, "type": chat.type}
    for field in ("title", "username", "first_name", "last_name"):
        value = getattr(chat, field, None)
        if value is not None:
            data[field] = value
    return data


def _entities(entities: list[MessageEntity] | None) -> list[dict[str, Any]] | None:
    if not entities:
        return None
    result: list[dict[str, Any]] = []
    for entity in entities:
        item: dict[str, Any] = {
            "type": entity.type,
            "offset": entity.offset,
            "length": entity.length,
        }
        if entity.url is not None:
            item["url"] = entity.url
        if entity.user is not None:
            item["user"] = _user(entity.user)
        if entity.language is not None:
            item["language"] = entity.language
        custom_emoji_id = getattr(entity, "custom_emoji_id", None)
        if custom_emoji_id is not None:
            item["custom_emoji_id"] = custom_emoji_id
        result.append(item)
    return result


def _media(message: Message) -> dict[str, Any] | None:
    if message.photo:
        return _file(message.photo[-1])
    for attribute in (
        "video",
        "animation",
        "audio",
        "voice",
        "document",
        "sticker",
        "video_note",
    ):
        item = getattr(message, attribute, None)
        if item is not None:
            return _file(item)
    return None


def _file(item) -> dict[str, Any]:
    data: dict[str, Any] = {
        "file_id": item.file_id,
        "file_unique_id": item.file_unique_id,
    }
    for field in _FILE_FIELDS:
        value = getattr(item, field, None)
        if value is not None:
            data[field] = value
    return data


def _location(location) -> dict[str, Any]:
    data: dict[str, Any] = {
        "latitude": location.latitude,
        "longitude": location.longitude,
    }
    for field in ("horizontal_accuracy", "live_period", "heading", "proximity_alert_radius"):
        value = getattr(location, field, None)
        if value is not None:
            data[field] = value
    return data


def _venue(venue) -> dict[str, Any]:
    data: dict[str, Any] = {
        "title": venue.title,
        "address": venue.address,
        "location": _location(venue.location),
    }
    for field in _VENUE_FIELDS:
        value = getattr(venue, field, None)
        if value is not None:
            data[field] = value
    return data


def _contact(contact) -> dict[str, Any]:
    data: dict[str, Any] = {
        "phone_number": contact.phone_number,
        "first_name": contact.first_name,
    }
    for field in ("last_name", "user_id", "vcard"):
        value = getattr(contact, field, None)
        if value is not None:
            data[field] = value
    return data


def _poll(poll) -> dict[str, Any]:
    data: dict[str, Any] = {
        "question": poll.question,
        "options": [
            {"text": option.text, "voter_count": option.voter_count}
            for option in poll.options
        ],
        "total_voter_count": poll.total_voter_count,
        "is_closed": poll.is_closed,
        "is_anonymous": poll.is_anonymous,
        "type": poll.type,
        "allows_multiple_answers": poll.allows_multiple_answers,
    }
    for field in _POLL_FIELDS:
        value = getattr(poll, field, None)
        if value is None:
            continue
        data[field] = _iso(value) if isinstance(value, datetime) else value
    explanation_entities = _entities(getattr(poll, "explanation_entities", None))
    if explanation_entities:
        data["explanation_entities"] = explanation_entities
    return data
