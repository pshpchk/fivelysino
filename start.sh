#!/bin/bash

echo "🎰 Запуск FivelySino бота..."
echo ""

# Проверка наличия Python
if ! command -v python3 &> /dev/null
then
    echo "❌ Python3 не найден. Установите Python 3.8+ с https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Python найден: $(python3 --version)"
echo ""

# Создание виртуального окружения, если его нет
if [ ! -d "venv" ]; then
    echo "📦 Создаю виртуальное окружение..."
    python3 -m venv venv
    echo "✅ Виртуальное окружение создано"
    echo ""
fi

# Активация виртуального окружения
echo "🔧 Активирую виртуальное окружение..."
source venv/bin/activate

# Установка зависимостей
echo "📥 Устанавливаю зависимости..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Зависимости установлены"
    echo ""
else
    echo "❌ Ошибка при установке зависимостей"
    exit 1
fi

# Запуск бота
echo "🚀 Запускаю бота..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
python3 slot_machine_bot.py