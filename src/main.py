import configparser
import os
from datetime import date, datetime, time
from pathlib import Path

import pandas as pd
import requests
import telebot
from styleframe import StyleFrame
from tabulate import tabulate

import utils

# import json

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

bot = telebot.TeleBot(API_TOKEN)


st = datetime.now()


today = str(date.today())
routes = "r=sortingCenter/routes/"
routes_full_info = routes + "resolveGetRoutesFullInfo:resolveGetRoutesFullInfo"
sortables = "r=sortingCenter/sortables/resolveSortableReport:resolveSortableReport"

url_for_request = "&".join(
    [
        "https://logistics.market.yandex.ru/api/resolve/?r=sortingCenter/sortables/resolveSortableStageStatistic:resolveSortableStageStatistic",  # Панель грузомест
        routes_full_info,  # CourierAll
        routes + "resolveGetRoutesSummary:resolveGetRoutesSummary",  # Courier cifri
        routes_full_info,  # Magistral
        sortables,  # D
        sortables,  # Drop
        sortables,  # Sort
        routes_full_info,
        sortables,
        sortables,
        sortables,
        sortables,
        "r=sortingCenter/inbounds/resolveInboundList:resolveInboundList",
        routes_full_info,
    ],
)

json_data_for_request = {
    "params": [
        {  # 0 Warehouse overwiew
            "sortingCenterId": SORTING_CENTER_ID,
        },
        {  # 1 ALL COURIERS
            "sortingCenterId": SORTING_CENTER_ID,
            "page": 0,
            "size": 100,
            "category": "COURIER",
            "hasCarts": False,
            "date": today,
            "sort": "acceptedButNotSorted,desc",
            "type": "OUTGOING_COURIER",
        },
        {  # 2 COURIERS DIGITS
            "sortingCenterId": SORTING_CENTER_ID,
            "date": today,
            "type": "OUTGOING_COURIER",
            "category": "COURIER",
        },
        {  # 3 MIDDLE_MILE
            "sortingCenterId": SORTING_CENTER_ID,
            "page": 0,
            "size": 100,
            "category": "MIDDLE_MILE_COURIER",
            "hasCarts": False,
            "date": today,
            "sort": "",
            "type": "OUTGOING_COURIER",
        },
        {  # 4 SORTABLES IN D
            "sortableStatuses": [],
            "stages": [],
            "cellName": "\\D-",
            "inboundIdTitle": "",
            "outboundIdTitle": "",
            "groupingDirectionId": "",
            "groupingDirectionName": "",
            "sortingCenterId": SORTING_CENTER_ID,
            "page": 0,
            "size": 200,
            "sortableTypes": [
                "PLACE",
            ],
            "crossDockOnly": False,
        },
        {  # 5 SORTABLES IN DROP
            "cellName": "Drop",
            "sortableStatuses": [],
            "inboundIdTitle": "",
            "outboundIdTitle": "",
            "groupingDirectionId": "",
            "groupingDirectionName": "",
            "stages": [],
            "sortingCenterId": SORTING_CENTER_ID,
            "page": 0,
            "size": 200,
            "sortableTypes": [],
            "crossDockOnly": False,
        },
        {  # 6 SORTABLES IN SORT CELL
            "cellName": "SORT",
            "sortableStatuses": [],
            "inboundIdTitle": "",
            "outboundIdTitle": "",
            "groupingDirectionId": "",
            "groupingDirectionName": "",
            "stages": [],
            "sortingCenterId": SORTING_CENTER_ID,
            "page": 0,
            "size": 200,
            "sortableTypes": [],
            "crossDockOnly": False,
        },
        {  # 7 hasMultiplaceIncompleteInCell
            "sortingCenterId": SORTING_CENTER_ID,
            "page": 0,
            "size": 20,
            "hasMultiplaceIncompleteInCell": True,
            "hasCarts": False,
            "date": today,
            "sort": "",
            "type": "OUTGOING_COURIER",
        },
        {  # 8 NEED TO SORT IN CHELNY
            "sortableStatuses": ["ARRIVED_DIRECT"],
            "stages": [],
            "courierId": "10000000060066",
            "sortingCenterId": SORTING_CENTER_ID,
            "page": 0,
            "size": 20,
            "sortableTypes": [
                "PLACE",
                "TOTE",
            ],
            "crossDockOnly": False,
        },
        {  # 9 NEED TO SORT IN IZHEVSK
            "sortableStatuses": ["ARRIVED_DIRECT"],
            "stages": [],
            "courierId": "10000000072156",
            "sortingCenterId": SORTING_CENTER_ID,
            "page": 0,
            "size": 20,
            "sortableTypes": [
                "PLACE",
                "TOTE",
            ],
            "crossDockOnly": False,
        },
        {  # 10 NEED TO SORT IN CHEBOKSARY
            "sortableStatuses": ["ARRIVED_DIRECT"],
            "stages": [],
            "courierId": "10000000028198",
            "sortingCenterId": SORTING_CENTER_ID,
            "page": 0,
            "size": 20,
            "sortableTypes": [
                "PLACE",
                "TOTE",
            ],
            "crossDockOnly": False,
        },
        {  # 11 NEED TO SORT IN KIROV
            "sortableStatuses": ["ARRIVED_DIRECT"],
            "stages": [],
            "courierId": "10000000076237",
            "sortingCenterId": SORTING_CENTER_ID,
            "page": 0,
            "size": 20,
            "sortableTypes": [
                "PLACE",
                "TOTE",
            ],
            "crossDockOnly": False,
        },
        {  # 12 LINEHAUL
            "sortingCenterId": SORTING_CENTER_ID,
            "date": f"{today}",
            "dateTo": f"{today}",
            "types": [],
            "movementTypes": [
                "LINEHAUL",
            ],
            "statuses": ["ARRIVED", "IN_PROGRESS", "SIGNED", "FIXED", "CREATED"],
            "page": 1,
            "size": 150,
        },
        {  # 13 INCOMING WAREHOUSE
            "sortingCenterId": SORTING_CENTER_ID,
            "page": 0,
            "size": 220,
            "hasCarts": False,
            "date": f"{today}",
            "sort": "",
            "type": "INCOMING_WAREHOUSE",
        },
    ],
    "path": f"/sorting-center/{SORTING_CENTER_ID}/stages",
}


