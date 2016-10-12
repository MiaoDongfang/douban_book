#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import urllib2
import requests
import logging
import multiprocessing
import Queue
import time
import threading

logger = logging.getLogger(__name__)

def get_html(url,timeout=3,headers={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.99 Safari/537.36"}):

    r=requests.get(url,headers=headers,timeout=timeout)
    page=r.text
    # request = urllib2.Request(url)
    # request.add_header("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.99 Safari/537.36")
    # html = urllib2.urlopen(request)
    return page

def get_soup(url,headers={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.99 Safari/537.36"}):
    soup = BeautifulSoup(get_html(url,headers=headers), "lxml")
    return soup

class FetchKuaidaili(threading.Thread):
    '''
    从http://www.kuaidaili.com/抓取代理
    :param page:
    :return:
    '''

    def __init__(self,queen):
        threading.Thread.__init__(self)
        self.queen=queen  #使用queen作为线程之间通信的变量，用来存储代理。

    def get_proxyes(self):
        try:
            for page in range(1,10):
                try:
                    url='http://www.kuaidaili.com/proxylist/%d/'%page
                    soup=get_soup(url)
                    table_tag=soup.find("table",attrs={'class':"table table-bordered table-striped  table-index"})
                    trs=table_tag.tbody.find_all('tr')
                    for tr in trs:
                        tds=tr.find_all('td')
                        ip=tds[0].text
                        port=tds[1].text
                        type=tds[3].text
                        anonymity=tds[2].text
                        if  anonymity==u'高匿名':
                            proxy = "%s:%s" % (ip, port)
                            self.queen.put(proxy)
                except:
                    continue
        except:
            logger.warning("fail to fetch from kuaidaili")

    def run(self):
        self.get_proxyes()

class FetchKxdaili(threading.Thread):
    """
    从www.kxdaili.com抓取免费代理
    """

    def __init__(self,queen):
        threading.Thread.__init__(self)
        self.queen=queen

    def get_proxyes(self):
        try:
            for page in range(1,10):
                try:
                    url = "http://www.kxdaili.com/dailiip/1/%d.html" % page
                    soup = get_soup(url)
                    table_tag = soup.find("table", attrs={"class": "segment"})
                    trs = table_tag.tbody.find_all("tr")
                    for tr in trs:
                        tds = tr.find_all("td")
                        ip = tds[0].text
                        port = tds[1].text
                        type=tds[3].text
                        latency = tds[4].text.split(" ")[0]
                        if float(latency) < 0.5: # 输出延迟小于0.5秒的代理
                            proxy = "%s:%s" % (ip, port)
                            self.queen.put(proxy)
                except:
                    continue
        except:
            logger.warning("fail to fetch from kxdaili")

    def run(self):
        self.get_proxyes()


def img2port(img_url):
    """
    mimvp.com的端口号用图片来显示, 本函数将图片url转为端口, 目前的临时性方法并不准确
    """
    code = img_url.split("=")[-1]
    if code.find("AO0OO0O")>0:
        return 80
    else:
        return None


class FetchMimvp(threading.Thread):
    """
    从http://proxy.mimvp.com/free.php抓免费代理
    智能查看第一页，且均为http
    """

    def __init__(self,queen):
        threading.Thread.__init__(self)
        self.queen=queen

    def get_proxyes(self):

        try:
            url = "http://proxy.mimvp.com/free.php?proxy=in_hp"
            soup = get_soup(url)
            table = soup.find("div", attrs={"id": "list"}).table
            tds = table.tbody.find_all("td")

            for i in range(0, len(tds), 10):
                id = tds[i].text
                ip = tds[i+1].text
                port = img2port(tds[i+2].img["src"])
                response_time = tds[i+7]["title"][:-1]
                transport_time = tds[i+8]["title"][:-1]
                if port is not None and float(response_time) < 1 :
                    proxy = "%s:%s" % (ip, port)
                    self.queen.put(proxy)
        except:
            logger.warning("fail to fetch from mimvp")

    def run(self):
        self.get_proxyes()


class FetchXici(threading.Thread):
    """
    http://www.xicidaili.com/nn/
    均为http
    """

    def __init__(self,queen):
        threading.Thread.__init__(self)
        self.queen=queen
    def get_proxyes(self):
        try:
            url = "http://www.xicidaili.com/nn/"
            soup = get_soup(url)
            table = soup.find("table", attrs={"id": "ip_list"})
            trs = table.find_all("tr")
            for i in range(1, len(trs)):
                tr = trs[i]
                tds = tr.find_all("td")
                ip = tds[1].text
                port = tds[2].text
                speed = tds[6].div["title"][:-1]
                latency = tds[7].div["title"][:-1]
                if float(speed) < 3 and float(latency) < 1:
                    self.queen.put("%s:%s" % (ip, port))
        except:
            logger.warning("fail to fetch from xici")

    def run(self):
        self.get_proxyes()


class FetchIp181(threading.Thread):
    """
    http://www.ip181.com/
    """
    def __init__(self,queen):
        threading.Thread.__init__(self)
        self.queen=queen

    def get_proxyes(self):
        try:
            url = "http://www.ip181.com/"
            soup = get_soup(url)
            table = soup.find("table")
            trs = table.find_all("tr")
            for i in range(1, len(trs)):
                tds = trs[i].find_all("td")
                ip = tds[0].text
                port = tds[1].text
                latency = tds[4].text[:-2]
                type=tds[3].text
                if float(latency) < 1 and type==u'HTTP,HTTPS':
                    self.queen.put("%s:%s" % (ip, port))
        except Exception as e:
            logger.warning("fail to fetch from ip181: %s" % e)
    def run(self):
        self.get_proxyes()


class FetchHttpdaili(threading.Thread):
    """
    http://www.httpdaili.com/mfdl/
    没有显示类型
    更新比较频繁
    """
    def __init__(self,queen):
        threading.Thread.__init__(self)
        self.queen=queen

    def get_proxyes(self):
        try:
            url = "http://www.httpdaili.com/mfdl/"
            soup = get_soup(url)
            table = soup.find("div", attrs={"kb-item-wrap11"}).table
            trs = table.find_all("tr")
            for i in range(1, len(trs)):
                try:
                    tds = trs[i].find_all("td")
                    ip = tds[0].text
                    port = tds[1].text
                    type = tds[2].text
                    if type == u"匿名":
                        self.queen.put("%s:%s" % (ip, port))
                except:
                    pass
        except Exception as e:
            logger.warning("fail to fetch from httpdaili: %s" % e)
    def run(self):
        self.get_proxyes()

class Fetch66ip(threading.Thread):
    """
    http://www.66ip.cn/
    不显示类型
    每次打开此链接都能得到一批代理, 速度不保证
    """
    def __init__(self,queen):
        threading.Thread.__init__(self)
        self.queen=queen

    def get_proxyes(self):
        try:
            # 修改getnum大小可以一次获取不同数量的代理
            url = "http://www.66ip.cn/nmtq.php?getnum=10&isp=0&anonymoustype=3&start=&ports=&export=&ipaddress=&area=1&proxytype=0&api=66ip"
            content = get_html(url)
            urls = content.split("</script>")[-1].split("<br />")
            for u in urls:
                if u.strip():
                    self.queen.put(u.strip())
        except Exception as e:
            logger.warning("fail to fetch from httpdaili: %s" % e)
    def run(self):
        self.get_proxyes()



class ProxyCheck(threading.Thread):
    # 所有线程最终结果汇总到checked列表中，将全局变量checked列表定义为初始化传入参数,同时定义queue
    def __init__(self, checked, queue):
        threading.Thread.__init__(self)
        self.data = queue
        self.testurl = "http://www.baidu.com"
        self.testcode = "030173"
        self.timeout = 5
        self.checked = checked
        self.temp_checked=[]

    def check_it(self):
        cookies = urllib2.HTTPCookieProcessor()
        # 从队列中读取一个数据
        ip = self.data.get()
        proxy_handler = urllib2.ProxyHandler({"http": r"http://%s" % ip})

        opener = urllib2.build_opener(proxy_handler, urllib2.HTTPHandler)

        opener.addHeader = [("User-Agent",
                             "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.18 Safari/537.36")]
        urllib2.install_opener(opener)

        start = time.time()
        # print " now is  : %s:%s " % (ip[0],ip[1])
        try:
            response = urllib2.urlopen(self.testurl, timeout=self.timeout)
            page=response.read()
            result = page.find(self.testcode)
            if result > -1:
                end = time.time()
                speed = end - start
                self.temp_checked.append([ip,speed])
                print "thread %s tested proxy: %s ,speed: %s " % (self.getName(), ip, speed)
                # else:
                # continue
        except:
            print "test fail: %s " % (ip)
            logger.info("test fail: %s " % (ip))
            #        continue

    def sort_list(self):
        self.temp_checked = sorted(self.temp_checked, cmp=lambda x, y: cmp(x[1], y[1]))
        for i in range(len(self.temp_checked)):
            self.checked.append(self.temp_checked[i][0])

    def run(self):
        self.check_it()
        self.sort_list()



def check(proxyes):
    import urllib2
    url = "http://www.baidu.com"
    test_str='030173'
    valid_proxyes=[]
    for proxy in proxyes:
        proxy_handler = urllib2.ProxyHandler({'http': "http://" + proxy})
        opener = urllib2.build_opener(proxy_handler,urllib2.HTTPHandler)

        opener.addHeader = [("User-Agent",
                             "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.18 Safari/537.36")]
        urllib2.install_opener(opener)

        start = time.time()

        try:
            response = opener.open(url,timeout=3)
            page=response.read()
            result = page.find(test_str)
            if result>-1:
                valid_proxyes.append(proxy)
            else:
                #print "test fail:%s"%proxy
                logger.info("test fail:%s"%proxy)
        except Exception:
            # print "test fail:%s,403" % proxy
            logger.info("test fail:%s,403" % proxy)
    return valid_proxyes



def fetch_all(endpage=10):
    # proxyes = []
    # proxyes+=fetch_kuaidaili()
    # proxyes += fetch_kxdaili()
    # proxyes += fetch_mimvp()
    # proxyes += fetch_xici()
    # proxyes += fetch_ip181()
    # proxyes += fetch_httpdaili()
    # proxyes += fetch_66ip()


    valid_proxyes = []

    q=Queue.Queue()

    fetch_threads=[]

    t_kuaidaili=FetchKuaidaili(q)
    t_kuaidaili.start()
    fetch_threads.append(t_kuaidaili)

    t_kxdaili=FetchKxdaili(q)
    t_kxdaili.start()
    fetch_threads.append(t_kxdaili)

    t_mimvp=FetchMimvp(q)
    t_mimvp.start()
    fetch_threads.append(t_mimvp)

    t_xici=FetchXici(q)
    t_xici.start()
    fetch_threads.append(t_xici)

    t_ip181=FetchIp181(q)
    t_ip181.start()
    fetch_threads.append(t_ip181)

    t_httpdaili=FetchHttpdaili(q)
    t_httpdaili.start()
    fetch_threads.append(t_httpdaili)

    t_66ip=Fetch66ip(q)
    t_66ip.start()
    fetch_threads.append(t_66ip)

    for th in fetch_threads:
        th.join()



    # for i in range(len(proxyes)):
    #     q.put(proxyes[i])

    logger.info("total %d proxies,now,checking proxyes validation"%q.qsize())

    #valid_proxyes=check(proxyes)

    #以下为多线程验证代理的有效性
    threads=[]
    #经测试，使用多线程能明显的提高程序的运行速度
    #接下来进行改进，根据queen长度来决定进程的数量
    for i in xrange(q.qsize()):
        t = ProxyCheck(valid_proxyes, q)
        t.start()
        threads.append(t)
    #等待所有进程完成再接着运行程序
    for t in threads:
        t.join()


    # for p in proxyes:
    #     if check(p):
    #         valid_proxyes.append(p)
    return valid_proxyes

if __name__ == '__main__':
    program_start=time.time()
    import sys
    root_logger = logging.getLogger("")
    stream_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(name)-8s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    proxyes = fetch_all()
    #print check("202.29.238.242:3128")
    print "Total %d useful proxies"%len(proxyes)
    for p in proxyes:
        print p
    program_stop=time.time()

    print "this program used for %d"%(program_stop-program_start)
