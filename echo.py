import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from config import BOT_TOKEN


logging.basicConfig(filename='logging.log',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
                    )

logger = logging.getLogger(__name__)


# async def echo(update, context):
#     # получаем обьект сообщения (локации)
#     message = update.message
#     print(message)
#     # вытаскиваем из него долготу и ширину
#     current_position = (message.location.longitude, message.location.latitude)
#     print(message)
#     # создаем строку в виде ДОЛГОТА,ШИРИНА
#     coords = f"{current_position[0]},{current_position[1]}"
#     await update.message.reply_text(coords)


async def echo(update, context):
    if update.edited_message:
        loc = update.edited_message
    else:
        loc = update.message
    current_position = (loc.location.latitude, loc.location.longitude)
    coords = f"{current_position[0]}, {current_position[1]}"
    await update.message.reply_text(coords)


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    text_handler = MessageHandler(filters.LOCATION, echo)
    application.add_handler(text_handler)
    application.run_polling()


if __name__ == '__main__':
    main()