# JSON Help Bot

Telegram-бот на Python: превращает сообщения в сырой JSON Telegram-апдейта и собирает сообщения обратно из JSON. Работает с текстом и медиа.

## Возможности

- **Сообщение → JSON.** Бот возвращает исходный Telegram update в виде JSON: с `update_id`, `from`, `chat`, `date` (Unix timestamp), `forward_origin`, `forward_from`, `forward_date`, `entities` и остальными полями.
  Если JSON не помещается в сообщение (больше ~3500 символов), бот присылает файл `message_<id>.json`.
- **JSON → сообщение.** Принимает JSON update-а (с объектом `message`) или просто объект сообщения — текстом или файлом `.json`.
- **Медиа.** Фото, видео, анимации, аудио, голосовые, документы, стикеры и видеозаметки — через `file_id` из Telegram JSON или через прямой `url`.
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
│   │   ├── schema.py            # константы типов
│   │   ├── message_to_json.py   # Update/Message → dict
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

Тесты не ходят в сеть: проверяются сериализация апдейтов в raw JSON, сборка вызовов Bot API и парсинг JSON.

## Формат JSON

### Сообщение → JSON

Бот отдаёт ровно то, что прислал Telegram, без собственной схемы. Пример пересланного сообщения:

```json
{
  "update_id": 938481316,
  "message": {
    "message_id": 3174559,
    "from": {
      "id": 1356971297,
      "is_bot": false,
      "first_name": "BebruxX",
      "username": "reset_data",
      "language_code": "ru",
      "is_premium": true
    },
    "chat": {
      "id": 1356971297,
      "first_name": "BebruxX",
      "username": "reset_data",
      "type": "private"
    },
    "date": 1794260253,
    "forward_origin": {
      "type": "user",
      "sender_user": {
        "id": 8896893123,
        "is_bot": true,
        "first_name": "Miku",
        "username": "hatsunemiku_userbot"
      },
      "date": 1794259728
    },
    "forward_from": {
      "id": 8896893123,
      "is_bot": true,
      "first_name": "Miku",
      "username": "hatsunemiku_userbot"
    },
    "forward_date": 1794259728,
    "text": "Hello",
    "entities": [
      {
        "type": "custom_emoji",
        "offset": 0,
        "length": 5,
        "custom_emoji_id": "5192670170157423644"
      }
    ]
  }
}
```

Даты — Unix timestamp, как в Bot API. Поля со значением `null` не выводятся.

### JSON → сообщение

Можно отправить как полный update (бот возьмёт объект `message`), так и просто объект сообщения. Тип определяется по полям сообщения.

| Содержимое | Поле |
|---|---|
| Текст | `text` |
| Фото | `photo` — массив размеров, отправляется самый большой |
| Видео / анимация / аудио / голосовое / документ / стикер / видеозаметка | одноимённое поле |
| Геолокация | `location` |
| Место | `venue` |
| Контакт | `contact` |
| Опрос | `poll` |
| Кубик | `dice` |

Примеры:

```json
{"text": "Hello"}
```

```json
{
  "message": {
    "message_id": 10,
    "date": 1700000000,
    "chat": {"id": 1, "type": "private"},
    "from": {"id": 1, "is_bot": false, "first_name": "A"},
    "text": "Hello from an update"
  }
}
```

```json
{
  "photo": [
    {
      "file_id": "AgACAgIAAxkBAAI...",
      "file_unique_id": "AQAD...",
      "width": 1280,
      "height": 960
    }
  ],
  "caption": "Кот"
}
```

```json
{
  "photo": {"url": "https://example.com/cat.jpg"},
  "caption": "Кот из интернета"
}
```

```json
{
  "location": {"latitude": 55.7522, "longitude": 37.6156}
}
```

```json
{
  "poll": {
    "question": "Пойдём гулять?",
    "options": [{"text": "Да"}, {"text": "Нет"}],
    "is_anonymous": true,
    "allows_multiple_answers": false
  }
}
```

```json
{"dice": {"emoji": "🎲"}}
```

При отправке метаданные (`update_id`, `message_id`, `date`, `chat`, `from`, `forward_origin` и т.п.) не обязательны и не влияют на результат. Пересылка не восстанавливается как пересылка: содержимое отправляется обычным сообщением.

### Медиа и `file_id`

`file_id` из JSON действителен только для этого же бота. Если нужно отправить медиа «наружу»
или из другого бота, замените медиа-объект на `{"url": "https://..."}` с прямой ссылкой на файл.
Для фото можно заменить как весь массив, так и один из элементов на объект с `url`.

Скачивание исходного файла в боте не реализовано: бот отправляет медиа по `file_id`/`url` средствами Bot API.

## Команды

- `/start` — краткая инструкция.
- `/help` — подробная справка.
- `/json` — ответьте этой командой на любое сообщение, чтобы получить его raw JSON. Для ответа на сообщение `update_id` недоступен, поэтому выводится только объект сообщения.

## Ограничения

- Клавиатуры, инлайн-кнопки, реакции и служебные апдейты не переносятся.
- Пересылка отправляется как обычное сообщение (forward-поля не восстанавливаются).
- Кубик при отправке выпадает заново.
- Опрос создаётся заново: старые голоса и `is_closed` не переносятся; для викторины нужен `correct_option_id`.
- Медиа по `file_id` работает только в этом боте.
- Текст сообщения ограничен Telegram (4096 символов), поэтому длинный JSON приходит файлом.
- JSON-файл на вход — до 5 МБ, кодировка UTF-8.

## Лицензия

Учебный/внутренний проект, используйте как хотите.
