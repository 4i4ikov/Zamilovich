import configparser
import json
from datetime import date
from pathlib import Path
from pprint import pprint

import pandas as pd
import requests
import urllib3

config = configparser.ConfigParser()
config.read("config.ini")
cookies = {
    "Session_id": config.get("Session", "Session_id"),
}
headers = {
    "sk": config.get("Session", "sk"),
}
urllib3.disable_warnings()
requestsSession = requests.Session()
requestsSession.verify = False
requestsSession.cookies.update(cookies)
requestsSession.headers.update(headers)
cookies = {
    "yuidss": "7680259031708324569",
    "ymex": "2023684574.yrts.1708324574",
    "gdpr": "0",
    "font_loaded": "YSv1",
    "yashr": "9456999641708434584",
    "amcuid": "6469114791709011715",
    "my": "YyYBAS4BAToBAQA=",
    "upa_completed": "1",
    "receive-cookie-deprecation": "1",
    "skid": "8210919001716468732",
    "yandexuid": "7680259031708324569",
    "user_checked_chef_offer_ids_cross_domain": "%5B%22NbRJAoOBy220jueccE769Q%22%5D",
    "addressId": "3?1681119910?99766?01HYFQC9Y9PE217YG158F3RVZB",
    "express_address": "2?01HYFQC9Y9PE217YG158F3RVZB?0J/QvtGH0YLQvtCy0LDRjyDRg9C70LjRhtCw?MQ==",
    "yandexmarket": "48%2CRUR%2C1%2C%2C%2C%2C2%2C0%2C0%2C120268%2C0%2C0%2C12%2C0%2C0",
    "yabs-vdrf": "A0",
    "utm_medium": "search",
    "utm_source": "yandex",
    "utm_campaign": "ymp_generic_product_adv_dyb_search_rus",
    "utm_term": "none",
    "is_gdpr": "0",
    "is_gdpr_b": "CM6LYRDviwIoAg==",
    "pof": "%7B%22clid%22%3A%5B%22703%22%5D%2C%22distr_type%22%3Anull%2C%22mclid%22%3Anull%2C%22opp%22%3Anull%2C%22vid%22%3Anull%2C%22erid%22%3Anull%7D",
    "cpa-pof": "%7B%22clid%22%3A%5B%22703%22%5D%2C%22distr_type%22%3Anull%2C%22mclid%22%3Anull%2C%22opp%22%3Anull%2C%22vid%22%3Anull%2C%22erid%22%3Anull%7D",
    "isa": "Tmrrmhn3iotn3io+/8yT6R13TV9HbC5nWAUu8d/3Nj38E8/YxoOVaRYV/HOvJGFYkfRSFROFCVmcurjdn/8Jcy3BY64=",
    "sae": "0:8537C95E-E420-4172-828D-3AF0A52A9FBA:p:24.7.0.2379:w:d:RU:20240219",
    "Session_id": "3:1723646707.5.1.1709102902135:kBrTsA:1c.1.2:1|1908752670.0.2.3:1709102902|1681119910.-1.2.2:7351865.3:1716454767|3:10293489.830754.5FRXA2FpOmUp_iX9GdcWCKO6lGM",
    "sessar": "1.1192.CiBFLemDZ9qmmDBxf_vVfkyZQyX_dbLEQPwZskTv1podKg.wUVTy_JBha6B3egNv_UMYPbdQeRPImDwaRCf8LQxuCs",
    "sessionid2": "3:1723646707.5.1.1709102902135:kBrTsA:1c.1.2:1|1908752670.0.2.3:1709102902|1681119910.-1.2.2:7351865.3:1716454767|3:10293489.830754.fakesign0000000000000000000",
    "L": "XilaVmB+dnZiS2FYeWEBdFdFSQlDWFF4KiMrLhc2eQ==.1723646707.15846.397513.0b91a447686811ee7c100d3598baa0b6",
    "yandex_login": "Rusegg1",
    "cycada": "AqXjXmPrQramIzvwC2ZmShbG1y0TjzqK/4YFkfOyJ84=",
    "i": "iFzZUpUG93pWChCuXMVyLByJ3MsN4Bic8h2S6zkzIQ3kZBLifnZ2WBv+c9687brt508Am0RKQCGiM6Km/qdEuv13txs=",
    "visits": "1708324960-1723789019-1724046175",
    "pi_exp": "pi_user",
    "ys": "def_bro.1#ead.2FECB7CF#udn.cDrQoNGD0YHQu9Cw0L0g0JTQvNC40YLRgNC40LXQstC40Ycg0JrQvtC30LvQvtCy#wprid.1723811207957094-17567933286378657058-balancer-l7leveler-kubr-yp-sas-108-BAL#c_chck.3313681631",
    "yp": "1724140565.uc.ru#1724140565.duc.ru#1748768493.brd.6302000000#1748768493.cld.2270452#2039006707.udn.cDrQoNGD0YHQu9Cw0L0g0JTQvNC40YLRgNC40LXQstC40Ycg0JrQvtC30LvQvtCy#2039171367.pcs.0#2031814767.multib.1#1725121366.hdrc.1#1724062566.gpauto.55_653549:49_282063:100000:3:1724055366#1737421313.szm.0_8999999761581421:1920x1080:2114x1044#1753254828.stltp.serp_bk-map_1_1721718828",
    "_yasc": "P3gDTPrdv7IDsqdIJ3QnxpAoqGCRkNyxNfGO0RCDnzdkW4OFyZenBMewbAF/WdhfowSzgAVkjok1MVfoFDkMAPip0885dQ==",
    "bh": "Ek8iTm90L0EpQnJhbmQiO3Y9IjgiLCAiQ2hyb21pdW0iO3Y9IjEyNiIsICJZYUJyb3dzZXIiO3Y9IjI0LjciLCAiWW93c2VyIjt2PSIyLjUiGgUieDg2IiINIjI0LjcuMC4yMzc5IioCPzAyAiIiOgkiV2luZG93cyJCByI3LjAuMCJKBCI2NCJSZyJOb3QvQSlCcmFuZCI7dj0iOC4wLjAuMCIsICJDaHJvbWl1bSI7dj0iMTI2LjAuNjQ3OC4xNTMiLCAiWWFCcm93c2VyIjt2PSIyNC43LjAuMjM3OSIsICJZb3dzZXIiO3Y9IjIuNSJaAj8wYI+CjLYGaiHcyuH/CJLYobEDn8/h6gP7+vDnDev//fYP/bHAlgTzgQI=",
}

