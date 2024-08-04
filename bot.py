import asyncio
import logging
import tempfile
import aiohttp
import pandas as pd
from styleframe import StyleFrame, Styler, utils
import requests
import telebot
import telebot.types as types
import re
import urllib3
import configparser
import warnings
import json
from pyzbar.pyzbar import decode as pyzdecode
from PIL import Image 
import cv2
from pylibdmtx.pylibdmtx import decode as pydecode
from datetime import datetime

async def gather_with_concurrency(n, *tasks):
    semaphore = asyncio.Semaphore(n)
    async def sem_task(task):
        async with semaphore:
            return await task
    return await asyncio.gather(*(sem_task(task) for task in tasks))


async def get_async(url, session, results):
    async with session.get(url) as response:
        i = url.split('=')[-1]
        if response.status == 200:
            obj = await response.read()
            results[i] = obj

default = [
    "437665887",
    "437667076",
    "PVZ_FBS_RET_873907",
    "437564522",
    "437665576",
    "LO-361255578",
]
async def getSortablesScanlog(sortableIds):
    session = aiohttp.ClientSession(cookies=cookies, headers=headers)
    results = {}

    urls = [f"https://logistics.market.yandex.ru/api/sorting-center/1100000040/sortable/scanlog?sortableId={i}" for i in sortableIds]

    conc_req = 40
    
    await gather_with_concurrency(conc_req, *[get_async(i, session, results) for i in urls])
    await session.close()
    API_TOKEN = config.get("BOT","API_TOKEN")

    bot = telebot.TeleBot(API_TOKEN)
    for i, j in results.items():
        with open(f"./papka/{i}.xlsx",'wb') as f: 
            f.write(j)
            bot.send_document(-4143093216,j,visible_file_name=f"{i}.xlsx")
    return results.items()

async def getOrdersScanlog(sortableIds):
    session = aiohttp.ClientSession(cookies=cookies, headers=headers)
    results = {}

    urls = [f"https://logistics.market.yandex.ru/api/sorting-center/1100000040/orders/{i}/scanLog.xlsx" for i in sortableIds]

    conc_req = 40

    await gather_with_concurrency(conc_req, *[get_async(i, session, results) for i in urls])
    await session.close()
    all_file_frames = []
    for j in results.values():
        tab = pd.read_excel(j)
        all_file_frames.append(tab)
    all_frame = pd.concat(all_file_frames)
    all_frame.reset_index(drop = True,inplace = True)
    excelWriter = StyleFrame.ExcelWriter('scans.xlsx')
    styler_obj=Styler(
        # bg_color=utils.colors.blue,
        bold=False,
        font_size=8
    )
    styledDataFrame = StyleFrame(all_frame,styler_obj=styler_obj)
    styledDataFrame.set_column_width(columns=styledDataFrame.columns,width=13) # type: ignore
    best = styledDataFrame.columns.values.tolist()
    styledDataFrame.apply_headers_style(Styler(bold=False, font_size=8))
    styledDataFrame.to_excel(excel_writer=excelWriter, row_to_add_filters=0,index=False)
    excelWriter.close()
    print('Скачал сканлоги, дальше осталось их скинуть..')

async def getOrdersStatuses(orders):
    session = aiohttp.ClientSession(cookies=cookies, headers=headers)
    results = {}
    urls = [f"https://logistics.market.yandex.ru/api/sorting-center/1100000040/sortables/download?orderExternalId={i}" for i in orders]
    conc_req = 40
    await gather_with_concurrency(conc_req, *[get_async(i, session, results) for i in urls])
    await session.close()

    all_file_frames = []
    for j in results.values():
        tab = pd.read_excel(j)
        all_file_frames.append(tab)
    all_frame = pd.concat(all_file_frames)
    
    all_frame.to_excel('orders.xlsx',index=False)

def getOrd(orders):
    asyncio.run(getOrdersStatuses(orders), debug=True)

def getScan(orders):
    asyncio.run(getOrdersScanlog(orders), debug=True)

async def getFile(urls):
    session = aiohttp.ClientSession(cookies=cookies, headers=headers)
    results = {}
    conc_req = 40
    await gather_with_concurrency(conc_req, *[get_async(i, session, results) for i in urls])
    await session.close()
    all_file_frames = []
    for j in results.values():
        tab = pd.read_excel(j)
        all_file_frames.append(tab)
    all_frame = pd.concat(all_file_frames)
    all_frame.to_excel('AcceptedButNotSorted.xlsx',index=False)
def getAccepterdButNotSorted(urls):
    asyncio.run(getFile(urls))







# Setup logging
logging.basicConfig(filename="log.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG,
                    encoding="utf-8")
logger = logging.getLogger(__name__)
logging.info("Бот запускается...")

# Disable warnings
# warnings.filterwarnings("ignore")
# urllib3.disable_warnings()

# Load configuration
config = configparser.ConfigParser()
config.read("config.ini")
logging.info(f"Загружен ЛОГ:\n{config}")

