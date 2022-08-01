import logging
import os
import pathlib
import pickle
import threading
import time

import feedparser
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
        # Stock feed URL
        self.URL = "https://rpilocator.com/feed/"

        # Retrive registered users
        if pathlib.Path("users.bip").exists():
            self.users = pickle.load(open("users.bip", "rb"))
        else:
            self.users = []

        # Setup bot
        self.updater = Updater(TOKEN, use_context=True)
        self.dispatcher = self.updater.dispatcher

        # Register handlers
        self.dispatcher.add_handler(CommandHandler("start", self.__startHandler))
        self.dispatcher.add_handler(CommandHandler("stop", self.__stopHandler))

        # Thread worker
        self.worker = threading.Thread(target=self.__worker).start()
        self.alive = False

    def startBot(self):
        """
        Start the bot
        """
        # Start bot
        self.updater.start_polling()
        self.updater.idle()

        # Start worker thread
        self.alive = True
        self.worker.start()

    def stopBot(self):
        """
        Stop the bot
        """
        self.updater.stop()
        self.alive = False
        self.worker.join()

    def __startHandler(self, update: Update, _):
        """
        Handler for the /start command
        """
        update.message.reply_text(
            "Hello there! From now I'll send you updates about RPi stocks 👋"
        )

        # Register user if not already registered
        if update.message.chat_id not in self.users:
            self.users.append(update.message.chat_id)
            pickle.dump(self.users, open("users.bip", "wb"))

    def __stopHandler(self, update: Update, _):
        """
        Handler for the /stop command
        """
        update.message.reply_text("As you wish! I'll stop sending you updates 🫠")

        # Unregister user if registered
        if update.message.chat_id in self.users:
            self.users.remove(update.message.chat_id)
            pickle.dump(self.users, open("users.bip", "wb"))

        # Remove user if registered
        if update.message.chat_id in self.users:
            self.users.remove(update.message.chat_id)
            pickle.dump(self.users, open("users.bip", "wb"))

    def __worker(self):
        """
        Worker thread
        """
        # Set start date
        feed = feedparser.parse(self.URL)
        last_update = feed.entries[0].published_parsed

        while self.alive:
            feed = feedparser.parse(self.URL)

            if feed.entries and feed.entries[0].published_parsed > last_update:
                last_update = feed.entries[0].published_parsed
                # Send message
                for user in self.users:
                    self.updater.bot.send_message(
                        user,
                        f"**{feed.entries[0].title}**\n\n"
                        f"{feed.entries[0].link}\n"
                        f"__{feed.entries[0].published}__",
                        parse_mode="Markdown",
                    )

            # Sleep for 2 minutes
            time.sleep(120)


def main():
    print("Starting BerryLocator...")
    TOKEN = os.environ["TOKEN"]
    berryLocator = BerryLocator(TOKEN)
    berryLocator.startBot()


if __name__ == "__main__":
    main()
