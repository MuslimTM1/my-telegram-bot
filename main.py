from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, ConversationHandler
from telegram.ext import CallbackContext
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# States for the conversation handler
PHONE_NUMBER, REPEATS = range(2)

# The bot token
TOKEN = "7618261878:AAGyoMuFThdLwOMbcBIR9W9rqo2wq2abVlA"

# Start command with button
def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("SPAM", callback_data='spam')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Welcome to SecretCALL SMS bot. Click the button to start spamming.', reply_markup=reply_markup)

# Start the spam process
def spam_button(update: Update, context: CallbackContext) -> int:
    update.callback_query.answer()
    update.callback_query.edit_message_text("Enter the phone number to start spamming.")
    return PHONE_NUMBER

# Handle phone number input
def phone_number(update: Update, context: CallbackContext) -> int:
    user_phone = update.message.text
    context.user_data['phone_number'] = user_phone
    update.message.reply_text(f"Got it! You want to spam {user_phone}. Now, please enter the number of repeats.")
    return REPEATS

# Handle repeats input
def repeats(update: Update, context: CallbackContext) -> int:
    try:
        repeats_count = int(update.message.text)
        phone_number = context.user_data['phone_number']
        update.message.reply_text(f"Starting to spam {phone_number} {repeats_count} times!")
        # Here you can trigger the function to actually start spamming based on phone_number and repeats_count
        return ConversationHandler.END
    except ValueError:
        update.message.reply_text("Please enter a valid number for repeats.")
        return REPEATS

# Cancel the conversation
def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("The spam process has been canceled.")
    return ConversationHandler.END

def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    # Define the conversation handler with states PHONE_NUMBER and REPEATS
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start), CallbackQueryHandler(spam_button, pattern='spam')],
        states={
            PHONE_NUMBER: [MessageHandler(Filters.text & ~Filters.command, phone_number)],
            REPEATS: [MessageHandler(Filters.text & ~Filters.command, repeats)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