# Setup requests session
cookies = {'Session_id': config.get("Session", "Session_id")}
headers = {'sk': config.get('Session', 'sk')}
requestsSession = requests.Session()
requestsSession.verify = False
requestsSession.cookies.update(cookies)
requestsSession.headers.update(headers)

def updatesk (cookies):
    response = requests.patch('https://logistics.market.yandex.ru/api/session',  cookies=cookies, verify=False)
    sk = ""
    if response.status_code==200:
        return response.json().get("user").get("sk")

# Compile regular expressions
ORDERS_REGEX = re.compile(r"^LO-\d{9}|^\d{9}|^VOZ_FBS_\d{8}|^PVZ_FBS_RET_\d{6}|^VOZ_FF_\d{8}|^VOZ_MK_\d{7}|^PVZ_FBY_RET_\d{6}", re.MULTILINE)
PALLET_REGEX = re.compile(r"^F1.{18}$", re.MULTILINE)
TOTE_REGEX = re.compile(r"^F2.{18}$", re.MULTILINE)

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
        requestsSession.headers.update({'sk': config.get('Session', 'sk')})
        with open('config.ini', 'w', encoding="utf8") as configfile:
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
    return ORDERS_REGEX.findall(inputstring)

def getPallets(inputstring):
    return PALLET_REGEX.findall(inputstring)

def getTOTEs(inputstring):
    return TOTE_REGEX.findall(inputstring)

ALLOW_USERS = [
    5291102003, 1063498880, 6478014074, 1019990315, 1133129646,
    6946675945, 1641769105, 6478014074, 1213362983
]

API_TOKEN = config.get("BOT", "API_TOKEN")
print("Запуск бота")
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['stop'])
def stop(message):
    bot.stop_bot()

# @bot.message_handler(content_types=['photo'], func=lambda message: message.chat.id == -904145156)
def photo(message):
    print('получил изображение')
    fileID = message.photo[-1].file_id
    file_info = bot.get_file(fileID)
    downloaded_file = bot.download_file(file_info.file_path)

    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp.write(downloaded_file)
        temp_path = temp.name

    if decoded := scanBarcode(temp_path):
        forward = bot.forward_message(chat_id=-1002205631792, from_chat_id=message.chat.id, message_id=message.id, message_thread_id=88)
        bot.reply_to(forward, '\n'.join(decoded))
    else:
        print("не распознал\n")

