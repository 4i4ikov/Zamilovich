# import datetime
# import asyncio
import configparser

# import aiohttp
# import json
import logging
import re

# import sys
import tempfile
from datetime import datetime

import cv2
import requests

# from pprint import pprint
# from bs4 import BeautifulSoup
import telebot

# import pandas as pd
# from requests.exceptions import RequestException
import urllib3

# from PIL import Image
from pylibdmtx.pylibdmtx import decode as pydecode
from pyzbar.pyzbar import decode as pyzdecode

import asinhrom as ass
from updatesk import updatesk

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    encoding="utf-8",
)

logger.info("Бот запускается...")
# EMOJI = ["👎","👍", "🤔"]

config = configparser.ConfigParser()
urllib3.disable_warnings()
config.read("config.ini")
logger.info(f"Загружен ЛОГ:\n{dict(config.items())}")
cookies = {
    "Session_id": config.get("Session", "Session_id"),
}
headers = {
    "sk": config.get("Session", "sk"),
}
requestsSession = requests.Session()
requestsSession.verify = False
requestsSession.cookies.update(cookies)
requestsSession.headers.update(headers)


def getOrder(order):
    json_data = {
        "params": [
            {
                "sortingCenterId": 1100000040,
                "orderId": order,
            },
        ],
        "path": f"/sorting-center/1100000040/orders/{order}",
    }

    response = requestsSession.post(
        "https://logistics.market.yandex.ru/api/resolve/?r=sortingCenter/orders/resolveOrder:resolveOrder",
        json=json_data,
        verify=False,
    )
    if response.status_code != 200:
        sk = updatesk(cookies)
        config.set("Session", "sk", sk)
        requestsSession.headers.update(
            {
                "sk": config.get("Session", "sk"),
            }
        )
        with open("config.ini", "w", encoding="utf8") as configfile:
            config.write(configfile)
        response = requestsSession.post(
            "https://logistics.market.yandex.ru/api/resolve/?r=sortingCenter/orders/resolveOrder:resolveOrder",
            json=json_data,
            verify=False,
        )
    if "data" in response.json()["results"][0].keys():
        return response.json()["results"][0]["data"]
    else:
        return False


def getSortablesOfOrder(order):
    json_data = {
        "params": [
            {
                "sortableStatuses": [],
                "stages": [],
                "orderExternalId": order,
                "inboundIdTitle": "",
                "outboundIdTitle": "",
                "groupingDirectionId": "",
                "groupingDirectionName": "",
                "sortingCenterId": 1100000040,
                "page": 0,
                "size": 20,
                "sortableTypes": [],
                "crossDockOnly": False,
            },
        ],
        "path": "/sorting-center/1100000040/sortables?sortableTypes=&sortableStatuses=&sortableStatusesLeafs=&orderExternalId=423501618&inboundIdTitle=&outboundIdTitle=&groupingDirectionId=&groupingDirectionName=",
    }
    sortables = requestsSession.post(
        "https://logistics.market.yandex.ru/api/resolve/?r=sortingCenter/sortables/resolveSortableReport:resolveSortableReport",
        json=json_data,
        verify=False,
    )
    if sortables.status_code == 200:
        sortables = sortables.json()["results"][0]["data"]["content"]

    return sortables


def getOrders(inputstring):
    RegularExpressionForOrders = r"\b(?:PVZ_FBS_RET_\d{7}|PVZ_FBY_RET_\d{7}|VOZ_MK_\d{7}|VOZ_FBS_\d{8}|VOZ_FF_\d{8}|\bLO-\d{9}\b|FF-\d{13}|[2-5]\d{8})\b"
    Orders = re.findall(RegularExpressionForOrders, inputstring, re.MULTILINE)
    return Orders


def getPallets(inputstring):
    RegularExpressionForPallets = r"^F1.{18}$"
    Pallets = re.findall(RegularExpressionForPallets,
                         inputstring, re.MULTILINE)
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


API_TOKEN = config.get("BOT", "API_TOKEN")
print("Запуск бота")

