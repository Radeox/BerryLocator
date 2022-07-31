import logging
import os
import pathlib
import pickle

# import requests
from telegram import Update
from telegram.ext import CommandHandler, Updater

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class BerryLocator:
    def __init__(self, TOKEN):
        """
        Initialize the bot and register handlers
        """
        # Retrive registered users
        if pathlib.Path("users.bip").exists():
            self.users = pickle.load(open("users.bip", "rb"))
            print(self.users)
        else:
            self.users = []

        # Setup bot
        self.updater = Updater(TOKEN, use_context=True)
        self.dispatcher = self.updater.dispatcher

        # Register handlers
        self.dispatcher.add_handler(CommandHandler("start", self.__startHandler))
        self.dispatcher.add_handler(CommandHandler("stop", self.__stopHandler))

    def startBot(self):
        """
        Start the bot
        """
        self.updater.start_polling()
        self.updater.idle()

    def stopBot(self):
        """
        Stop the bot
        """
        self.updater.stop()

    def __startHandler(self, update: Update, _):
        """
        Handler for the /start command
        """
        update.message.reply_text("Hello!")

        # Register user if not already registered
        if update.message.chat_id not in self.users:
            self.users.append(update.message.chat_id)
            pickle.dump(self.users, open("users.bip", "wb"))

    def __stopHandler(self, update: Update, _):
        """
        Handler for the /stop command
        """
        update.message.reply_text("Bye!")

        # Remove user if registered
        if update.message.chat_id in self.users:
            self.users.remove(update.message.chat_id)
            pickle.dump(self.users, open("users.bip", "wb"))


def main():
    print("Starting BerryLocator...")
    TOKEN = os.environ["TOKEN"]
    berryLocator = BerryLocator(TOKEN)
    berryLocator.startBot()


if __name__ == "__main__":
    main()
