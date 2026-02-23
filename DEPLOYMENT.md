# 🚀 Деплой FivelySino на Vercel

## ⚠️ Важное замечание

**Vercel не подходит для постоянно работающих ботов!** Vercel предназначен для serverless функций, которые работают по запросу. Для телеграм-ботов лучше использовать:

1. **Heroku** (бесплатный tier, поддерживает polling)
2. **Railway.app** (бесплатный tier)
3. **Render.com** (бесплатный tier)
4. **VPS** (DigitalOcean, AWS, etc.)

Но если вы хотите использовать Vercel, вот как это сделать:

---

## 📋 Что изменилось

### ✅ Переменные окружения

Теперь чувствительные данные не хранятся в коде:
- `TELEGRAM_BOT_TOKEN` - токен бота
- `INITIAL_COINS` - начальный баланс
- `BET_AMOUNT` - размер ставки

### ✅ Файловая структура

```
.
├── .env                    # Локальные переменные (не коммитить!)
├── .env.example           # Пример переменных
├── .gitignore             # Игнорируемые файлы
├── config.py              # Загрузка конфигурации
├── slot_machine_bot.py    # Основной бот (для локального запуска)
├── requirements.txt       # Зависимости Python
├── vercel.json           # Конфигурация Vercel
└── api/
    └── webhook.py        # Webhook handler для Vercel
```

---

## 🔧 Локальная разработка

### 1. Настройка переменных окружения

Скопируйте `.env.example` в `.env`:
```bash
cp .env.example .env
```

Откройте `.env` и добавьте свой токен:
```env
TELEGRAM_BOT_TOKEN=your_actual_token_here
INITIAL_COINS=1000
BET_AMOUNT=10
```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 3. Запуск локально

```bash
python slot_machine_bot.py
```

Или через скрипт:
```bash
./start.sh  # Mac/Linux
start.bat   # Windows
```

---

## 🌐 Деплой на Vercel (НЕ РЕКОМЕНДУЕТСЯ)

### Шаг 1: Установка Vercel CLI

```bash
npm install -g vercel
```

### Шаг 2: Логин в Vercel

```bash
vercel login
```

### Шаг 3: Деплой проекта

```bash
vercel
```

Следуйте инструкциям в терминале.

### Шаг 4: Настройка переменных окружения

В веб-интерфейсе Vercel:
1. Откройте ваш проект
2. Settings → Environment Variables
3. Добавьте:
   - `TELEGRAM_BOT_TOKEN` = ваш токен
   - `INITIAL_COINS` = 1000
   - `BET_AMOUNT` = 10

### Шаг 5: Настройка Webhook

После деплоя получите URL вашего приложения:
```
https://your-app.vercel.app
```

Установите webhook для бота:
```bash
curl -X POST https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook \
  -d "url=https://your-app.vercel.app/api/webhook"
```

Замените:
- `<YOUR_TOKEN>` - на ваш токен
- `your-app` - на имя вашего приложения

---

## ❌ Почему Vercel не идеален для ботов

1. **Serverless ограничения**
   - Функции запускаются только при запросе
   - Нет постоянного соединения
   - Холодный старт при каждом запросе

2. **База данных**
   - `user_data.json` не будет сохраняться между запросами
   - Нужна внешняя база данных (PostgreSQL, MongoDB Atlas)

3. **Таймауты**
   - Vercel ограничивает время выполнения функций
   - Анимации могут не работать корректно

---

## ✅ Рекомендуемые альтернативы

### 1. Railway.app (ЛУЧШИЙ ВАРИАНТ)

**Преимущества:**
- ✅ Бесплатный tier: 500 часов/месяц
- ✅ Поддержка постоянных процессов
- ✅ Встроенная PostgreSQL
- ✅ Простой деплой из GitHub

**Как задеплоить:**
```bash
# 1. Создайте аккаунт на railway.app
# 2. Подключите GitHub репозиторий
# 3. Добавьте переменные окружения
# 4. Railway автоматически задеплоит!
```

### 2. Render.com

**Преимущества:**
- ✅ Бесплатный tier
- ✅ Автоматический SSL
- ✅ Поддержка Docker

**Создайте `render.yaml`:**
```yaml
services:
  - type: web
    name: fivelysino-bot
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python slot_machine_bot.py
    envVars:
      - key: TELEGRAM_BOT_TOKEN
        sync: false
```

### 3. Heroku

**Преимущества:**
- ✅ Популярный, хорошая документация
- ✅ Много плагинов

**Создайте `Procfile`:**
```
worker: python slot_machine_bot.py
```

**Создайте `runtime.txt`:**
```
python-3.11.0
```

**Деплой:**
```bash
heroku login
heroku create fivelysino-bot
heroku config:set TELEGRAM_BOT_TOKEN=your_token
git push heroku main
heroku ps:scale worker=1
```

---

## 🗄️ База данных для продакшена

Для хранения данных пользователей используйте:

### Option 1: Supabase (PostgreSQL)
```bash
pip install supabase
```

### Option 2: MongoDB Atlas
```bash
pip install pymongo
```

### Option 3: Redis Cloud
```bash
pip install redis
```

Обновите код для работы с выбранной БД вместо `user_data.json`

---

## 📝 Checklist перед деплоем

- [ ] `.env` добавлен в `.gitignore`
- [ ] Все секреты в переменных окружения
- [ ] `requirements.txt` актуален
- [ ] База данных настроена (если не локальная)
- [ ] Протестировано локально
- [ ] Выбрана правильная платформа (не Vercel!)

---

## 🆘 Поддержка

Если нужна помощь с деплоем на другую платформу - дайте знать!

**Рекомендация:** Используйте **Railway.app** - это самый простой способ задеплоить телеграм-бота бесплатно с постоянной работой 24/7.
