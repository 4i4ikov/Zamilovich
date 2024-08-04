import configparser
import warnings
import os
import urllib3
import updatesk as updatesk
from datetime import datetime, time,date
import json
import asinhrom
from styleframe import StyleFrame
import pandas as pd
# import json

import requests
# from pprint import pprint
# from bs4 import BeautifulSoup
import telebot
warnings.filterwarnings("ignore")
urllib3.disable_warnings()

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
UrlForRequest = 'https://logistics.market.yandex.ru/api/resolve/?'
UrlForRequest +='r=sortingCenter/sortables/resolveSortableStageStatistic:resolveSortableStageStatistic'#Панель грузомест
UrlForRequest +='&r=sortingCenter/routes/resolveGetRoutesFullInfo:resolveGetRoutesFullInfo'#CourierAll
UrlForRequest +='&r=sortingCenter/routes/resolveGetRoutesSummary:resolveGetRoutesSummary'#Courier cifri
UrlForRequest +='&r=sortingCenter/routes/resolveGetRoutesFullInfo:resolveGetRoutesFullInfo'#Magistral
UrlForRequest +='&r=sortingCenter/sortables/resolveSortableReport:resolveSortableReport' #D
UrlForRequest +='&r=sortingCenter/sortables/resolveSortableReport:resolveSortableReport' #Drop
UrlForRequest +='&r=sortingCenter/sortables/resolveSortableReport:resolveSortableReport' #Sort
UrlForRequest +='&r=sortingCenter/routes/resolveGetRoutesFullInfo:resolveGetRoutesFullInfo'
UrlForRequest +='&r=sortingCenter/sortables/resolveSortableReport:resolveSortableReport'
UrlForRequest +='&r=sortingCenter/sortables/resolveSortableReport:resolveSortableReport'
UrlForRequest +='&r=sortingCenter/sortables/resolveSortableReport:resolveSortableReport'
UrlForRequest +='&r=sortingCenter/sortables/resolveSortableReport:resolveSortableReport'
UrlForRequest +='&r=sortingCenter/inbounds/resolveInboundList:resolveInboundList'
UrlForRequest +='&r=sortingCenter/routes/resolveGetRoutesFullInfo:resolveGetRoutesFullInfo'


