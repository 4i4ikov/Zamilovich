import configparser
# import json
from datetime import date
from pathlib import Path
from pprint import pprint

import pandas as pd
import requests
import urllib3

config = configparser.ConfigParser()
config.read("config.ini")
cookies = {
    'Session_id': config.get("Session", "Session_id"),
}
headers = {
    'sk': config.get('Session', 'sk'),
}
urllib3.disable_warnings()
main_session = requests.Session()
main_session.verify = False
main_session.cookies.update(cookies)
main_session.headers.update(headers)


def get_info_by_order(order):
    pprint(order)
    Path(order).mkdir(parents=True, exist_ok=True)
    json_data = {
        'params': [
            {
                'sortingCenterId': 1100000040,
                'orderId': order,
            },
            {
                'sortableStatuses': [],
                'stages': [],
                'orderExternalId': order,
                'inboundIdTitle': '',
                'outboundIdTitle': '',
                'groupingDirectionId': '',
                'groupingDirectionName': '',
                'sortingCenterId': 1100000040,
                'page': 0,
                'size': 20,
                'sortableTypes': [],
                'crossDockOnly': False,
            },
        ],
        'path': '/sorting-center/1100000040/sortables',
    }

    response = main_session.post(
        'https://logistics.market.yandex.ru/api/resolve/?r=sortingCenter/orders/resolveOrder:resolveOrder&r=sortingCenter/sortables/resolveSortableReport:resolveSortableReport',
        cookies=cookies,
        headers=headers,
        json=json_data,
        verify=False
    )
    if response.status_code == 200:
        sortables = response.json()["results"][1]["data"]["content"]
        return_string = f"{order}:"
        for sortable in sortables:
            sortable_id = sortable["sortableId"]
            sortable_history = get_sortable_history(sortable_id)
            pd_sortable_history = pd.json_normalize(
                sortable_history.json()["results"][0]["data"])
            index = pd_sortable_history["parentId"].last_valid_index()
            lot_of_sortable = pd_sortable_history.iloc[[
                index]]["parentBarcode"].values[0]
            pprint(lot_of_sortable)
            lot_info = get_info_of_sortable(lot_of_sortable)
            inbound_external_id = pd.json_normalize(lot_info.json(
            )["results"][0]["data"]["content"])["inboundExternalId"].values[0]
            inbound_info = get_inbound_by_external_id(inbound_external_id)
            inbound_info_formatted = pd.json_normalize(
                inbound_info.json()["results"][0]["data"]["content"])
            pprint(inbound_info_formatted.values)
            inbound_supplier_name = inbound_info_formatted["supplierName"].values[0]
            inbound_timeslot = inbound_info_formatted["supplierName"].values[0]
            return_string += f"\n{sortable['sortableBarcode']
                                  } {lot_of_sortable}, {inbound_supplier_name}"
            # min_row = panda[panda.createdAt == panda.createdAt.min()]
            pd_sortable_history.to_excel(
                f"{order}/{sortable_id}.xlsx", index=False)
        all_info_for_return = [order, sortable['sortableBarcode'], lot_of_sortable,
                               inbound_external_id, inbound_supplier_name, inbound_timeslot]
        pprint(all_info_for_return)
    else:
        print('Ошибка в результате запроса.')


def do_next_step(response):

    sortableId = response.json(
    )["results"][0]["data"]["content"][0]["sortableId"]
    get_sortable_history(sortableId)


def get_inbound_by_external_id(inboundExternalId):
    today = str(date.today())
    json_data = {
        'params': [
            {
                'sortingCenterId': 1100000040,
                'date': today,
                'dateTo': today,
                'namePart': inboundExternalId,
                'page': 1,
                'size': 20,
            },
        ],
        'path': '/sorting-center/1100000040/inbounds?namePart='+inboundExternalId,
    }

    return main_session.post(
        'https://logistics.market.yandex.ru/api/resolve/?r=sortingCenter/inbounds/resolveInboundList:resolveInboundList',
        cookies=cookies,
        headers=headers,
        json=json_data,
    )


def get_info_of_sortable(sortableBarcode):
    json_data = {
        'params': [
            {
                'sortableStatuses': [],
                'stages': [],
                'inboundIdTitle': '',
                'outboundIdTitle': '',
                'groupingDirectionId': '',
                'groupingDirectionName': '',
                'sortableBarcode': sortableBarcode,
                'sortingCenterId': 1100000040,
                'page': 0,
                'size': 1,
                'sortableTypes': [],
                'crossDockOnly': False,
            },
        ],
        'path': '/sorting-center/1100000040/sortables?sortableTypes=&sortableStatuses=&sortableStatusesLeafs=&inboundIdTitle=&outboundIdTitle=&groupingDirectionId=&groupingDirectionName=&sortableBarcode=DRP3020133358',
    }

    return main_session.post(
        'https://logistics.market.yandex.ru/api/resolve/?r=sortingCenter/sortables/resolveSortableReport:resolveSortableReport',
        cookies=cookies,
        headers=headers,
        json=json_data,
    )


def get_sortable_history(sortableIds):
    pprint(sortableIds)
    json_data = {
        'params': [
            {
                'sortingCenterId': 1100000040,
                'id': sortableIds,
            },
        ],
        'path': '/sorting-center/1100000040/sortables/10000094719325',
    }
    response = main_session.post(
        'https://logistics.market.yandex.ru/api/resolve/?r=sortingCenter/sortables/resolveSortableHistory:resolveSortableHistory',
        cookies=cookies,
        headers=headers,
        json=json_data,
        verify=False
    )
    return response


if __name__ == "__main__":
    get_info_by_order("508898429")
