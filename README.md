# 🎰 FivelySino - Telegram Casino Bot

Телеграм-бот для игры в однорукий бандит с виртуальной валютой FivelyCoin.

## ✨ Возможности

- 🎰 Классический слот с 3 барабанами
- 💰 Виртуальная валюта FivelyCoin
- 🏆 Топ игроков и статистика
- 🎨 Яркая анимация
- 👥 Работа в личных сообщениях и группах
- 📊 Таблица лидеров

## 🚀 Быстрый старт

### Локальный запуск

1. **Клонируйте репозиторий**
```bash
git clone <your-repo-url>
cd fivelysino
```

2. **Создайте .env файл**
```bash
cp .env.example .env
```

Отредактируйте `.env` и добавьте свой токен от @BotFather:
```env
TELEGRAM_BOT_TOKEN=your_token_here
```

3. **Запустите бота**
```bash
# Mac/Linux
./start.sh

# Windows
start.bat

# Или напрямую
python slot_machine_bot.py
```

## 📦 Установка зависимостей

```bash
pip install -r requirements.txt
```

## 🌐 Деплой

### Railway.app (Рекомендуется)

1. Создайте аккаунт на [railway.app](https://railway.app)
2. Подключите GitHub репозиторий
3. Добавьте переменную окружения `TELEGRAM_BOT_TOKEN`
4. Railway автоматически задеплоит бота!

Подробнее: [DEPLOYMENT.md](DEPLOYMENT.md)

## 📝 Переменные окружения

| Переменная | Описание | По умолчанию |
|-----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Токен бота от @BotFather | - |
| `INITIAL_COINS` | Стартовый баланс | 1000 |
| `BET_AMOUNT` | Размер ставки | 10 |

## 🎮 Команды бота

- `/start` - Начать игру
- `/balance` - Баланс и статистика
- `/leaderboard` или `/top` - Топ игроков
- `/addcoins` - Добавить монеты (тестирование)

## 🏗️ Структура проекта

```
.
├── slot_machine_bot.py    # Основной код бота
├── config.py              # Конфигурация из .env
├── .env                   # Переменные окружения (не коммитить!)
├── .env.example          # Пример переменных
├── requirements.txt       # Python зависимости
├── Procfile              # Для Railway/Heroku
├── railway.json          # Конфигурация Railway
└── user_data.json        # База данных игроков (создается автоматически)
```

## 🎨 Кастомизация

Отредактируйте `slot_machine_bot.py` для изменения:
- Символов на барабанах
- Вероятностей выпадения
- Таблицы выплат
- Анимации

Или измените настройки в `.env`:
```env
INITIAL_COINS=2000
BET_AMOUNT=20
```

## 🛠️ Технологии

- Python 3.8+
- python-telegram-bot 21.0+
- python-dotenv

## 📄 Лицензия

MIT License - свободное использование

## 🤝 Поддержка

Если возникли проблемы:
- [Сетевые проблемы](NETWORK_TROUBLESHOOTING.md)
- [Деплой](DEPLOYMENT.md)
- [Настройка групп](GROUP_SETUP.md)

---

**Удачной игры! 🎰💰**
