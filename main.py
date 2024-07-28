import configparser
import warnings
import os
import urllib3
import updatesk as updatesk
from datetime import datetime, date, time
import json
import asinhrom
from styleframe import StyleFrame
import pandas as pd
import requests
import telebot

warnings.filterwarnings("ignore")
urllib3.disable_warnings()

st = datetime.now()
config = configparser.ConfigParser()
config.read("config.ini")
cookies = {
    'Session_id': config.get("Session", "Session_id"),
}
headers = {
    'sk': config.get('Session', 'sk'),
}

sess = requests.Session()
sess.cookies.update(cookies)
sess.headers.update(headers)
today = str(date.today())

url_parts = [
    'https://logistics.market.yandex.ru/api/resolve/?',
    'r=sortingCenter/sortables/resolveSortableStageStatistic:resolveSortableStageStatistic',
    'r=sortingCenter/routes/resolveGetRoutesFullInfo:resolveGetRoutesFullInfo',
    'r=sortingCenter/routes/resolveGetRoutesSummary:resolveGetRoutesSummary',
    'r=sortingCenter/routes/resolveGetRoutesFullInfo:resolveGetRoutesFullInfo',
    'r=sortingCenter/sortables/resolveSortableReport:resolveSortableReport',
    'r=sortingCenter/sortables/resolveSortableReport:resolveSortableReport',
    'r=sortingCenter/sortables/resolveSortableReport:resolveSortableReport',
    'r=sortingCenter/routes/resolveGetRoutesFullInfo:resolveGetRoutesFullInfo',
    'r=sortingCenter/sortables/resolveSortableReport:resolveSortableReport',
    'r=sortingCenter/sortables/resolveSortableReport:resolveSortableReport',
    'r=sortingCenter/sortables/resolveSortableReport:resolveSortableReport',
    'r=sortingCenter/sortables/resolveSortableReport:resolveSortableReport',
    'r=sortingCenter/inbounds/resolveInboundList:resolveInboundList',
    'r=sortingCenter/routes/resolveGetRoutesFullInfo:resolveGetRoutesFullInfo'
]
UrlForRequest = '&'.join(url_parts)

json_data = {
    'params': [
        {'sortingCenterId': 1100000040},
        {'sortingCenterId': 1100000040, 'page': 0, 'size': 100, 'category': 'COURIER', 'hasCarts': False, 'date': today, 'sort': 'acceptedButNotSorted,desc', 'type': 'OUTGOING_COURIER'},
        {'sortingCenterId': '1100000040', 'date': today, 'type': 'OUTGOING_COURIER', 'category': 'COURIER'},
        {'sortingCenterId': 1100000040, 'page': 0, 'size': 100, 'category': 'MIDDLE_MILE_COURIER', 'hasCarts': False, 'date': today, 'sort': '', 'type': 'OUTGOING_COURIER'},
        {'sortableStatuses': [], 'stages': [], 'cellName': '\\D-', 'inboundIdTitle': '', 'outboundIdTitle': '', 'groupingDirectionId': '', 'groupingDirectionName': '', 'sortingCenterId': 1100000040, 'page': 0, 'size': 200, 'sortableTypes': ['PLACE'], 'crossDockOnly': False},
        {'cellName': 'Drop', 'sortableStatuses': [], 'inboundIdTitle': '', 'outboundIdTitle': '', 'groupingDirectionId': '', 'groupingDirectionName': '', 'stages': [], 'sortingCenterId': 1100000040, 'page': 0, 'size': 200, 'sortableTypes': [], 'crossDockOnly': False},
        {'cellName': 'SORT', 'sortableStatuses': [], 'inboundIdTitle': '', 'outboundIdTitle': '', 'groupingDirectionId': '', 'groupingDirectionName': '', 'stages': [], 'sortingCenterId': 1100000040, 'page': 0, 'size': 200, 'sortableTypes': [], 'crossDockOnly': False},
        {'sortingCenterId': 1100000040, 'page': 0, 'size': 20, 'hasMultiplaceIncompleteInCell': True, 'hasCarts': False, 'date': today, 'sort': '', 'type': 'OUTGOING_COURIER'},
        {'sortableStatuses': ['ARRIVED_DIRECT'], 'stages': [], 'courierId': '10000000060066', 'sortingCenterId': 1100000040, 'page': 0, 'size': 20, 'sortableTypes': ['PLACE', 'TOTE'], 'crossDockOnly': False},
        {'sortableStatuses': ['ARRIVED_DIRECT'], 'stages': [], 'courierId': '10000000072156', 'sortingCenterId': 1100000040, 'page': 0, 'size': 20, 'sortableTypes': ['PLACE', 'TOTE'], 'crossDockOnly': False},
        {'sortableStatuses': ['ARRIVED_DIRECT'], 'stages': [], 'courierId': '10000000028198', 'sortingCenterId': 1100000040, 'page': 0, 'size': 20, 'sortableTypes': ['PLACE', 'TOTE'], 'crossDockOnly': False},
        {'sortableStatuses': ['ARRIVED_DIRECT'], 'stages': [], 'courierId': '10000000076237', 'sortingCenterId': 1100000040, 'page': 0, 'size': 20, 'sortableTypes': ['PLACE', 'TOTE'], 'crossDockOnly': False},
        {'sortingCenterId': 1100000040, 'date': f'{today}', 'dateTo': f'{today}', 'types': [], 'movementTypes': ['LINEHAUL'], 'statuses': ['ARRIVED', 'IN_PROGRESS', 'SIGNED', 'FIXED', 'CREATED'], 'page': 1, 'size': 150},
        {'sortingCenterId': 1100000040, 'page': 0, 'size': 220, 'hasCarts': False, 'date': f'{today}', 'sort': '', 'type': 'INCOMING_WAREHOUSE'}
    ],
    'path': '/sorting-center/1100000040/stages',
}

