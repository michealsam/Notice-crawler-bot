import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from bot import Webscraper
from dotenv import load_dotenv # edit edit.env folder to .env to use load your environment variable 

load_dotenv() # loads the environment variable
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s",
                    level=logging.INFO)

logger = logging.getLogger(__name__)
logger.info("\n\n Bot is Starting......")

user_list  = []

WEBSITE = Webscraper(url="https://bitsindri.ac.in/")

previous = WEBSITE.scrape('nav menu menu-treemenu')
## uncomment the the comment bellow for testing purposes
# previous = {'Provisional Name List of B.Tech 1st sem Student (Session 2022-23) through JCECEB, Ranchi after 4th counselling': 'https://bitsindri.ac.in//images/2022files/Provisional_Name_List_of_BTech_1st_sem_Student_Session_2022-23_through_JCECEB_Ranchi_after_4th_counselling.pdf', 'Provisional Name list of B.Tech 3rd sem LE (2022-23) admitted student through JCECEB, Ranchi': 'https://bitsindri.ac.in//images/2022files/Provisional_Name_list_of_BTech_3rd_sem_LE_2022-23_admitted_student_through_JCECEB_Ranchi.pdf', 'Provisional Name List of B.Tech 3rd sem (Regular) Session 2022-23': 'https://bitsindri.ac.in//images/2022files/Provisional_Name_List_of_BTech_3rd_sem_Regular_Session_2022-23.pdf', 'Notice for commencement of classes of B.Tech 3rd sem': 'https://bitsindri.ac.in//images/2022files/Notice_for_commencement_of_classes_of_BTech_3rd_sem.pdf', 'Notice for commencement of classes of B.Tech 1st sem': 'https://bitsindri.ac.in//images/2022files/Notice_for_commencement_of_classes_of_BTech_1st_sem.pdf', 'Notice for B.Tech 3rd sem (LE)Admission for session 2022-23 through JCECEB Ranchi,4th counselling': 'https://bitsindri.ac.in//images/2022files/Notice_for_BTech_3rd_sem_LEAdmission_for_session_2022-23_through_JCECEB_Ranchi4th_counselling.pdf', 'Notice for M.Tech Admission form on vacant seat session 2022-24': 'https://bitsindri.ac.in//images/2022files/Notice_for_MTech_Admission_form_on_vacant_seat_session_2022-24.pdf', 'Notice for B.Tech 1st sem Admission for session 2022-23 through JCECEB Ranchi,4th counselling': 'https://bitsindri.ac.in//images/2022files/Notice_for_BTech_1st_sem_Admission_for_session_2022-23_through_JCECEB_Ranchi4th_counselling.pdf', 'BIT SINDRI new website': 'https://bits.techax.in/'}
def checkupdate():
    global previous
    new = WEBSITE.scrape('nav menu menu-treemenu')
    if previous != new:
        previous_first_key = list(previous.keys())[0]
        indexof_previous_key = list(new.keys()).index(previous_first_key)
        previous = new
        return dict(list(new.items())[:indexof_previous_key])
    else:
        return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """It send the status of bot and website"""
    user = update.effective_user
    await update.message.reply_html(f"""✋🏻Hi {user.mention_html()}!\n\n \t<b>Websites status:</b>\n
    \t{'Website is 🟢Active , Send me any commands' if WEBSITE.status() == 200 else '🔴There is some problem in website'}\n
    """)


def text_decorator(func):
    """ This is decorator function that converts dictionary returned from the function(which is in parameter)
    to formatted text and send it to the user"""

    async def text_formater(update, context):
        notices = await func(update, context)
        if notices:
            text = '📑Notices:\n' + '\n\n'.join(str(x) + " " + notices[x] for x in notices)
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
    user_list.append(str(update.message.chat_id))
    await update.message.reply_text("You have successfully subscribed to notifications, you will recevive a "
                                    "notification everytime the bit sidri website updates their notices. "
                                    "\nsend me /unsubscribe to unsubscribe")


async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """It help user to unsubscribe to notifications from website"""
    chat_id =  update.message.chat_id
    if str(chat_id) in user_list:
        user_list.remove(str(update.message.chat_id))
        await update.message.reply_text("you have successfully unsubscribed to the notification")
    else:
        await update.message.reply_text("you haven't subscribe yet, if you want to subscribe use /subscribe")
        

async def callback_minute( context: ContextTypes.DEFAULT_TYPE):
    global user_list
    Website_update = checkupdate()
    if Website_update:
        for i in user_list:
            await context.bot.send_message(chat_id = i, text = '🟢Updates from website:\n\n' + '\n\n'.join(str(x) + " " + Website_update[x] for x in Website_update))

def main() -> None:
    """start the bot."""

    # This create the Application and pass it to your bot's token
    application = Application.builder().token(
        os.getenv("BOT_TOKEN")).build()  # Add token here directly or in .env file/environment variable

    job_queue = application.job_queue

    job_minute = job_queue.run_repeating(callback_minute, interval = 15, first = 15)

    # Adding different handlers to handle different commands given to bot
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("topfive", topfive))
    application.add_handler(CommandHandler("subscribe", subscribe))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe))
    # The following will start the long polling in short 'it will start the bot'
    application.run_polling()


if __name__ == "__main__":
    main()
