import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Конфигурация из .env
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
INITIAL_COINS = int(os.getenv('INITIAL_COINS', 1000))
BET_AMOUNT = int(os.getenv('BET_AMOUNT', 10))
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

# Валидация
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN не найден! Проверьте .env файл")

print("✅ Конфигурация загружена:")
print(f"   - Токен бота: {'*' * 20}{TELEGRAM_BOT_TOKEN[-4:]}")
print(f"   - Начальные монеты: {INITIAL_COINS}")
print(f"   - Ставка: {BET_AMOUNT}")
print(f"   - Окружение: {ENVIRONMENT}")
