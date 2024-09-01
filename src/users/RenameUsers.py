import configparser
import updatesk as updatesk
from datetime import datetime, time,date
import json
# import json
import logging
import pandas as pd
import requests
# from pprint import pprint
# from bs4 import BeautifulSoup
import telebot
logging.basicConfig(level=logging.DEBUG)
st = datetime.now()
config = configparser.ConfigParser()
config.read("config.ini")
cookies = {
    'Session_id': config.get("Session","Session_id"),
}
headers = {
    'sk': config.get('Session','sk'),
}

sess = requests.Session()
sess.cookies.update(cookies)
sess.headers.update(headers)
today = str(date.today())

file = open("renameUsers.json","r", encoding="utf-8")
json_users = json.load(file)

new_user_json = []
for user in json_users:
    user_new = {
        'user' : user,
        'userId' : user["id"],
        'sortingCenterId' :'1100000040',
    }
    new_user_json.append(user_new)

UrlForRequest = 'https://logistics.market.yandex.ru/api/resolve/?'
UrlForRequest +='&r=sortingCenter/users/resolveUpdateUser:resolveUpdateUser' * len(new_user_json)

json_data = {
    'params': new_user_json,
    'path': '/sorting-center/1100000040/users/197567',
}
response = sess.post(
    UrlForRequest,
    json=json_data,
    verify=False
)

API_TOKEN = config.get("BOT","API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)
chat_id = '-4143093216'
if response.status_code == 400:
    bot.send_message(chat_id, "Сессия закончилась, но я сам её обновлю")
    config.set('Session','sk', updatesk.updatesk(cookies))
    headers = {
    'sk': config.get('Session','sk'),
    }
    sess.headers.update(headers)
    response = sess.post( 
    UrlForRequest,
    json=json_data,
    )
    
panda = pd.json_normalize(response.json()["results"])

panda.to_excel("results2.xlsx",index=False)
strings = {
"Текущая дата и время: " : str(st.replace(microsecond=0)),
"<b>Количество users: </b>" : len(new_user_json),
# "ТЕКСТ ОТВЕТА:" : response.json()
}

message = ""
for key,value in strings.items():
    # if (value.isdigit() and int(value) > 0) > 0:
    #     value = "<b><u>" + value + "</u></b>"
    message += key +  str (value) + "\n"

# pprint(message)
bot.send_document(chat_id=chat_id,document=open("results2.xlsx",'rb'),visible_file_name=f"Result.xlsx")
message += f"Время выполнения скрипта: {round((datetime.now()-st).total_seconds(),2)} сек."
bot.send_message(chat_id, message,parse_mode='HTML')    
with open('config.ini','w', encoding="utf8") as configfile:
    config.write(configfile)

# with open('somefile.json', 'w',encoding="utf8") as outfile:  
#     json.dump(response.json(), outfile,indent=4,ensure_ascii=False)