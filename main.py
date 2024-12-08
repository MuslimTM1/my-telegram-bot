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
        return {"last_used_number": None, "paid_users": {"users": []}}

# Save data to data.json
def save_data(data):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("SPAM", callback_data='spam'), InlineKeyboardButton("AUTOSPAM", callback_data='autospam')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)

# Handle SPAM button
async def spam_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = load_data()
    keyboard = []
    if data["last_used_number"]:
        keyboard.append([InlineKeyboardButton(f"Последний номер: {data['last_used_number']}", callback_data="latest_number")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Введите номер, например: +77XXXXXXXXX", reply_markup=reply_markup)
    context.user_data['spam_state'] = 'waiting_for_number_spam'

# Handle AUTOSPAM button
async def autospam_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = load_data()
    keyboard = []
    if data["last_used_number"]:
        keyboard.append([InlineKeyboardButton(f"Последний номер: {data['last_used_number']}", callback_data="latest_number")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Введите номер, например: +77XXXXXXXXX", reply_markup=reply_markup)
    context.user_data['spam_state'] = 'waiting_for_number_autospam'

# Handle user input for SPAM and AUTOSPAM
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'spam_state' in context.user_data:
        state = context.user_data['spam_state']

        if state == 'waiting_for_number_spam' or state == 'waiting_for_number_autospam':
            phone_number = update.message.text.strip()

            # If the user selects "latest number"
            if phone_number == "latest_number":
                data = load_data()
                phone_number = data["last_used_number"]
                if phone_number:
                    await update.message.reply_text(f"Вы выбрали номер: {phone_number}. Введите число на спам.")
                    context.user_data['phone_number'] = phone_number
                    context.user_data['spam_state'] = 'waiting_for_repeats_spam'
                    return

            # Validate and save the phone number
            context.user_data['phone_number'] = phone_number
            data = load_data()
            data["last_used_number"] = phone_number
            save_data(data)

            await update.message.reply_text("Введите число на спам.")
            context.user_data['spam_state'] = 'waiting_for_repeats_spam'

        elif state == 'waiting_for_repeats_spam':
            try:
                repeats = int(update.message.text)
                phone_number = context.user_data['phone_number']
                context.user_data['spam_state'] = None

                # Run spam process (add your spam logic here)
                # For now, let's just send a success message
                await update.message.reply_text(f"Успешный спам завершён на номер {phone_number} за {repeats} раз!")
            except ValueError:
                await update.message.reply_text("Пожалуйста, введите корректное число.")

# Main function to run the bot
def main():
    application = Application.builder().token(TOKEN).build()

    # Command Handlers
    application.add_handler(CommandHandler("start", start))

    # Callback query handlers
    application.add_handler(CallbackQueryHandler(spam_button, pattern='spam'))
    application.add_handler(CallbackQueryHandler(autospam_button, pattern='autospam'))

    # Message handler for user input
    application.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
