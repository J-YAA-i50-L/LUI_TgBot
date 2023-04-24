import datetime
import logging
import threading

import schedule as schedule
from telegram import ForceReply, Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler, \
    CallbackContext
from for_db import *
from geocod import *
from work_of_api import *

from TOKEN import TOKEN  # Токен

# Enable logging
logging.basicConfig(filename='logging.log',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
                    )

logger = logging.getLogger(__name__)


reply_keyboard = [['/maps', '/weather', '/music'],
                  ['/constructed_maps', '/KinoPoisk']]

constructed_maps_keyboard = [['/user_maps', '/all_maps'],
                             ['/constructed'],
                             ['/return_maps']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
constructed_maps_markup = ReplyKeyboardMarkup(constructed_maps_keyboard, one_time_keyboard=False)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    add_user(user.first_name, user.id, user.username, user.language_code, user.last_name)
    await update.message.reply_photo('LUI_logotip.png')
    await update.message.reply_html(
        f"Привет, {user.mention_html()}! Я Telegram-бот помощник LUI, который умеет работать с сервисами  Яндекса. \n"
        f"Для начала работы выберите сервис, либо пишите, что хотите: \n"
        f"  - /maps - Яндекс карта\n"
        f"  - /weather - Яндекс погода\n"
        f"  - /music - Яндекс музыка\n"
        f"  - /KinoPoisk - КиноПоиск\n",
        reply_markup=markup)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправит список команд, когда будет выдана команда /help."""
    await update.message.reply_text('Команды: \n "/catalog" - показывает каталог товаров магазина \n')


async def document_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправит xls файл, когда будет выдана команда /document."""
    if is_status(update.effective_user.id):
        get_info_for_base()
        await update.message.reply_document(document='Таблица_Excel_БД.xlsx')
    else:
        await update.message.reply_text('У вас нет прав для данной команды.')


async def location(update, context):
    """Принимает геопозицию пользователя и обрабатывает её"""
    if update.edited_message:
        loc = update.edited_message
    else:
        loc = update.message
    current_position = (loc.location.latitude, loc.location.longitude)
    # Создаем строку вида {ДОЛГОТА}, {ШИРИНА}
    coords = f"{current_position[0]},{current_position[1]}"
    await update.message.reply_text(coords)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Повторите сообщение пользователя."""
    print(update.message.chat_id)
    await update.message.reply_text(update.message.text)


async def doc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ждет файл xlxs т администратора"""
    await update.message.reply_text('Отпавте файл xlsx с изминениями')
    return 0


async def document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Повторите сообщение пользователя."""
    get_info_for_base()
    await update.message.reply_document('Таблица_Excel_БД.xlsx')


async def statys(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Назначает пользователя администратором, когда будет выдана команда /statys [password]."""
    password = update.message.text[8:]
    user = update.effective_user
    if password == '1234':
        remove_status(user.id)
        await update.message.reply_html(rf"{user.mention_html()} назначен администратором!",
                                        reply_markup=ForceReply(selective=True), )
    else:
        await update.message.reply_text('У вас нет прав!!!')


async def check_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Повторите сообщение пользователя."""
    a = update.message.document
    if not a:
        await update.message.reply_text('не то')
        return ConversationHandler.END

    get_file_of_tg(a.file_id, TOKEN)
    if not check_file_of_tg():
        await update.message.reply_text('pppp')
    else:
        await update.message.reply_text('Полностью ')
        return 1
    return ConversationHandler.END


async def remove_bzd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    dow_remove_for_tg(update.message.text)
    await update.message.reply_text('внесены изменения')


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Связь с админимтратором, когда будет выдана команда /admin."""
    await update.message.reply_text('Администратор ответит на все интересующие вас вопросы. '
                                    'С ним можно связаться по телефону: +79202980333')


async def home_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Магазины на карте, когда будет выдана команда /geo."""
    try:
        maps = maps_global()
        print(maps)
        await update.message.reply_photo(maps)
        await update.message.reply_text('У нас две точки по адресам:'
                                        '\n\t 1. г.Арзамас, просп. Ленина, 121, TЦ «Метро» 3 здание, 1 этаж'
                                        '\n\t 2. г.Арзамас, Парковая ул., 14А, ТЦ «Славянский»,1 этаж, отдел номер 7')
    except RuntimeError as ex:
        await update.message.reply_text('Что то пошло не по плану')


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Магазины на карте, когда будет выдана команда /geo."""
    await update.message.reply_text('stop')
    return ConversationHandler.END


async def send_of_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Связь с админимтратором, когда будет выдана команда /admin."""
    await update.message.reply_text('Введите текст, который вы планнируете отправить пользователям.')
    return 0


async def get_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Связь с админимтратором, когда будет выдана команда /admin."""
    context.user_data['0'] = update.message.text

    await update.message.reply_text('Введите дату в формате год:месяц:день, например, 2023:03:19\n'
                                    'Если вы хотите отправить сообщение сейчас отправьте "сейчас".')
    return 1


async def get_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Связь с админимтратором, когда будет выдана команда /admin."""
    if update.message.text == 'Сейчас':
        send_message()
    print(context.user_data['0'])

    await update.message.reply_text('')
    return ConversationHandler.END


def send_message(flag, text=''):
    if flag:
        today = ':'.join([str(datetime.date.today().year), str(datetime.date.today().month), str(datetime.date.today().day)])
        print(today)
        text = [i[1] for i in get_notification() if i[2] == today]
        print(text)
    for i in get_no_admin_id():
        sendMessage(i, '\n'.join(text), TOKEN)


def threat():  # второй поток для рассылки
    while True:
        schedule.run_pending()


async def constructed_maps_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Вы выбрали сервис яндекс карты. Команды:\n'
                                    '   - /all_maps - показывает все карты общего доступа\n'
                                    '   - /user_maps - выводит карты пользователя\n'
                                    '   - /constructed - конструктор карт яндекс\n'
                                    '   - /return_maps - Вернет ссылку на яндекс карту\n',
                                    reply_markup=constructed_maps_markup)


async def all_maps_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'Карты общего доступа:\n{get_all_maps()}',
                                    reply_markup=markup)


async def user_maps_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    dem = get_user_maps(user.id)
    if dem:
        await update.message.reply_text(f'Ваши карты:\n{get_user_maps(user.id)}', reply_markup=markup)
    else:
        await update.message.reply_text(f'У вас нет карт', reply_markup=markup)


async def constructed_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'Создать новую карту можно на cайте:https://yandex.ru/map-constructor/',
                                    reply_markup=markup)
    await update.message.reply_photo('qr_constructed.png')


async def return_maps_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'Отправите название интересующей вас карты я верну ссылку на карту',
                                    reply_markup=markup)
    return 0


async def return_maps_http_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    t = update.message.text.upper()
    user = update.effective_user
    dem = get_status_maps(t, user.id)
    if dem:
        await update.message.reply_text(f'{dem}', reply_markup=markup)
    else:
        await update.message.reply_text(f'Данная карта не найдена или у вас нет доступа к ней', reply_markup=markup)


def main() -> None:
    """Запустите бота."""
    # Создайте приложение и передайте ему токен вашего бота.
    application = Application.builder().token(TOKEN).build()
    # script_registration = ConversationHandler(
    #     # Точка входа в диалог.
    #     # В данном случае — команда /start. Она задаёт первый вопрос.
    #     entry_points=[CommandHandler('doc_post', doc)],
    #     # Состояние внутри диалога.
    #     states={
    #         0: [MessageHandler(filters.ALL & ~filters.COMMAND, check_file)],
    #         1: [MessageHandler(filters.ALL & ~filters.COMMAND, remove_bzd)]
    #     },
    #     # Точка прерывания диалога. В данном случае — команда /stop.
    #     allow_reentry=False,
    #     fallbacks=[CommandHandler('stop', stop)]
    # )
    # script_constructed_maps = ConversationHandler(
    #     # Точка входа в диалог.
    #     # В данном случае — команда /start. Она задаёт первый вопрос.
    #     entry_points=[CommandHandler('constructed_maps', constructed_maps_command)],
    #     # Состояние внутри диалога.
    #     states={
    #         0: [MessageHandler(filters.ALL & ~filters.COMMAND, asortiment)]
    #     },
    #     # Точка прерывания диалога. В данном случае — команда /stop.
    #     allow_reentry=False,
    #     fallbacks=[CommandHandler('my_maps', constructed_maps_comand)]
    # )
    script_return_maps = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('return_maps', return_maps_command)],
        # Состояние внутри диалога.
        states={
            0: [MessageHandler(filters.TEXT, return_maps_http_command)]
        },
        # Точка прерывания диалога. В данном случае — команда /stop.
        allow_reentry=False,
        fallbacks=[CommandHandler('stop', stop)]
    )
    # script_send = ConversationHandler(
    #     # Точка входа в диалог.
    #     # В данном случае — команда /start. Она задаёт первый вопрос.
    #     entry_points=[CommandHandler("send_message", send_of_admin_message)],
    #     # Состояние внутри диалога.
    #     states={
    #         0: [MessageHandler(filters.ALL & ~filters.COMMAND, get_text)],
    #         1: [MessageHandler(filters.ALL & ~filters.COMMAND, get_time)]
    #     },
    #     # Точка прерывания диалога. В данном случае — команда /stop.
    #     allow_reentry=False,
    #     fallbacks=[CommandHandler('stop', stop)]
    # )
    # по разным командам - отвечайте в Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("statys", statys))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("administrator", admin_command))
    application.add_handler(CommandHandler("dnt", document))

    application.add_handler(CommandHandler('constructed_maps', constructed_maps_command))
    application.add_handler(CommandHandler('all_maps', all_maps_command))
    application.add_handler(CommandHandler('user_maps', user_maps_command))
    application.add_handler(CommandHandler('constructed', constructed_command))

    # application.add_handler(script_registration)
    # application.add_handler(script_catalog)
    application.add_handler(script_return_maps)
    application.add_handler(CommandHandler("document", document_command))
    # по некомандному, то есть сообщению - повторить сообщение в Telegram
    # createBD()
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Запускайте бота до тех пор, пока пользователь не нажмет Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()

