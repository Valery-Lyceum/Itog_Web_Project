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


def remove_job_if_exists(name, context):
    """Удаляем задачу по имени.
    Возвращаем True если задача была успешно удалена."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


TIMER = 5


async def set_timer(update, context):
    """Добавляем задачу в очередь"""
    chat_id = update.effective_message.chat_id
    # Добавляем задачу в очередь
    # и останавливаем предыдущую (если она была)
    job_removed = remove_job_if_exists(str(chat_id), context)
    context.job_queue.run_once(task, TIMER, chat_id=chat_id, name=str(chat_id), data=TIMER)

    text = f'Вернусь через 5 с.!'
    if job_removed:
        text += ' Старая задача удалена.'
    await update.effective_message.reply_text(text)


async def task(context):
    """Выводит сообщение"""
    await context.bot.send_message(context.job.chat_id, text=f'КУКУ! 5c. прошли!')


async def unset(update, context):
    """Удаляет задачу, если пользователь передумал"""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Таймер отменен!' if job_removed else 'У вас нет активных таймеров'
    await update.message.reply_text(text)


async def get_file_schedule_olimps(update, context):
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


async def start(update, context):
    global markup
    await update.message.reply_text(
        "Я бот-справочник. Какая информация вам нужна?",
        reply_markup=markup
    )


async def close_keyboard(update, context):
    await update.message.reply_text(
        "Ok",
        reply_markup=ReplyKeyboardRemove()
    )


async def stop(update, context):
    await update.message.reply_text("Всего доброго!")
    return ConversationHandler.END


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    # Вместо слова "TOKEN" надо разместить полученный от @BotFather токен
    application = Application.builder().token("TOKEN").build()
    # Регистрируем обработчик в приложении.
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("olimps", get_file_schedule_olimps))
    application.add_handler(CommandHandler("close", close_keyboard))
    reply_keyboard = [['/olimps', '/geo'],
                      ['/timer', '/results']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    conv_handler = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('start', start)],
        # Состояние внутри диалога.
        # Вариант с двумя обработчиками, фильтрующими текстовые сообщения.
        states={
            # Функция читает ответ на первый вопрос и задаёт второй.
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_file_schedule_olimps)],
            # Функция читает ответ на второй вопрос и завершает диалог.
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, stop)]
        },
        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop)]
    )
    # Запускаем приложение.
    application.run_polling()
