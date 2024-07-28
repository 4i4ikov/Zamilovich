# import datetime
# import asyncio
from datetime import datetime
# import aiohttp
# import json
import logging
# import sys
import tempfile
import time
import requests
# from pprint import pprint
# from bs4 import BeautifulSoup
import telebot
import re
# import pandas as pd
# from requests.exceptions import RequestException
import urllib3
import asinhrom as ass
import configparser
import warnings
from pyzbar.pyzbar import decode as pyzdecode
from PIL import Image 
import cv2
from pylibdmtx.pylibdmtx import decode as pydecode
from updatesk import updatesk

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

logging.basicConfig(filename="log.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG,
                    encoding="utf-8")
logger = logging.getLogger(__name__)

logger.addHandler(ch)
logging.info("Бот запускается...")
# EMOJI = ["👎","👍", "🤔"]


warnings.filterwarnings("ignore")
config = configparser.ConfigParser()
urllib3.disable_warnings()
config.read("config.ini")
logging.info(f"Загружен ЛОГ:\n{config}")
cookies = {
    'Session_id': config.get("Session","Session_id"),
}
headers = {
    'sk': config.get('Session','sk'),
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
        verify=False
    )
    if response.status_code != 200:
        sk = updatesk(cookies)
        config.set("Session","sk",sk)
        requestsSession.headers.update({
    'sk': config.get('Session','sk'),
})
        with open('config.ini','w', encoding="utf8") as configfile:
            config.write(configfile)
        response = requestsSession.post(
        "https://logistics.market.yandex.ru/api/resolve/?r=sortingCenter/orders/resolveOrder:resolveOrder",
        json=json_data,
        verify=False
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
        verify=False
    )
    if sortables.status_code == 200:
        sortables = sortables.json()["results"][0]["data"]["content"]

    return sortables


def getOrders(inputstring):
    RegularExpressionForOrders = r"^LO-\d{9}|^\d{9}|^VOZ_FBS_\d{8}|^PVZ_FBS_RET_\d{6}|^VOZ_FF_\d{8}|^VOZ_MK_\d{7}|^PVZ_FBY_RET_\d{6}"
    return re.findall(RegularExpressionForOrders, inputstring, re.MULTILINE)


def getPallets(inputstring):
    RegularExpressionForPallets = r"^F1.{18}$"
    return re.findall(RegularExpressionForPallets, inputstring, re.MULTILINE)


def getTOTEs(inputstring):
    RegularExpressionForTOTEs = r"^F2.{18}$"
    return re.findall(RegularExpressionForTOTEs, inputstring, re.MULTILINE)
ALLOW_USERS = [
    5291102003,
    1063498880,
    6478014074,
    1019990315,
    1133129646,
    6946675945,
    1641769105,
    6478014074,
    1213362983
]


API_TOKEN = config.get("BOT","API_TOKEN")
print ("Запуск бота")
bot = telebot.TeleBot(API_TOKEN)
# Распознать ШК заказов по фото
@bot.message_handler(content_types=['photo'], func=lambda message: message.from_user.id == message.chat.id)
def photo(message):
    # if (message.caption and "qr" in message.caption):
    print('получил изображение')
    # bot.set_message_reaction(message.chat.id,message.id,[telebot.types.ReactionTypeEmoji(EMOJI[2])])
    fileID = message.photo[-1].file_id
    file_info = bot.get_file(fileID)

    downloaded_file = bot.download_file(file_info.file_path)


    temp = tempfile.NamedTemporaryFile(delete_on_close=False)
    temp.write(downloaded_file)
    temp.close()

    with open(temp.name, mode='rb') as f:
        image = cv2.imread(temp.name)
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # cv2.imwrite(temp[1].name,gray)
    except Exception as err: print(err)
    else:
        gray = image
        # cv2.imwrite(temp[1].name,gray)

# The line `barcodeScanners = [` is initializing a list named `barcodeScanners`. This list will be
# used to store the results of barcode decoding from different methods. Each element in the list will
# hold the decoded information from a specific barcode scanning method.
    barcodeScanners = [pyzdecode(gray)]
    decoder = cv2.QRCodeDetector()
    retval, decoded_info, points, straight_qrcode = decoder.detectAndDecodeMulti(gray)

    barcodeScanners.append(decoded_info)

    barcodeScanners.append(pydecode(gray))

    print(barcodeScanners)
    decoded = set()
    if barcodeScanners[0]:
        for qrcode in barcodeScanners[0]:decoded.add( qrcode.data.decode())
    if retval:
        for qrcode in barcodeScanners[1]:
            decoded.add(qrcode)
    if barcodeScanners[2]:
        for qrcode in barcodeScanners[2]:decoded.add( qrcode.data.decode())

    # with open("image.jpg", 'wb+') as new_file:
    #     new_file.write(downloaded_file)
    # bot.send_photo(chat_id=message.chat.id,message_thread_id=message.message_thread_id,reply_to_message_id=message.message_id,photo=open("gray.png","rb"))
    if (decoded):
        # bot.set_message_reaction(message.chat.id,message.id,[telebot.types.ReactionTypeEmoji(EMOJI[1])])
        forward = bot.forward_message(chat_id=-1002205631792,from_chat_id=message.chat.id,message_id=message.id,message_thread_id=88)
        bot.reply_to(forward,f"{'\n'.join(decoded)}")
    else:
        print("не распознал\n")
        # forward = bot.forward_message(chat_id=-1002205631792,from_chat_id=message.chat.id,message_id=message.id,message_thread_id=94)
        # bot.reply_to(forward,f"Не смог распознать.")

