import urllib
import re
import urllib
import http.cookiejar
import logging
import urllib.request
import time
import os
import json
start_num=0
end_num=50
#爬虫小工具
class spider(object):
    def __init__(self):
        logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s')
        logging.root.setLevel(level=logging.INFO)
        self.cj=http.cookiejar.CookieJar()
        redirect=urllib.request.HTTPRedirectHandler()
        self.opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cj))

    def get(self,url,header):
        req=urllib.request.Request(url,headers=header,method="GET")
        res=self.opener.open(req)
        return res.read().decode('utf8')
    def get_gbk(self,url,header):
        req=urllib.request.Request(url,headers=header,method="GET")
        res=self.opener.open(req)
        return res.read().decode('GBK')
    def get_json(self,url,header={}):
        return json.loads(self.get(url,header))

    def post(self,url,header,data):
        postdata=urllib.parse.urlencode(data).encode('utf8')
        req=urllib.request.Request(url,postdata,header,method="POST")
        res=self.opener.open(req)
        return res.read().decode('utf8')

    def post_json(self,url,header,data):
        return json.loads(self.post(url,header,data))

    #从文件中载入字典 key:value形式
    # 一般来说，要使用某个类的方法，需要先实例化一个对象再调用方法。而使用@staticmethod或@classmethod，就可以不需要实例化，直接类名.方法名()来调用。
    @staticmethod
    def load_header(filename):
        header={}
        with open(filename,encoding='utf8') as f:
            for item in f.readlines():
                index=item.rstrip('\n').index(':')
                if index>0:
                    header[item[:index]]=item[index+1:].strip()
        return header

s=spider()
header=spider.load_header('header')
def get_list(page):
    url='http://api.db.auto.sohu.com/restful/news/list/news/%d/20.json?callback=news&_=1478457564137'%page
    films=s.get(url,header)
    result=json.loads(re.findall('^news\(([\s\S]+)\)',films)[0])
    return result

for i in range(100,200):
    num=0
    res=get_list(i)
    if(res):
        urls=[item['url'] for item in res['result']]
        for j in urls:
            html=urllib.request.urlopen(j).read()
            with open('../data/'+j[:-6].replace('/','|'),'wb')as f:
                print(j)
                f.write(html)
        time.sleep(0.1)
    else:
        continue

