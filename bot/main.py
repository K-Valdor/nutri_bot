import os
import logging
import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Конфигурация из env переменных
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
DB_PATH = os.getenv('DB_PATH', '/opt/nutrition-bot/data/nutrition.db')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, LOG_LEVEL)
)
logger = logging.getLogger(__name__)

def init_db():
    """Инициализация базы данных"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            user_name TEXT,
            message_text TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f'🍎 Привет, {user.first_name}!\n\n'
        'Я бот для учета питания. Просто присылай мне что ты съел.'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        text = update.message.text
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO entries (user_id, user_name, message_text) VALUES (?, ?, ?)',
            (user_id, user_name, text)
        )
        conn.commit()
        conn.close()
        
        await update.message.reply_text('✅ Записал!')
        logger.info(f"User {user_name} added: {text}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text('❌ Ошибка')

def main():
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set")
        return
    
    init_db()
    
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Bot starting...")
    application.run_polling()

if __name__ == '__main__':
    main()