bot.send_chat_action(chat_id=CHAT_ID, action="typing")  # 'upload_document'
response = sess.post(url_for_request, json=json_data_for_request,)

if response.status_code == 400:
    bot.send_message(CHAT_ID, "Сессия закончилась, но я сам её обновлю")
    utils.updatesk(sess)
    response = sess.post(
        url_for_request,
        json=json_data_for_request,
    )

result = response.json()["results"]
Panel = result[0]["data"]
CourierAll = result[1]["data"]
CourierDigits = result[2]["data"]
# Magistral = result[3]["data"]["content"]

InDropOffCells = result[4]["data"]
InDROPCell = result[5]["data"]
InSORTCell = result[6]["data"]
InSORTCellOrders = result[6]["data"]["content"]

NotFulledMM = result[7]["data"]
ChelnyPredsort = result[8]["data"]
IzhevskPredsort = result[9]["data"]
CheboksaryPredsort = result[10]["data"]
KirovPredsort = result[11]["data"]
predsort = ""
hranenie = ""
forsort = ""
for check in Panel["PLACE"]:
    match check["id"]:
        case 4531:
            predsort = str(check["count"])
        case 3100:
            hranenie = str(check["count"])
        case 4100:
            forsort = str(check["count"])

# routes = [courier["id"] for courier in CourierAll["content"]]

# urlsNotAcceptedByCourier = [f"https://logistics.market.yandex.ru/api/sorting-center/SORTING_CENTER_ID/sortables/download?searchRouteIdInOldRoutes=false&sortableStatuses=ARRIVED_DIRECT&sortableStatuses=KEEPED_DIRECT&sortingCenterId=SORTING_CENTER_ID&page=0&size=20&sortableTypes=PLACE&sortableTypes=TOTE&crossDockOnly=false&routeId={route}&" for route in routes]
# asinhrom.getAccepterdButNotSorted(urlsNotAcceptedByCourier)
inboundLinehaul = result[12]["data"]["content"]
inboundLinehaulDataFrame = pd.json_normalize(inboundLinehaul)
# inboundLinehaulDataFrame.drop(['car','trailerNumber',	'id',	'externalId',	'inboundStatus',	'movementType',	'movementSubtype',	'palletAmount',	'plannedPalletAmount',	'boxAmount',	'plannedBoxAmount',	'arrivalIntervalEnd','actions',	'complexActions',	'transportationId',	'documents',	'type']
# ,axis=1,inplace=True)
inboundLinehaulDataFrame = inboundLinehaulDataFrame[
    [
        # 'car',
        # 'trailerNumber',
        "inboundExternalId",
        "supplierName",
        "courierName",
        "arrivalIntervalStart",
        "boxAmount",
        "plannedBoxAmount",
    ]
]
inboundLinehaulDataFrame.columns = [
    # "ТЯГАЧ",
    # "ПРИЦЕП",
    "ПОСТАВКА",
    "ОТКУДА",
    "ВОДИТЕЛЬ",
    "ВРЕМЯ",
    "Принято",
    "План",
]
inboundLinehaulDataFrame["ВРЕМЯ"] = pd.to_datetime(
    inboundLinehaulDataFrame["ВРЕМЯ"])
