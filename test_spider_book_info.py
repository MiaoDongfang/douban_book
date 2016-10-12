# -*- coding:utf-8 -*-

#import sys
#reload(sys)
#sys.setdefaultencoding('utf-8')

import requests
from lxml import html


url='https://book.douban.com/subject/1084336/'

headers={'User-Agent':'Mozilla / 5.0(Windows NT 10.0;WOW64) AppleWebKit /537.36(KHTML, likeGecko) Chrome / 51.0.2704.103Safari / 537.36'}

r=requests.get(url,headers=headers)

tree=html.fromstring(r.text)

datas=tree.xpath("//div[@id='info']//text()")

datas = [data.strip() for data in datas]
datas = [data for data in datas if data != ""]
