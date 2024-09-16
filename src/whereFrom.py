import configparser
from datetime import date

import pandas as pd
import requests
import urllib3

import utils


def get_info_by_orders(orders, requestsSession_local):
    print(f"узнаю откуда заказы:{orders}")
    global requestsSession
    requestsSession = requestsSession_local
    return_dataframes = []
    for order in orders:
        print("узнаю откуда заказ", order)
        return_dataframes.append(get_info_by_order(order))
    is_empty_dfs = [not x.empty for x in return_dataframes]
    if any(is_empty_dfs):
        return_dataframe = pd.concat(return_dataframes)
    else:
        return_dataframe = pd.DataFrame(columns=["Не удалось"])
    return_dataframe.to_excel("output.xlsx", index=False)
    print(return_dataframe)


def get_info_by_order(order):
    response = request_get_info_by_order_request(order)
    list_dataframe_of_sortables = []
    if response.status_code == 200:
        response_json = response.json()
        sortables = response_json["results"][1]["data"]["content"]
        columns = [
            "Код грузоместа",
            "Номер заказа",
            "В каком лоте пришел",
            "Номер поставки",
            "Откуда",
            "Таймслот прибытия",
        ]
        if response_json["results"][0].get("error"):
            print("Response has error")
            dataframe_of_sortables = pd.DataFrame(columns=columns)
            dataframe_of_sortables.loc[0] = [
                None,
                order,
                None,
                None,
                None,
                None,
            ]
        else:
            list_dataframe_of_sortables.append(get_info_by_sortables(order, sortables, columns))
            dataframe_of_sortables = pd.concat(list_dataframe_of_sortables)
        return dataframe_of_sortables
    else:
        utils.updatesk(requestsSession)
        return get_info_by_order(order)


def get_info_by_sortables(order, sortables, columns) -> pd.DataFrame:
    return_dataframe_of_sortables = pd.DataFrame(columns=columns)

    for sortable in sortables:
        sortable_id = sortable["sortableId"]
        inbound_External_Id = None
        inbound_supplier_name = None
        inbound_timeslot = None
        parent_lot_of_sortable, parent_lot_of_sortable_id = get_parent_lot_of_sortable(sortable_id)
        if parent_lot_of_sortable:
            lot_info = request_get_info_of_sortable(parent_lot_of_sortable)

            lot_info_json = pd.json_normalize(lot_info.json()["results"][0]["data"]["content"])
            values = lot_info_json["groupingDirections"].values
            is_it_potovarka_group = False
            if values:
                is_it_potovarka_group = (
                    "group" in str(values[0][0]["code"]).lower()
                    or "presort" in str(values[0][0]["code"]).lower()
                )
            # потоварка
            if is_it_potovarka_group:
                grandparent_lot, grandparent_lot_id = get_parent_lot_of_sortable(
                    parent_lot_of_sortable_id
                )
                lot_info = request_get_info_of_sortable(grandparent_lot)
                lot_info_json = pd.json_normalize(lot_info.json()["results"][0]["data"]["content"])
            if "inboundExternalId" in lot_info_json.columns:
                inbound_External_Id = lot_info_json["inboundExternalId"].values[0]
                inbound_info = request_get_inbound_by_external_id(inbound_External_Id)
                inbound_info_formatted = pd.json_normalize(
                    inbound_info.json()["results"][0]["data"]["content"]
                )
                inbound_supplier_name = inbound_info_formatted["supplierName"].values[0]
                inbound_timeslot = (
                    inbound_info_formatted["arrivalIntervalStart"]
                    .astype("datetime64[ns]")
                    .values[0]
                )

        return_dataframe_of_sortables.loc[len(return_dataframe_of_sortables.index)] = [
            sortable["sortableBarcode"],
            order,
            parent_lot_of_sortable,
            inbound_External_Id,
            inbound_supplier_name,
            inbound_timeslot,
        ]

        # pd_sortable_history.to_excel(
        #     f"{order}/{sortable_id}.xlsx", index=False)

    return return_dataframe_of_sortables


