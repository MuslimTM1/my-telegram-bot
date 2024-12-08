import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
import logging

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Your Telegram bot token
TOKEN = "7618261878:AAGyoMuFThdLwOMbcBIR9W9rqo2wq2abVlA"

# Load data from data.json
def load_data():
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"last_used_number": None, "paid_users": {"users": []}, "services": {}}

# Save data to data.json
def save_data(data):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("SPAM", callback_data='spam')],
        [InlineKeyboardButton("AUTOSPAM", callback_data='autospam')],
        [InlineKeyboardButton("Send to Multiple Numbers", callback_data='multiple_numbers')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)

# Handle Send to Multiple Numbers button
async def multiple_numbers_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['multiple_numbers'] = []  # Initialize the list for storing phone numbers
    await query.edit_message_text("Введите первый номер, например: +77XXXXXXXX")
    context.user_data['spam_state'] = 'waiting_for_multiple_numbers'

# Handle user input for multiple phone numbers
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'spam_state' in context.user_data:
        state = context.user_data['spam_state']

        if state == 'waiting_for_multiple_numbers':
            phone_number = update.message.text.strip()

            # Validate the phone number
            if not phone_number.startswith("+77") or len(phone_number) != 12 or not phone_number[1:].isdigit():
                await update.message.reply_text("Пожалуйста, введите корректный номер, например: +77XXXXXXXX.")
                return

            # Add the phone number to the list
            context.user_data['multiple_numbers'].append(phone_number)
            await update.message.reply_text(
                f"Номер {phone_number} добавлен. Введите следующий номер или отправьте 'STOP', чтобы прекратить."
            )
        elif state == 'waiting_for_repeats_multiple':
            try:
                repeats = int(update.message.text)
                phone_numbers = context.user_data['multiple_numbers']
                context.user_data['spam_state'] = None

                # Run spam process for each phone number
                for number in phone_numbers:
                    # Add your spam logic here
                    # For now, let's just simulate success
                    logger.info(f"Spamming {number} for {repeats} times!")

                numbers_list = " и ".join(phone_numbers)
                await update.message.reply_text(
                    f"Успешный спам завершён на номера: {numbers_list} за {repeats} раз!"
                )
            except ValueError:
                await update.message.reply_text("Пожалуйста, введите корректное число.")

# Callback query handlers
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "spam":
        await query.edit_message_text("SPAM выбрано. (Допишите функционал здесь.)")
    elif query.data == "autospam":
        await query.edit_message_text("AUTOSPAM выбрано. (Допишите функционал здесь.)")
    elif query.data == "multiple_numbers":
        await multiple_numbers_button(update, context)

# Main function to run the bot
def main():
    application = Application.builder().token(TOKEN).build()

    # Command Handlers
    application.add_handler(CommandHandler("start", start))

    # Callback query handlers
    application.add_handler(CallbackQueryHandler(callback_handler))

    # Message handler for user input
    application.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
