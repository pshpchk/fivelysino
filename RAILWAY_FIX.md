# 🔧 Решение ошибки "No start command was found"

## ❌ Проблема
```
No start command was found
```

Railway не может определить, как запустить ваше приложение.

---

## ✅ Решения (в порядке предпочтения)

### Решение 1: Использовать Dockerfile (РЕКОМЕНДУЕТСЯ)

Railway автоматически обнаружит `Dockerfile` и использует его.

**Что делать:**
1. Убедитесь, что файл `Dockerfile` находится в корне проекта
2. Закоммитьте и запушьте:
```bash
git add Dockerfile .dockerignore
git commit -m "Add Dockerfile for Railway"
git push
```
3. Railway автоматически пересоберет проект

### Решение 2: Использовать nixpacks.toml

Если не хотите использовать Docker:

**Что делать:**
1. Убедитесь, что файл `nixpacks.toml` в корне проекта
2. Закоммитьте:
```bash
git add nixpacks.toml
git commit -m "Add nixpacks config"
git push
```

### Решение 3: Настроить через UI Railway

1. Откройте ваш проект в Railway
2. Перейдите в **Settings**
3. В разделе **Deploy** найдите **Start Command**
4. Введите:
```
python slot_machine_bot.py
```
5. Нажмите **Save**

### Решение 4: Использовать Procfile

Railway поддерживает Procfile (уже есть в проекте):

**Содержимое Procfile:**
```
worker: python slot_machine_bot.py
```

**Примечание:** Railway иногда игнорирует Procfile, поэтому лучше использовать Dockerfile.

---

## 🎯 Рекомендуемый порядок действий

### Шаг 1: Добавьте все файлы в Git

```bash
git add Dockerfile .dockerignore nixpacks.toml railway.json Procfile
git commit -m "Add deployment configs"
git push
```

### Шаг 2: Railway автоматически пересоберет

Railway обнаружит `Dockerfile` и использует его автоматически.

### Шаг 3: Проверьте логи

В Railway:
1. Откройте ваш проект
2. Перейдите во вкладку **Deployments**
3. Кликните на последний деплой
4. Проверьте логи

Вы должны увидеть:
```
🤖 Бот запущен!
📡 Подключение к Telegram...
```

---

## 📋 Checklist

- [ ] `Dockerfile` в корне проекта
- [ ] `.dockerignore` в корне проекта
- [ ] `requirements.txt` актуален
- [ ] Переменная `TELEGRAM_BOT_TOKEN` добавлена в Railway
- [ ] Все файлы закоммичены в Git
- [ ] Изменения запушены в GitHub

---

## 🐛 Если всё равно не работает

### Вариант 1: Проверьте структуру проекта

Убедитесь, что в корне есть:
```
.
├── Dockerfile              ← Должен быть!
├── slot_machine_bot.py     ← Должен быть!
├── requirements.txt        ← Должен быть!
├── config.py
└── .env (не коммитится)
```

### Вариант 2: Проверьте переменные окружения

В Railway → Settings → Variables:
```
TELEGRAM_BOT_TOKEN=ваш_токен
INITIAL_COINS=1000
BET_AMOUNT=10
```

### Вариант 3: Ручная команда запуска

В Railway → Settings → Deploy → Start Command:
```
python slot_machine_bot.py
```

### Вариант 4: Проверьте Python версию

В `nixpacks.toml` указана Python 3.10. Если нужна другая версия:

```toml
[phases.setup]
nixPkgs = ["python311"]  # или python39, python312
```

---

## 💡 Альтернатива: Render.com

Если Railway не работает, попробуйте Render:

1. Зайдите на [render.com](https://render.com)
2. **New** → **Web Service**
3. Подключите GitHub репозиторий
4. Настройки:
   - **Name:** fivelysino-bot
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python slot_machine_bot.py`
5. Добавьте переменную `TELEGRAM_BOT_TOKEN`
6. **Create Web Service**

---

## 🆘 Последняя надежда: Heroku

```bash
# Установите Heroku CLI
brew install heroku  # Mac
# или скачайте с heroku.com

# Логин
heroku login

# Создайте приложение
heroku create fivelysino-bot

# Добавьте токен
heroku config:set TELEGRAM_BOT_TOKEN=ваш_токен

# Деплой
git push heroku main

# Запустите worker
heroku ps:scale worker=1

# Проверьте логи
heroku logs --tail
```

---

**Удачи! Если нужна помощь - напишите!** 🚀
