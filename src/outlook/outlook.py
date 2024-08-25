import configparser
# import os
import time

import pandas as pd
import telebot
import win32com.client

# from datetime import datetime


config = configparser.ConfigParser()
config.read("config.ini")

API_TOKEN = config.get("BOT", "API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)
chat_id = -1002205631792
thread_id = 5
# bot.send_chat_action(chat_id=chat_id,action='typing')

outlook = win32com.client.Dispatch('outlook.application')
mapi = outlook.GetNamespace("MAPI")
Accounts = mapi.Session.Accounts
for folder in mapi.Folders:
    print(folder.Name)

inbox1 = mapi.Folders[0]
for folder in inbox1.Folders:
    print(folder.Name)
inbox = inbox1.Folders[1]
messages = inbox.Items
data_frame = pd.DataFrame(messages)
data_frame.to_excel("outlook.xlsx")
print('***'*30)
for message in messages:
    # try:
    unread = message.UnRead
    subject = message.Subject
    try:
        sender = message.Sender
        sndremail = sender.Address
    except Exception:
        sender = "No sender"
        sndremail = "No email"
    body = message.Body
    msg = f'{sndremail}\n<b>{subject}</b>\n{body}'
    try:
        bot.send_message(chat_id, msg, parse_mode='HTML',
                         message_thread_id=thread_id)
    except Exception:
        time.sleep(1)
        bot.send_message(chat_id, msg, parse_mode='HTML',
                         message_thread_id=thread_id)
    # except Exception as e:
    #     bot.send_message(chat_id, f"{str(e.args[0])}" ,message_thread_id=thread_id)
    # print(body)
