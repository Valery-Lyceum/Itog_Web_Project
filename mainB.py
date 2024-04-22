import logging
import aiohttp
from LxmlSoup import LxmlSoup
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)
START = 0
OlIMP = 1
CLASS = 2

async def olimps(update, context):
    # получаем html код сайта
    html = await get_response(
        "https://olimpiada.ru/activities?subject%5B6%5D=on&class=11&type=any&period_date=&period=year")
    soup = LxmlSoup(html)
    # получаем список наименований
    links = soup.find_all('span', class_='headline')
    # получаем список дат
    links2 = soup.find_all('span', class_='headline red')
    # сопоставляем наименование с датой
    result = []
    for i in range(len(links)):
        result.append([links[i].text()])
    for i in range(len(links)):
        result[i].append(links2[i].text())
    print(result)


async def get_response(url):
    logger.info(f"getting {url}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.text()


async def subject(update, context):
    reply_keyboard = [["math"], ["phisics"], ["informatics"]]
    await update.message.reply_text(
        "Ыelect the subject you want to learn about",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Send subject"
        ),
    )
    return OlIMP


async def start(update, context):
    reply_keyboard = [["olimps", 'geo'], ["timer", "results"]]
    await update.message.reply_text(
        "Я бот-справочник. Какая информация вам нужна?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Send those you want"
        ),
    )
    return START


async def stop(update, context):
    await update.message.reply_text("Всего доброго!")
    return ConversationHandler.END


if __name__ == '__main__':
    application = Application.builder().token("TOKEN").build()
    application.add_handler(CommandHandler("start", start))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            START: [MessageHandler(filters.Regex("^(olimps)$"), subject),""", MessageHandler(filters.Regex("^(geo)$"), geo),
                    MessageHandler(filters.Regex("^(timer)$"), timer), MessageHandler(filters.Regex("^(results)$"), results)"""]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    application.add_handler(conv_handler)
    application.run_polling()
