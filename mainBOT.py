import logging
import aiohttp
from data.users import User
from LxmlSoup import LxmlSoup
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

START = 0
CLASS = 1
OLIMP = 2
ACTION = 3
NAME = 4
NAMEPOINT = 5

async def olimps(update, context):
    context.user_data['studing_class'] = update.message.text
    cls = context.user_data['studing_class']
    sbjct = context.user_data['subject']
    if sbjct == 'math':
        sbjct = '%5B6%5D'
    elif sbjct == 'phisics':
        sbjct = '%5B12%5D'
    elif sbjct == 'informatics':
        sbjct = '%5B7%5D'
    html = await get_response(
        f"https://olimpiada.ru/activities?subject{sbjct}=on&class={cls}&type=any&period_date=&period=year")
    soup = LxmlSoup(html)
    links = soup.find_all('span', class_='headline')
    links2 = soup.find_all('span', class_='headline red')
    result = []
    if len(links) != len(links) or len(links) * len(links) == 0:
        await update.message.reply_text(
            "Плохое соединение с сервером",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        for i in range(len(links)):
            result.append([links[i].text()])
        for i in range(len(links)):
            result[i].append(links2[i].text())
        print(result)
        await update.message.reply_text(
            "end",
            reply_markup=ReplyKeyboardRemove()
        )
    return ConversationHandler.END


async def get_response(url):
    logger.info(f"getting {url}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.text()


async def subject(update, context):
    reply_keyboard = [["math"], ["phisics"], ["informatics"]]
    await update.message.reply_text(
        "Select the subject you want to learn about",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Send subject"
        ),
    )
    return CLASS


async def studing_class(update, context):
    context.user_data['subject'] = update.message.text
    reply_keyboard = [["8"], ["9"], ["10"], ["11"]]
    await update.message.reply_text(
        "Select your trainig class",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Send class"
        ),
    )
    return OLIMP


async def action(update, context):
    reply_keyboard = [["add"], ["del"], ["see"]]
    await update.message.reply_text(
        "Select action",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Send action"
        ),
    )
    return ACTION


async def needs(update, context):
    context.user_data["need"] = update.message.text
    need = context.user_data["need"] = update.message.text
    if need == "add" or need == "del":
        await update.message.reply_text(
            "enter name olimpiads",
            reply_markup=ReplyKeyboardRemove()
            )
        return NAME
    elif need == "see":
        await update.message.reply_text(
            "enter name olimpiads and points for it",
            reply_markup=ReplyKeyboardRemove()
            )
        return NAMEPOINT


async def add_del(update, context):
    nazv = update.message.text



async def see(update, context):
    pass


async def start(update, context):
    reply_keyboard = [["olimps", 'geo'], ["timer", "results"]]
    await update.message.reply_text(
        "Я бот-справочник. Какая информация вам нужна?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Send those you want"
        ),
    )
    return START


async def close_keyboard(update, context):
    await update.message.reply_text(
        "Ok",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


if __name__ == '__main__':
    application = Application.builder().token("TOKEN").build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            START: [MessageHandler(filters.Regex("^(olimps)$"), subject), MessageHandler(filters.Regex("^(results)$"), action)],
            CLASS: [MessageHandler(filters.Regex("^(math|phisics|informatics)$"), studing_class)],
            OLIMP: [MessageHandler(filters.Regex("^(8|9|10|11)$"), olimps)],

            ACTION: [MessageHandler(filters.Regex("^(add|del|see)$"), needs)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_del)],
            NAMEPOINT: [MessageHandler(filters.TEXT & ~filters.COMMAND, see)]
        },
        fallbacks=[CommandHandler('close', close_keyboard)]
    )
    application.add_handler(conv_handler)
    application.run_polling()