# mistakes_bot = telebot.TeleBot("7216110457:AAEs2vp5onOeKWMZHwaiKSKrlpiozZibeKU")
bot = telebot.TeleBot(API_TOKEN)


# Распознать ШК заказов по фото
# @bot.message_handler(content_types=['photo'], func=lambda message: message.chat.id == -904145156)
def photo(message):
    # if (message.caption and "qr" in message.caption):
    print("получил изображение")
    # bot.set_message_reaction(message.chat.id,message.id,[telebot.types.ReactionTypeEmoji(EMOJI[2])])
    fileID = message.photo[-1].file_id
    file_info = bot.get_file(fileID)

    downloaded_file = bot.download_file(file_info.file_path)

    temp = tempfile.NamedTemporaryFile(delete_on_close=False)
    temp.write(downloaded_file)
    temp.close()

    image = cv2.imread(temp.name)
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # cv2.imwrite(temp[1].name,gray)
    except Exception as err:
        print(err)
    else:
        gray = image
        # cv2.imwrite(temp[1].name,gray)

    barcodeScanners = []
    barcodeScanners.append(pyzdecode(gray))
    decoder = cv2.QRCodeDetector()
    retval, decoded_info, points, straight_qrcode = decoder.detectAndDecodeMulti(
        gray)

    barcodeScanners.append(decoded_info)

    barcodeScanners.append(pydecode(gray))

    print(barcodeScanners)
    decoded = set()
    if barcodeScanners[0]:
        for qrcode in barcodeScanners[0]:
            decoded.add(qrcode.data.decode())
    if retval:
        for qrcode in barcodeScanners[1]:
            decoded.add(qrcode)
    if barcodeScanners[2]:
        for qrcode in barcodeScanners[2]:
            decoded.add(qrcode.data.decode())

    # with open("image.jpg", 'wb+') as new_file:
    #     new_file.write(downloaded_file)
    # bot.send_photo(chat_id=message.chat.id,message_thread_id=message.message_thread_id,reply_to_message_id=message.message_id,photo=open("gray.png","rb"))
    if decoded:
        # bot.set_message_reaction(message.chat.id,message.id,[telebot.types.ReactionTypeEmoji(EMOJI[1])])
        forward = bot.forward_message(
            chat_id=-1002205631792,
            from_chat_id=message.chat.id,
            message_id=message.id,
            message_thread_id=88,
        )
        bot.reply_to(forward, f"{'\n'.join(decoded)}")
    else:
        print("не распознал\n")
        # forward = bot.forward_message(chat_id=-1002205631792,from_chat_id=message.chat.id,message_id=message.id,message_thread_id=94)
        # bot.reply_to(forward,f"Не смог распознать.")


# Узнать ID текущего чата
@bot.message_handler(commands=["id"])  # Узнать ID чата
def echo_message(message):
    bot.reply_to(
        message, f"Chat_id: {message.chat.id}\nThread_id: {
            message.message_thread_id}"
    )


