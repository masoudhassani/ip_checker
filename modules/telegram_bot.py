import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.

class TelegramBot:

    def __init__(self, config, logger):

        self.logger = logger
        """Start the bot."""
        # Create the Updater and pass it your bot's token.
        # Make sure to set use_context=True to use the new context based callbacks
        # Post version 12 this will no longer be necessary

        token = config['telegram_token']
        self.chat_id = config['chat_id']

        self.updater = Updater(token, use_context=True)

        # Get the dispatcher to register handlers
        dp = self.updater.dispatcher

        # on different commands - answer in Telegram
        dp.add_handler(CommandHandler("start", self.start))
        dp.add_handler(CommandHandler("help", self.help))

        # on noncommand i.e message - echo the message on Telegram
        dp.add_handler(MessageHandler(Filters.text, self.echo))

        # log all errors
        dp.add_error_handler(self.error)

        # Start the Bot
        self.updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        # self.updater.idle()


    def start(self, update, context):
        """Send a message when the command /start is issued."""
        update.message.reply_text('Hi!')


    def help(self, update, context):
        """Send a message when the command /help is issued."""
        update.message.reply_text('Help!')


    def echo(self, update, context):
        """Echo the user message."""
        update.message.reply_text(update.message.text)

    def error(self, update, context):
        """Log Errors caused by Updates."""
        self.logger.warning('Update "%s" caused error "%s"', update, context.error)

    # send a message to the telegram chat. 
    # to get the chat id, go to https://api.telegram.org/bot<token>/getUpdates
    # send a command in the group and see the respond in above link
    def send(self, message):
        self.updater.bot.sendMessage(self.chat_id, message)