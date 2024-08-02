import logging
from uuid import uuid4

from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import Application, CommandHandler, ContextTypes, InlineQueryHandler, filters, MessageHandler

from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole

GIGACHAT_API_KEY = ""

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

def get_answer_from_gigachad(context):
    connection_to_gigachat = GigaChat(credentials=GIGACHAT_API_KEY, scope="GIGACHAT_API_PERS", verify_ssl_certs=False)
    chat = context
    return connection_to_gigachat.chat(chat)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text("Hi! Use /help for list of commands")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    message_text = update.message.text.split()
    message_text.pop(0)
    message_len = len(message_text)
    if message_len > 2:
        return await update.message.reply_text("/help may have only 0,1 or 2 parameters, send /help help for full documentation")
    form_p_help = {"description": "<b>form_product</b>: составляет основные шаги к реализации проекта,краткий функционал и описание инструментов которые могут помочь в реализации, <b>не генерирует название продукта</b>\n",
                         "syntax": "<b>синтаксис</b>: /form_product что делаем? язык программирования\n",
                         "example": "<b>пример</b>: /form_product мессенджер python\n"}
    h_help = {"description": "<b>help</b> - вспомогательная команда, может вывести описание и синтаксис всех команд или вывести отдельный параметр у какой-либо команды\n",
            "syntax": "<b>синтаксис</b>: /help название команды(не обязательно) параметр(не обязательно)\n <b>Параметры</b>: \n description - описание комадны\n syntax - синтаксис команды\n example - пример как можно написать комманду\n",
            "example": "<b>пример без аргументов</b>: /help \n <b>1 аргумент</b>: /help команда \n <b>2 аргумента</b>: /help команда параметр\n"}
    info_ab_help = {"description": "<b>info_about</b>: рассказывает какие библиотеки указанного языка программирования можно использовать для указанной задачи\n",
                    "syntax": "<b>синтаксис</b>: /info_about язык программирования задача. P.S если задачу нельзя описать одним словом - вместо пробелов используйте _ , например_так\n",
                    "example": "<b>пример</b>: /info_about python графики\n"}
    info_ab_lib_help = {"description": "<b>info_about_library</b>: рассказывает как использовать указанную библиотеку на указанном языке программирования с примерами кода\n",
                        "syntax": "<b>синтаксис</b>: /info_about_library название библиотеки язык программирования\n",
                        "example": "<b>пример</b>: /info_about_library Matplotlib python\n"}
    help_data = {"help": h_help,"form_product": form_p_help, "info_about": info_ab_help, "info_ab_lib_help": info_ab_lib_help}
    keys = ["description", "syntax", "example"]
    answer = ""

    if message_len == 0:
        keys.pop(2)
    elif message_len == 1:
        if message_text[0] in help_data:
            help_data = {message_text[0]: help_data[message_text[0]]}
        else:
            return await update.message.reply_text("incorrect command_name, try /help whitout parameters")
    elif message_len == 2:
        if message_text[0] in help_data:
            help_data = {message_text[0]: help_data[message_text[0]]}
            if message_text[1] in keys:
                keys = [message_text[1]]
            else:
                return await update.message.reply_text("incorrect parameter, try description, syntax or example")
        else:
            return await update.message.reply_text("incorrect command_name, try /help whitout parameters")
    for i in help_data:
        for j in keys:
            answer += help_data[i][j]
        answer += '\n'
    await update.message.reply_text(answer, parse_mode="HTML")


async def unknown_command(update: Update, context:ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Sorry I don't understand this command, use /help for a list of commands.")


def form_context(params):
    message = " ".join(["Ты программист, я хочу  сделать", params[0],
    "на языке программирования", params[1], "сформируй шаги которые помогут мне в создании этого проекта",
    "и также сформируй краткое описание функционала и набор технологий которые могут пригодится."])
    return Chat(messages=[Messages(role=MessagesRole.USER, content=message)])


async def form_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_text = update.message.text.split()
    message_text.pop(0)
    if len(message_text) < 2:
        return await update.message.reply_text('params error, use /help form_product for documentation')
    res = get_answer_from_gigachad(form_context(message_text))
    await update.message.reply_text(res.choices[0].message.content, parse_mode="Markdown")


def info_context(params):
    message = " ".join(["Ты программист, расскажи мне какие библиотеки на языке программирования", params[0], "нужны для", params[1]])
    return Chat(messages=[Messages(role=MessagesRole.USER, content=message)])


async def info_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text.split()
    message_text.pop(0)
    if len(message_text) < 2:
        return await update.message.reply_text("params error, use /help info_about for documentation")
    res = get_answer_from_gigachad(info_context(message_text))
    await update.message.reply_text(res.choices[0].message.content, parse_mode="Markdown")

def info_about_library_context(params):
    message = "".join(["Ты программист,  расскажи мне как пользоваться ", params[0], "с примером кода на языке", params[1]])
    return Chat(messages=[Messages(role=MessagesRole.USER, content=message)])

async def info_about_library(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text.split()
    message_text.pop(0)
    if len(message_text) < 2:
        return await update.message.reply_text("params error, use /help info_about_library for documentation")
    res = get_answer_from_gigachad(info_about_library_context(message_text))
    await update.message.reply_text(res.choices[0].message.content, parse_mode="Markdown")

def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("").build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("form_product", form_product))
    application.add_handler(CommandHandler("info_about", info_about))
    application.add_handler(CommandHandler("info_about_library", info_about_library))
    # on inline queries - show corresponding inline results
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
