from typing import Union
from hmac import new
from hashlib import sha1
from base64 import b64encode, urlsafe_b64decode
from json import loads
from os import urandom
from time import time as timestamp
sid = None
user_Id = None
PREFIX = bytes.fromhex("19")
SIG_KEY = bytes.fromhex("DFA5ED192DDA6E88A12FE12130DC6206B1251E44")
DEVICE_KEY = bytes.fromhex("E7309ECC0953C6FA60005B2765F99DBBC965C8E9")
def signature(data: Union[str, bytes]):
	data = data if isinstance(data, bytes) else data.encode("utf-8")
	return b64encode(PREFIX + new(SIG_KEY, data, sha1).digest()).decode("utf-8")
def generate_deviceId():
	ur = PREFIX + (urandom(20))
	mac = new(DEVICE_KEY, ur, sha1)
	return f"{ur.hex()}{mac.hexdigest()}".upper()
class Headers:
    def __init__(self, sid: str = None,data:str=None,user_agent: str = "Apple iPhone12,1 iOS v15.5 Main/3.12.2", language: str = "en"):
        self.headers = {
            "cookie": f"sid={sid}",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/73.0.3683.86 Chrome/73.0.3683.86 Safari/537.36",
            "x-requested-with": "xmlhttprequest"
            }
        self.headers["set-cookie"] = f"sid={sid}"
        if user_Id:
                self.user_Id = user_Id
      

        self.headers_v2 = {
		"NDCDEVICEID": generate_deviceId(),
		"NDCLANG": language.lower(),
		"Accept-Language": f"{language.lower()}-{language.upper()}",
		"User-Agent": user_agent,
		"Host": "service.aminoapps.com",
		"Accept-Encoding": "identity",
		"Accept": "*/*",
		"Connection": "keep-alive",
		}
        if data:
        	self.headers_v2["Content-Length"] = str(len(data))
		self.headers_v2["Content-Type"]="application/json; charset=utf-8"
        	self.headers_v2["NDC-MSG-SIG"] = signature(data=data)
        if sid:self.headers_v2["NDCAUTH"] = f"sid={sid}"
        if user_Id:self.headers_v2["AUID"] = user_Id
