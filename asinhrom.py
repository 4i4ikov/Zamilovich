import asyncio
from os import system
import os
import re
import aiohttp
import pandas as pd
import telebot
import configparser
from urllib.parse import unquote
config = configparser.ConfigParser()
config.read("config.ini")
cookies = {
    'Session_id': config.get("Session","Session_id"),
}
headers = {
    'sk': config.get('Session','sk'),
}
async def gather_with_concurrency(n, *tasks):
    semaphore = asyncio.Semaphore(n)
    async def sem_task(task):
        async with semaphore:
            return await task
    return await asyncio.gather(*(sem_task(task) for task in tasks))

def get_filename(response):
    header = response.headers.get('Content-Disposition')
    if not header: return False
    filename = re.findall(r"filename\*=UTF-8''(.+)", header)
    filename = unquote(filename[0])
    return str(filename)
async def get_async(url, session, results):
    async with session.get(url) as response:
        i = url.split('=')[-1]
        if response.status == 200:
            obj = await response.read()
            filename = get_filename(response)
            results[filename] = obj

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
    all_frame.to_excel('scans.xlsx',index=False)
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

def getDocuments(urls,day):
    asyncio.run(getFile(urls,day),debug=True)

async def getFile(urls,day):
    session = aiohttp.ClientSession(cookies=cookies, headers=headers)
    results = {}
    conc_req = 40
    await gather_with_concurrency(conc_req, *[get_async(i, session, results) for i in urls.values()])
    await session.close()
    all_file_frames = []
    os.mkdir("rashodilis")
    os.mkdir("rashodilis/{0}".format(day))
    # writer = pd.ExcelWriter("files.xlsx", engine = 'openpyxl')
    for i, j in results.items():
        with open(f'./rashodilis/{day}/{i}',"wb+") as f:
            f.write(j)
        # tab = pd.read_excel(j)
        # tab.to_excel(writer,sheet_name=f"test{i}")
        # all_file_frames.append(tab)
    # all_frame = pd.concat(all_file_frames)
   
    # writer.close()
    # all_frame.to_excel('files.xlsx',index=False)

# def getAccepterdButNotSorted(urls):
#     asyncio.run(getFile(urls))

# asyncio.run(getOrdersStatuses())
