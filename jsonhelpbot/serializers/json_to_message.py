from __future__ import annotations

from typing import Any

from aiogram import Bot
from aiogram.types import InputPollOption, MessageEntity, ReplyParameters

from jsonhelpbot.serializers.schema import EXTRA_KEYS, MEDIA_METHODS


class PayloadError(ValueError):
    pass


_MEDIA_EXTRA_FIELDS = {
    "photo": (),
    "video": ("width", "height", "duration"),
    "animation": ("width", "height", "duration"),
    "audio": ("duration", "performer", "title"),
    "voice": ("duration",),
    "document": (),
    "sticker": ("emoji",),
    "video_note": ("length", "duration"),
}


def build_send_call(payload: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    message = extract_message(payload)
    message_type = detect_type(message)
    if message_type == "text":
        return _text_call(message)
    if message_type in MEDIA_METHODS:
        return _media_call(message_type, message)
    if message_type == "location":
        return _location_call(message)
    if message_type == "venue":
        return _venue_call(message)
    if message_type == "contact":
        return _contact_call(message)
    if message_type == "poll":
        return _poll_call(message)
    if message_type == "dice":
        return _dice_call(message)
    raise PayloadError("The message does not contain supported content")


async def send_from_json(
    bot: Bot,
    chat_id: int,
    payload: dict[str, Any],
    reply_to_message_id: int | None = None,
) -> None:
    method_name, kwargs = build_send_call(payload)
    if reply_to_message_id is not None:
        kwargs["reply_parameters"] = ReplyParameters(message_id=reply_to_message_id)
    method = getattr(bot, method_name)
    await method(chat_id=chat_id, **kwargs)


def extract_message(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise PayloadError("JSON payload must be an object")
    wrapped = payload.get("message")
    if isinstance(wrapped, dict):
        return wrapped
    if "update_id" in payload:
        raise PayloadError("The update does not contain a 'message' object")
    return payload


def detect_type(message: dict[str, Any]) -> str | None:
    if isinstance(message.get("text"), str):
        return "text"
    for key in MEDIA_METHODS:
        if key in message:
            return key
    for key in EXTRA_KEYS:
        if key in message:
            return key
    return None


def _text_call(message: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    text = message.get("text")
    if not isinstance(text, str) or not text:
        raise PayloadError("The message has no 'text'")
    kwargs: dict[str, Any] = {"text": text}
    entities = _entities(message.get("entities"))
    if entities:
        kwargs["entities"] = entities
    return "send_message", kwargs


def _media_call(
    message_type: str,
    message: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    media = message.get(message_type)
    source = _find_source(media)
    if source is None:
        raise PayloadError(f"'{message_type}' does not contain 'file_id' or 'url'")
    kwargs: dict[str, Any] = {message_type: source}
    caption = message.get("caption")
    if isinstance(caption, str) and caption:
        kwargs["caption"] = caption
        caption_entities = _entities(message.get("caption_entities"))
        if caption_entities:
            kwargs["caption_entities"] = caption_entities
    extra = _extra_media_data(media)
    for field in _MEDIA_EXTRA_FIELDS[message_type]:
        value = extra.get(field)
        if isinstance(value, str) and value:
            kwargs[field] = value
        elif isinstance(value, int) and not isinstance(value, bool):
            kwargs[field] = value
    return MEDIA_METHODS[message_type], kwargs


def _location_call(message: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    location = message.get("location")
    if not isinstance(location, dict):
        raise PayloadError("The message has no 'location' object")
    latitude, longitude = _coordinates(location)
    kwargs: dict[str, Any] = {"latitude": latitude, "longitude": longitude}
    if _is_number(location.get("horizontal_accuracy")):
        kwargs["horizontal_accuracy"] = location["horizontal_accuracy"]
    for field in ("live_period", "heading", "proximity_alert_radius"):
        value = location.get(field)
        if isinstance(value, int) and not isinstance(value, bool):
            kwargs[field] = value
    return "send_location", kwargs


def _venue_call(message: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    venue = message.get("venue")
    if not isinstance(venue, dict):
        raise PayloadError("The message has no 'venue' object")
    location = venue.get("location")
    if not isinstance(location, dict):
        raise PayloadError("'venue' must contain a 'location' object")
    latitude, longitude = _coordinates(location)
    title = venue.get("title")
    address = venue.get("address")
    if not isinstance(title, str) or not title:
        raise PayloadError("'venue' requires a non-empty 'title' field")
    if not isinstance(address, str) or not address:
        raise PayloadError("'venue' requires a non-empty 'address' field")
    kwargs: dict[str, Any] = {
        "latitude": latitude,
        "longitude": longitude,
        "title": title,
        "address": address,
    }
    for field in (
        "foursquare_id",
        "foursquare_type",
        "google_place_id",
        "google_place_type",
    ):
        value = venue.get(field)
        if isinstance(value, str) and value:
            kwargs[field] = value
    return "send_venue", kwargs


def _contact_call(message: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    contact = message.get("contact")
    if not isinstance(contact, dict):
        raise PayloadError("The message has no 'contact' object")
    phone_number = contact.get("phone_number")
    first_name = contact.get("first_name")
    if not isinstance(phone_number, str) or not phone_number:
        raise PayloadError("'contact' requires a non-empty 'phone_number' field")
    if not isinstance(first_name, str) or not first_name:
        raise PayloadError("'contact' requires a non-empty 'first_name' field")
    kwargs: dict[str, Any] = {
        "phone_number": phone_number,
        "first_name": first_name,
    }
    for field in ("last_name", "vcard"):
        value = contact.get(field)
        if isinstance(value, str) and value:
            kwargs[field] = value
    return "send_contact", kwargs


def _poll_call(message: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    poll = message.get("poll")
    if not isinstance(poll, dict):
        raise PayloadError("The message has no 'poll' object")
    question = poll.get("question")
    if not isinstance(question, str) or not question:
        raise PayloadError("'poll' requires a non-empty 'question' field")
    raw_options = poll.get("options")
    if not isinstance(raw_options, list):
        raise PayloadError("'poll' requires an 'options' array")
    options: list[InputPollOption] = []
    for option in raw_options:
        text = option.get("text") if isinstance(option, dict) else option
        if isinstance(text, str) and text:
            options.append(InputPollOption(text=text))
    if len(options) < 2:
        raise PayloadError("A poll must have at least two options")
    kwargs: dict[str, Any] = {"question": question, "options": options}
    poll_type = poll.get("type")
    if poll_type in ("quiz", "regular"):
        kwargs["type"] = poll_type
    for field in ("is_anonymous", "allows_multiple_answers"):
        value = poll.get(field)
        if isinstance(value, bool):
            kwargs[field] = value
    correct_option_id = poll.get("correct_option_id")
    if isinstance(correct_option_id, int) and not isinstance(correct_option_id, bool):
        kwargs["correct_option_id"] = correct_option_id
    explanation = poll.get("explanation")
    if isinstance(explanation, str) and explanation:
        kwargs["explanation"] = explanation
    explanation_entities = _entities(poll.get("explanation_entities"))
    if explanation_entities:
        kwargs["explanation_entities"] = explanation_entities
    open_period = poll.get("open_period")
    if isinstance(open_period, int) and not isinstance(open_period, bool):
        kwargs["open_period"] = open_period
    return "send_poll", kwargs


def _dice_call(message: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    dice = message.get("dice")
    kwargs: dict[str, Any] = {}
    if isinstance(dice, dict):
        emoji = dice.get("emoji")
        if isinstance(emoji, str) and emoji:
            kwargs["emoji"] = emoji
    return "send_dice", kwargs


def _find_source(media: Any) -> str | None:
    if isinstance(media, str):
        return media or None
    if isinstance(media, dict):
        source = media.get("url") or media.get("file_id")
        if isinstance(source, str) and source:
            return source
        return None
    if isinstance(media, list):
        for item in reversed(media):
            source = _find_source(item)
            if source is not None:
                return source
    return None


def _extra_media_data(media: Any) -> dict[str, Any]:
    if isinstance(media, list) and media:
        media = media[-1]
    return media if isinstance(media, dict) else {}


def _entities(raw: Any) -> list[MessageEntity] | None:
    if not isinstance(raw, list):
        return None
    entities: list[MessageEntity] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        data: dict[str, Any] = {
            "type": item.get("type"),
            "offset": item.get("offset"),
            "length": item.get("length"),
        }
        for field in ("url", "language", "custom_emoji_id"):
            if item.get(field) is not None:
                data[field] = item[field]
        if isinstance(item.get("user"), dict):
            data["user"] = item["user"]
        try:
            entities.append(MessageEntity(**data))
        except ValueError:
            continue
    return entities or None


def _coordinates(location: dict[str, Any]) -> tuple[float, float]:
    latitude = location.get("latitude")
    longitude = location.get("longitude")
    if not _is_number(latitude) or not _is_number(longitude):
        raise PayloadError("'latitude' and 'longitude' must be numbers")
    return float(latitude), float(longitude)


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)