@bot.message_handler(commands=["сканы"])  # Выгрузка заказов из ПИ
def echo_message_scanlog(msg):
    canUserUseMyBot = msg.from_user.id in ALLOW_USERS
    if canUserUseMyBot:
        st = datetime.now()
        msg.text = (
            msg.text.replace(",", "\n")
            .replace(" ", "\n")
            .replace("(", "\n")
            .replace(")", "\n")
        )
        # bot.reply_to(message, f"Привет, {message.from_user.full_name}, взял в работу, время {st}\nТвой user_id: {message.from_user.id}\n")
        my_msg = bot.reply_to(
            msg, f"Привет, {msg.from_user.full_name}, выгружаю сканлоги\n"
        )
        # reply = "ты написал мне: \"" + message.text + "\" длина твоего сообщения: " + str (len(message.text) )   + "\n"

        Orders = getOrders(msg.text)
        Pallets = getPallets(msg.text)
        TOTEs = getTOTEs(msg.text)

        returnMessage = f""
        checksortables = "/yes" in msg.text
        logger.info(
            f"{st}: Взял в работу сообщение от {
                msg.from_user.full_name} чекаем заказы в ПИ? {checksortables}"
        )
        if Orders:
            Orders = set(Orders)
            normalorders = set()
            notnormalorders = set()
            for order in Orders:
                if checksortables:
                    ord = getOrder(order)
                else:
                    ord = True
                if ord:
                    normalorders.add(order)
                else:
                    notnormalorders.add(order)
            if not normalorders:
                returnMessage += "Вы скинули только засылы?? зачем?????\n"
            else:
                for order in normalorders:
                    print(order)

                ass.getScan(normalorders)
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

                if checksortables:
                    returnMessage += f"Заказы есть в ПИ: {
                        ' '.join(normalorders)}\n"
                else:
                    returnMessage += f"Я не проверял есть ли заказы в ПИ, из-за отсутствия команды /yes\n"
            if notnormalorders:
                returnMessage += f"Засылы: {'\n'.join(notnormalorders)}\n"
        if TOTEs:
            TOTEs = set(TOTEs)
            returnMessage += f"ТОТы: {str(TOTEs)}\n"
        if Pallets:
            Pallets = set(Pallets)
            returnMessage += f"Паллеты: {str(Pallets)}\n"
    else:
        returnMessage += f"Ты не можешь взаимодействовать с ботом, обратись к @rusegg1\n {
            msg.from_user.id}"
    # bot.send_document(returnMessage,)
    returnMessage += f"Время выполнения скрипта:{
        (datetime.now()-st).total_seconds()}\n"
    if len(returnMessage) > 4096:
        for x in range(0, len(returnMessage), 4096):
            bot.reply_to(msg, "{}".format(returnMessage[x: x + 4096]))
    else:
        bot.edit_message_text(
            chat_id=my_msg.chat.id,
            message_id=my_msg.message_id,
            text=f"{my_msg.text}\n{returnMessage}",
        )


@bot.message_handler(commands=["откуда"])  # Выгрузка заказов из ПИ
def echo_message_scanlog(msg):
    st = datetime.now()
    msg.text = (
        msg.text.replace(",", "\n")
        .replace(" ", "\n")
        .replace("(", "\n")
        .replace(")", "\n")
    )
    # bot.reply_to(message, f"Привет, {message.from_user.full_name}, взял в работу, время {st}\nТвой user_id: {message.from_user.id}\n")
    my_msg = bot.reply_to(
        msg, f"Привет, {msg.from_user.full_name}, выгружаю сканлоги\n"
    )
    # reply = "ты написал мне: \"" + message.text + "\" длина твоего сообщения: " + str (len(message.text) )   + "\n"
    Orders = getOrders(msg.text)
    Pallets = getPallets(msg.text)
    TOTEs = getTOTEs(msg.text)
    returnMessage = f""
    canUserUseMyBot = msg.from_user.id in ALLOW_USERS

    if canUserUseMyBot:
        checksortables = "/yes" in msg.text
        logger.info(
            f"{st}: Взял в работу сообщение от {
                msg.from_user.full_name} чекаем заказы в ПИ? {checksortables}"
        )
        if Orders:
            Orders = set(Orders)
            normalorders = set()
            notnormalorders = set()
            for order in Orders:
                if checksortables:
                    ord = getOrder(order)
                else:
                    ord = True
                if ord:
                    normalorders.add(order)
                else:
                    notnormalorders.add(order)
            if not normalorders:
                returnMessage += "Вы скинули только засылы?? зачем?????\n"
            else:
                ass.getScan(normalorders)
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
                if checksortables:
                    returnMessage += f"Заказы есть в ПИ: {
                        ' '.join(normalorders)}\n"
                else:
                    returnMessage += f"Я не проверял есть ли заказы в ПИ, из-за отсутствия команды /yes\n"
            if notnormalorders:
                returnMessage += f"Засылы: {'\n'.join(notnormalorders)}\n"
        if TOTEs:
            TOTEs = set(TOTEs)
            returnMessage += f"ТОТы: {str(TOTEs)}\n"
        if Pallets:
            Pallets = set(Pallets)
            returnMessage += f"Паллеты: {str(Pallets)}\n"
    else:
        returnMessage += f"Ты не можешь взаимодействовать с ботом, обратись к @N0no0no\n {
            msg.from_user.id}"
    # bot.send_document(returnMessage,)
    returnMessage += f"Время выполнения скрипта:{
        (datetime.now()-st).total_seconds()}\n"
    if len(returnMessage) > 4096:
        for x in range(0, len(returnMessage), 4096):
            bot.reply_to(msg, "{}".format(returnMessage[x: x + 4096]))
    else:
        bot.edit_message_text(
            chat_id=my_msg.chat.id,
            message_id=my_msg.message_id,
            text=f"{my_msg.text}\n{returnMessage}",
        )


