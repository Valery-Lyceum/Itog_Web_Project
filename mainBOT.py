import logging
import math
import aiohttp
import datetime
from data.users import User
import mainDB
from LxmlSoup import LxmlSoup
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
logger = logging.getLogger(__name__)
START, CLASS, OLIMP, ACTION, NAME, NAMEPOINTS, UADRESS, OADRESS, GEO = range(9)


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
        vivod = ''
        for i in result:
            vivod += f"{i[0]}: {i[1]}\t"
        await update.message.reply_text(
            f"{vivod}",
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
    if need == "see":
        return NAME
    elif need == "del":
        await update.message.reply_text(
            "enter name olimpiads",
            reply_markup=ReplyKeyboardRemove()
            )
        return NAMEPOINTS
    elif need == "add":
        await update.message.reply_text(
            "enter name olimpiads and points for it",
            reply_markup=ReplyKeyboardRemove()
            )
        return NAMEPOINTS


async def see(update, context):
    cash = mainDB.nomain(context.user_data["need"], update.message.from_user.id)
    """
    f = open(f"{datetime}", 'w')
    for i in cash:
        print(f"{i[0]}: {i[1]}", file=f)
    f.close()
    """
    vivod = ''
    for i in cash:
        vivod += f"{i[0]}: {i[1]}\t"
    await update.message.reply_text(
        f"{vivod}",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END



async def add_del(update, context):
    nazv = update.message.text
    need = context.user_data["need"]
    if need == "add":
        t = nazv.split()
        l = len(t)
        nazv, pt = ' '.join(t[:l-1]), int(t[-1])
        mainDB.nomain(context.user_data["need"], update.message.from_user.id, nazv, pt)
    elif need == "del":
        mainDB.nomain(context.user_data["need"], update.message.from_user.id, nazv)


async def entr_adress(update, context):
    await update.message.reply_text(
        "enter your adress",
        reply_markup=ReplyKeyboardRemove()
    )
    return UADRESS


async def u_adress(update, context):
    u_adrs = update.message.text
    context.user_data['u_adress'] = u_adrs
    await update.message.reply_text(
        "enter object adress"
    )
    return OADRESS


async def obj_adress(update, context):
    obj_adrs = update.message.text
    context.user_data['o_adress'] = obj_adrs
    return GEO


async def geocoder(update, context):
    toponym_to_find = context.user_data['u_adress']
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": toponym_to_find,
        "format": "json"}
    response = await get_response2(geocoder_api_server, params=geocoder_params)
    if not response:
        return ConversationHandler.END
    toponym = response["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]
    toponym_coodrinates = toponym["Point"]["pos"]
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

    toponym_to_find = context.user_data['o_adress']
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": toponym_to_find,
        "format": "json"}
    response = await get_response2(geocoder_api_server, params=geocoder_params)
    if not response:
        return ConversationHandler.END
    toponym = response["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]
    toponym_coodrinates = toponym["Point"]["pos"]
    toponym_longitude2, toponym_lattitude2 = toponym_coodrinates.split(" ")

    delta = "0.05"

    longitude, lattitude = max(float(toponym_longitude), float(toponym_longitude2)), max(float(toponym_lattitude),
                                                                                         float(toponym_lattitude2))
    longitude, lattitude = str(longitude), str(lattitude)
    ll = ",".join([longitude, lattitude])
    spn = ",".join([delta, delta])
    pt = ",".join([toponym_longitude, toponym_lattitude]) + "~" + ",".join([toponym_longitude2, toponym_lattitude2])
    pl = ",".join([toponym_longitude, toponym_lattitude]) + "," + ",".join([toponym_longitude2, toponym_lattitude2])
    static_api_request = f"http://static-maps.yandex.ru/1.x/?ll={ll}&spn={spn}&pt={pt}&pl={pl}&l=map"
    await context.bot.send_photo(
        update.message.chat_id,
        static_api_request,
        caption=lonlat_distance([float(toponym_longitude), float(toponym_lattitude)], [float(toponym_longitude2), float(toponym_lattitude2)])
    )
    return ConversationHandler.END


def lonlat_distance(a, b):
    degree_to_meters_factor = 111000
    a_lon, a_lat = a
    b_lon, b_lat = b
    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor
    distance = math.sqrt(dx * dx + dy * dy)
    return str(round(distance)) + " m"


async def get_response2(url, params):
    logger.info(f"getting {url}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            return await resp.json()


async def start(update, context):
    reply_keyboard = [["olimps", 'geo'], ["results"]]
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
            START: [MessageHandler(filters.Regex("^(olimps)$"), subject),
                    MessageHandler(filters.Regex("^(results)$"), action),
                    MessageHandler(filters.Regex("^(geo)$"), entr_adress)],
            CLASS: [MessageHandler(filters.Regex("^(math|phisics|informatics)$"), studing_class)],
            OLIMP: [MessageHandler(filters.Regex("^(8|9|10|11)$"), olimps)],

            ACTION: [MessageHandler(filters.Regex("^(add|del|see)$"), needs)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, see)],
            NAMEPOINTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_del)],

            UADRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, u_adress)],
            OADRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, obj_adress)],
            GEO: [MessageHandler(filters.TEXT & ~filters.COMMAND, geocoder)]
        },
        fallbacks=[CommandHandler('close', close_keyboard)]
    )
    application.add_handler(conv_handler)
    application.run_polling()
