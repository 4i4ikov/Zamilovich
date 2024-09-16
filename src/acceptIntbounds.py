import asyncio
import datetime
import time
from pathlib import Path

import pandas as pd
import telebot

import asinhrom as ass
import utils


def delete_all_special_chars(input_string):
    return "".join(e for e in input_string if e.isalnum())


def accept_all_inbounds(main_session, sorting_center_id, dateToAccept):
    response = resolve_inbound_list_v2(
        main_session,
        dateToAccept,
        sorting_center_id,
        statuses=["ARRIVED", "IN_PROGRESS"],
    )
    response_format = response.json()["results"][0]["data"]["content"]
    pd_inbounds_list = pd.json_normalize(response_format, max_level=3)
    params = []
    for index, row in pd_inbounds_list.iterrows():
        params.append(
            {
                "action": "FIX_INBOUND",
                "inboundId": row["id"],
                "sortingCenterId": sorting_center_id,
                "externalInboundId": row["inboundExternalId"],
                "isV3": True,
            }
        )

    # ФИКСАЦИЯ ПОСТАВКИ
    json_data = {
        "params": params,
        "path": f"/sorting-center/{sorting_center_id}/inbounds",
    }
    url = (
        "https://logistics.market.yandex.ru/api/resolve/?"
        + "&r=sortingCenter/inbounds/resolvePerformActionOnInbound:resolvePerformActionOnInbound"
        * len(params)
    )
    response = main_session.post(
        url,
        json=json_data,
    )
    print("response", response)
    # ФИКСАЦИЯ ПОСТАВКИ


def resolve_inbound_list(main_session, json_data):
    return main_session.post(
        "https://logistics.market.yandex.ru/api/resolve/?r=sortingCenter/inbounds/resolveInboundList:resolveInboundList",
        json=json_data,
        verify=False,
    )


def download_discrepancy_acts(
    main_session,
    sorting_center_id,
    dateToAccept,
):
    response = resolve_inbound_list_v2(main_session, dateToAccept, sorting_center_id)
    response_format = response.json()["results"][0]["data"]["content"]
    pd_inbounds_list = pd.json_normalize(response_format, max_level=3)

    search = "DISCREPANCY_ACT"
    pd_filtered_list = pd_inbounds_list[
        pd_inbounds_list.apply(lambda row: row.astype(str).str.contains(search).any(), axis=1)
    ]
    urls = {}
    pd_filtered_list["url"] = ""
    for index, row in pd_filtered_list.iterrows():
        discrepancy_act_id = row["documents"][0]["id"]
        inbound_id = row["id"]
        url = f"https://logistics.market.yandex.ru/api/sorting-center/{
            sorting_center_id}/inbounds/document?type=DISCREPANCY_ACT&id={discrepancy_act_id}&inboundId={inbound_id}"
        if row["movementType"] != "LINEHAUL":
            urls[delete_all_special_chars(f"{row['supplierName']} {row['inboundExternalId']}")] = (
                url
            )
        pd_filtered_list.at[index, "url"] = url

    filename = "inboundsToTest.xlsx"
    pd_filtered_list.to_excel(filename, index=False)
    # TODO: make it work with async
    asyncio.run(ass.get_file(urls, dateToAccept))
    return filename


def resolve_inbound_list_v2(
    main_session,
    dateToAccept,
    sorting_center_id,
    statuses=["ARRIVED", "IN_PROGRESS", "SIGNED", "FIXED"],
):
    json_data = {
        "params": [
            {
                "sortingCenterId": sorting_center_id,
                "date": dateToAccept,
                "dateTo": dateToAccept,
                "types": [],
                "statuses": statuses,
                "page": 1,
                "size": 300,
            },
        ],
        "path": f"/sorting-center/{sorting_center_id}/inbounds",
    }
    response = resolve_inbound_list(main_session, json_data)
    if response.status_code != 200:
        utils.updatesk(main_session)
        response = resolve_inbound_list(main_session, json_data)
    return response


def main():
    config, main_session, sorting_center_id, chat_id, message_thread_id, bot = utils.load_config()
    chat_id, message_thread_id = ("-1002130148271", "5053")
    yesterday = datetime.date.today() - datetime.timedelta(days=1)

    date_to_accept = str(yesterday)
    accept_all_inbounds(main_session, sorting_center_id, date_to_accept)
    download_discrepancy_acts(
        main_session,
        sorting_center_id,
        date_to_accept,
    )
    send_to_chat(chat_id, message_thread_id, bot, date_to_accept)
    utils.save_config(config)


def send_to_chat(chat_id, message_thread_id, bot, date_to_accept):
    bot.send_message(
        chat_id=chat_id,
        text=f"Поставки с расхождениями за {date_to_accept}:\n\t",
        message_thread_id=message_thread_id,
        parse_mode="HTML",
    )
    bot.send_document(
        chat_id=chat_id,
        document=open("inboundsToTest.xlsx", "rb"),
        visible_file_name=f"Расхождения за {date_to_accept}.xlsx",
        message_thread_id=message_thread_id,
    )
    directory = Path(f"rashodilis/{date_to_accept}")
    for file in directory.iterdir():
        if file.is_file():
            with open(file, "rb") as f:
                send_file_with_retries(chat_id, message_thread_id, bot, file.name, f, max_retries=3)
    bot.send_message(
        chat_id=chat_id,
        text=f"Отправил все расхождения за {date_to_accept} в чат.\n\t",
        message_thread_id=message_thread_id,
        parse_mode="HTML",
    )


def send_file_with_retries(chat_id, message_thread_id, bot, filename, f, max_retries=3):
    retry_count = 0
    while retry_count < max_retries:
        try:
            bot.send_document(
                chat_id=chat_id,
                document=f.read(),
                visible_file_name=filename,
                message_thread_id=message_thread_id,
            )
            break
        except telebot.apihelper.ApiTelegramException as e:
            if e.error_code == 429:
                retry_after = 30
                print(f"Rate limit exceeded. Retrying after {
                      retry_after} seconds...")
                time.sleep(retry_after)
                retry_count += 1
            else:
                print(e)


if __name__ == "__main__":
    main()
