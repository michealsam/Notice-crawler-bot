import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from bot import Webscraper
#uncomment the comment below when testing bot using .env
from dotenv import load_dotenv 

#uncomment this after filling the .env folder
load_dotenv()
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s",
                    level=logging.INFO)

logger = logging.getLogger(__name__)
logger.info("\n\n Bot is Starting......")

user_list = []

WEBSITE = Webscraper(url="https://bitsindri.ac.in/")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """It send the status of bot and website"""
    user = update.effective_user
    await update.message.reply_html(f"""✋🏻Hi {user.mention_html()}!\n\n \t<b>Websites status:</b>\n
    \t{'🟢Active' if WEBSITE.status() == 200 else '🔴There is some problem in website'}\n
    """)


def text_decorator(func):
    """ This is decorator function that converts dictionary returned from the function(which is in parameter)
    to formatted text and send it to the user"""

    async def text_formater(update, context):
        notices = await func(update, context)
        if notices:
            text = 'Notices:\n' + '\n\n'.join(str(x) + " " + notices[x] for x in notices)
        else:
            text = "Some error"
        try:
            await update.message.reply_text(text)
        except Exception as e:
            logger.error(e)
            await update.message.reply_text("🔴There was an error")

    return text_formater


@text_decorator
async def topfive(update: Update, context: ContextTypes.DEFAULT_TYPE) -> dict:
    """It fetches the 5 new notices from the website"""
    notices = WEBSITE.scrape('nav menu menu-treemenu')
    return dict(list(notices.items())[:5])


async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """It help user to subscribe to notifications when website updates notices"""
    user_list.append(update.message.chat_id)
    await update.message.reply_text("You have successfully subscribed to notifications, you will recevive a "
                                    "notification everytime the bit sidri website updates their notices. "
                                    "\nsend me /unsubscribe to unsubscribe")


async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """It help user to unsubscribe to notifications from website"""
    chat_id =  update.message.chat_id
    if chat_id in user_list:
        user_list.remove(update.message.chat_id)
        await update.message.reply_text("you have successfully unsubscribed to the notification")
    else:
        await update.message.reply_text("you haven't subscribe yet, if you want to subscribe use /subscribe")


def main() -> None:
    """start the bot."""

    # This create the Application and pass it to your bot's token
    application = Application.builder().token(
        os.getenv("BOT_TOKEN")).build()  # Add token here directly or in .env file/environment variable

    # Adding different handlers to handle different commands given to bot
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("topfive", topfive))
    application.add_handler(CommandHandler("subscribe", subscribe))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe))
    # The following will start the long polling in short 'it will start the bot'
    application.run_polling()


if __name__ == "__main__":
    main()