inboundLinehaulDataFrame = inboundLinehaulDataFrame.loc[inboundLinehaulDataFrame["План"] > 0]
inboundLinehaulDataFrame.sort_values(by="ВРЕМЯ", inplace=True)
columns = inboundLinehaulDataFrame.columns
now = st.strftime("%Y-%m-%d %H_%M")
Path("./OUTPUT/LINEHAUL/").mkdir(parents=True, exist_ok=True)
fileName = f"./OUTPUT/LINEHAUL/{now}.xlsx"
excelWriter = StyleFrame.ExcelWriter(fileName)
styledDataFrame = StyleFrame(inboundLinehaulDataFrame)
styledDataFrame.to_excel(
    excel_writer=excelWriter,
    best_fit=(list(columns.values)),
    row_to_add_filters=0,
    index=False,
)
excelWriter.close()
bot.send_document(
    chat_id=CHAT_ID,
    document=open(fileName, "rb"),
    visible_file_name=f"ЛАЙНХОЛЛЫ {now}.xlsx",
    message_thread_id=THREAD_ID,
)
ekb = "Склад, СЦ МК Екатеринбург"
ekaterinburg_inbound_linehaul = inboundLinehaulDataFrame.query(
    "ОТКУДА ==  @ekb")
ekb_accepted_amount = ekaterinburg_inbound_linehaul["Принято"].to_numpy()[0]
ekb_planned_amount = ekaterinburg_inbound_linehaul["План"].to_numpy()[0]

incoming = result[13]["data"]["content"]
incomingDataFrame = pd.json_normalize(incoming)

vals = "warehouse.type	ordersPlanned	ordersCreated	ordersAccepted	ordersSorted	ordersShipped	acceptedButNotSorted".split(
    "	",
)
valsRenamed = "Откуда	План	Не принято	Принято	Отсортировано	Отгружено	Осталось отсортировать".split(
    "	",
)

groupTableincoming = incomingDataFrame.groupby(
    ["warehouse.type"]).sum().reset_index()
groupTableincoming = groupTableincoming[vals]
groupTableincoming.columns = valsRenamed
groupTableincoming["Дата"] = st
Path("./OUTPUT/POSTAVKI/").mkdir(parents=True, exist_ok=True)
fileName = f"./OUTPUT/POSTAVKI/{now}.xlsx"
excelWriter = StyleFrame.ExcelWriter(fileName)
styledDataFrame = StyleFrame(groupTableincoming)
styledDataFrame.to_excel(
    excel_writer=excelWriter,
    best_fit=list(styledDataFrame.columns),
    index=False,
)
excelWriter.close()
bot.send_document(
    chat_id=CHAT_ID,
    document=open(fileName, "rb"),
    visible_file_name=f"МАРШРУТЫ {now}.xlsx",
    message_thread_id=THREAD_ID,
)

routes = [courier["id"] for courier in CourierAll["content"]]

# urlsNotAcceptedByCourier = [f"https://logistics.market.yandex.ru/api/sorting-center/SORTING_CENTER_ID/sortables/download?searchRouteIdInOldRoutes=false&sortableStatuses=ARRIVED_DIRECT&sortableStatuses=KEEPED_DIRECT&sortingCenterId=SORTING_CENTER_ID&page=0&size=20&sortableTypes=PLACE&sortableTypes=TOTE&crossDockOnly=false&routeId={route}&" for route in routes]
# asinhrom.getAccepterdButNotSorted(urlsNotAcceptedByCourier)

# insort = []
# insortStr = ""
# for Order in InSORTCellOrders:
#     if "orderExternalId" in Order.keys():
#         insort.append(f"{Order["orderExternalId"]}")  # {Order["cellName"]}
# for Order in set(insort):
#     insortStr += f"{Order}\n"
# strings["Заказы в ячейках СОРТ:\n"] = insortStr

# for j in Magistral:
#     match j["courier"]["id"]:
#         case 1100000000062363:
#             strings["Осталось отсортировать Ижевск: "] = str(j["acceptedButNotSorted"])
#         case 1100000000058185:
#             strings["Осталось отсортировать Челны: "] = str(j["acceptedButNotSorted"])

