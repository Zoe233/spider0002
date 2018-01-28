#!/usr/bin/env python
# -*- coding:utf-8 -*-

from getdata import getData
import os
import requests

class FileSpider(object):

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
        "Accept-Encoding": "gzip, deflate, br",
    }

    def __init__(self):
        self.filedic ={}
        self.index =0
        self.base_path ='/Users/zoe/文件管理/药智数据_爬虫/爬虫结果/文件汇总结果'

        self.session = requests.Session()
        self.session.headers = FileSpider.headers
        self.unloadfiles =[]


    def __getFileUrls(self):
        g = getData()
        g.transform()
        for k in g.data:
            subdic={}
            self.filedic[self.index] = subdic
            subdic['Code'] = k['Code']
            subdic['FileMark'] = k['FileMark']
            subdic['FileUrl'] = k['FileUrl']
            self.index+=1
        return self.filedic

    def __mkCodeDir(self):
        self.__getFileUrls()
        for v in self.filedic.values():
            codepath = os.path.join(self.base_path,str(v['Code']))

            if os.path.exists(codepath):
                continue
            else:
                os.mkdir(codepath)

    def __getHtml(self):
        '''根据mark的字段value来判断'''
        count=0
        for k,v in self.filedic.items():
            if os.path.exists(os.path.join(self.base_path+'/'+str(v['Code']),'instruction.doc')):
                continue
            else:
                try:
                    html = self.session.get(v['FileUrl'], timeout=15)
                    if v['FileMark'] =='下载':
                        print('又下载了1个')
                        with open(os.path.join(self.base_path+'/'+str(v['Code']),'instruction.doc'),'wb') as f:
                            f.write(html.content)
                        count+=1
                    elif v['FileMark'] =='查看全文':
                        self.__getOnlineWord(v)
                except Exception as e:
                    print('%s遇到了ConnectionError'%v['FileUrl'])
        print('成功下载%s个doc文件',count)


    def __getOnlineWord(self,v):
        '''获取'''
        self.unloadfiles.append(v)


    def run(self):
        self.__mkCodeDir()
        self.__getHtml()



if __name__ =='__main__':
    f = FileSpider()
    f.run()
    # print(f.filedic)
    # print(len(f.filedic))
    # for k,v in f.filedic.values():
    #     print(v)
    print(f.unloadfiles)
    for v in f.unloadfiles:
        print(v)


