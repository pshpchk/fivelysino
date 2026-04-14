import asyncio
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMemberAdministrator, ChatMemberOwner
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.constants import ParseMode, ChatType
from telegram.error import BadRequest, RetryAfter, NetworkError, TimedOut
import json
import os
import time

# Загрузка конфигурации из .env
try:
    from config import TELEGRAM_BOT_TOKEN, INITIAL_COINS, BET_AMOUNT
except ImportError:
    # Если config.py не найден, используем значения по умолчанию
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN')
    INITIAL_COINS = int(os.getenv('INITIAL_COINS', 1000))
    BET_AMOUNT = int(os.getenv('BET_AMOUNT', 10))

# Символы для слот-машины (можно заменить на кастомные изображения)
SYMBOLS = {
    'cherry': '🍒',
    'lemon': '🍋',
    'orange': '🍊',
    'watermelon': '🍉',
    'grape': '🍇',
    'seven': '7️⃣',
    'diamond': '💎',
    'star': '⭐'
}

# Опциональные Custom Emoji ID для Telegram.
# Чтобы включить кастомные эмодзи на барабанах, вставьте сюда emoji-id.
# Пример: 'cherry': '5368324170671202286'
CUSTOM_REEL_EMOJI_IDS = {
    'cherry': None,
    'lemon': None,
    'orange': None,
    'watermelon': None,
    'grape': None,
    'seven': None,
    'diamond': None,
    'star': None
}

# Настройки игры (загружаются из config.py или .env)
SPIN_ANIMATION_STEPS = 5  # Уменьшаем кадры чтобы избежать flood control

# Таблица выплат (множитель ставки)
PAYOUTS = {
    ('diamond', 'diamond', 'diamond'): 100,
    ('seven', 'seven', 'seven'): 50,
    ('star', 'star', 'star'): 30,
    ('watermelon', 'watermelon', 'watermelon'): 20,
    ('grape', 'grape', 'grape'): 15,
    ('orange', 'orange', 'orange'): 10,
    ('lemon', 'lemon', 'lemon'): 8,
    ('cherry', 'cherry', 'cherry'): 5,
}

# Вероятности выпадения символов
SYMBOL_WEIGHTS = {
    'cherry': 25,
    'lemon': 20,
    'orange': 18,
    'watermelon': 15,
    'grape': 10,
    'star': 7,
    'seven': 4,
    'diamond': 1
}

# Файл для хранения данных пользователей
USER_DATA_FILE = 'user_data.json'

def load_user_data():
    """Загрузка данных пользователей"""
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_user_data(data):
    """Сохранение данных пользователей"""
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_user_coins(user_id, user_name=None):
    """Получить баланс пользователя"""
    data = load_user_data()
    user_id_str = str(user_id)
    if user_id_str not in data:
        data[user_id_str] = {
            'coins': INITIAL_COINS, 
            'total_spins': 0, 
            'total_wins': 0,
            'username': user_name or 'Игрок'
        }
        save_user_data(data)
    elif user_name and 'username' not in data[user_id_str]:
        # Добавляем имя если его не было
        data[user_id_str]['username'] = user_name
        save_user_data(data)
    return data[user_id_str]['coins']

def update_user_coins(user_id, amount, is_win=False, user_name=None):
    """Обновить баланс пользователя"""
    data = load_user_data()
    user_id_str = str(user_id)
    if user_id_str not in data:
        data[user_id_str] = {
            'coins': INITIAL_COINS, 
            'total_spins': 0, 
            'total_wins': 0,
            'username': user_name or 'Игрок'
        }
    
    data[user_id_str]['coins'] += amount
    data[user_id_str]['total_spins'] += 1
    if is_win:
        data[user_id_str]['total_wins'] += 1
    
    # Обновляем имя пользователя если передано
    if user_name:
        data[user_id_str]['username'] = user_name
    
    save_user_data(data)
    return data[user_id_str]['coins']

def spin_reels():
    """Вращение барабанов - генерация случайных символов"""
    symbols_list = list(SYMBOLS.keys())
    weights = [SYMBOL_WEIGHTS[s] for s in symbols_list]
    
    result = random.choices(symbols_list, weights=weights, k=3)
    return result

