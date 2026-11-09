# JSON Help Bot

Telegram-бот на Python: превращает сообщения в JSON и собирает сообщения обратно из JSON. Работает с текстом и медиа.

## Возможности

- **Сообщение → JSON.** Любое поддерживаемое сообщение бот возвращает в виде JSON.
  Если JSON не помещается в сообщение (больше ~3500 символов), бот присылает файл `message_<id>.json`.
- **JSON → сообщение.** JSON можно отправить текстом или файлом `.json` — бот пришлёт собранное сообщение.
- **Медиа.** Фото, видео, анимации, аудио, голосовые, документы, стикеры и видеозаметки — через `file_id` или `url`.
- **Разные типы.** Текст, геолокация, место (venue), контакт, опрос, кубик.
- **Команды.** `/start`, `/help`, `/json` (JSON сообщения, на которое ответили).

## Структура проекта

```
jsonhelpbot/
├── jsonhelpbot/
│   ├── __main__.py              # python -m jsonhelpbot
│   ├── main.py                  # создание бота и polling
│   ├── config.py                # чтение BOT_TOKEN из .env
│   ├── texts.py                 # тексты /start и /help
│   ├── handlers/
│   │   ├── common.py            # команды
│   │   └── convert.py           # маршрутизация сообщение ↔ JSON
│   ├── serializers/
│   │   ├── schema.py            # константы формата
│   │   ├── message_to_json.py   # Message → dict
│   │   └── json_to_message.py   # dict → вызов Bot API
│   └── utils/
│       ├── json_tools.py        # парсинг и дамп JSON
│       └── replies.py           # ответ JSON-ом (текст или файл)
├── tests/                       # pytest
├── .env.example
├── requirements.txt
├── requirements-dev.txt
└── pyproject.toml
```

## Быстрый старт

Нужен Python 3.10+ (проверено на 3.12).

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
Copy-Item .env.example .env
notepad .env
```

Впишите в `.env` токен от [@BotFather](https://t.me/BotFather):

```
BOT_TOKEN=123456789:AA...
```

Запуск:

```powershell
python -m jsonhelpbot
```

## Тесты

```powershell
pytest
```

Тесты не ходят в сеть: проверяются сериализация сообщений, сборка вызовов Bot API и парсинг JSON.

## Формат JSON

### Сообщение → JSON

Пример текстового сообщения:

```json
{
  "schema": 1,
  "type": "text",
  "message_id": 15,
  "date": "2026-11-09T12:00:00+00:00",
  "from": {
    "id": 123456789,
    "is_bot": false,
    "first_name": "Иван",
    "username": "ivan"
  },
  "chat": {
    "id": 123456789,
    "type": "private",
    "first_name": "Иван"
  },
  "text": "Привет",
  "entities": [
    {"type": "bold", "offset": 0, "length": 6}
  ]
}
```

Пример фото:

```json
{
  "schema": 1,
  "type": "photo",
  "message_id": 16,
  "date": "2026-11-09T12:01:00+00:00",
  "chat": {"id": 123456789, "type": "private"},
  "caption": "Кот",
  "caption_entities": [
    {"type": "bold", "offset": 0, "length": 3}
  ],
  "media": {
    "file_id": "AgACAgIAAxkBAAI...",
    "file_unique_id": "AQAD...",
    "width": 1280,
    "height": 960,
    "file_size": 123456
  }
}
```

Поля `schema`, `message_id`, `date`, `from`, `chat`, `edit_date`, `reply_to_message_id` — справочные. При сборке сообщения из JSON они не обязательны.

### JSON → сообщение

Обязательно нужен `type` и данные конкретного типа. Все лишние поля игнорируются.

| `type` | Обязательные поля |
|---|---|
| `text` | `text` |
| `photo`, `video`, `animation`, `audio`, `voice`, `document`, `sticker`, `video_note` | `media.file_id` или `media.url`; `caption` — по желанию |
| `location` | `location.latitude`, `location.longitude` |
| `venue` | `venue.title`, `venue.address`, `venue.location.latitude`, `venue.location.longitude` |
| `contact` | `contact.phone_number`, `contact.first_name` |
| `poll` | `poll.question`, `poll.options` (от 2 вариантов) |
| `dice` | ничего: `dice.emoji` — по желанию |

Примеры:

```json
{"type": "text", "text": "Привет"}
```

```json
{
  "type": "photo",
  "caption": "Кот из интернета",
  "media": {"url": "https://example.com/cat.jpg"}
}
```

```json
{
  "type": "photo",
  "caption": "Подпись",
  "media": {"file_id": "AgACAgIAAxkBAAI..."}
}
```

```json
{
  "type": "location",
  "location": {"latitude": 55.7522, "longitude": 37.6156}
}
```

```json
{
  "type": "poll",
  "poll": {
    "question": "Пойдём гулять?",
    "options": [{"text": "Да"}, {"text": "Нет"}],
    "is_anonymous": true,
    "allows_multiple_answers": false
  }
}
```

```json
{"type": "dice", "dice": {"emoji": "🎲"}}
```

### Медиа и `file_id`

`file_id` из JSON действителен только для этого же бота. Если нужно отправить медиа «наружу»
или из другого бота, используйте `media.url` с прямой ссылкой на файл.

Скачивание исходного файла в боте не реализовано: бот пересылает медиа по `file_id`/`url` средствами Bot API.

## Команды

- `/start` — краткая инструкция.
- `/help` — подробная справка.
- `/json` — ответьте этой командой на любое сообщение, чтобы получить его JSON.

## Ограничения

- Клавиатуры, инлайн-кнопки, реакции и forwarded-метаданные не переносятся.
- Кубик при отправке выпадает заново.
- Опрос создаётся заново: старые голоса и `is_closed` не переносятся; для викторины нужен `correct_option_id`.
- Медиа по `file_id` работает только в этом боте.
- Текст сообщения ограничен Telegram (4096 символов), поэтому длинный JSON приходит файлом.
- JSON-файл на вход — до 5 МБ, кодировка UTF-8.

## Лицензия

Учебный/внутренний проект, используйте как хотите.