headers = {
    "Accept": "*/*",
    "Accept-Language": "ru,en;q=0.9",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    # 'Cookie': 'yuidss=7680259031708324569; ymex=2023684574.yrts.1708324574; gdpr=0; font_loaded=YSv1; yashr=9456999641708434584; amcuid=6469114791709011715; my=YyYBAS4BAToBAQA=; upa_completed=1; receive-cookie-deprecation=1; skid=8210919001716468732; yandexuid=7680259031708324569; user_checked_chef_offer_ids_cross_domain=%5B%22NbRJAoOBy220jueccE769Q%22%5D; addressId=3?1681119910?99766?01HYFQC9Y9PE217YG158F3RVZB; express_address=2?01HYFQC9Y9PE217YG158F3RVZB?0J/QvtGH0YLQvtCy0LDRjyDRg9C70LjRhtCw?MQ==; yandexmarket=48%2CRUR%2C1%2C%2C%2C%2C2%2C0%2C0%2C120268%2C0%2C0%2C12%2C0%2C0; yabs-vdrf=A0; utm_medium=search; utm_source=yandex; utm_campaign=ymp_generic_product_adv_dyb_search_rus; utm_term=none; is_gdpr=0; is_gdpr_b=CM6LYRDviwIoAg==; pof=%7B%22clid%22%3A%5B%22703%22%5D%2C%22distr_type%22%3Anull%2C%22mclid%22%3Anull%2C%22opp%22%3Anull%2C%22vid%22%3Anull%2C%22erid%22%3Anull%7D; cpa-pof=%7B%22clid%22%3A%5B%22703%22%5D%2C%22distr_type%22%3Anull%2C%22mclid%22%3Anull%2C%22opp%22%3Anull%2C%22vid%22%3Anull%2C%22erid%22%3Anull%7D; isa=Tmrrmhn3iotn3io+/8yT6R13TV9HbC5nWAUu8d/3Nj38E8/YxoOVaRYV/HOvJGFYkfRSFROFCVmcurjdn/8Jcy3BY64=; sae=0:8537C95E-E420-4172-828D-3AF0A52A9FBA:p:24.7.0.2379:w:d:RU:20240219; Session_id=3:1723646707.5.1.1709102902135:kBrTsA:1c.1.2:1|1908752670.0.2.3:1709102902|1681119910.-1.2.2:7351865.3:1716454767|3:10293489.830754.5FRXA2FpOmUp_iX9GdcWCKO6lGM; sessar=1.1192.CiBFLemDZ9qmmDBxf_vVfkyZQyX_dbLEQPwZskTv1podKg.wUVTy_JBha6B3egNv_UMYPbdQeRPImDwaRCf8LQxuCs; sessionid2=3:1723646707.5.1.1709102902135:kBrTsA:1c.1.2:1|1908752670.0.2.3:1709102902|1681119910.-1.2.2:7351865.3:1716454767|3:10293489.830754.fakesign0000000000000000000; L=XilaVmB+dnZiS2FYeWEBdFdFSQlDWFF4KiMrLhc2eQ==.1723646707.15846.397513.0b91a447686811ee7c100d3598baa0b6; yandex_login=Rusegg1; cycada=AqXjXmPrQramIzvwC2ZmShbG1y0TjzqK/4YFkfOyJ84=; i=iFzZUpUG93pWChCuXMVyLByJ3MsN4Bic8h2S6zkzIQ3kZBLifnZ2WBv+c9687brt508Am0RKQCGiM6Km/qdEuv13txs=; visits=1708324960-1723789019-1724046175; pi_exp=pi_user; ys=def_bro.1#ead.2FECB7CF#udn.cDrQoNGD0YHQu9Cw0L0g0JTQvNC40YLRgNC40LXQstC40Ycg0JrQvtC30LvQvtCy#wprid.1723811207957094-17567933286378657058-balancer-l7leveler-kubr-yp-sas-108-BAL#c_chck.3313681631; yp=1724140565.uc.ru#1724140565.duc.ru#1748768493.brd.6302000000#1748768493.cld.2270452#2039006707.udn.cDrQoNGD0YHQu9Cw0L0g0JTQvNC40YLRgNC40LXQstC40Ycg0JrQvtC30LvQvtCy#2039171367.pcs.0#2031814767.multib.1#1725121366.hdrc.1#1724062566.gpauto.55_653549:49_282063:100000:3:1724055366#1737421313.szm.0_8999999761581421:1920x1080:2114x1044#1753254828.stltp.serp_bk-map_1_1721718828; _yasc=P3gDTPrdv7IDsqdIJ3QnxpAoqGCRkNyxNfGO0RCDnzdkW4OFyZenBMewbAF/WdhfowSzgAVkjok1MVfoFDkMAPip0885dQ==; bh=Ek8iTm90L0EpQnJhbmQiO3Y9IjgiLCAiQ2hyb21pdW0iO3Y9IjEyNiIsICJZYUJyb3dzZXIiO3Y9IjI0LjciLCAiWW93c2VyIjt2PSIyLjUiGgUieDg2IiINIjI0LjcuMC4yMzc5IioCPzAyAiIiOgkiV2luZG93cyJCByI3LjAuMCJKBCI2NCJSZyJOb3QvQSlCcmFuZCI7dj0iOC4wLjAuMCIsICJDaHJvbWl1bSI7dj0iMTI2LjAuNjQ3OC4xNTMiLCAiWWFCcm93c2VyIjt2PSIyNC43LjAuMjM3OSIsICJZb3dzZXIiO3Y9IjIuNSJaAj8wYI+CjLYGaiHcyuH/CJLYobEDn8/h6gP7+vDnDev//fYP/bHAlgTzgQI=',
    "Pragma": "no-cache",
    "Referer": "https://hubs.market.yandex.ru/sorting-center/1100000040/zones",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 YaBrowser/24.7.0.0 Safari/537.36",
    "dnt": "1",
    "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "YaBrowser";v="24.7", "Yowser";v="2.5"',
    "sec-ch-ua-arch": '"x86"',
    "sec-ch-ua-bitness": '"64"',
    "sec-ch-ua-full-version-list": '"Not/A)Brand";v="8.0.0.0", "Chromium";v="126.0.6478.153", "YaBrowser";v="24.7.0.2379", "Yowser";v="2.5"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-ch-ua-platform-version": '"7.0.0"',
    "sec-ch-ua-wow64": "?0",
    "sec-gpc": "1",
}

response = requests.get(
    "https://hubs.market.yandex.ru/api/gateway/sorting-center/1100000040/zones",
    cookies=cookies,
    headers=headers,
)
if response.status_code != 200: print("ошибка запроса")
panda = pd.json_normalize(response.json()["zones"])
