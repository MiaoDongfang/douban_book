# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from douban_book.items import DoubanBookItem,DoubanBookComment
from douban_book.settings import MONGODB_SERVER,MONGODB_PORT,MONGODB_DB,MONGODB_BOOK_COL,MOGODB_COMMENT_COL
import pymongo
from scrapy.exceptions import DropItem
from scrapy import log
import json
import codecs
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

class MongoDBPipeline(object):
    def __init__(self):
        self.client=pymongo.MongoClient(MONGODB_SERVER,MONGODB_PORT)

        self.db=self.client[MONGODB_DB]
        self.book_col=self.db[MONGODB_BOOK_COL]
        self.comment_col=self.db[MOGODB_COMMENT_COL]
        self.book_num=0
        self.comment_num=0


    def process_item(self, item, spider):

        #传入的item是DoubanBookItem时
        if isinstance(item,DoubanBookItem):
            if not item['book_name']:
                raise DropItem("Missing book's name!")
            else:
                self.book_col.insert(dict(item))
                log.msg(u"%s 已被添加到mongoDB数据库"%item['book_name'],level=log.DEBUG,spider=spider)
                self.book_num=self.book_num+1

        # 传入的item是DoubanBookComment时
        # if isinstance(item,DoubanBookComment):
            # if not item['comment_user']:
                # raise  DropItem("Missing comment user name")
            # else:
                # self.comment_col.insert(dict(item))
				# self.comment_num
                # log.msg(u"%s关于%s的的评论已添加到mongoDB数据库中"%(item["comment_user"],item["comment_book"]),level=log.DEBUG,spider=spider)



    def close_spider(self,spider):
        log.msg(u"共抓取了%d本书和%d条评论"%(self.book_num,self.comment_num),level=log.DEBUG,spider=spider)
        self.client.close()
        



