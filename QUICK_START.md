# 🚀 Быстрый запуск FivelySino бота

## Шаг 1: Установка Python
Убедись, что у тебя установлен Python 3.8+ 
Проверить: открой терминал/командную строку и набери:
```bash
python --version
```
или
```bash
python3 --version
```

Если Python не установлен, скачай с https://www.python.org/downloads/

## Шаг 2: Установка библиотеки

Открой терминал/командную строку в папке с файлами и выполни:

### Windows:
```bash
pip install python-telegram-bot
```

### Mac/Linux:
```bash
pip3 install python-telegram-bot --break-system-packages
```

или
```bash
pip3 install python-telegram-bot --user
```

## Шаг 3: Запуск бота

В той же папке выполни:

### Windows:
```bash
python slot_machine_bot.py
```

### Mac/Linux:
```bash
python3 slot_machine_bot.py
```

Если всё прошло успешно, увидишь:
```
🤖 Бот запущен!
```

## Шаг 4: Тестирование

1. Открой Telegram
2. Найди своего бота (имя которое дал при создании)
3. Нажми START или напиши `/start`
4. Играй! 🎰

## 🐛 Если что-то пошло не так

### Ошибка "No module named 'telegram'"
Значит библиотека не установилась. Попробуй:
```bash
pip install python-telegram-bot --user
```

### Ошибка с SSL/сертификатами (Mac)
```bash
pip3 install python-telegram-bot certifi
```

### Бот не отвечает
- Проверь интернет-соединение
- Проверь что токен правильный
- Убедись что скрипт запущен (в терминале должно быть "Бот запущен!")

## 💡 Полезные команды в боте

- `/start` - начать игру
- `/balance` - посмотреть баланс и статистику  
- `/addcoins` - добавить монеты для теста

---

**Важно:** Не останавливай скрипт (не закрывай терминал), пока хочешь чтобы бот работал!

Для остановки нажми `Ctrl+C` в терминале.
