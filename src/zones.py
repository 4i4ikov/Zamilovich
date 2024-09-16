import configparser
import json
from datetime import date
from pathlib import Path
from pprint import pprint

import pandas as pd
import requests
import urllib3

config = configparser.ConfigParser()
config.read("config.ini")
COOKIES = {
    "Session_id": config.get("Session", "Session_id"),
}
headers = {
    "sk": config.get("Session", "sk"),
}
API_TOKEN = config.get("BOT", "API_TOKEN")
CHAT_ID = config.get("BOT", "CHAT_ID")
THREAD_ID = config.get("BOT", "message_thread_id")
SORTING_CENTER_ID = config.get("SC", "SORTING_CENTER_ID")

sess = requests.Session()
sess.cookies.update(COOKIES)
sess.headers.update(headers)
sess.verify = False

response = sess.get(
    "https://hubs.market.yandex.ru/api/gateway/sorting-center/1100000040/zones",
)
if response.status_code != 200:
    print("ошибка запроса")
panda = pd.json_normalize(response.json()["zones"])
panda = panda[panda["statistic.totalUsersOnlyZone"] > 0]
cols = ["name", "statistic.totalUsersOnlyZone", "statistic.activeUsers"]
cols_renamed = ["Зона", "Всего", "Активных"]
panda = panda[cols]
panda.columns = cols_renamed
panda = panda.sort_values(by="Активных", ascending=False)
text = panda.to_string(index=False)
print(text)
panda.to_excel("OUTPUT/Testing.xlsx")
