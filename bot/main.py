import os
import logging
import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Базовая настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class NutritionBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

        self.db_path = '/opt/nutrition-bot/data/nutrition.db'
        self.init_db()

    def init_db(self):
        """Минимальная инициализация БД"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        conn = sqlite3.connect(self.db_path)
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
        logger.info("Database initialized")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Простая команда старт"""
        user = update.effective_user
        await update.message.reply_text(
            f'🍎 Привет, {user.first_name}!\n\n'
            'Я бот для учета питания. Просто присылай мне что ты съел.\n\n'
            'Примеры:\n'
            '• "Овсянка 150г"\n' 
            '• "300 ккал курица гречка"\n'
            '• "Завтрак: 2 яйца, тост"'
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Универсальный обработчик сообщений"""
        try:
            user_id = update.effective_user.id
            user_name = update.effective_user.first_name
            text = update.message.text

            # Сохраняем в базу
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO entries (user_id, user_name, message_text) VALUES (?, ?, ?)',
                (user_id, user_name, text)
            )
            conn.commit()
            conn.close()

            await update.message.reply_text('✅ Записал!')
            logger.info(f"User {user_name} added entry: {text}")

        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await update.message.reply_text('❌ Ошибка, попробуй еще раз')

    def run(self):
        """Запуск бота"""
        application = Application.builder().token(self.token).build()

        # Минимальные обработчики
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        logger.info("Bot starting...")
        application.run_polling()

if __name__ == '__main__':
    bot = NutritionBot()
    bot.run()
