import re
from datetime import datetime

import telebot

import asinhrom as ass
import utils
import whereFrom


def main():
    config, main_session, api_token, sorting_center_id, chat_id, message_thread_id, bot = (
        utils.load_config()
    )
    print("Запуск бота")
    return bot


bot = main()


def getOrders(inputstring):
    RegularExpressionForOrders = r"\b(?:PVZ_FBS_RET_\d{7}|PVZ_FBY_RET_\d{7}|VOZ_MK_\d{7}|VOZ_FBS_\d{8}|VOZ_FF_\d{8}|\bLO-\d{9}\b|FF-\d{13}|[2-5]\d{8})\b"
    Orders = re.findall(RegularExpressionForOrders, inputstring, re.MULTILINE)
    return Orders


def getPallets(inputstring):
    RegularExpressionForPallets = r"^F1.{18}$"
    Pallets = re.findall(RegularExpressionForPallets, inputstring, re.MULTILINE)
    return Pallets


def getTOTEs(inputstring):
    RegularExpressionForTOTEs = r"^F2.{18}$"
    TOTes = re.findall(RegularExpressionForTOTEs, inputstring, re.MULTILINE)
    return TOTes


ALLOW_USERS = [
    5291102003,
    1063498880,
    6478014074,
    1019990315,
    1133129646,
    6946675945,
    1641769105,
    6478014074,
    1213362983,
]

# Узнать ID текущего чата


@bot.message_handler(commands=["id"])  # Узнать ID чата
def echo_message(message):
    bot.reply_to(
        message,
        f"Chat_id: {message.chat.id}\nThread_id: {
            message.message_thread_id}",
    )


@bot.message_handler(
    func=lambda message: message.from_user.id == message.chat.id
    or message.chat.id == -1002008327465
)  # Выгрузка заказов из ПИ
def echo_message_bot(msg):
    st = datetime.now()
    msg.text = msg.text.replace(",", "\n").replace(" ", "\n").replace("(", "\n").replace(")", "\n")
    # bot.reply_to(message, f"Привет, {message.from_user.full_name}, взял в работу, время {st}\nТвой user_id: {message.from_user.id}\n")
    my_msg = bot.reply_to(msg, f"Привет, {msg.from_user.full_name}, взял в работу\n")
    # reply = "ты написал мне: \"" + message.text + "\" длина твоего сообщения: " + str (len(message.text) )   + "\n"
    Orders = getOrders(msg.text)
    Pallets = getPallets(msg.text)
    TOTEs = getTOTEs(msg.text)
    returnMessage = f""
    canUserUseMyBot = msg.from_user.id in ALLOW_USERS

    if canUserUseMyBot:
        print(
            f"{st}: Взял в работу сообщение от {
                msg.from_user.full_name}"
        )
        if Orders:
            Orders = sorted(set(Orders), key=Orders.index)

            if "откуда" in msg.text:
                requestsSession_local = whereFrom.get_config()
                whereFrom.get_info_by_orders(Orders, requestsSession_local)
                bot.send_document(
                    chat_id=msg.chat.id,
                    reply_to_message_id=msg.message_id,
                    document=open("output.xlsx", "rb"),
                    visible_file_name=f"Откуда заказики.xlsx",
                )
            elif "сканы" in msg.text:
                ass.getScan(Orders)
                bot.send_document(
                    chat_id=msg.chat.id,
                    reply_to_message_id=msg.message_id,
                    document=open("scans.xlsx", "rb"),
                    visible_file_name=f"Все сканы.xlsx",
                    timeout=120,
                )
                bot.send_document(
                    chat_id=msg.chat.id,
                    reply_to_message_id=msg.message_id,
                    document=open("scansGrouped.xlsx", "rb"),
                    visible_file_name=f"Последние сканы.xlsx",
                    timeout=120,
                )
            else:
                ass.getOrd(Orders)
                bot.send_document(
                    chat_id=msg.chat.id,
                    reply_to_message_id=msg.message_id,
                    document=open("orders.xlsx", "rb"),
                    visible_file_name=f"Статусы по ПИ.xlsx",
                )
        if TOTEs:
            TOTEs = set(TOTEs)
            returnMessage += f"ТОТы: {str(TOTEs)}\n"
        if Pallets:
            Pallets = set(Pallets)
            returnMessage += f"Паллеты: {str(Pallets)}\n"
    else:
        returnMessage += f"Ты не можешь взаимодействовать с ботом, обратись к @rusegg1\n {
            msg.from_user.id}"

    returnMessage += f"Количество Orders:{len(Orders)}\nВремя выполнения скрипта:{
        (datetime.now()-st).total_seconds()}\n"
    if len(returnMessage) > 4096:
        for x in range(0, len(returnMessage), 4096):
            bot.reply_to(msg, "{}".format(returnMessage[x : x + 4096]))
    else:
        if len(Orders) == 0 and canUserUseMyBot:
            bot.delete_message(chat_id=my_msg.chat.id, message_id=my_msg.message_id)
        else:
            bot.edit_message_text(
                chat_id=my_msg.chat.id,
                message_id=my_msg.message_id,
                text=f"{my_msg.text}\n{returnMessage}",
            )


# bot.infinity_polling(timeout=600, long_polling_timeout=600)
bot.polling()