# Узнать ID текущего чата
@bot.message_handler(commands=['id']) # Узнать ID чата
def echo_message(message):
    bot.reply_to(message,f"Chat_id: {message.chat.id}\nThread_id: {message.message_thread_id}")



# Выгрузка заказов из ПИ
@bot.message_handler(commands=['bot']) #Выгрузка заказов из ПИ
def echo_message(msg): 
    st = datetime.now()
    msg.text = msg.text.replace(',','\n').replace(' ','\n').replace('(','\n').replace(')','\n')
    # bot.reply_to(message, f"Привет, {message.from_user.full_name}, взял в работу, время {st}\nТвой user_id: {message.from_user.id}\n")
    my_msg = bot.reply_to(msg, f"Привет, {msg.from_user.full_name}, взял в работу\n")
    # reply = "ты написал мне: \"" + message.text + "\" длина твоего сообщения: " + str (len(message.text) )   + "\n"
    Orders = getOrders(msg.text)
    Pallets = getPallets(msg.text)
    TOTEs = getTOTEs(msg.text)
    returnMessage = f""
    canUserUseMyBot = msg.from_user.id in ALLOW_USERS

    if canUserUseMyBot:
        checksortables = not ("/no" in msg.text)
        logging.info(f"{st}: Взял в работу сообщение от {msg.from_user.full_name} чекаем заказы в ПИ? {checksortables}")
        if Orders:
            Orders = set(Orders)
            normalorders = set ()
            notnormalorders = set()
            for order in Orders:
                if checksortables:
                    ord = getOrder(order)
                else:
                    ord = True
                if ord: normalorders.add(order) 
                else: notnormalorders.add(order)
            if not normalorders:
                returnMessage += "Вы скинули только засылы?? зачем?????\n"
            else:
                ass.getOrd(normalorders)
                bot.send_document(chat_id=msg.chat.id,reply_to_message_id=msg.message_id,document=open("orders.xlsx",'rb'),visible_file_name=f"Orders.xlsx")
                if checksortables: returnMessage += f"Заказы есть в ПИ: {' '.join(normalorders)}\n"
                else: returnMessage += f"Я не проверял есть ли заказы в ПИ, из-за присутствия команды /no\n"
            if notnormalorders:
                returnMessage += f"Засылы: {'\n'.join(notnormalorders)}\n"  
        if TOTEs:
            TOTEs = set(TOTEs)
            returnMessage += f"ТОТы: {str(TOTEs)}\n"
        if Pallets:
            Pallets = set(Pallets)
            returnMessage += f"Паллеты: {str(Pallets)}\n"
    else: returnMessage += f"Ты не можешь взаимодействовать с ботом, обратись к @N0no0no\n {msg.from_user.id}"
    # bot.send_document(returnMessage,)
    returnMessage += f"Время выполнения скрипта:{(datetime.now()-st).total_seconds()}\n"
    if len(returnMessage) > 4096:
        for x in range(0, len(returnMessage), 4096):
                bot.reply_to(msg, '{}'.format(returnMessage[x:x + 4096]))
    else: bot.edit_message_text(chat_id=my_msg.chat.id,message_id=my_msg.message_id, text=f'{my_msg.text}\n{returnMessage}')   
     
    # if Orders:
    #     Orders = set(Orders)
    #     for i in Orders:
    #         reply = ""
    #         Order = str(i)
    #         sortables = getSortablesOfOrder(Order)
    #         # pprint(sortables)
    #         getOrd = getOrder(Order)
    #         reply += Order + "\n"

    #         if getOrd != "" :
    #             wgh = getOrd['weightAndDimensions']
    #             reply += f"Статус: {getOrd["ffStatus"]}\nВГХ: {wgh["width"]}x{wgh["height"]}x{wgh["length"]}, вес: {wgh["weight"]}кг\n"
    #         else: reply += "Заказ не найден в ПИ\n"
    #         SortablesCount = 0
    #         for sortable in sortables:
    #              if "orderExternalId" in sortable.keys() and sortable["orderExternalId"].lower() == Order.lower():
    #                 SortablesCount += 1
    #                 inside = ""
    #                 for i in sortable.keys():
    #                     match i:
    #                         case "cellName":
    #                             inside = " - " + sortable["cellName"]
    #                         case "lotExternalId":
    #                             inside = " - " + sortable["lotExternalId"]

    #                 reply += f"{sortable["sortableBarcode"]} - {sortable["stageDisplayName"]}{inside}\n"
    #         if not SortablesCount:
    #             reply += f"Грузоместа не найдены"
    #         bot.reply_to(message, reply)
debug = True
if not debug:
    while True:
        try:
            logging.info("Бот запущен, ребята, работает!!1")
            bot.polling()
        except Exception as err:
            print(err)
            time.sleep(10)
            print("* Reconnecting.")
bot.polling()