#!/usr/bin/env python
# -*- coding:utf-8 -*-
import requests
from bs4 import BeautifulSoup
import docx
import os

class RequestsHeaders(object):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
        "Accept-Encoding": "gzip, deflate, br",
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers = RequestsHeaders.headers


    def chakanquanwen(self):
        html = self.session.get('https://db.yaozh.com/instruct/53982.html',timeout=15)
        html.encoding='utf-8'
        # print(html.text)
        html_soup = BeautifulSoup(html.text,'lxml')
        print(html_soup.find_all(_class ='manual'))

    def pic(self):
        html = self.session.get('https://zy.yaozh.com/instruct/imagesout/TB1Xr9oNpXXXXX7XpXXXXXXXXXX_!!0-item_pic.jpg_430x430q90.jpg',timeout=15)
        with open('/users/zoe/a.jpg','wb') as f:
            f.write(html.content)

if __name__=='__main__':
    r = RequestsHeaders()
    r.pic()