json_data = { # ПАНЕЛЬ ГРУЗОМЕСТ
    'params': [
        {# 0 Панель грузомест
            'sortingCenterId': 1100000040,
        },
        {# 1 КУРЬЕРКА, ВСЕ КУРЬЕРЫ
            'sortingCenterId': 1100000040,
            'page': 0,
            'size': 100,
            'category': 'COURIER',
            'hasCarts': False,
            'date': today,
            'sort': 'acceptedButNotSorted,desc',
            'type': 'OUTGOING_COURIER',
        },
        { # 2 КУРЬЕРКА, ЦИФРЫ
            'sortingCenterId': '1100000040',
            'date': today,
            'type': 'OUTGOING_COURIER',
            'category': 'COURIER',
        },
        { # 3 МАГИСТРАЛЬ
            'sortingCenterId': 1100000040,
            'page': 0,
            'size': 100,
            'category': 'MIDDLE_MILE_COURIER',
            'hasCarts': False,
            'date': today,
            'sort': '',
            'type': 'OUTGOING_COURIER',
        },
        { # 4 ГРУЗОМЕСТА В ЯЧ Д
            'sortableStatuses': [
            ],
            'stages': [],
            'cellName': '\\D-',
            'inboundIdTitle': '',
            'outboundIdTitle': '',
            'groupingDirectionId': '',
            'groupingDirectionName': '',
            'sortingCenterId': 1100000040,
            'page': 0,
            'size': 200,
            'sortableTypes': [
                'PLACE',
            ],
            'crossDockOnly': False,
        },
        { # 5 ГРУЗОМЕСТА В ДРОП
            'cellName': 'Drop',
            'sortableStatuses': [],
            'inboundIdTitle': '',
            'outboundIdTitle': '',
            'groupingDirectionId': '',
            'groupingDirectionName': '',
            'stages': [],
            'sortingCenterId': 1100000040,
            'page': 0,
            'size': 200,
            'sortableTypes': [],
            'crossDockOnly': False,
        },
        { # 6 ГРУЗОМЕСТА В СОРТ
            'cellName': 'SORT',
            'sortableStatuses': [],
            'inboundIdTitle': '',
            'outboundIdTitle': '',
            'groupingDirectionId': '',
            'groupingDirectionName': '',
            'stages': [],
            'sortingCenterId': 1100000040,
            'page': 0,
            'size': 200,
            'sortableTypes': [],
            'crossDockOnly': False,
        },
        { # 7 НЕ ПОЛНЫЕ МНОГОМЕСТКИ
            'sortingCenterId': 1100000040,
            'page': 0,
            'size': 20,
            'hasMultiplaceIncompleteInCell': True,
            'hasCarts': False,
            'date': today,
            'sort': '',
            'type': 'OUTGOING_COURIER',
        },
        { # 8 ПРЕДСОРТ ПРОЙДЕН ЧЕЛНЫ
            'sortableStatuses': ['ARRIVED_DIRECT'],
            'stages': [],
            'courierId': '10000000060066',
            'sortingCenterId': 1100000040,
            'page': 0,
            'size': 20,
            'sortableTypes': [
                'PLACE',
                'TOTE',
            ],
            'crossDockOnly': False,
        },
        {# 9 ПРЕДСОРТ ПРОЙДЕН ИЖЕВСК
            'sortableStatuses': ['ARRIVED_DIRECT'],
            'stages': [],
            'courierId': '10000000072156',
            'sortingCenterId': 1100000040,
            'page': 0,
            'size': 20,
            'sortableTypes': [
                'PLACE',
                'TOTE',
            ],
            'crossDockOnly': False,
        },
        {# 10 ПРЕДСОРТ ПРОЙДЕН ЧЕБОКСАРЫ
            'sortableStatuses': ['ARRIVED_DIRECT'],
            'stages': [],
            'courierId': '10000000028198',
            'sortingCenterId': 1100000040,
            'page': 0,
            'size': 20,
            'sortableTypes': [
                'PLACE',
                'TOTE',
            ],
            'crossDockOnly': False,
        },
        {# 11 ПРЕДСОРТ ПРОЙДЕН КИРОВ
            'sortableStatuses': ['ARRIVED_DIRECT'],
            'stages': [],
            'courierId': '10000000076237',
            'sortingCenterId': 1100000040,
            'page': 0,
            'size': 20,
            'sortableTypes': [
                'PLACE',
                'TOTE',
            ],
            'crossDockOnly': False,
        },
        {# 12 ЛАЙНХОЛЛЫ
            'sortingCenterId': 1100000040,
            'date': f'{today}',
            'dateTo': f'{today}',
            'types': [],
            'movementTypes': [
                'LINEHAUL',
            ],
            'statuses': [
                'ARRIVED',
                'IN_PROGRESS',
                'SIGNED',
                'FIXED',
                'CREATED'
            ],
            'page': 1,
            'size': 150,
        },
        {# 13 ПОСТАВКИ ПО МАРШРУТАМ
            'sortingCenterId': 1100000040,
            'page': 0,
            'size': 220,
            'hasCarts': False,
            'date': f'{today}',
            'sort': '',
            'type': 'INCOMING_WAREHOUSE',
        }
    ],
    'path': '/sorting-center/1100000040/stages',
}

