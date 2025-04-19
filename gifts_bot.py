from telethon import TelegramClient, events
import sqlite3
import random

# Конфиг Test DC (получи API на https://my.telegram.org/apps/test)
API_ID = 20594153  
API_HASH = "3b96d309703a9a58d6d8dc4b3eefdf12" 
BOT_TOKEN = "2200956077:AAHbKj_mTto6T7YSrzohuoVBi_44fhjvqAA"  

# Подключение к Test DC
bot = TelegramClient('gift_bot', API_ID, API_HASH, test_servers=True).start(bot_token=BOT_TOKEN)

# База данных для подарков и звёзд
conn = sqlite3.connect('gifts.db')
cursor = conn.cursor()

# Создаём таблицы
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    stars INTEGER DEFAULT 0
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS gifts (
    gift_id INTEGER PRIMARY KEY,
    name TEXT,
    cost INTEGER
)
''')

# Наполняем базу тестовыми подарками (если пусто)
cursor.execute("SELECT COUNT(*) FROM gifts")
if cursor.fetchone()[0] == 0:
    sample_gifts = [
        ("🎮 Игровая клавиатура", 50),
        ("📱 Чехол для телефона", 30),
        ("🎧 Наушники", 70),
        ("💻 Курс по Python", 100)
    ]
    cursor.executemany("INSERT INTO gifts (name, cost) VALUES (?, ?)", sample_gifts)
    conn.commit()

# Команда /start
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    user_id = event.sender_id
    cursor.execute("INSERT OR IGNORE INTO users (user_id, stars) VALUES (?, 100)", (user_id,))
    conn.commit()
    await event.reply(
        "🎁 **Магазин подарков**\n"
        f"У тебя: 100 ⭐\n\n"
        "Доступные команды:\n"
        "/gifts - Список подарков\n"
        "/buy [номер] - Купить подарок"
    )

# Команда /gifts
@bot.on(events.NewMessage(pattern='/gifts'))
async def list_gifts(event):
    cursor.execute("SELECT gift_id, name, cost FROM gifts")
    gifts = cursor.fetchall()
    
    response = "🎁 **Доступные подарки:**\n"
    for gift in gifts:
        response += f"{gift[0]}. {gift[1]} - {gift[2]} ⭐\n"
    
    await event.reply(response)

# Команда /buy
@bot.on(events.NewMessage(pattern='/buy (\d+)'))
async def buy_gift(event):
    user_id = event.sender_id
    gift_id = int(event.pattern_match.group(1))
    
    # Проверяем подарок
    cursor.execute("SELECT name, cost FROM gifts WHERE gift_id = ?", (gift_id,))
    gift = cursor.fetchone()
    
    if not gift:
        await event.reply("❌ Подарок не найден!")
        return
    
    gift_name, cost = gift
    
    # Проверяем баланс
    cursor.execute("SELECT stars FROM users WHERE user_id = ?", (user_id,))
    stars = cursor.fetchone()[0]
    
    if stars >= cost:
        cursor.execute("UPDATE users SET stars = stars - ? WHERE user_id = ?", (cost, user_id))
        conn.commit()
        await event.reply(
            f"🎉 Ты купил **{gift_name}** за {cost} ⭐!\n"
            f"Осталось: {stars - cost} ⭐"
        )
    else:
        await event.reply(f"❌ Недостаточно звёзд! Нужно {cost} ⭐")

bot.run_until_disconnected()