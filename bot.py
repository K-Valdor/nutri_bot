import logging
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from config import config
from database import Database

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class NutritionBot:
    def __init__(self):
        config.validate()
        self.db = Database(config.database_url)
        self.application = Application.builder().token(config.telegram_token).build()
        self._setup_handlers()

    def _setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self._start))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))

    async def _start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("📊 Бот для учёта питания")

    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != config.admin_user_id:
            await update.message.reply_text("⛔ Нет доступа")
            return

        meal_data = self._parse_nutrition_data(update.message.text)
        if not meal_data:
            await update.message.reply_text("❌ Не распознано")
            return

        try:
            meal_id = self.db.save_meal(meal_data)
            await update.message.reply_text(f"✅ Сохранено! ID: {meal_id}")
        except Exception as e:
            await update.message.reply_text("❌ Ошибка сохранения")

    def _parse_nutrition_data(self, text: str) -> dict:
        # Базовый парсинг - можно улучшать постепенно
        meal_type = "other"
        if "завтрак" in text.lower(): meal_type = "breakfast"
        elif "обед" in text.lower(): meal_type = "lunch"
        elif "ужин" in text.lower(): meal_type = "dinner"

        # Простейший парсинг чисел
        calories = self._extract_number(text, "ккал")
        protein = self._extract_number(text, "белк")
        fat = self._extract_number(text, "жир")
        carbs = self._extract_number(text, "углев")

        if not all([calories, protein, fat, carbs]):
            return None

        return {
            'meal_type': meal_type,
            'description': text,
            'calories': calories,
            'protein': protein,
            'fat': fat,
            'carbs': carbs
        }

    def _extract_number(self, text: str, keyword: str) -> float:
        match = re.search(f"{keyword}.*?(\\d+[,.]?\\d*)", text.lower())
        return float(match.group(1).replace(',', '.')) if match else None

    def run(self):
        self.application.run_polling()

if __name__ == "__main__":
    NutritionBot().run()
