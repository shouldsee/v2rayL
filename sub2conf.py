# -*- coding:utf-8 -*-
# author: Suummmmer

import base64
import json
import pickle
import requests
from config import conf_template as conf
import os
import json

CONFIG_DIR = "./v2rayL-config"
if not os.path.isdir(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)


class Sub2Conf(object):
    def __init__(self, subs_url=None, conf_url=None):
        # 订阅原始数据
        self.origin = []
        
        self.subs_url = subs_url
        self.conf_url = conf_url

        # 解析后配置
        try:
            with open(CONFIG_DIR + "/data", "rb") as f:
                self.saved_conf = pickle.load(f)
        except:
            self.saved_conf = {
                "local": {},
                "subs": {}
            }
        
        self.conf = dict(self.saved_conf['local'], **self.saved_conf['subs'])

        '''
        self.conf结构
        {
            "地区"： "配置"
        }

        配置为解析得到的内容 + 协议
        '''

        # if subs_url:  
        #     try:
        #         ret = requests.get(subs_url)
        #         if ret.status_code != 200:
        #             return 
        #         all_subs = base64.b64decode(ret.text + "==").decode().strip().split("\n")
        #     except Exception as e:
        #         pass

        #     for sub in all_subs:
        #         self.origin.append(sub.split("://"))

        #     for ori in self.origin:
        #         if ori[0] == "vmess":
        #             self.b642conf("vmess", ori[1])
        #         elif ori[0] == "ss":
        #             self.b642conf("ss", ori[1])

        # if conf_url:
        #     try:
        #         op = conf_url.split("://")
        #         if op[0] == "vmess":
        #             self.b642conf("vmess", op[1])
        #         elif op[0] == "ss":
        #             self.b642conf("ss", op[1])
        #     except:
        #         pass
 
        # with open("/etc/v2rayL/data", "wb") as jf:
        #     pickle.dump(self.conf, jf)


    def b642conf(self, prot, tp, b64str):
        if prot == "vmess":
            x = base64.b64decode(b64str + "==").decode()
            ret = json.loads(x)
            region = ret['ps']

        elif prot == "ss":
            string = b64str.split("#")
            cf = string[0].split("@")
            if len(cf) == 1:
                tmp = base64.b64decode(cf[0] + "==").decode()  # aes-256-cfb:541603466@142.93.50.78:9898
            else:
                tmp = base64.b64decode(cf[0] + "==").decode()+"@"+cf[1]
            ret = {
                "method": tmp.split(":")[0],
                "port": tmp.split(":")[2],
                "password": tmp.split(":")[1].split("@")[0],
                "add": tmp.split(":")[1].split("@")[1],
            }
            region = string[1]

        ret["prot"] = prot
        self.saved_conf[["local", "subs"][tp]][region] = ret


    def setconf(self, region):
        use_conf = self.conf[region]
        if use_conf['prot'] == "vmess":
            conf['outbounds'][0]["protocol"] = "vmess"
            conf['outbounds'][0]["settings"]["vnext"] = list()
            conf['outbounds'][0]["settings"]["vnext"].append({
                "address": use_conf["add"],
                "port": int(use_conf["port"]),
                "users": [
                  {
                    "id": use_conf["id"],
                    "alterId": use_conf["aid"]
                  }
                ] 
            })

            conf['outbounds'][0]["streamSettings"] = {
                "network": use_conf["net"],
                "wsSettings":{
                  "path": use_conf["path"],
                  "headers": {
                    "Host": use_conf['host']
                  }
                }
            }

        elif use_conf['prot'] == "ss":
            conf['outbounds'][0]["protocol"] = "shadowsocks"
            conf['outbounds'][0]["settings"]["servers"] = list()
            conf['outbounds'][0]["settings"]["servers"].append({
                "address": use_conf["add"],
                "port": int(use_conf["port"]),
                "password": use_conf["password"],
                "ota": False,
                "method": use_conf["method"]
            })
            conf['outbounds'][0]["streamSettings"] = {
                "network": "tcp"
            }

        
        with open(CONFIG_DIR + "/config.json", "w") as f:
            f.write(json.dumps(conf, indent=4))

    
    def delconf(self, region):
        self.conf.pop(region)
        try:
            self.saved_conf['local'].pop(region)
        except:
            self.saved_conf['subs'].pop(region)

        with open(CONFIG_DIR + "/data/", "wb") as jf:
            pickle.dump(self.saved_conf, jf)
    

    def update(self):
        """
        更新订阅
        """
        try:
            ret = requests.get(self.subs_url, headers={'user-agent': 'v2rayL/1.0'})
            if ret.status_code != 200:
                return 
            all_subs = base64.b64decode(ret.text + "==").decode().strip().split("\n")
        except Exception as e:
            raise "wrong"

        for sub in all_subs:
            self.origin.append(sub.split("://"))

        self.saved_conf["subs"] = {}

        for ori in self.origin:
            if ori[0] == "vmess":
                self.b642conf("vmess", 1, ori[1])
            elif ori[0] == "ss":
                self.b642conf("ss", 1, ori[1])

        self.conf = dict(self.saved_conf['local'], **self.saved_conf['subs'])

        with open(CONFIG_DIR +"/data", "wb") as jf:
            pickle.dump(self.saved_conf, jf)


    def add_conf_by_uri(self):
        """
        通过分享的连接添加配置
        """
        try:
            op = self.conf_url.split("://")
            if op[0] == "vmess":
                self.b642conf("vmess", 0, op[1])
            elif op[0] == "ss":
                self.b642conf("ss", 0, op[1])
        except:
            raise "wrong"

        self.conf = dict(self.saved_conf['local'], **self.saved_conf['subs'])

        with open( CONFIG_DIR + "/data", "wb") as jf:
            pickle.dump(self.saved_conf, jf)

