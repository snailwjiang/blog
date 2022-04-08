import datetime
import hashlib
import base64
import json

import requests  # 可以发送请求


class YunTongXin():
    base_url = 'https://app.cloopen.com:8883'

    def __init__(self, accountSid, accountToken, appId, templateId):
        self.accountSid = accountSid
        self.accountToken = accountToken
        self.appId = appId
        self.templateId = templateId

    # 1.构造请求的url
    def get_request_url(self, sig):
        self.url = self.base_url + '/2013-12-26/Accounts/%s/SMS/TemplateSMS?sig=%s' % (self.accountSid, sig)
        return self.url

    # 生成时间戳
    def get_timestamp(self):
        now = datetime.datetime.now()
        now_str = now.strftime('%Y%m%d%H%M%S')
        return now_str

    # 计算sig参数
    def get_sig(self, timestamp):
        s = self.accountSid + self.accountToken + timestamp
        md5 = hashlib.md5()
        md5.update(s.encode())
        sig = md5.hexdigest().upper()
        return sig

    # 2 构造请求包的包头
    def get_request_header(self, timestamp):
        s = self.accountSid + ':' + timestamp
        b_s = base64.b64encode(s.encode()).decode()
        return {
            'Accept': 'application/json',
            'Content-Type': 'application/json;charset=utf-8',
            'Authorization': b_s,
            'Connection':'close'
        }

    # 3 构造请求包的包体
    def get_request_body(self, phone, code):
        data = {
            'to': phone,
            'appId': self.appId,
            'templateId': self.templateId,
            'datas': [code, 3]
        }
        return data

    # 4 发送请求
    def do_request(self, url, header, body):
        res = requests.post(url=url,
                            headers=header,
                            data=json.dumps(body),verify=False)
        return res.text

    # 5 运行(将以上1~4串联起来)
    def run(self, phone, code):
        timestamp = self.get_timestamp()
        sig = self.get_sig(timestamp)
        url = self.get_request_url(sig)
        print(url)
        header = self.get_request_header(timestamp)
        print(header)
        body = self.get_request_body(phone, code)
        print(body)
        res = self.do_request(url, header, body)
        print(res)
        return res


if __name__ == '__main__':
    sid = '8aaf07087fe90a320180019f9c4a05b7'
    stoken = '60cacad6353c4e9d9237fe92967472e8'
    pid = '8aaf07087fe90a320180019f9da005be'
    tid = '1'
    x = YunTongXin(sid, stoken, pid, tid)
    res = x.run('18071054713', '122331')
    print(res)
