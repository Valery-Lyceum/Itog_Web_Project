import logging
import math
import aiohttp
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
        "Выберите предмет",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Send subject"
        ),
    )
    return CLASS


async def studing_class(update, context):
    context.user_data['subject'] = update.message.text
    reply_keyboard = [["8"], ["9"], ["10"], ["11"]]
    await update.message.reply_text(
        "Выберите класс обучения",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Send class"
        ),
    )
    return OLIMP


async def action(update, context):
    reply_keyboard = [["add"], ["del"], ["see"]]
    await update.message.reply_text(
        "Выберите действие",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Send action"
        ),
    )
    return ACTION


async def needs(update, context):
    context.user_data["need"] = update.message.text
    need = context.user_data["need"]
    if need == "see":
        reply_keyboard = [["Выполнить запрос"]]
        await update.message.reply_text(
            "Подтвердите запрос",
            reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
            ),
        )
        return NAME
    elif need == "del":
        await update.message.reply_text(
            "Введите название олимпиады",
            reply_markup=ReplyKeyboardRemove()
            )
        return NAMEPOINTS
    elif need == "add":
        await update.message.reply_text(
            "Введите название олимпиады и баллы за нее",
            reply_markup=ReplyKeyboardRemove()
            )
        return NAMEPOINTS


async def see(update, context):
    cash = mainDB.nomain(context.user_data["need"], update.message.from_user.id)
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
    try:
        if need == "add":
            t = nazv.split()
            l = len(t)
            nazv, pt = ' '.join(t[:l-1]), int(t[-1])
            mainDB.nomain(context.user_data["need"], update.message.from_user.id, nazv, pt)
        elif need == "del":
            mainDB.nomain(context.user_data["need"], update.message.from_user.id, nazv)
        await update.message.reply_text(
            "Изменения приняты"
        )
    except:
        await update.message.reply_text(
            "Ошибка!"
        )
    return ConversationHandler.END


async def entr_adress(update, context):
    await update.message.reply_text(
        "Введите адрес начальной точки",
        reply_markup=ReplyKeyboardRemove()
    )
    return UADRESS


async def u_adress(update, context):
    u_adrs = update.message.text
    context.user_data['u_adress'] = u_adrs
    await update.message.reply_text(
        "Введите адрес конечной точки"
    )
    return OADRESS


async def obj_adress(update, context):
    obj_adrs = update.message.text
    context.user_data['o_adress'] = obj_adrs
    reply_keyboard = [["Выполнить запрос"]]
    await update.message.reply_text(
        "Подтвердите запрос",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        ),
    )
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
        await update.message.reply_text(
            "Плохое соединение с сервером",
            reply_markup=ReplyKeyboardRemove()
        )
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
        await update.message.reply_text(
            "Плохое соединение с сервером",
            reply_markup=ReplyKeyboardRemove()
        )
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
        caption=lonlat_distance([float(toponym_longitude), float(toponym_lattitude)], [float(toponym_longitude2), float(toponym_lattitude2)]),
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def get_response2(url, params):
    logger.info(f"getting {url}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            return await resp.json()


def lonlat_distance(a, b):
    degree_to_meters_factor = 111000
    a_lon, a_lat = a
    b_lon, b_lat = b
    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor
    distance = math.sqrt(dx * dx + dy * dy)
    return str(round(distance)) + " м"


async def alarm(context):
    job = context.job
    await context.bot.send_message(job.chat_id, text=f"Биип! {job.data} секунд прошли!")


def remove_job_if_exists(name, context):
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def set_timer(update, context) -> None:
    chat_id = update.effective_message.chat_id
    try:
        due = float(context.args[0])
        if due < 0:
            await update.effective_message.reply_text("К сожалению, мы не можем вернуться в будущее!")
            return

        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_once(alarm, due, chat_id=chat_id, name=str(chat_id), data=due)

        text = "Таймер успешно установлен!"
        if job_removed:
            text += " Старый удалили."
        await update.effective_message.reply_text(text)
    except (IndexError, ValueError):
        await update.effective_message.reply_text("Используйте: /set <seconds>")


async def unset(update, context):
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    if job_removed:
        text = "Таймер успешно отменен!"
    else:
        text = "У вас нет активного таймера."
    await update.message.reply_text(text)


async def menu(update, context):
    reply_keyboard = [["olimps", 'geo'], ["results"]]
    await update.message.reply_text(
        "Какая информация вам нужна?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Send those you want"
        ),
    )
    return START


async def start(update, context):
    await update.message.reply_text(
        """Здравствуйте! Я бот-помощник для олимпиадника.
           У меня есть следуюший функционал:
           /menu - вызывает меню с тремя ветками:
           1) Выдает список и расписание олимпиад.
           2) Показывает маршрут и расстояние до интересующего вас кружка.
           3) Позволяет записать, удалить или посмотреть результаты олимпиады.
           /set <seconds> - создает таймер для контроля выполнения задач.
           /unset - удаляет текущий таймер.
        """
    )


if __name__ == '__main__':
    application = Application.builder().token("TOKEN").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("set", set_timer))
    application.add_handler(CommandHandler("unset", unset))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('menu', menu)],
        states={
            START: [MessageHandler(filters.Regex("^(olimps)$"), subject),
                    MessageHandler(filters.Regex("^(results)$"), action),
                    MessageHandler(filters.Regex("^(geo)$"), entr_adress)],

            CLASS: [MessageHandler(filters.Regex("^(math|phisics|informatics)$"), studing_class)],
            OLIMP: [MessageHandler(filters.Regex("^(8|9|10|11)$"), olimps)],

            ACTION: [MessageHandler(filters.Regex("^(add|del|see)$"), needs)],
            NAME: [MessageHandler(filters.Regex("^(Выполнить запрос)$"), see)],
            NAMEPOINTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_del)],

            UADRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, u_adress)],
            OADRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, obj_adress)],
            GEO: [MessageHandler(filters.Regex("^(Выполнить запрос)$"), geocoder)]
        },
        fallbacks=[CommandHandler('menu', menu)]
    )
    application.add_handler(conv_handler)
    application.run_polling()
