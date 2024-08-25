import configparser
import logging
from datetime import date, datetime
from itertools import batched

import pandas as pd
import requests

# from pprint import pprint
# from bs4 import BeautifulSoup
import telebot

# import updatesk as updatesk

# from time import sleep


logging.basicConfig(level=logging.DEBUG)
st = datetime.now()
config = configparser.ConfigParser()
config.read("config.ini")
cookies = {
    "Session_id": config.get("Session", "Session_id"),
}
headers = {
    "sk": config.get("Session", "sk"),
}

sess = requests.Session()
sess.cookies.update(cookies)
sess.headers.update(headers)
today = str(date.today())
file = open("cellsToDelete.txt", "r")
data = file.read()
users = data.split("\n")
users = set(users)
batchedusers = batched(users, 100)


i = 0
responses = []
for batch in batchedusers:
    UrlForRequest = "https://logistics.market.yandex.ru/api/resolve/?"
    UrlForRequest += "&r=sortingCenter/cells/resolveDeleteCell:resolveDeleteCell" * len(
        batch
    )  # Панель грузомест
    json1_datas = [
        {
            "cellId": f"{user}",
            "sortingCenterId": 1100000040,
        }
        for user in batch
    ]

    json_data = {
        "params": json1_datas,
        "path": "/sorting-center/1100000040/stages",
    }
    resp = sess.post(UrlForRequest, json=json_data, verify=False)
    responses.append(resp)
    i = i + 1
response = responses[0]
API_TOKEN = config.get("BOT", "API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)
chat_id = -1002174558932
thread_id = 2
if responses[0].status_code != 200:
    raise Exception(responses[0])

pandas = []
for response in responses:
    pandas.append(pd.json_normalize(response.json()["results"]))

panda = pd.concat(pandas)
# panda.to_json("results2.json",index=False)
panda.to_excel("results22.xlsx", index=False)
strings = {
    "Текущая дата и время: ": str(st.replace(microsecond=0)),
    "<b>Количество cells: </b>": len(users),
    # "ТЕКСТ ОТВЕТА:" : response.json()
}

message = ""
for key, value in strings.items():
    # if (value.isdigit() and int(value) > 0) > 0:
    #     value = "<b><u>" + value + "</u></b>"
    message += key + str(value) + "\n"

# pprint(message)
bot.send_document(
    chat_id=chat_id,
    document=open("results22.xlsx", "rb"),
    visible_file_name="Result.xlsx",
    message_thread_id=thread_id,
)
message += (
    f"Время выполнения скрипта: {round((datetime.now()-st).total_seconds(), 2)} сек."
)
bot.send_message(chat_id, message, parse_mode="HTML", message_thread_id=thread_id)
with open("config.ini", "w", encoding="utf8") as configfile:
    config.write(configfile)

# with open('somefile.json', 'w',encoding="utf8") as outfile:
#     json.dump(response.json(), outfile,indent=4,ensure_ascii=False)