# Выгрузка заказов из ПИ
@bot.message_handler(
    func=lambda message: message.from_user.id == message.chat.id
    or message.chat.id == -1002008327465
)  # Выгрузка заказов из ПИ
def echo_message_bot(msg):
    st = datetime.now()
    msg.text = (
        msg.text.replace(",", "\n")
        .replace(" ", "\n")
        .replace("(", "\n")
        .replace(")", "\n")
    )
    # bot.reply_to(message, f"Привет, {message.from_user.full_name}, взял в работу, время {st}\nТвой user_id: {message.from_user.id}\n")
    my_msg = bot.reply_to(
        msg, f"Привет, {msg.from_user.full_name}, взял в работу\n")
    # reply = "ты написал мне: \"" + message.text + "\" длина твоего сообщения: " + str (len(message.text) )   + "\n"
    Orders = getOrders(msg.text)
    Pallets = getPallets(msg.text)
    TOTEs = getTOTEs(msg.text)
    returnMessage = f""
    canUserUseMyBot = msg.from_user.id in ALLOW_USERS

    if canUserUseMyBot:
        checksortables = "/no" in msg.text
        logger.info(
            f"{st}: Взял в работу сообщение от {
                msg.from_user.full_name} чекаем заказы в ПИ? {checksortables}"
        )
        if Orders:
            Orders = set(Orders)
            normalorders = set()
            notnormalorders = set()
            for order in Orders:
                if checksortables:
                    ord = getOrder(order)
                else:
                    ord = True
                if ord:
                    normalorders.add(order)
                else:
                    notnormalorders.add(order)
            if not normalorders:
                returnMessage += "Вы скинули только засылы?? зачем?????\n"
            else:
                ass.getOrd(normalorders)
                bot.send_document(
                    chat_id=msg.chat.id,
                    reply_to_message_id=msg.message_id,
                    document=open("orders.xlsx", "rb"),
                    visible_file_name=f"Orders.xlsx",
                )
                if checksortables:
                    returnMessage += f"Заказы есть в ПИ: {
                        ' '.join(normalorders)}\n"
                else:
                    returnMessage += f"Я не проверял есть ли заказы в ПИ, из-за отсутствия команды /yes\n"
            if notnormalorders:
                returnMessage += f"Засылы: {'\n'.join(notnormalorders)}\n"
        if TOTEs:
            TOTEs = set(TOTEs)
            returnMessage += f"ТОТы: {str(TOTEs)}\n"
        if Pallets:
            Pallets = set(Pallets)
            returnMessage += f"Паллеты: {str(Pallets)}\n"
    else:
        returnMessage += f"Ты не можешь взаимодействовать с ботом, обратись к @N0no0no\n {
            msg.from_user.id}"
    # bot.send_document(returnMessage,)
    returnMessage += f"Время выполнения скрипта:{
        (datetime.now()-st).total_seconds()}\n"
    if len(returnMessage) > 4096:
        for x in range(0, len(returnMessage), 4096):
            bot.reply_to(msg, "{}".format(returnMessage[x: x + 4096]))
    else:
        bot.edit_message_text(
            chat_id=my_msg.chat.id,
            message_id=my_msg.message_id,
            text=f"{my_msg.text}\n{returnMessage}",
        )


bot.infinity_polling(timeout=600, long_polling_timeout=600)