# def b642conf(prot, b64str):
#         if prot == "vmess":
#             ret = eval(base64.b64decode(b64str).decode())
#             region = ret['ps']
#         elif prot == "ss":
#             string = b64str.split("#")
#             tmp = base64.b64decode(string[0]).decode()  # aes-256-cfb:541603466@142.93.50.78:9898
#             ret = {
#                 "method": tmp.split(":")[0],
#                 "port": tmp.split(":")[2],
#                 "password": tmp.split(":")[1].split("@")[0],
#                 "address": tmp.split(":")[1].split("@")[1],
#             }
#             region = string[1]

#         ret["prot"] = prot
#         print(ret)
#         exit()
#         self.conf[region] = ret

if __name__ == '__main__':
    # s = Sub2Conf("https://sub.qianglie.xyz/subscribe.php?sid=4594&token=TCDWnwMD0rGg")
    # print(s.conf)

    # s.setconf("1.0x TW-BGP-A 台湾")

    # t = base64.b64decode("ewoidiI6ICIyIiwKInBzIjogIjIzM3YyLmNvbV8xNDIuOTMuNTAuNzgiLAoiYWRkIjogIjE0Mi45My41MC43OCIsCiJwb3J0IjogIjM5Mzk4IiwKImlkIjogIjc1Y2JmYzI0LTZhNjAtNDBmMC05Yjc2LTUyMTlmNTIwYTJlMCIsCiJhaWQiOiAiMjMzIiwKIm5ldCI6ICJrY3AiLAoidHlwZSI6ICJ1dHAiLAoiaG9zdCI6ICIiLAoicGF0aCI6ICIiLAoidGxzIjogIiIKfQo=").decode().strip()
    # print(t)
    t = "d3d3Lmdvb2dsZS5jb206MTphdXRoX2NoYWluX2E6Y2hhY2hhMjA6dGxzMS4yX3RpY2tldF9hdXRoOlluSmxZV3QzWVd4cy8_b2Jmc3BhcmFtPSZwcm90b3BhcmFtPSZyZW1hcmtzPTVZbXA1TDJaNXJXQjZZZVA3N3lhTVRBd0xqQXdKU0F4TURJMFRVSSZncm91cD1Uak5TVHc"
    # t = base64.b64decode("d3d3Lmdvb2dsZS5jb206MTphdXRoX2NoYWluX2E6Y2hhY2hhMjA6dGxzMS4yX3RpY2tldF9hdXRoOlluSmxZV3QzWVd4cy8_b2Jmc3BhcmFtPSZwcm90b3BhcmFtPSZyZW1hcmtzPTVZbXA1TDJaNXJXQjZZZVA3N3lhTVRBd0xqQXdKU0F4TURJMFRVSSZncm91cD1Uak5TVHc'], ['ssr', 'd3d3Lmdvb2dsZS5jb206MjphdXRoX2NoYWluX2E6Y2hhY2hhMjA6dGxzMS4yX3RpY2tldF9hdXRoOlluSmxZV3QzWVd4cy8_b2Jmc3BhcmFtPSZwcm90b3BhcmFtPSZyZW1hcmtzPTZMLUg1cHlmNXBlMjZaZTA3N3lhTWpBeU1DMHdPQzB5TVNBeE1qbzBNam94TVEmZ3JvdXA9VGpOU1R3")
    # t = base64.b64decode(t)
    print(t)
    # assert 0
    # b642conf("ss","YWVzLTI1Ni1jZmI6NTQxNjAzNDY2QDE0Mi45My41MC43ODo5ODk4#ss")
    # b642conf("ssr","d3d3Lmdvb2dsZS5jb206MTphdXRoX2NoYWluX2E6Y2hhY2hhMjA6dGxzMS4yX3RpY2tldF9hdXRoOlluSmxZV3QzWVd4cy8_b2Jmc3BhcmFtPSZwcm90b3BhcmFtPSZyZW1hcmtzPTVZbXA1TDJaNXJXQjZZZVA3N3lhTVRBd0xqQXdKU0F4TURJMFRVSSZncm91cD1Uak5TVHc")
    url = "https://nnn3ro.link/link/yutP0XvyPEIIa9n1?mu=4"


    x = Sub2Conf(url)
    # "https://nnn3ro.link/link/yutP0XvyPEIIa9n1?mu=1")
    x.update()
    print(vars(x))