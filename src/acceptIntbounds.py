import asyncio
import configparser
import re

# import updatesk as updatesk
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import unquote

import aiohttp
import pandas as pd
import requests
import telebot

st = datetime.now()
config = configparser.ConfigParser()
config.read("config.ini")
cookies = {
    'Session_id': config.get("Session", "Session_id"),
}
headers = {
    'sk': config.get('Session', 'sk'),
}





def updatesk(cookies, config, requestsSession):
    response = requests.patch(
        'https://logistics.market.yandex.ru/api/session',  cookies=cookies, verify=False)
    sk = ""
    if response.status_code == 200:
        sk = response.json().get("user").get("sk")
        headers = {'sk': sk}
        requestsSession.headers.update(headers)
        config.set("Session", "sk", sk)
        return sk


main_session = requests.Session()
main_session.cookies.update(cookies)
main_session.headers.update(headers)

today = date.today()
tomorrow = today + timedelta(days=1)
yesterday = today - timedelta(days=1)

dateToAccept = str(yesterday)


def delete_all_special_chars(input_string):
    return ''.join(e for e in input_string if e.isalnum())


def download_send_discrepancy_acts(config, cookies, headers, main_session, dateToAccept):
    json_data = {
        'params': [
            {
                "sortingCenterId": 1100000040,
                "date": dateToAccept,
                "dateTo": dateToAccept,
                "types": [],
                "statuses": ["ARRIVED", "IN_PROGRESS", "SIGNED", "FIXED"],
                "page": 1,
                "size": 250
            },
        ],
        'path': '/sorting-center/1100000040/inbounds',
    }
    response = main_session.post(
        'https://logistics.market.yandex.ru/api/resolve/?r=sortingCenter/inbounds/resolveInboundList:resolveInboundList',
        json=json_data,
        verify=False
    )
    if response.status_code != 200:
        sk = updatesk(cookies, config, main_session)
        response = main_session.post(
            'https://logistics.market.yandex.ru/api/resolve/?r=sortingCenter/inbounds/resolveInboundList:resolveInboundList',
            json=json_data,
            verify=False
        )

    responseFormat = response.json()["results"][0]["data"]["content"]
    pdInboundsList = pd.json_normalize(responseFormat, max_level=3)

    search = "DISCREPANCY_ACT"
    pdFilteredList = pdInboundsList[pdInboundsList.apply(
        lambda row: row.astype(str).str.contains(search).any(), axis=1)]
    urls = {}
    pdFilteredList["url"] = ""
    for index, row in pdFilteredList.iterrows():
        DISCREPANCY_ACT_id = row["documents"][0]["id"]
        inbound_id = row["id"]
        url = f"https://logistics.market.yandex.ru/api/sorting-center/1100000040/inbounds/document?type=DISCREPANCY_ACT&id={
            DISCREPANCY_ACT_id}&inboundId={inbound_id}"
        if row["movementType"] != "LINEHAUL":
            urls[delete_all_special_chars(f"{row["supplierName"]} {
                                          row["inboundExternalId"]}")] = url
        pdFilteredList.at[index, "url"] = url

    pdFilteredList.to_excel("inboundsToTest.xlsx", index=False)

    API_TOKEN = config.get("BOT", "API_TOKEN")
    bot = telebot.TeleBot(API_TOKEN)
    chat_id = -4283452246
    message_thread_id = None
    bot.send_document(chat_id=chat_id, document=open("inboundsToTest.xlsx", 'rb'),
                      visible_file_name=f"TEST.xlsx", message_thread_id=message_thread_id)
    asyncio.run(get_file(urls, dateToAccept))

    # bot.send_document(chat_id=chat_id,document=open("files.xlsx",'rb'),visible_file_name=f"Файлики.xlsx",message_thread_id=message_thread_id)


download_send_discrepancy_acts(config, cookies, headers, main_session, dateToAccept)

# ФИКСАЦИЯ ПОСТАВКИ
# json_data = {
#     'params': [
#         {
#             'action': 'FIX_INBOUND',
#             'inboundId': 10000000844650,
#             'sortingCenterId': 1100000040,
#             'externalInboundId': 'TMU106295148',
#             'isV3': True,
#         },
#     ],
#     'path': '/sorting-center/1100000040/inbounds',
# }

# response = main_session.post(
#     'https://logistics.market.yandex.ru/api/resolve/?r=sortingCenter/inbounds/resolvePerformActionOnInbound:resolvePerformActionOnInbound',
#     cookies=cookies,
#     headers=headers,
#     json=json_data,
# )
# ФИКСАЦИЯ ПОСТАВКИ


# file = open("cellsToDelete.txt","r")
# data = file.read()
# users = data.split("\n")
# users = set(users)
# batchedusers = batched(users,100)


# i = 0
# responses = []
# for batch in batchedusers:
#     UrlForRequest = 'https://logistics.market.yandex.ru/api/resolve/?'
#     UrlForRequest +='&r=sortingCenter/cells/resolveDeleteCell:resolveDeleteCell' * len(batch)#Панель грузомест
#     json1_datas = [
#         {
#         'cellId': f'{user}',
#         'sortingCenterId': 1100000040,
#         } for user in batch
#     ]

#     json_data = { #
#         'params': json1_datas,
#         'path': '/sorting-center/1100000040/stages',
#     }
#     resp = sess.post(
#         UrlForRequest,
#         json=json_data,
#         verify=False
#     )
#     responses.append(resp)
#     i = i+1
# response = responses[0]
# API_TOKEN = config.get("BOT","API_TOKEN")
# bot = telebot.TeleBot(API_TOKEN)
# chat_id = -1002174558932
# thread_id = 2
# if responses[0].status_code != 200: raise Exception(responses[0])

# pandas = []
# for response in responses:
#     pandas.append(pd.json_normalize(response.json()["results"]))

# panda = pd.concat(pandas)
# panda.to_json("results2.json",index=False)
# panda.to_excel("results22.xlsx",index=False)
# strings = {
# "Текущая дата и время: " : str(st.replace(microsecond=0)),
# "<b>Количество cells: </b>" : len(users),
# # "ТЕКСТ ОТВЕТА:" : response.json()
# }

# message = ""
# for key,value in strings.items():
#     # if (value.isdigit() and int(value) > 0) > 0:
#     #     value = "<b><u>" + value + "</u></b>"
#     message += key +  str (value) + "\n"

# # pprint(message)
# bot.send_document(chat_id=chat_id,document=open("results22.xlsx",'rb'),visible_file_name=f"Result.xlsx",message_thread_id=thread_id)
# message += f"Время выполнения скрипта: {round((datetime.now()-st).total_seconds(),2)} сек."
# bot.send_message(chat_id, message,parse_mode='HTML',message_thread_id=thread_id)


with open('config.ini', 'w', encoding="utf8") as configfile:
    config.write(configfile)