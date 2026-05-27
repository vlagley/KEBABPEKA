import asyncio
import json
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

# --- НАСТРОЙКИ ТОКЕНОВ ---
BOT_TOKEN = "ТВОЙ_ТОКЕН_БОТА"  # Получи у @BotFather
WORKER_CHAT_ID = 123456789     # ID чата (или группы), куда отправлять заказы повару
MINI_APP_URL = "https://your-domain.com/index.html"  # Ссылка на твой развернутый HTML

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    """
    Обработчик команды /start. Показывает главную кнопку
    для вызова Mini App через необходимый ReplyKeyboardMarkup.
    """
    web_app = WebAppInfo(url=MINI_APP_URL)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🍕 Открыть меню", web_app=web_app)]
        ],
        resize_keyboard=True
    )
    
    await message.answer(
        text=f"Привет, {message.from_user.first_name}! 🐾\n"
             f"Нажми на кнопку ниже, чтобы заказать сочную шаурму в PekaKebab.",
        reply_markup=keyboard
    )

@dp.message(F.web_app_data)
async def handle_web_app_data(message: types.Message):
    """
    Слушатель событий web_app_data. Срабатывает в момент,
    когда клиент нажимает 'Оформить заказ' внутри Mini App.
    """
    try:
        # Извлекаем и декодируем строку JSON, отправленную из JS
        order_data = json.loads(message.web_app_data.data)
        
        item_title = order_data.get("title", "Неизвестно")
        item_size = order_data.get("size", "Неизвестно")
        item_price = order_data.get("price", "0")
        
        # Получаем данные о клиенте
        username = f"@{message.from_user.username}" if message.from_user.username else "Скрыт"
        user_fullname = message.from_user.full_name
        current_time = datetime.now().strftime("%H:%M:%S")

        # Формируем сообщение-уведомление для кухни/сотрудника
        worker_message = (
            f"🚨 **НОВЫЙ ЗАКАЗ ИЗ МИНИ-АПП!**\n\n"
            f"📦 **Блюдо:** {item_title}\n"
            f"📐 **Размер:** {item_size}\n"
            f"💰 **Сумма:** {item_price} ₽\n\n"
            f"👤 **Клиент:** {user_fullname} ({username})\n"
            f"🕒 **Время:** {current_time}"
        )

        # 1. Отправляем карточку заказа рабочему на кухню
        await bot.send_message(chat_id=WORKER_CHAT_ID, text=worker_message, parse_mode="Markdown")
        
        # 2. Дублируем текстовое подтверждение клиенту в личные сообщения бота
        await message.answer(
            text=f"✅ Твой заказ на **{item_title} ({item_size})** принят администратором.\n"
                 f"Сумма к оплате при получении: *{item_price} ₽*.",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logging.error(f"Ошибка обработки заказа: {e}")
        await message.answer("Произошла ошибка при отправке заказа на кухню. Попробуйте еще раз.")

async def main():
    print("Бот PekaKebab успешно запущен и готов принимать заказы...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())