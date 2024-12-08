import re  # Import regex for phone number validation

# Modify the handle_message function to validate phone numbers
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'spam_state' in context.user_data:
        state = context.user_data['spam_state']

        if state == "waiting_for_number_spam" or state == "waiting_for_number_autospam":
            phone_number = update.message.text.strip()

            # Validate the phone number
            if not re.match(r"^\+77\d{9}$", phone_number):  # Ensure it matches the format +77XXXXXXXXX
                if not re.match(r"^\+[\d]+$", phone_number):  # If it contains invalid characters
                    await update.message.reply_text("Пожалуйста, введите номер, например: +77XXXXXXXXX.")
                elif len(phone_number) != 12:  # If the length is incorrect
                    await update.message.reply_text("Номер должен состоять из 11 символов.")
                else:
                    await update.message.reply_text("Неправильный формат номера. Попробуйте снова.")
                return  # Exit the function and don't proceed further

            # If the phone number is valid, save it
            context.user_data["phone_number"] = phone_number
            await update.message.reply_text("Введите число на спам.")
            context.user_data["spam_state"] = "waiting_for_repeats_spam"

        elif state == "waiting_for_repeats_spam":
            try:
                repeats = int(update.message.text)
                phone_number = context.user_data["phone_number"]

                # Run spam process
                bloodtrail = BloodTrail(phone_number)
                bloodtrail.format_data()
                bloodtrail.start_threads(repeats)

                await update.message.reply_text(f"Успешный спам завершён на номер {phone_number} за {repeats} раз!")
                context.user_data.clear()  # Clear state after completion
            except ValueError:
                await update.message.reply_text("Пожалуйста, введите корректное число.")

# Update spam_button and autospam_button handlers to use validation
async def spam_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Введите номер, например: +77XXXXXXXXX")
    context.user_data['spam_state'] = 'waiting_for_number_spam'

async def autospam_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Введите номер, например: +77XXXXXXXXX")
    context.user_data['spam_state'] = 'waiting_for_number_autospam'
