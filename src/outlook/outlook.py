import configparser
# import os
import time

import pandas as pd
import telebot
import tenacity
import win32com.client

# from datetime import datetime


config = configparser.ConfigParser()
config.read("config.ini")

API_TOKEN = config.get("BOT", "API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)
chat_id = -1002205631792
thread_id = 5
# bot.send_chat_action(chat_id=chat_id,action='typing')


def tooLongMessageSend(returnMessage):
    if len(returnMessage) > 4096:
        for x in range(0, len(returnMessage), 4096):
            bot.send_message(chat_id=chat_id,
                             text="{}".format(returnMessage[x: x + 4096]),
                             message_thread_id=thread_id)
    else:
        bot.send_message(chat_id=chat_id,
                         text=returnMessage,
                         message_thread_id=thread_id)


outlook = win32com.client.Dispatch('outlook.application')
mapi = outlook.GetNamespace("MAPI")
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


@tenacity.retry(wait=tenacity.wait_fixed(1))
def sendMessageWithRetries(message):
    unread = message.UnRead
    subject = message.Subject
    sender = "No sender"
    sndremail = "No email"
    try:
        sender = message.Sender
        sndremail = sender.Address
    except Exception as e:
        pass

    body = message.Body
    categories = message.Categories
    msg = f'{sndremail}\n<b>{subject}</b>\n{categories}\n{body}'
    print(subject)
    tooLongMessageSend(msg)

    message.UnRead = False
    message.Save()
    message.Close(0)


for message in messages:
    # try:

    sendMessageWithRetries(message)

    # except Exception as e:
    #     bot.send_message(chat_id, f"{str(e.args[0])}" ,message_thread_id=thread_id)
    # print(body)
