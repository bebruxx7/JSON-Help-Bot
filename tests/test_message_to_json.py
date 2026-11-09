from __future__ import annotations

from aiogram.types import (
    Audio,
    Contact,
    Dice,
    Document,
    Location,
    MessageEntity,
    PhotoSize,
    Poll,
    PollOption,
    Sticker,
    Venue,
    Video,
    Voice,
)

from jsonhelpbot.serializers.message_to_json import message_to_dict
from tests.factories import make_message


def test_text_message():
    message = make_message(
        text="Hello world",
        entities=[MessageEntity(type="bold", offset=0, length=5)],
    )

    payload = message_to_dict(message)

    assert payload["schema"] == 1
    assert payload["type"] == "text"
    assert payload["message_id"] == 1
    assert payload["date"] == "2024-01-01T12:00:00+00:00"
    assert payload["text"] == "Hello world"
    assert payload["entities"] == [{"type": "bold", "offset": 0, "length": 5}]
    assert payload["from"]["id"] == 100
    assert payload["from"]["is_bot"] is False
    assert payload["from"]["username"] == "tester"
    assert payload["chat"] == {"id": 100, "type": "private", "first_name": "Tester"}


def test_photo_uses_largest_size():
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

    assert payload["type"] == "photo"
    assert payload["caption"] == "A cat"
    assert payload["caption_entities"] == [
        {"type": "italic", "offset": 0, "length": 5}
    ]
    assert payload["media"] == {
        "file_id": "large",
        "file_unique_id": "large-u",
        "file_size": 1234,
        "width": 800,
        "height": 600,
    }


def test_video_media():
    message = make_message(
        video=Video(
            file_id="video-id",
            file_unique_id="video-u",
            width=1920,
            height=1080,
            duration=30,
            file_name="clip.mp4",
            mime_type="video/mp4",
            file_size=999,
        )
    )

    media = message_to_dict(message)["media"]

    assert media["file_id"] == "video-id"
    assert media["file_name"] == "clip.mp4"
    assert media["duration"] == 30
    assert media["width"] == 1920


def test_audio_media():
    message = make_message(
        audio=Audio(
            file_id="audio-id",
            file_unique_id="audio-u",
            duration=180,
            performer="Artist",
            title="Song",
            file_name="song.mp3",
            mime_type="audio/mpeg",
            file_size=555,
        )
    )

    payload = message_to_dict(message)

    assert payload["type"] == "audio"
    assert payload["media"]["performer"] == "Artist"
    assert payload["media"]["title"] == "Song"
    assert payload["media"]["duration"] == 180


def test_voice_media():
    message = make_message(
        voice=Voice(
            file_id="voice-id",
            file_unique_id="voice-u",
            duration=7,
            mime_type="audio/ogg",
            file_size=321,
        )
    )

    media = message_to_dict(message)["media"]

    assert media["file_id"] == "voice-id"
    assert media["duration"] == 7


def test_document_media():
    message = make_message(
        document=Document(
            file_id="doc-id",
            file_unique_id="doc-u",
            file_name="data.json",
            mime_type="application/json",
            file_size=42,
        )
    )

    payload = message_to_dict(message)

    assert payload["type"] == "document"
    assert payload["media"]["file_name"] == "data.json"
    assert payload["media"]["mime_type"] == "application/json"


def test_sticker_media():
    message = make_message(
        sticker=Sticker(
            file_id="sticker-id",
            file_unique_id="sticker-u",
            type="regular",
            width=512,
            height=512,
            is_animated=False,
            is_video=False,
            emoji="🙂",
            set_name="test_set",
        )
    )

    media = message_to_dict(message)["media"]

    assert media["emoji"] == "🙂"
    assert media["set_name"] == "test_set"
    assert media["is_animated"] is False


def test_location():
    message = make_message(
        location=Location(latitude=55.7522, longitude=37.6156, horizontal_accuracy=12.5)
    )

    payload = message_to_dict(message)

    assert payload["type"] == "location"
    assert payload["location"] == {
        "latitude": 55.7522,
        "longitude": 37.6156,
        "horizontal_accuracy": 12.5,
    }


def test_venue():
    message = make_message(
        venue=Venue(
            location=Location(latitude=55.7539, longitude=37.6208),
            title="Red Square",
            address="Moscow",
        )
    )

    venue = message_to_dict(message)["venue"]

    assert venue["title"] == "Red Square"
    assert venue["address"] == "Moscow"
    assert venue["location"]["latitude"] == 55.7539


def test_contact():
    message = make_message(
        contact=Contact(
            phone_number="+15550000000",
            first_name="Ivan",
            last_name="Petrov",
        )
    )

    contact = message_to_dict(message)["contact"]

    assert contact["phone_number"] == "+15550000000"
    assert contact["first_name"] == "Ivan"
    assert contact["last_name"] == "Petrov"


def test_poll():
    message = make_message(
        poll=Poll(
            id="poll-1",
            question="Walk?",
            options=[
                PollOption(text="Yes", voter_count=1, persistent_id="yes"),
                PollOption(text="No", voter_count=2, persistent_id="no"),
            ],
            total_voter_count=3,
            is_closed=False,
            is_anonymous=True,
            type="regular",
            allows_multiple_answers=False,
            allows_revoting=False,
            members_only=False,
        )
    )

    poll = message_to_dict(message)["poll"]

    assert poll["question"] == "Walk?"
    assert poll["options"] == [
        {"text": "Yes", "voter_count": 1},
        {"text": "No", "voter_count": 2},
    ]
    assert poll["type"] == "regular"
    assert poll["is_anonymous"] is True


def test_dice():
    message = make_message(dice=Dice(emoji="🎲", value=4))

    payload = message_to_dict(message)

    assert payload["type"] == "dice"
    assert payload["dice"] == {"emoji": "🎲", "value": 4}
