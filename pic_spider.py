#!/usr/bin/env python
# -*- coding:utf-8 -*-

from getdata import getData
import os
import requests

class PicSpider(object):
    headers ={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
        "Accept-Encoding": "gzip, deflate, br",
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers = PicSpider.headers

        self.picdic = {}
        self.index = 0
        self.base_path = '/Users/zoe/文件管理/药智数据_爬虫/爬虫结果/文件汇总结果'
        self.unloadurl = []

    def __getPicUrls(self):
        g = getData()
        g.transform()
        for k in g.data:
            subdic ={}
            self.picdic[self.index] = subdic
            subdic['Code'] = k['Code']
            subdic['PicUrl'] = k['PicUrls']
            self.index +=1
        return self.picdic

    def __checkDir(self):
        self.__getPicUrls()
        for v in self.picdic.values():
            if os.path.exists(os.path.join(self.base_path,str(v['Code']))):
                    continue
            else:
                print('这里还有目录未创建',v['Code'])

    def __loadPic(self):
        count = 0
        for v in self.picdic.values():
            # print(v)  # {'Code': '53973', 'PicUrl': ['...','....']
            for u in v['PicUrl']:
                try:
                    html = self.session.get(u,timeout=60)
                    with open(os.path.join(self.base_path+'/'+v['Code'],u[-14:-4]+'.jpg'),'wb') as f:
                        f.write(html.content)
                    count+=1
                    print('%s成功添加1个图片'%v['Code'])
                except Exception as e:
                    print('这个url失败',u)
                    self.unloadurl.append(u)
        print('成功下载了%s个图片', count)


    def run(self):
        self.__checkDir()
        self.__loadPic()


if __name__=='__main__':
    p = PicSpider()
    p.run()