API_TOKEN = config.get("BOT", "API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)
chat_id = config.get("BOT", "CHAT_ID")
thread_id = 0
bot.send_chat_action(chat_id=chat_id, action='typing')

response = sess.post(UrlForRequest, json=json_data, verify=False)

if response.status_code == 400:
    bot.send_message(chat_id, "Сессия закончилась, но я сам её обновлю")
    config.set('Session', 'sk', updatesk.updatesk(cookies))
    headers = {'sk': config.get('Session', 'sk')}
    sess.headers.update(headers)
    response = sess.post(UrlForRequest, json=json_data)

resultFromResponse = response.json()["results"]
Panel = resultFromResponse[0]["data"]
CourierAll = resultFromResponse[1]["data"]
CourierDigits = resultFromResponse[2]["data"]

InDropOffCells = resultFromResponse[4]["data"]
InDROPCell = resultFromResponse[5]["data"]
InSORTCell = resultFromResponse[6]["data"]
InSORTCellOrders = resultFromResponse[6]["data"]["content"]

NotFulledMM = resultFromResponse[7]["data"]
ChelnyPredsort = resultFromResponse[8]["data"]
IzhevskPredsort = resultFromResponse[9]["data"]
CheboksaryPredsort = resultFromResponse[10]["data"]
KirovPredsort = resultFromResponse[11]["data"]

predsort = hranenie = forsort = ""
id_to_var = {4531: 'predsort', 3100: 'hranenie', 4100: 'forsort'}
for check in Panel["PLACE"]:
    if check["id"] in id_to_var:
        locals()[id_to_var[check["id"]]] = str(check["count"])

strings = {
    "ОСТАЛОСЬ ОТСОРТИРОВАТЬ В DO МЕШКИ: ": str(InDropOffCells["totalElements"]),
    "В ячейке DROP: ": str(InDROPCell["totalElements"]),
    "В ячейках SORT: ": str(InSORTCell["totalElements"]),
    "На хранении: ": hranenie,
    "Предсорт пройден: ": predsort,
    "Челны: ": str(ChelnyPredsort["totalElements"]),
    "Ижевск: ": str(IzhevskPredsort["totalElements"]),
    "Чебоксары: ": str(CheboksaryPredsort["totalElements"]),
    "Киров: ": str(KirovPredsort["totalElements"]),
    "Для сортировки: ": forsort,
    "Заказов курьерки к отгрузке: ": str(CourierDigits["ordersPlanned"]),
    "Курьеров к отгрузке: ": str(CourierAll["totalElements"]),
    "Не полные многоместки: ": str(NotFulledMM["totalElements"]),
    "Осталось отсортировать курьерку: ": str(CourierDigits["acceptedButNotSorted"])
}

inboundLinehaul = resultFromResponse[12]["data"]["content"]
inboundLinehaulDataFrame = pd.json_normalize(inboundLinehaul)
inboundLinehaulDataFrame = inboundLinehaulDataFrame[[
    'inboundExternalId', 'supplierName', 'courierName', 'arrivalIntervalStart', 'acceptedAmount', 'totalAmount'
]]
inboundLinehaulDataFrame.columns = [
    "ПОСТАВКА", "ОТКУДА", "ВОДИТЕЛЬ", "ВРЕМЯ", "Принято", "План"
]
inboundLinehaulDataFrame["ВРЕМЯ"] = pd.to_datetime(inboundLinehaulDataFrame["ВРЕМЯ"])
inboundLinehaulDataFrame = inboundLinehaulDataFrame.loc[inboundLinehaulDataFrame['План'] > 0]
inboundLinehaulDataFrame.sort_values(by="ВРЕМЯ", inplace=True)
columns = inboundLinehaulDataFrame.columns
now = st.strftime('%Y-%m-%d %H_%M')
fileName = f"./LINEHAUL/{now}.xlsx"
excelWriter = StyleFrame.ExcelWriter(fileName)
styledDataFrame = StyleFrame(inboundLinehaulDataFrame)
styledDataFrame.to_excel(excel_writer=excelWriter, best_fit=(list(columns.values)), row_to_add_filters=0, index=False)
excelWriter.close()
bot.send_document(chat_id=chat_id, document=open(fileName, 'rb'), visible_file_name=f"ЛАЙНХОЛЛЫ {now}.xlsx", message_thread_id=thread_id)

incoming = resultFromResponse[13]["data"]["content"]
incomingDataFrame = pd.json_normalize(incoming)

vals = "warehouse.type ordersPlanned ordersCreated ordersAccepted ordersSorted ordersShipped acceptedButNotSorted".split()
valsRenamed = "Откуда План Не принято Принято Отсортировано Отгружено Осталось отсортировать".split()

groupTableincoming = incomingDataFrame.groupby(['warehouse.type']).sum().reset_index()
groupTableincoming = groupTableincoming[vals]
groupTableincoming.columns = valsRenamed
groupTableincoming["Дата"] = st
fileName = f"./POSTAVKI/{now}.xlsx"
excelWriter = StyleFrame.ExcelWriter(fileName)
styledDataFrame = StyleFrame(groupTableincoming)
styledDataFrame.to_excel(excel_writer=excelWriter, best_fit=list(styledDataFrame.columns), index=False)
excelWriter.close()
bot.send_document(chat_id=chat_id, document=open(fileName, 'rb'), visible_file_name=f"МАРШРУТЫ {now}.xlsx", message_thread_id=thread_id)

insort = [Order["orderExternalId"] for Order in InSORTCellOrders if "orderExternalId" in Order.keys()]
insortStr = "\n".join(set(insort))
strings["Заказы в ячейках СОРТ:\n"] = insortStr

id_to_message = {
    "PACKED_KEEPED_DIRECT": "Батч упакован, на хранении: ",
    "NOT_ACCEPTED_BY_COURIER_DIRECT": "Батч не принят курьером: ",
    "AWAITING_SORT_DIRECT": "Батч для сортировки: ",
    "KEEPED_DIRECT": "Батч на хранении: ",
    "SORTING_IN_LOT_DIRECT": "Батч наполняется посылками: ",
    "SORTING_IN_LOT_KEEPED_DIRECT": "Батч наполняется посылками, в хранении: ",
    "SORTING_IN_LOT_RETURN": "ДО мешок наполняется посылками (не закрыт): "
}
for i in Panel["ORPHAN_PALLET"]:
    if i["systemName"] in id_to_message:
        strings[id_to_message[i["systemName"]]] = f"{i['count']}"

message = f"Текущая дата и время: {st.replace(microsecond=0)}\nКомпьютер: {os.getenv('COMPUTERNAME')}\n"
for key, value in strings.items():
    checkvalue = value.split("/")[0]
    if checkvalue.isdigit() and int(checkvalue) > 0:
        value = "<u>" + value + "</u>"
    message += key + str(value) + "\n"

with open('insort.csv', 'w+') as file:
    file.write(strings['Заказы в ячейках СОРТ:\n'])
bot.send_document(chat_id=chat_id, document=open('insort.csv', 'rb'), visible_file_name="В ячейках СОРТ.csv")
message += f"Время выполнения скрипта: {round((datetime.now() - st).total_seconds(), 2)} сек."
bot.send_message(chat_id, message, parse_mode='HTML')
if time(7, 00) <= st.time() <= time(9, 10):
    bot.send_message(1063498880, message, parse_mode='HTML')
with open('config.ini', 'w+', encoding="utf8") as configfile:
    config.write(configfile)
