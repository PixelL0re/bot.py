from telethon import TelegramClient, events
import sqlite3

# Настройки
API_ID = 20594153
API_HASH = "3b96d309703a9a58d6d8dc4b3eefdf12"
BOT_TOKEN = "2200956077:AAHbKj_mTto6T7YSrzohuoVBi_44fhjvqAA" 

# Подключение к боту
bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# База данных для хранения "проданных" товаров
conn = sqlite3.connect('gifts.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS gifts (
    id INTEGER PRIMARY KEY,
    name TEXT,
    price INTEGER,
    buyer_id INTEGER
)''')
conn.commit()

# Команда /start
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply('🎁 Бот для раздачи подарков!\n\n'
                    'Используй /gift чтобы получить подарок за звёзды!')

# Команда /gift (получить подарок)
@bot.on(events.NewMessage(pattern='/gift'))
async def gift(event):
    user_id = event.sender_id
    cursor.execute("SELECT * FROM gifts WHERE buyer_id IS NULL LIMIT 1")
    gift_data = cursor.fetchone()

    if gift_data:
        gift_id, name, price, _ = gift_data
        cursor.execute("UPDATE gifts SET buyer_id = ? WHERE id = ?", (user_id, gift_id))
        conn.commit()
        await event.reply(f'🎉 Ты получил подарок: **{name}** (стоимость: {price} ⭐)')
    else:
        await event.reply('😔 Подарки закончились!')

# Запуск бота
print("Бот запущен!")
bot.run_until_disconnected()