from datetime import datetime
import logging
import tempfile
import time
import requests
import telebot
import re
import urllib3
import configparser
import warnings
from pyzbar.pyzbar import decode as pyzdecode
from PIL import Image 
import cv2
from pylibdmtx.pylibdmtx import decode as pydecode
from updatesk import updatesk

# Logging setup
logging.basicConfig(filename="log.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG,
                    encoding="utf-8")
logger = logging.getLogger(__name__)
logging.info("Бот запускается...")

# Configuration setup
warnings.filterwarnings("ignore")
config = configparser.ConfigParser()
urllib3.disable_warnings()
config.read("config.ini")
logging.info(f"Загружен ЛОГ:\n{config}")

# Session setup
cookies = {'Session_id': config.get("Session", "Session_id")}
headers = {'sk': config.get('Session', 'sk')}
requestsSession = requests.Session()
requestsSession.verify = False
requestsSession.cookies.update(cookies)
requestsSession.headers.update(headers)
"""
Get order details from the sorting center API.

Args:
    order: The order ID to retrieve details for.

Returns:
    dict: The data of the order if successful, False otherwise.

Raises:
    No specific exceptions are raised within this function.
"""
def getOrder(order):
    json_data = {
        "params": [{"sortingCenterId": 1100000040, "orderId": order}],
        "path": f"/sorting-center/1100000040/orders/{order}",
    }

    response = requestsSession.post(
        "https://logistics.market.yandex.ru/api/resolve/?r=sortingCenter/orders/resolveOrder:resolveOrder",
        json=json_data,
        verify=False
    )
    if response.status_code != 200:
        sk = updatesk(cookies)
        config.set("Session", "sk", sk)
        requestsSession.headers.update({'sk': sk})
        with open('config.ini', 'w', encoding="utf8") as configfile:
            config.write(configfile)
        response = requestsSession.post(
            "https://logistics.market.yandex.ru/api/resolve/?r=sortingCenter/orders/resolveOrder:resolveOrder",
            json=json_data,
            verify=False
        )
    results = response.json().get("results", [])
    return results[0]["data"] if results and "data" in results[0].keys() else False

def getSortablesOfOrder(order):
    json_data = {
        "params": [{
            "sortableStatuses": [], "stages": [], "orderExternalId": order,
            "inboundIdTitle": "", "outboundIdTitle": "", "groupingDirectionId": "",
            "groupingDirectionName": "", "sortingCenterId": 1100000040, "page": 0,
            "size": 20, "sortableTypes": [], "crossDockOnly": False,
        }],
        "path": "/sorting-center/1100000040/sortables?sortableTypes=&sortableStatuses=&sortableStatusesLeafs=&orderExternalId=423501618&inboundIdTitle=&outboundIdTitle=&groupingDirectionId=&groupingDirectionName=",
    }
    sortables = requestsSession.post(
        "https://logistics.market.yandex.ru/api/resolve/?r=sortingCenter/sortables/resolveSortableReport:resolveSortableReport",
        json=json_data,
        verify=False
    )
    if sortables.status_code == 200:
        return sortables.json()["results"][0]["data"]["content"]
    return []

def getOrders(inputstring):
    regex = r"^LO-\d{9}|^\d{9}|^VOZ_FBS_\d{8}|^PVZ_FBS_RET_\d{6}|^VOZ_FF_\d{8}|^VOZ_MK_\d{7}|^PVZ_FBY_RET_\d{6}"
    return re.findall(regex, inputstring, re.MULTILINE)

def getPallets(inputstring):
    regex = r"^F1.{18}$"
    return re.findall(regex, inputstring, re.MULTILINE)

def getTOTEs(inputstring):
    regex = r"^F2.{18}$"
    return re.findall(regex, inputstring, re.MULTILINE)

ALLOW_USERS = [
    5291102003, 1063498880, 6478014074, 1019990315, 1133129646,
    6946675945, 1641769105, 6478014074, 1213362983
]