API_TOKEN = config.get("BOT","API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)
chat_id = config.get("BOT","CHAT_ID")
thread_id = 0
bot.send_chat_action(chat_id=chat_id,action='typing') # 'upload_document'
response = sess.post( 
    UrlForRequest,
    json=json_data,
    verify=False
)

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

resultFromResponse = response.json()["results"]
Panel = resultFromResponse[0]["data"]
CourierAll = resultFromResponse[1]["data"]
CourierDigits = resultFromResponse[2]["data"]
# Magistral = resultFromResponse[3]["data"]["content"]

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
for check in Panel["PLACE"]:
    match check["id"]:
        case 4531: predsort = str (check["count"])
        case 3100: hranenie = str (check["count"])
        case 4100: forsort = str (check["count"])

strings = {
"ОСТАЛОСЬ ОТСОРТИРОВАТЬ В DO МЕШКИ: " : str(InDropOffCells["totalElements"]),
"В ячейке DROP: " : str(InDROPCell["totalElements"]),
"В ячейках SORT: " : str(InSORTCell["totalElements"]),
"На хранении: " : hranenie,
"Предсорт пройден: " : predsort,
"Челны: " : str(ChelnyPredsort["totalElements"]),
"Ижевск: " : str(IzhevskPredsort["totalElements"]),
"Чебоксары: " : str(CheboksaryPredsort["totalElements"]),
"Киров: " : str(KirovPredsort["totalElements"]),
"Для сортировки: " : forsort,
"Заказов курьерки к отгрузке: " : str(CourierDigits["ordersPlanned"]),
"Курьеров к отгрузке: " : str(CourierAll["totalElements"]),
"Не полные многоместки: " : str(NotFulledMM["totalElements"]),
"Осталось отсортировать курьерку: " : str(CourierDigits["acceptedButNotSorted"])
}

# routes = [courier["id"] for courier in CourierAll["content"]]

# urlsNotAcceptedByCourier = [f"https://logistics.market.yandex.ru/api/sorting-center/1100000040/sortables/download?searchRouteIdInOldRoutes=false&sortableStatuses=ARRIVED_DIRECT&sortableStatuses=KEEPED_DIRECT&sortingCenterId=1100000040&page=0&size=20&sortableTypes=PLACE&sortableTypes=TOTE&crossDockOnly=false&routeId={route}&" for route in routes]
# asinhrom.getAccepterdButNotSorted(urlsNotAcceptedByCourier)
inboundLinehaul = resultFromResponse[12]["data"]["content"]
inboundLinehaulDataFrame = pd.json_normalize(inboundLinehaul)
# inboundLinehaulDataFrame.drop(['car','trailerNumber',	'id',	'externalId',	'inboundStatus',	'movementType',	'movementSubtype',	'palletAmount',	'plannedPalletAmount',	'boxAmount',	'plannedBoxAmount',	'arrivalIntervalEnd','actions',	'complexActions',	'transportationId',	'documents',	'type']
# ,axis=1,inplace=True)
inboundLinehaulDataFrame = inboundLinehaulDataFrame[[
    # 'car',
    # 'trailerNumber',
    'inboundExternalId',
    'supplierName',
    'courierName',
    'arrivalIntervalStart',
    'acceptedAmount',	
    'totalAmount'
    ]]
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
inboundLinehaulDataFrame["ВРЕМЯ"] = pd.to_datetime(inboundLinehaulDataFrame["ВРЕМЯ"])
inboundLinehaulDataFrame = inboundLinehaulDataFrame.loc[inboundLinehaulDataFrame['План'] > 0]
inboundLinehaulDataFrame.sort_values(by="ВРЕМЯ",inplace=True)
columns = inboundLinehaulDataFrame.columns
now = st.strftime('%Y-%m-%d %H_%M')
fileName = f"./LINEHAUL/{now}.xlsx"
excelWriter = StyleFrame.ExcelWriter(fileName)
styledDataFrame = StyleFrame(inboundLinehaulDataFrame)
styledDataFrame.to_excel(excel_writer=excelWriter,best_fit=(list(columns.values)), row_to_add_filters=0,index=False)
excelWriter.close()
bot.send_document(chat_id=chat_id,document=open(fileName,'rb'),visible_file_name=f"ЛАЙНХОЛЛЫ {now}.xlsx",message_thread_id=thread_id)

incoming = resultFromResponse[13]["data"]["content"]
incomingDataFrame = pd.json_normalize(incoming)

vals = "warehouse.type	ordersPlanned	ordersCreated	ordersAccepted	ordersSorted	ordersShipped	acceptedButNotSorted".split("	")
valsRenamed = "Откуда	План	Не принято	Принято	Отсортировано	Отгружено	Осталось отсортировать".split("	")

groupTableincoming = incomingDataFrame.groupby(['warehouse.type']).sum().reset_index()
groupTableincoming = groupTableincoming[vals]
groupTableincoming.columns = valsRenamed
groupTableincoming["Дата"] = st
fileName = f"./POSTAVKI/{now}.xlsx"
excelWriter = StyleFrame.ExcelWriter(fileName)
styledDataFrame = StyleFrame(groupTableincoming)
styledDataFrame.to_excel(excel_writer=excelWriter,
                         best_fit=list(styledDataFrame.columns),
                         index=False)
excelWriter.close()
bot.send_document(chat_id=chat_id,document=open(fileName,'rb'),visible_file_name=f"МАРШРУТЫ {now}.xlsx",message_thread_id=thread_id)

# routes = [courier["id"] for courier in CourierAll["content"]]

# urlsNotAcceptedByCourier = [f"https://logistics.market.yandex.ru/api/sorting-center/1100000040/sortables/download?searchRouteIdInOldRoutes=false&sortableStatuses=ARRIVED_DIRECT&sortableStatuses=KEEPED_DIRECT&sortingCenterId=1100000040&page=0&size=20&sortableTypes=PLACE&sortableTypes=TOTE&crossDockOnly=false&routeId={route}&" for route in routes]
# asinhrom.getAccepterdButNotSorted(urlsNotAcceptedByCourier)

# if time(5,00) <= st.time() <= time(10,10):
insort = []
insortStr = ""
for Order in InSORTCellOrders:
    if "orderExternalId" in Order.keys():
        insort.append(f"{Order["orderExternalId"]}") #  {Order["cellName"]}
for Order in set(insort):
    insortStr += f"{Order}\n"
strings["Заказы в ячейках СОРТ:\n"] = insortStr

# for j in Magistral:
#     match j["courier"]["id"]:
#         case 1100000000062363:
#             strings["Осталось отсортировать Ижевск: "] = str(j["acceptedButNotSorted"])
#         case 1100000000058185:
#             strings["Осталось отсортировать Челны: "] = str(j["acceptedButNotSorted"])



for i in Panel["ORPHAN_PALLET"]:
      match i["systemName"]:
       case "PACKED_KEEPED_DIRECT": # Батч подготовлен в хранении
           strings["Батч упакован, на хранении: "] = f"{i["count"]}"
       case "NOT_ACCEPTED_BY_COURIER_DIRECT": # не принят курьером
           strings["Батч не принят курьером: "] = f"{i["count"]}"
       case "AWAITING_SORT_DIRECT": # для сортировки
           strings["Батч для сортировки: "] = f"{i["count"]}"
       case "KEEPED_DIRECT": # на хранении
           strings["Батч на хранении: "] = f"{i["count"]}"
       case "SORTING_IN_LOT_DIRECT": # наполняется посылками
           strings["Батч наполняется посылками: "] = f"{i["count"]}"
       case "SORTING_IN_LOT_KEEPED_DIRECT": # наполняется посылками в хранении
           strings["Батч наполняется посылками, в хранении: "] = f"{i["count"]}"
       case "SORTING_IN_LOT_RETURN": # возвратный батч наполняется посылками
           strings["ДО мешок наполняется посылками (не закрыт): "] = f"{i["count"]}"

message = f"Текущая дата и время: {st.replace(microsecond=0)}\nКомпьютер: {os.getenv('COMPUTERNAME')}\n"
for key,value in strings.items():
    checkvalue = value.split("/")[0]
    if (checkvalue.isdigit() and int(checkvalue) > 0):
        value = "<u>" + value + "</u>"
        message += key +  str (value) + "\n"
# message += f'Заказы в ячейках СОРТ: {}'
# pprint(message)
with open('insort.csv','w+') as file:
    file.write(strings['Заказы в ячейках СОРТ:\n'])
bot.send_document(chat_id=chat_id,document=open('insort.csv','rb'),visible_file_name=f"В ячейках СОРТ.csv")
# bot.send_document(chat_id=chat_id,document=open("AcceptedButNotSorted.xlsx",'rb'),visible_file_name=f"Осталось отсортировать {now}.xlsx")
message += f"Время выполнения скрипта: {round((datetime.now()-st).total_seconds(),2)} сек."
bot.send_message(chat_id, message,parse_mode='HTML')    
if time(7,00) <= st.time() <= time(9,10):
    bot.send_message(1063498880,message,parse_mode='HTML')
with open('config.ini','w+', encoding="utf8") as configfile:
    config.write(configfile)

# with open('somefile.json', 'w',encoding="utf8") as outfile:
    
#     json.dump(response.json(), outfile,indent=4,ensure_ascii=False)