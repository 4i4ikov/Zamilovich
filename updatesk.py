import json
import warnings
# import logging
import requests
import urllib3
# logging.basicConfig(level=logging.DEBUG)
# import requests
warnings.filterwarnings("ignore")
urllib3.disable_warnings()

cookiesdefault = {
    'Session_id': '3:1712557139.5.0.1709102902135:kBrTsA:1c.1.2:1|1908752670.0.2.3:1709102902|3:10285709.69391.9NaRCtREm-DBXQxMWg9LaecvFAs',
}
def updatesk (cookies = cookiesdefault):
    response = requests.patch('https://logistics.market.yandex.ru/api/session',  cookies=cookies, verify=False)
    sk = ""
    if response.status_code==200:
        sk = response.json().get("user").get("sk")
    with open('sk.json', 'w',encoding="utf8") as outfile:
        json.dump(response.json(), outfile,indent=4,ensure_ascii=False)
    return sk
    
if __name__ == '__main__':
    updatesk()