def get_parent_lot_of_sortable(sortable_id):
    sortable_history = get_sortable_history(sortable_id)
    pd_sortable_history = pd.json_normalize(sortable_history.json()["results"][0]["data"])
    if (
        "parentId" in pd_sortable_history.columns
        and not pd_sortable_history["parentId"].isnull().all()
    ):
        index = pd_sortable_history["parentId"].last_valid_index()
        lot_of_sortable = pd_sortable_history.iloc[[index]]["parentBarcode"].values[0]
        lot_of_sortable_id = pd_sortable_history.iloc[[index]]["parentId"].values[0]
        return lot_of_sortable, lot_of_sortable_id
    else:
        return None, None


def request_get_info_by_order_request(order):
    json_data = {
        "params": [
            {
                "sortingCenterId": 1100000040,
                "orderId": order,
            },
            {
                "sortableStatuses": [],
                "stages": [],
                "orderExternalId": order,
                "inboundIdTitle": "",
                "outboundIdTitle": "",
                "groupingDirectionId": "",
                "groupingDirectionName": "",
                "sortingCenterId": 1100000040,
                "page": 0,
                "size": 20,
                "sortableTypes": [],
                "crossDockOnly": False,
            },
        ],
        "path": "/sorting-center/1100000040/sortables",
    }

    response = requestsSession.post(
        "https://logistics.market.yandex.ru/api/resolve/?r=sortingCenter/orders/resolveOrder:resolveOrder&r=sortingCenter/sortables/resolveSortableReport:resolveSortableReport",
        json=json_data,
        verify=False,
    )

    return response


def request_get_inbound_by_external_id(inboundExternalId):
    today = str(date.today())
    json_data = {
        "params": [
            {
                "sortingCenterId": 1100000040,
                "date": today,
                "dateTo": today,
                "namePart": inboundExternalId,
                "page": 1,
                "size": 20,
            },
        ],
        "path": "/sorting-center/1100000040/inbounds?namePart=" + inboundExternalId,
    }

    return requestsSession.post(
        "https://logistics.market.yandex.ru/api/resolve/?r=sortingCenter/inbounds/resolveInboundList:resolveInboundList",
        json=json_data,
    )


def request_get_info_of_sortable(sortableBarcode):
    json_data = {
        "params": [
            {
                "sortableStatuses": [],
                "stages": [],
                "inboundIdTitle": "",
                "outboundIdTitle": "",
                "groupingDirectionId": "",
                "groupingDirectionName": "",
                "sortableBarcode": sortableBarcode,
                "sortingCenterId": 1100000040,
                "page": 0,
                "size": 1,
                "sortableTypes": [],
                "crossDockOnly": False,
            },
        ],
        "path": "/sorting-center/1100000040/sortables?sortableTypes=&sortableStatuses=&sortableStatusesLeafs=&inboundIdTitle=&outboundIdTitle=&groupingDirectionId=&groupingDirectionName=&sortableBarcode=DRP3020133358",
    }

    return requestsSession.post(
        "https://logistics.market.yandex.ru/api/resolve/?r=sortingCenter/sortables/resolveSortableReport:resolveSortableReport",
        json=json_data,
    )


def get_sortable_history(sortableIds):
    json_data = {
        "params": [
            {
                "sortingCenterId": 1100000040,
                "id": sortableIds,
            },
        ],
        "path": "/sorting-center/1100000040/sortables/10000094719325",
    }
    response = requestsSession.post(
        "https://logistics.market.yandex.ru/api/resolve/?r=sortingCenter/sortables/resolveSortableHistory:resolveSortableHistory",
        json=json_data,
        verify=False,
    )
    return response


requestsSession = requests.Session()


def get_config():
    config = configparser.ConfigParser()
    config.read("config.ini")
    cookies = {
        "Session_id": config.get("Session", "Session_id"),
    }
    headers = {
        "sk": config.get("Session", "sk"),
    }
    urllib3.disable_warnings()
    requestsSession_local = requests.Session()
    requestsSession_local.verify = False
    requestsSession_local.cookies.update(cookies)
    requestsSession_local.headers.update(headers)
    return requestsSession_local


if __name__ == "__main__":
    requestsSession_local = get_config()
    file = open("input/input.txt", "r")
    data = file.read()
    orders = data.split("\n")
    orders = sorted(set(orders), key=orders.index)
    get_info_by_orders(orders, requestsSession_local)