API_TOKEN = config.get("BOT", "API_TOKEN")
print("Запуск бота")
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(content_types=['photo'], func=lambda message: message.from_user.id == message.chat.id)
def photo(message):
    print('получил изображение')
    fileID = message.photo[-1].file_id
    file_info = bot.get_file(fileID)
    downloaded_file = bot.download_file(file_info.file_path)

    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp.write(downloaded_file)
        temp_path = temp.name

    image = cv2.imread(temp_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    barcodeScanners = [pyzdecode(gray)]
    decoder = cv2.QRCodeDetector()
    retval, decoded_info, points, straight_qrcode = decoder.detectAndDecodeMulti(gray)
    barcodeScanners.append(decoded_info)
    barcodeScanners.append(pydecode(gray))

    print(barcodeScanners)
    decoded = {qrcode.data.decode() for qrcode in barcodeScanners[0]} if barcodeScanners[0] else set()
    if retval:
        decoded.update(decoded_info)
    if barcodeScanners[2]:
        decoded.update(qrcode.data.decode() for qrcode in barcodeScanners[2])

    if decoded:
        forward = bot.forward_message(chat_id=-1002205631792, from_chat_id=message.chat.id, message_id=message.id, message_thread_id=88)
        bot.reply_to(forward, f"{'\n'.join(decoded)}")
    else:
        print("не распознал\n")

@bot.message_handler(commands=['id'])
def echo_message(message):
    bot.reply_to(message, f"Chat_id: {message.chat.id}\nThread_id: {message.message_thread_id}")

@bot.message_handler(commands=['bot'])
def echo_message(msg): 
    st = datetime.now()
    msg.text = msg.text.replace(',', '\n').replace(' ', '\n').replace('(', '\n').replace(')', '\n')
    my_msg = bot.reply_to(msg, f"Привет, {msg.from_user.full_name}, взял в работу\n")
    Orders = getOrders(msg.text)
    Pallets = getPallets(msg.text)
    TOTEs = getTOTEs(msg.text)
    returnMessage = ""
    canUserUseMyBot = msg.from_user.id in ALLOW_USERS

    if canUserUseMyBot:
        checksortables = "/no" not in msg.text
        logging.info(f"{st}: Взял в работу сообщение от {msg.from_user.full_name} чекаем заказы в ПИ? {checksortables}")
        if Orders:
            Orders = set(Orders)
            normalorders = set()
            notnormalorders = set()
            for order in Orders:
                order = getOrder(order) if checksortables else True
                if order: normalorders.add(order) 
                else: notnormalorders.add(order)
            if not normalorders:
                returnMessage += "Вы скинули только засылы?? зачем?????\n"
            else:
                ass.getOrd(normalorders)
                bot.send_document(
                    chat_id=msg.chat.id,
                    reply_to_message_id=msg.message_id,
                    document=open("orders.xlsx", 'rb'),
                    visible_file_name="Orders.xlsx",
                )
                if checksortables: returnMessage += f"Заказы есть в ПИ: {' '.join(normalorders)}\n"
                else: returnMessage += f"Я не проверял есть ли заказы в ПИ, из-за присутствия команды /no\n"
            if notnormalorders:
                returnMessage += f"Засылы: {'\n'.join(notnormalorders)}\n"
                returnMessage += f"Засылы: {'\n'.join(notnormalorders)}\n"
        if TOTEs:
            TOTEs = set(TOTEs)
            returnMessage += f"ТОТы: {TOTEs}\n"
        if Pallets:
            Pallets = set(Pallets)
            returnMessage += f"Паллеты: {Pallets}\n"
    else: returnMessage += f"Ты не можешь взаимодействовать с ботом, обратись к @N0no0no\n {msg.from_user.id}"
    # bot.send_document(returnMessage,)
    returnMessage += f"Время выполнения скрипта:{(datetime.now()-st).total_seconds()}\n"
    if len(returnMessage) > 4096:
        for x in range(0, len(returnMessage), 4096):
            bot.reply_to(msg, f'{returnMessage[x:x + 4096]}')
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
debug = False
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
