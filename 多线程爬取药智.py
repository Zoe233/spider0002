#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import os
import urllib
import requests
import json
import time
from bs4 import BeautifulSoup
import re
import threading
from datetime import datetime as dt
from multiprocessing.dummy import Pool
from multiprocessing import Queue
from queue import Queue
from bs4 import BeautifulSoup

class DataCrawler(object):
    '''
    爬取网站https://db.yaozh.com/instruct，主站访问为这个，
    '''

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
        "Accept-Encoding": "gzip, deflate, br",
    }

    base_dir =os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def __init__(self):

        # 所有表单数据，药智数据字典集
        self.yaozh_dic = {}

        # 所有的表单数据写到写到json文件内
        self.formFile = os.path.join(DataCrawler.base_dir,'step_by_step_res.txt')
        self.logFile = os.path.join(DataCrawler.base_dir,'log.txt')

        # 所有文档的说明书和图片怎么存？
        # Code为主目录，内部两个子文件夹 Instruction，Pictures，分别存入说明书和图片


        self.pool = Pool(7)

        self.session = requests.Session()
        self.session.headers = DataCrawler.headers

        self.queue = Queue()
        self.messageQueue = Queue()

        self.index = 0
        self.promptNum = 10


        self.lock = threading.Lock()
        self.delay = 120
        self.QUIT='QUIT'
        self.printPrefix = '**'





    def start(self):
        '''类主调用函数'''

        # 守护线程，日志log输出
        t = threading.Thread(target = self.__log)
        t.setDaemon(True)
        t.start()

        # 从功能上来讲，辅助进程，控制台输出
        self.messageQueue.put(self.printPrefix +'脚本开始执行')
        start_time =dt.now()

        # 第一步：构建urls，返回的是列表
        yaozh_urls = self.__buildRequestsUrls()  # 此处返回的是7个urls，只要请求这7个urls就可以了。
        self.messageQueue.put(self.printPrefix+'已获取 %s 个Json请求网址'% len(yaozh_urls))

        # 开发期间保留用以检测获取的urls是否正确，防止输出错漏。
        self.messageQueue.put(self.printPrefix+'获取的网址列表为：'+str(yaozh_urls))

        # 第二步：将请求的urls都扔给线程池中国的self.__resolveHtml,会在线程池中一一开始
        # 由于药智
        # try:
        #     self.pool.map(self.__resolveHtml,yazh_urls)
        # except Exception as e:
        #     print('!!!!!! Error!!!!!',e)
        for url in yaozh_urls:
            try:
                self.__resolveHtml(url)
                self.__writeFormData()
            except:
                self.messageQueue.put(self.printPrefix+'未能成功连接到urls：'+str(url))
            finally:
                time.sleep(self.delay)

        # 第三步：将请求的结果self.yaozh_dic的所有结果都写入到self.formFile
        # while not self.queue.empty():
        #     self.pool.map_async(self.__writeFormData)

        self.pool.close()
        self.pool.join()

        self.messageQueue.put(self.printPrefix + "下载完成！已下载 %s 行记录，总用时 %s" %
                              (self.index + 1, dt.now() - start_time))
        self.messageQueue.put(self.printPrefix + "请到 %s 查看结果！" % os.path.split(self.formFile)[1])
        self.messageQueue.put(self.printPrefix + "日志信息保存在 %s" % self.logFile)
        self.messageQueue.put(self.QUIT)


    # 第一步：构建请求urls，此处共7个
    def __buildRequestsUrls(self):
        '''
        每个page的网页构成为：https://db.yaozh.com/instruct?p=2&pageSize=30
        目前有个问题，这些urls上显示的page总共就只有210条药品记录
        :return: 返回表单页面，总共7页，每页30个。
        '''
        base_url = 'https://db.yaozh.com/instruct?p={}&pageSize={}'
        urls = [base_url.format(x,30) for x in range(1,8)]
        return urls

    # 第二步：根据队列map对应的url，用get方法获取html信息，并将结果存入到self.yaozh_dic
    def __resolveHtml(self,url):
        yaozh_html =self.session.get(url,cookies={})
        yaozh_html.encoding='utf-8'

        yaozh_soup = BeautifulSoup(yaozh_html.text,'lxml')
        table_list =[]
        table_list = yaozh_soup.find_all('tr')[1:]

        for tr in table_list:
            sub_dic={}
            self.yaozh_dic[self.index] =sub_dic
            sub_dic['Code'] = tr.th.string

            content_list = tr.find_all('td')
            sub_dic['MedName'] = content_list[0].string
            sub_dic['IntruSource'] = content_list[1].string

            # 文件url
            sub_dic['FileMark'] = content_list[2].string if content_list[2].string else '下载'
            if sub_dic['FileMark'] == '查看全文':
                file_url = 'https://db.yaozh.com'+content_list[2].a.get('href')
            elif sub_dic['FileMark'] == '下载':
                file_url = content_list[2].a.get('href')
            sub_dic['FileUrl'] = file_url

            # 图片url
            sub_dic['PicUrls'] = tr.find_all('div')[0].string.split(',')
            self.index +=1
        # time.sleep(self.delay)
        return self.yaozh_dic

    # 第三步：将请求的结果self.yaozh_dic的所有结果都写入到self.formFile
    def __writeFormData(self):
        with open(self.formFile,'a') as f:
            for k,v in self.yaozh_dic.items():
                f.write(str(v)+'; ')

    # 辅助函数，作为守护线程运行
    def __log(self):
        with open(self.logFile,'w',encoding='utf-8') as f:
            while True:
                '''死循环一直判断消息队列中有没有传入QUIT指令，但是下面并没有响应'''
                message = self.messageQueue.get()
                if message == self.QUIT:
                    break
                message = str(dt.now()) + " " + message  # '2018-01-24 17:41:50.676418'+" " +message
                if self.printPrefix in message:
                    print(message)
                f.write(message + '\n')
                f.flush()

    # 辅助函数，load一个条记录的文件和图片都根据code和type创建文件夹，未写，等测通才行
    def __mkDir(self):
        for v in self.yaozh_dic.values():
            pass



if __name__=='__main__':
    print('爬取药智数据脚本启动')
    print('*'*50)
    down = DataCrawler()
    # down.start()
    first =down._DataCrawler__buildRequestsUrls()
    print(first)
    second = down._DataCrawler__resolveHtml(first[6])
    print(second)
    # third = down._DataCrawler__writeFormData()
    # print(third)