strings = {
    "ОСТАЛОСЬ ОТСОРТИРОВАТЬ В DO МЕШКИ: ": f"{InDropOffCells['totalElements']}",
    "В ячейке DROP: ": f"{InDROPCell['totalElements']}",
    "В ячейках SORT: ": f"{InSORTCell['totalElements']}",
    "На хранении: ": f"{hranenie}",
    "Предсорт пройден: ": f"{predsort}",
    "Челны: ": f"{ChelnyPredsort['totalElements']}",
    "Ижевск: ": f"{IzhevskPredsort['totalElements']}",
    "Чебоксары: ": f"{CheboksaryPredsort['totalElements']}",
    "Киров: ": f"{KirovPredsort['totalElements']}",
    "Для сортировки: ": f"{forsort}",
    "Екатеринбург отсортировано: ": f"{ekb_accepted_amount}/{ekb_planned_amount}",
    "Заказов курьерки к отгрузке: ": f"{CourierDigits['ordersPlanned']}",
    "Курьеров к отгрузке: ": f"{CourierAll['totalElements']}",
    "Не полные многоместки: ": f"{NotFulledMM['totalElements']}",
    "Осталось отсортировать курьерку: ": f"{CourierDigits['acceptedButNotSorted']}",
}

for i in Panel["ORPHAN_PALLET"]:
    batch = i["systemName"]
    match batch:
        case "PACKED_KEEPED_DIRECT":  # Батч подготовлен в хранении
            strings["Батч упакован, на хранении: "] = f"{i["count"]}"
        case "NOT_ACCEPTED_BY_COURIER_DIRECT":  # не принят курьером
            strings["Батч не принят курьером: "] = f"{i["count"]}"
        case "AWAITING_SORT_DIRECT":  # для сортировки
            strings["Батч для сортировки: "] = f"{i["count"]}"
        case "KEEPED_DIRECT":  # на хранении
            strings["Батч на хранении: "] = f"{i["count"]}"
        case "SORTING_IN_LOT_DIRECT":  # наполняется посылками
            strings["Батч наполняется посылками: "] = f"{i["count"]}"
        case "SORTING_IN_LOT_KEEPED_DIRECT":  # наполняется посылками в хранении
            strings["Батч наполняется посылками, в хранении: "] = f"{
                i["count"]}"
        case "SORTING_IN_LOT_RETURN":  # возвратный батч наполняется посылками
            strings["ДО мешок наполняется посылками (не закрыт): "] = f"{
                i["count"]}"

message = f"Текущая дата и время: {st.replace(microsecond=0)}\nКомпьютер: {
    os.getenv('COMPUTERNAME')}\n"
for key, value in strings.items():
    checkvalue = value.split("/")[0]
    if checkvalue.isdigit() and int(checkvalue) > 0:
        value = "<u>" + value + "</u>"
        message += key + str(value) + "\n"
# message += f'Заказы в ячейках СОРТ: {}'
# pprint(message)
# with open("insort.csv", "w+") as file:
#     file.write(strings["Заказы в ячейках СОРТ:\n"])
# bot.send_document(
#     chat_id=CHAT_ID,
#     document=open("insort.csv", "rb"),
#     visible_file_name="В ячейках СОРТ.csv",
# )
# bot.send_document(chat_id=chat_id,document=open("AcceptedButNotSorted.xlsx",'rb'),visible_file_name=f"Осталось отсортировать {now}.xlsx")
# message += f"Время выполнения скрипта: {
#     round((datetime.now()-st).total_seconds(), 2)} сек."
bot.send_message(CHAT_ID, message, parse_mode="HTML")
if time(7, 00) <= st.time() <= time(9, 10):
    bot.send_message(1063498880, message, parse_mode="HTML")

response_zones = sess.get(
    "https://hubs.market.yandex.ru/api/gateway/sorting-center/1100000040/zones",
)
if response_zones.status_code == 200:
    panda = pd.json_normalize(response_zones.json()["zones"])
    panda = panda[panda["statistic.totalUsersOnlyZone"] > 0]
    cols = ["name", "statistic.activeUsers"]
    cols_renamed = ["Зона", "Активных"]
    panda = panda[cols]
    panda.columns = cols_renamed
    panda = panda.sort_values(by="Активных", ascending=False)
    text = tabulate(panda, headers=panda.columns, showindex=False,
                    tablefmt="plain", colalign=["left"])
    bot.send_message(CHAT_ID, f"Активность на СЦ:\n<pre>{
                     text}</pre>", parse_mode="HTML")
    with open("config.ini", "w+", encoding="utf8") as configfile:
        config.write(configfile)
