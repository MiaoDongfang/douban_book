# -*- coding:utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import logging

from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor
import scrapy

from douban_book.items import DoubanBookItem,DoubanBookComment

logger = logging.getLogger("doubanbook spider")

class BookSpider(CrawlSpider):
    name = "doubanbook"
    #download_delay = 1

    start_urls=['https://book.douban.com/top250']

    rules = (
        #当只有一个Rule时，Rule最后也要加上“,”，否则会报错
        Rule(LinkExtractor(allow=r"https://book.douban.com/top250\?start=\d+"),),
        Rule(LinkExtractor(allow=r'https://book.douban.com/subject/\d+/$'), callback='parse_item'),
        #Rule(LinkExtractor(allow=r"https://book.douban.com/subject/\d+/comments/$"),callback='parse_comment'),
        #Rule(LinkExtractor(allow=r"https://book.douban.com/subject/\d+/comments/hot\?p=\d+"),callback='parse_comment')

        #r"https://book.douban.com/top250\?start=\d+"

    )



    #def parse_url(self,response):
    #    sel=response.xpath('//div[@class="indent"]/table/tr/td[2]/div[1]/a/@href').extract()
    #    #//*[@id="content"]/div/div[1]/div/table/tbody/tr/td[2]/div[1]/a
        #print sel
    #    for url in sel:
    #        print url
    #        yield scrapy.Request(url,callback=self.parse_item)

    def parse_item(self,response):

        logger.info("got page: %s" % response.body)

        item=DoubanBookItem()

        item['book_name']=response.xpath('//div[@id="wrapper"]/h1/span/text()').extract()
        item['book_score']=response.xpath('//*[@id="interest_sectl"]/div/div[2]/strong/text()').extract()

        #item['book_author']=response.xpath('//div[@id="info"]/span[1]/span/text()').extract()
        #item['book_press']=response.xpath('//*[@id="info"]/text()[1]')

        datas = response.xpath("//div[@id='info']//text()").extract()
        datas = [data.strip() for data in datas]
        datas = [data for data in datas if data != ""]

        # 打印每一项内容
        # for i, data in enumerate(datas):
        # print "index %d " %i, data

        for data in datas:
            if u"作者" in data:
                if u":" in data:
                    item["book_author"] = datas[datas.index(data) + 1]
                elif u":" not in data:
                    item["book_author"] = datas[datas.index(data) + 2]
            # 找出版社中有个坑, 因为很多出版社名包含"出版社"
            # 如: 上海译文出版社，不能用下面注释的代码进行查找
            # elif u"出版社" in data:
            #    if u":" in data:
            #        item["press"] = datas[datas.index(data)+1]
            #    elif u":" not in data:
            #        item["press"] = datas[datas.index(data)+2]
            elif u"出版社:" in data:
                item["book_press"] = datas[datas.index(data) + 1]
            elif u"出版年:" in data:
                item["book_year"] = datas[datas.index(data) + 1]
            elif u"页数:" in data:
                item["book_pagenum"] = datas[datas.index(data) + 1]
            elif u"定价:" in data:
                item["book_price"] = datas[datas.index(data) + 1]
            elif u"ISBN:" in data:
                item["book_ISBN"] = datas[datas.index(data) + 1]

        # comment_url=response.xpath('//div[@class="mod-hd"]/h2/span[2]/a/@href').extract()
        # if len(comment_url)>0:
            #回调parse_comment函数，以抓取评论信息
            # yield scrapy.Request(comment_url[0],callback=self.parse_comment)

        yield item

    # def parse_comment(self,response):
        # comment_item=DoubanBookComment()



        # book_name=response.xpath('//*[@id="content"]/h1/text()').extract()[0].split(' ')[0]

        # select=response.xpath('//div[@class="comment-list hot "]/ul/li')

        # for sel in select:
            # comment_item['comment_user']=sel.xpath('h3/span[2]/a/text()').extract()
            # comment_item['comment_date']=sel.xpath('h3/span[2]/span[2]/text()').extract()
            # comment_item['comment_usefulnum']=sel.xpath('h3/span[1]/span/text()').extract()
            # comment_item['comment_content']=sel.xpath('p/text()').extract()
            # comment_item['comment_book']=book_name

            # yield comment_item

        # 以下是实现翻页抓取的功能
        # href=response.xpath('//ul[@class="comment-paginator"]/li[3]/a/@href').extract()
        # if len(href)>0:
            # l=response.url.split('/')
            # url=l[0]+'//'+l[2]+'/'+l[3]+'/'+l[4]+'/'+l[5]+'/'+href[0]
            # https://book.douban.com/subject/3266968/comments/
            # https://book.douban.com/subject/3266968/comments/hot?p=2
            # 形成request，并递归的回调自身，实现翻页抓取的功能
            # yield scrapy.Request(url,callback=self.parse_comment)