def check_win(reels):
    """Проверка выигрыша"""
    reels_tuple = tuple(reels)
    if reels_tuple in PAYOUTS:
        return PAYOUTS[reels_tuple]
    
    # Проверка на два одинаковых символа (мини-выигрыш)
    if reels[0] == reels[1] or reels[1] == reels[2] or reels[0] == reels[2]:
        return 2  # Возврат ставки x2
    
    return 0

def format_reels(reels):
    """Форматирование барабанов для отображения"""
    return ' '.join([format_symbol(symbol) for symbol in reels])

def format_symbol(symbol):
    """Форматирование символа с поддержкой Telegram custom emoji"""
    custom_emoji_id = CUSTOM_REEL_EMOJI_IDS.get(symbol)
    if custom_emoji_id:
        return f'<tg-emoji emoji-id="{custom_emoji_id}"></tg-emoji>'
    return SYMBOLS[symbol]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    coins = get_user_coins(user_id, user_name)
    
    # Проверяем, это группа или личный чат
    is_group = update.effective_chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]
    
    keyboard = [
        [InlineKeyboardButton("🎰 Крутить барабаны", callback_data='spin')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if is_group:
        welcome_text = (
            f"🎰✨ <b>FivelySino запущен в группе!</b> ✨🎰\n\n"
            f"{'🎉' * 10}\n\n"
            f"Привет, <b>{user_name}</b>! 👋\n\n"
            f"💼 Твой баланс: <b>{coins} FivelyCoin</b>\n"
            f"💵 Ставка: <b>{BET_AMOUNT} FivelyCoin</b>\n\n"
            f"{'━' * 25}\n"
            f"🎲 Нажми кнопку и испытай удачу! 🍀\n"
            f"{'━' * 25}"
        )
    else:
        welcome_text = (
            f"🎰✨ <b>Добро пожаловать в FivelySino!</b> ✨🎰\n\n"
            f"{'🎉' * 10}\n\n"
            f"Привет, <b>{user_name}</b>! 🎊\n\n"
            f"💼 Стартовый баланс: <b>{coins} FivelyCoin</b>\n"
            f"💵 Ставка за вращение: <b>{BET_AMOUNT} FC</b>\n\n"
            f"{'━' * 25}\n"
            f"🏆 <b>Таблица выплат:</b> 🏆\n"
            f"{'━' * 25}\n\n"
            f"💎 💎 💎 = <b>x100</b> 🤑\n"
            f"7️⃣ 7️⃣ 7️⃣ = <b>x50</b> 💰\n"
            f"⭐ ⭐ ⭐ = <b>x30</b> ✨\n"
            f"🍉 🍉 🍉 = <b>x20</b> 🎯\n"
            f"🍇 🍇 🍇 = <b>x15</b> 🎪\n"
            f"🍊 🍊 🍊 = <b>x10</b> 🎨\n"
            f"🍋 🍋 🍋 = <b>x8</b> 🌈\n"
            f"🍒 🍒 🍒 = <b>x5</b> 🎵\n"
            f"Два одинаковых = <b>x2</b> 🎲\n\n"
            f"{'━' * 25}\n"
            f"🍀 Удачи! Начинай игру! 🎰\n"
            f"{'━' * 25}"
        )
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /balance - показать баланс и статистику"""
    user_id = update.effective_user.id
    data = load_user_data()
    user_data = data.get(str(user_id), {
        'coins': INITIAL_COINS,
        'total_spins': 0,
        'total_wins': 0
    })
    
    win_rate = (user_data['total_wins'] / user_data['total_spins'] * 100) if user_data['total_spins'] > 0 else 0
    
    stats_text = (
        f"💰 <b>Ваша статистика:</b>\n\n"
        f"💵 Баланс: <b>{user_data['coins']} FivelyCoin</b>\n"
        f"🎰 Всего вращений: {user_data['total_spins']}\n"
        f"🏆 Выигрышей: {user_data['total_wins']}\n"
        f"📊 Процент побед: {win_rate:.1f}%"
    )
    
    keyboard = [
        [InlineKeyboardButton("🎰 Крутить барабаны", callback_data='spin')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        stats_text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /leaderboard - показать топ игроков"""
    data = load_user_data()
    
    if not data:
        await update.message.reply_text(
            "📊 Пока никто не играл!\n"
            "Будь первым - нажми /start",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Сортируем игроков по балансу
    sorted_players = sorted(
        data.items(), 
        key=lambda x: x[1].get('coins', 0), 
        reverse=True
    )
    
    # Берём топ-10
    top_players = sorted_players[:10]
    
    # Формируем сообщение
    leaderboard_text = "🏆 <b>Топ игроков FivelySino</b> 🏆\n\n"
    
    medals = ["🥇", "🥈", "🥉"]
    
    for idx, (user_id, user_data) in enumerate(top_players, 1):
        username = user_data.get('username', 'Игрок')
        coins = user_data.get('coins', 0)
        total_spins = user_data.get('total_spins', 0)
        total_wins = user_data.get('total_wins', 0)
        win_rate = (total_wins / total_spins * 100) if total_spins > 0 else 0
        
        # Добавляем медали для топ-3
        medal = medals[idx-1] if idx <= 3 else f"{idx}."
        
        leaderboard_text += (
            f"{medal} <b>{username}</b>\n"
            f"   💰 {coins} FivelyCoin | "
            f"🎰 {total_spins} игр | "
            f"📊 {win_rate:.0f}% побед\n\n"
        )
    
    # Показываем позицию текущего игрока если он не в топе
    current_user_id = str(update.effective_user.id)
    current_user_position = None
    
    for idx, (user_id, _) in enumerate(sorted_players, 1):
        if user_id == current_user_id:
            current_user_position = idx
            break
    
    if current_user_position and current_user_position > 10:
        user_data = data[current_user_id]
        username = user_data.get('username', 'Вы')
        coins = user_data.get('coins', 0)
        leaderboard_text += (
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📍 <b>Ваша позиция: #{current_user_position}</b>\n"
            f"💰 {coins} FivelyCoin\n"
        )
    
    keyboard = [
        [InlineKeyboardButton("🎰 Играть", callback_data='spin')],
        [InlineKeyboardButton("📊 Моя статистика", callback_data='stats')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        leaderboard_text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )

async def spin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатия кнопки вращения"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    coins = get_user_coins(user_id, user_name)
    
    # Проверяем, это группа или личный чат
    is_group = update.effective_chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]
    player_prefix = f"Игрок: {user_name}\n" if is_group else ""
    
    # Проверка баланса
    if coins < BET_AMOUNT:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                f"{player_prefix}"
                f"😔 <b>Недостаточно монет!</b>\n\n"
                f"Баланс: {coins} FivelyCoin\n"
                f"Необходимо: {BET_AMOUNT} FivelyCoin\n\n"
                f"Пополнение отключено. Дождитесь пополнения от администратора."
            ),
            parse_mode=ParseMode.HTML
        )
        return
    
    # Списание ставки
    update_user_coins(user_id, -BET_AMOUNT, is_win=False, user_name=user_name)
    
    # Отправляем начальное сообщение с анимацией
    animation_text = (
        f"{player_prefix}"
        f"🎰✨ <b>FivelySino</b> ✨🎰\n\n"
        f"<code>══════════════════════\n"
        f"  💫 ПОДГОТОВКА... 💫  \n"
        f"══════════════════════\n\n"
        f"      ╔═══╦═══╦═══╗\n"
        f"      ║ 🎲 ║ 🎲 ║ 🎲 ║\n"
        f"      ╚═══╩═══╩═══╝\n\n"
        f"══════════════════════\n"
        f"  Ставка: {BET_AMOUNT} FC     \n"
        f"══════════════════════</code>"
    )
    spin_message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=animation_text,
        parse_mode=ParseMode.HTML
    )
    
    await asyncio.sleep(0.6)  # Увеличиваем задержку
    
    # Анимация вращения с одинаковыми размерами кадров
    spin_effects = ["💨 ВРАЩЕНИЕ 💨", "⚡ КРУТИМ! ⚡", "✨ УДАЧА... ✨", "💫 ИГРАЕМ! 💫", "🌟 ВПЕРЁД! 🌟"]
    
    for i in range(SPIN_ANIMATION_STEPS):
        random_reels = [random.choice(list(SYMBOLS.keys())) for _ in range(3)]
        effect = spin_effects[i % len(spin_effects)]
        
        # Все кадры с одинаковой структурой для плавности
        # Используем моноширинный шрифт <code> для стабильности
        frame = (
            f"{player_prefix}"
            f"🎰✨ <b>FivelySino</b> ✨🎰\n\n"
            f"<code>══════════════════════\n"
            f"    {effect}    \n"
            f"══════════════════════\n\n"
            f"      ╔═══╦═══╦═══╗\n"
            f"      ║ 🎲 ║ 🎲 ║ 🎲 ║\n"
            f"      ╚═══╩═══╩═══╝\n"
            f"        {format_reels(random_reels)}\n\n"
            f"══════════════════════\n"
            f"  {'⚡' * min(i + 1, 5)}{' ' * (10 - 2 * min(i + 1, 5))}\n"
            f"══════════════════════</code>"
        )
        
        try:
            await spin_message.edit_text(frame, parse_mode=ParseMode.HTML)
        except RetryAfter as e:
            # Если получили RetryAfter - ждём указанное время
            await asyncio.sleep(e.retry_after)
            try:
                await spin_message.edit_text(frame, parse_mode=ParseMode.HTML)
            except Exception:
                pass  # Если снова ошибка - пропускаем
        except Exception:
            pass  # Другие ошибки игнорируем
        
        await asyncio.sleep(0.5)  # Увеличиваем задержку чтобы избежать flood control
    
    # Финальный результат
    final_reels = spin_reels()
    multiplier = check_win(final_reels)
    
    # Сначала показываем драматическую паузу
    dramatic_text = (
        f"{player_prefix}"
        f"🎰✨ <b>FivelySino</b> ✨🎰\n\n"
        f"<code>══════════════════════\n"
        f"  ⏳ ОСТАНОВКА... ⏳   \n"
        f"══════════════════════\n\n"
        f"      ╔═══╦═══╦═══╗\n"
        f"      ║ ? ║ ? ║ ? ║\n"
        f"      ╚═══╩═══╩═══╝\n\n"
        f"══════════════════════\n"
        f"    🤞 Удача? 🤞     \n"
        f"══════════════════════</code>"
    )
    try:
        await spin_message.edit_text(dramatic_text, parse_mode=ParseMode.HTML)
    except RetryAfter as e:
        await asyncio.sleep(e.retry_after)
        try:
            await spin_message.edit_text(dramatic_text, parse_mode=ParseMode.HTML)
        except Exception:
            pass
    except Exception:
        pass  # Если ошибка - просто пропускаем
    
    await asyncio.sleep(1.0)  # Увеличиваем задержку
    
    if multiplier > 0:
        winnings = BET_AMOUNT * multiplier
        new_balance = update_user_coins(user_id, winnings, is_win=True, user_name=user_name)
        profit = winnings - BET_AMOUNT
        
        # Разные уровни празднования в зависимости от выигрыша
        if multiplier >= 50:
            celebration = "🎊🎉🎊🎉🎊🎉🎊🎉🎊"
            title = "💎 МЕГА ДЖЕКПОТ! 💎"
            emojis = "🏆✨🏆✨🏆✨🏆"
        elif multiplier >= 20:
            celebration = "🎉🎉🎉🎉🎉🎉🎉"
            title = "БОЛЬШОЙ ВЫИГРЫШ!"
            emoji_line = "💰💰💰💰💰"
        elif multiplier >= 10:
            celebration = "🎉🎉🎉🎉🎉"
            title = "ОТЛИЧНЫЙ ВЫИГРЫШ!"
            emoji_line = "💵💵💵💵💵"
        else:
            celebration = "🎉🎉🎉"
            title = "ВЫИГРЫШ!"
            emoji_line = "💸💸💸💸💸"
        
        result_text = (
            f"{player_prefix}"
            f"🎰✨ <b>FivelySino</b> ✨🎰\n\n"
            f"<code>══════════════════════\n"
            f"    {celebration}    \n"
            f"  {title}  \n"
            f"    {celebration}    \n"
            f"══════════════════════\n\n"
            f"      ╔═══╦═══╦═══╗\n"
            f"      ║ 🎰 ║ 🎰 ║ 🎰 ║\n"
            f"      ╚═══╩═══╩═══╝\n"
            f"        {format_reels(final_reels)}\n\n"
            f"══════════════════════</code>\n"
            f"💰 Множитель: <b>x{multiplier}</b>\n"
            f"💵 Выигрыш: <b>{winnings} FC</b>\n"
            f"📈 Прибыль: <b>+{profit} FC</b>\n"
            f"<code>══════════════════════</code>\n"
            f"💼 Баланс: <b>{new_balance} FC</b>\n"
            f"<code>══════════════════════</code>"
        )
    else:
        new_balance = get_user_coins(user_id, user_name)
        result_text = (
            f"{player_prefix}"
            f"🎰✨ <b>FivelySino</b> ✨🎰\n\n"
            f"<code>══════════════════════\n"
            f"   😔 НЕ ПОВЕЗЛО 😔   \n"
            f"══════════════════════\n\n"
            f"      ╔═══╦═══╦═══╗\n"
            f"      ║ 🎰 ║ 🎰 ║ 🎰 ║\n"
            f"      ╚═══╩═══╩═══╝\n"
            f"        {format_reels(final_reels)}\n\n"
            f"══════════════════════</code>\n"
            f"💔 Ничего не совпало\n"
            f"💸 Потеряно: <b>{BET_AMOUNT} FC</b>\n"
            f"<code>══════════════════════</code>\n"
            f"💼 Баланс: <b>{new_balance} FC</b>\n"
            f"<code>══════════════════════</code>\n\n"
            f"🍀 Попробуй еще! 🍀"
        )
    
    keyboard = [
        [InlineKeyboardButton("🎰 КРУТИТЬ СНОВА 🎰", callback_data='spin')],
        [InlineKeyboardButton("📊 МОЯ СТАТИСТИКА", callback_data='stats'),
         InlineKeyboardButton("🏆 ТОП ИГРОКОВ", callback_data='leaderboard')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await spin_message.edit_text(
            result_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    except RetryAfter as e:
        await asyncio.sleep(e.retry_after)
        try:
            await spin_message.edit_text(
                result_text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )
        except Exception:
            # Если снова не получилось, отправляем новое сообщение
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=result_text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )
    except Exception:
        # Если не получилось отредактировать, отправляем новое сообщение
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=result_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )

async def stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик показа статистики"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    data = load_user_data()
    user_data = data.get(str(user_id), {
        'coins': INITIAL_COINS,
        'total_spins': 0,
        'total_wins': 0
    })
    
    win_rate = (user_data['total_wins'] / user_data['total_spins'] * 100) if user_data['total_spins'] > 0 else 0
    
    stats_text = (
        f"📊 <b>Ваша статистика:</b>\n\n"
        f"💵 Баланс: <b>{user_data['coins']} FivelyCoin</b>\n"
        f"🎰 Всего вращений: {user_data['total_spins']}\n"
        f"🏆 Выигрышей: {user_data['total_wins']}\n"
        f"📈 Процент побед: {win_rate:.1f}%"
    )
    
    keyboard = [
        [InlineKeyboardButton("🎰 Крутить барабаны", callback_data='spin')],
        [InlineKeyboardButton("🏆 Топ игроков", callback_data='leaderboard')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=stats_text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )

async def leaderboard_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки топа игроков"""
    query = update.callback_query
    await query.answer()
    
    data = load_user_data()
    
    if not data:
        keyboard = [
            [InlineKeyboardButton("🎰 Крутить барабаны", callback_data='spin')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                "📊 Пока никто не играл!\n"
                "Будь первым!"
            ),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        return
    
    # Сортируем игроков по балансу
    sorted_players = sorted(
        data.items(), 
        key=lambda x: x[1].get('coins', 0), 
        reverse=True
    )
    
    # Берём топ-10
    top_players = sorted_players[:10]
    
    # Формируем сообщение
    leaderboard_text = "🏆 <b>Топ игроков FivelySino</b> 🏆\n\n"
    
    medals = ["🥇", "🥈", "🥉"]
    
    for idx, (user_id, user_data) in enumerate(top_players, 1):
        username = user_data.get('username', 'Игрок')
        coins = user_data.get('coins', 0)
        total_spins = user_data.get('total_spins', 0)
        total_wins = user_data.get('total_wins', 0)
        win_rate = (total_wins / total_spins * 100) if total_spins > 0 else 0
        
        # Добавляем медали для топ-3
        medal = medals[idx-1] if idx <= 3 else f"{idx}."
        
        leaderboard_text += (
            f"{medal} <b>{username}</b>\n"
            f"   💰 {coins} | 🎰 {total_spins} | 📊 {win_rate:.0f}%\n\n"
        )
    
    # Показываем позицию текущего игрока если он не в топе
    current_user_id = str(update.effective_user.id)
    current_user_position = None
    
    for idx, (user_id, _) in enumerate(sorted_players, 1):
        if user_id == current_user_id:
            current_user_position = idx
            break
    
    if current_user_position and current_user_position > 10:
        user_data = data[current_user_id]
        username = user_data.get('username', 'Вы')
        coins = user_data.get('coins', 0)
        leaderboard_text += (
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📍 <b>Ваша позиция: #{current_user_position}</b>\n"
            f"💰 {coins} FivelyCoin\n"
        )
    
    keyboard = [
        [InlineKeyboardButton("🎰 Играть", callback_data='spin')],
        [InlineKeyboardButton("📊 Моя статистика", callback_data='stats')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=leaderboard_text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )

def main():
    """Запуск бота"""
    # Проверяем наличие токена
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == 'YOUR_BOT_TOKEN':
        print("❌ Ошибка: TELEGRAM_BOT_TOKEN не настроен!")
        print("💡 Создайте файл .env и добавьте:")
        print("   TELEGRAM_BOT_TOKEN=ваш_токен_от_BotFather")
        return
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Регистрация обработчиков команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("leaderboard", leaderboard))
    application.add_handler(CommandHandler("top", leaderboard))  # Альтернативная команда
    
    # Регистрация обработчиков callback кнопок
    application.add_handler(CallbackQueryHandler(spin_handler, pattern='^spin$'))
    application.add_handler(CallbackQueryHandler(stats_handler, pattern='^stats$'))
    application.add_handler(CallbackQueryHandler(leaderboard_handler, pattern='^leaderboard$'))
    
    # Запуск бота с автоматическим переподключением
    print("🤖 Бот запущен!")
    print("📡 Подключение к Telegram...")
    
    retry_count = 0
    max_retries = 5
    
    while retry_count < max_retries:
        try:
            application.run_polling(allowed_updates=Update.ALL_TYPES)
            break  # Выходим из цикла если polling завершился нормально
        except KeyboardInterrupt:
            print("\n⛔ Остановка бота...")
            break
        except (NetworkError, TimedOut) as e:
            retry_count += 1
            print(f"\n❌ Ошибка сети ({retry_count}/{max_retries}): {e}")
            if retry_count < max_retries:
                wait_time = min(5 * retry_count, 30)  # Постепенно увеличиваем задержку
                print(f"🔄 Переподключение через {wait_time} секунд...")
                time.sleep(wait_time)
                print("📡 Попытка переподключения...")
            else:
                print("❌ Превышено максимальное количество попыток переподключения")
                print("💡 Проверьте интернет-соединение и попробуйте снова")
        except Exception as e:
            print(f"\n❌ Неожиданная ошибка: {e}")
            print("🔄 Перезапуск через 5 секунд...")
            time.sleep(5)
            retry_count = 0  # Сбрасываем счётчик для других типов ошибок

if __name__ == '__main__':
    # Исправление для Python 3.14
    import sys
    if sys.version_info >= (3, 14):
        import asyncio
        try:
            asyncio.get_event_loop()
        except RuntimeError:
            asyncio.set_event_loop(asyncio.new_event_loop())
    
    main()
