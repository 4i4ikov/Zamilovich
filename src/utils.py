import configparser

import requests
import telebot


def load_config():
    config, cookies, headers = get_config()
    api_token = config.get("BOT", "API_TOKEN")
    sorting_center_id = config.get("SC", "SORTING_CENTER_ID")
    chat_id = config.get("BOT", "CHAT_ID")
    message_thread_id = config.get("BOT", "MESSAGE_THREAD_ID")

    main_session = requests.Session()
    main_session.cookies.update(cookies)
    main_session.headers.update(headers)
    bot = telebot.TeleBot(api_token)
    return config, main_session, api_token, sorting_center_id, chat_id, message_thread_id, bot


def get_config():
    config = configparser.ConfigParser()
    config.read("config.ini")
    cookies = {
        "Session_id": config.get("Session", "Session_id"),
    }
    headers = {
        "sk": config.get("Session", "sk"),
    }

    return config, cookies, headers


def save_config(config):
    with open("config.ini", "w", encoding="utf8") as configfile:
        config.write(configfile)


def updatesk(main_session):
    config, cookies, headers = get_config()
    response = requests.patch(
        "https://logistics.market.yandex.ru/api/session", cookies=cookies, verify=False
    )
    if response.status_code == 200:
        sk = response.json().get("user").get("sk")
        main_session.headers.update({"sk": sk})
        config.set("Session", "sk", sk)
        save_config(config)
    else:
        raise Exception(f"Ошибка получения нового sk: {response.status_code}")