def scanBarcode(temp_path):
    image = cv2.imread(temp_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image is not None else image

    barcodeScanners = [pyzdecode(gray)]
    decoder = cv2.QRCodeDetector()
    retval, decoded_info, points, straight_qrcode = decoder.detectAndDecodeMulti(gray)
    barcodeScanners.append(decoded_info) # type: ignore
    barcodeScanners.append(pydecode(gray))
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
    return decoded

@bot.message_handler(commands=['id'])
def echo_id(message):
    bot.reply_to(message, f"Chat_id: {message.chat.id}\nThread_id: {message.message_thread_id}")



def check_message(message):
    return message.chat.type == 'private' or message.chat.id == -6946675945


@bot.message_handler(func=check_message)
def buttons(message):
    markup = get_markup(message)
    bot.send_message(chat_id=message.chat.id,message_thread_id=message.message_thread_id, text="Что вы хотите получить?", reply_markup=markup)

def get_markup(message):
    callback_data = {
        "m" :message.id,
        "u" : message.from_user.id,
        "t": "/scans",
    }

    scan_logs_button = types.InlineKeyboardButton(text="Сканлоги",callback_data=json.dumps(callback_data))
    callback_data["t"] = "/bot"
    statuses_button = types.InlineKeyboardButton(text="Статусы",callback_data=json.dumps(callback_data))
    callback_data["t"] = "/vgh"
    vgh_button = types.InlineKeyboardButton(text="ВГХ",callback_data=json.dumps(callback_data))
    markup = types.InlineKeyboardMarkup()
    markup.add(scan_logs_button,statuses_button,vgh_button)
    return markup
    
    
def request_scanlogs(message):
    bot.send_message(chat_id=message.chat.id,message_thread_id=message.message_thread_id,text="Отправьте номера заказов для получения сканлогов :)")
    bot.register_next_step_handler(message, echo_message_scanlog)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            data_json = json.loads(call.data)
            msg = bot.forward_message(chat_id=-4283452246,from_chat_id=data_json["u"],message_id=data_json["m"])
            if data_json["t"] == "/scans":
                echo_message_scanlog(msg,data_json)
            print(data_json)
    except Exception as e:
        print(repr(e))




@bot.message_handler(commands=['scans'])

def echo_message_scanlog(msg, reply_msg = None):
    if reply_msg:
        msg.chat.id = reply_msg["u"]
        msg.id = reply_msg["m"]
        msg.message_id = reply_msg["m"]
    st = datetime.now()
    MESSAGE = format_input_message(msg.text)
    my_msg = bot.reply_to(msg, f"Привет, {msg.from_user.full_name}, выгружаю сканлоги\n")
    Orders, Pallets, TOTEs = get_all_types_of_places(MESSAGE)
    returnMessage = ""
    canUserUseMyBot = msg.from_user.id in ALLOW_USERS

    if canUserUseMyBot:
        # checksortables = "/no" not in MESSAGE
        # logging.info(f"{st}: Взял в работу сообщение от {msg.from_user.full_name} чекаем заказы в ПИ? {checksortables}")
        # if Orders:
        #     Orders = set(Orders)
        #     normalorders = set()
        #     notnormalorders = set()
        #     for order in Orders:
        #         buffer_order = getOrder(order) if checksortables else True
        #         if buffer_order:
        #             normalorders.add(order)
        #         else:
        #             notnormalorders.add(order)
        #     if not normalorders:
        #         returnMessage += "Вы скинули только засылы?? зачем?????\n"
        #     else:
        getScan(Orders)
        bot.send_document(chat_id=msg.chat.id, reply_to_message_id=msg.message_id, document=open("scans.xlsx", 'rb'), visible_file_name="Scans.xlsx")
                # if checksortables:
                #     returnMessage += f"Заказы есть в ПИ: {' '.join(normalorders)}\n"
                # else:
                #     returnMessage += f"Я не проверял есть ли заказы в ПИ, из-за присутствия команды /no\n"
            # if notnormalorders:
            #     returnMessage += f"Засылы: {'\n'.join(notnormalorders)}\n"
        if TOTEs:
            returnMessage += f"ТОТы: {TOTEs}\n"
        if Pallets:
            returnMessage += f"Паллеты: {Pallets}\n"
    else:
        returnMessage += f"Ты не можешь взаимодействовать с ботом, обратись к @N0no0no\n {msg.from_user.id}"
    returnMessage += f"Время выполнения скрипта:{(datetime.now() - st).total_seconds()}\n"
    if len(returnMessage) > 4096:
        for x in range(0, len(returnMessage), 4096):
            bot.reply_to(msg, f'{returnMessage[x:x + 4096]}')
    else:
        bot.edit_message_text(chat_id=my_msg.chat.id, message_id=my_msg.message_id, text=returnMessage)

def get_all_types_of_places(MESSAGE):
    Orders = set(getOrders(MESSAGE))
    Pallets = getPallets(MESSAGE)
    TOTEs = getTOTEs(MESSAGE)
    return Orders, Pallets, TOTEs

@bot.message_handler(func=lambda message: message.from_user.id == message.chat.id)
def echo_message_bot(msg):
    START_TIME = datetime.now()
    MESSAGE = format_input_message(msg.text)
    my_msg = bot.reply_to(msg, f"Привет, {msg.from_user.full_name}, взял в работу\n")
    Orders, Pallets, TOTEs = get_all_types_of_places(MESSAGE)
    returnMessage = ""
    canUserUseMyBot = msg.from_user.id in ALLOW_USERS

    if canUserUseMyBot:
        checksortables = "/no" not in MESSAGE
        logging.info(f"{START_TIME}: Взял в работу сообщение от {msg.from_user.full_name} чекаем заказы в ПИ? {checksortables}")
        if Orders:
            Orders = set(Orders)
            normalorders = set()
            notnormalorders = set()
            for order in Orders:
                buffered_order = getOrder(order) if checksortables else True
                if buffered_order:
                    normalorders.add(order)
                else:
                    notnormalorders.add(order)
            if not normalorders:
                returnMessage += "Вы скинули только засылы?? зачем?????\n"
            else:
                getOrd(normalorders)
                bot.send_document(chat_id=msg.chat.id, reply_to_message_id=msg.message_id, document=open("orders.xlsx", 'rb'), visible_file_name="Orders.xlsx")
                if checksortables:
                    returnMessage += f"Заказы есть в ПИ: {' '.join(normalorders)}\n"
                else:
                    returnMessage += f"Я не проверял есть ли заказы в ПИ, из-за присутствия команды /no\n"
            if notnormalorders:
                returnMessage += f"Засылы: {'\n'.join(notnormalorders)}\n"
        if TOTEs:
            returnMessage += f"ТОТы: {TOTEs}\n"
        if Pallets:
            returnMessage += f"Паллеты: {Pallets}\n"
    else:
        returnMessage += f"Ты не можешь взаимодействовать с ботом, обратись к @N0no0no\n {msg.from_user.id}"
    returnMessage += f"Время выполнения скрипта:{(datetime.now() - START_TIME).total_seconds()}\n"
    if len(returnMessage) > 4096:
        for x in range(0, len(returnMessage), 4096):
            bot.reply_to(msg, f'{returnMessage[x:x + 4096]}')
    else:
        bot.edit_message_text(chat_id=my_msg.chat.id, message_id=my_msg.message_id, text=returnMessage)

def format_input_message(text):
    return text.replace(',', '\n').replace(' ', '\n').replace('(', '\n').replace(')', '\n')


bot.polling()
# bot.infinity_polling(timeout=120, long_polling_timeout=5)
