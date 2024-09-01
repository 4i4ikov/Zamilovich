import asyncio
import configparser
import json
import logging
import warnings
from datetime import date, datetime, time
from pprint import pprint

import aiohttp
import pandas as pd
import requests
# from pprint import pprint
# from bs4 import BeautifulSoup
import telebot
import urllib3

import updatesk as updatesk

# import json

logging.basicConfig(filename="log.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG,
                    encoding="utf-8")
logging.info("Running Urban Planning")
logger = logging.getLogger('urbanGUI')
warnings.filterwarnings("ignore")
urllib3.disable_warnings()

st = datetime.now()
config = configparser.ConfigParser()
config.read("config.ini")
cookies = {
    'Session_id': config.get("Session", "Session_id"),
}
headers = {
    'sk': config.get('Session', 'sk'),
}

API_TOKEN = config.get("BOT", "API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)
chat_id = '-4143093216'

today = str(date.today())
UrlForRequest = 'https://logistics.market.yandex.ru/api/resolve/?r=sortingCenter/orders/resolveOrder:resolveOrder'


# ----------
async def gather_with_concurrency(n, *tasks):
    semaphore = asyncio.Semaphore(n)

    async def sem_task(task):
        async with semaphore:
            return await task
    return await asyncio.gather(*(sem_task(task) for task in tasks))


# async def get_async(url, session, results):
#     async with session.get(url) as response:
#         i = url.split('=')[-1]
#         if response.status == 200:
#             obj = await response.read()
#             results[i] = obj

async def post_async(url, session, data, results):
    async with session as session:
        response = await session.post(url=url, json=data, ssl=False)
        if response.status != 200:
            pprint(response)
        if response.status == 200:
            results.append(response)


async def getOrdersVGH(orders):
    session = aiohttp.ClientSession(cookies=cookies, headers=headers)
    results = []
    datas = [{  # ПАНЕЛЬ ГРУЗОМЕСТ
        'params': [
            {
                'sortingCenterId': 1100000040,
                'orderId': order,
            },
        ],
        'path': '/sorting-center/1100000040/sortables/10000064983960',
        # 'path': '/sorting-center/1100000040/stages',
    } for order in orders]

    conc_req = 40
    await gather_with_concurrency(conc_req, *[post_async(UrlForRequest, session, i, results) for i in datas])
    # await session.close()
    pprint("nothingf")
    pprint(json)
    # all_file_frames = []
    # for i in results:
    #     tab = pd.read_excel(i)
    #     all_file_frames.append(tab)
    # all_frame = pd.concat(all_file_frames)
    # all_frame.to_excel('orders.xlsx',index=False)


def getOrd(orders):
    asyncio.run(getOrdersVGH(orders), debug=True)


getOrd(["456427178"])
# ------

# ForTest = response.json()["results"][0]["data"]["content"]
# panda = pd.DataFrame(ForTest)
# panda.to_excel('test.xlsx',index=False)
# bot.send_document(chat_id=chat_id,document=open("test.xlsx",'rb'),visible_file_name=f"TEST.xlsx")


message = ""


message += f"Время выполнения скрипта: {
    round((datetime.now()-st).total_seconds(), 2)} сек."
bot.send_message(chat_id, message, parse_mode='HTML')

with open('config.ini', 'w', encoding="utf8") as configfile:
    config.write(configfile)

# with open('somefile.json', 'w',encoding="utf8") as outfile:

#     json.dump(response.json(), outfile,indent=4,ensure_ascii=False)
