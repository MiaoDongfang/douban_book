# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class DoubanBookItem(scrapy.Item):
    book_name=scrapy.Field()
    book_author=scrapy.Field()
    book_press=scrapy.Field()
    book_year=scrapy.Field()
    book_pagenum=scrapy.Field()
    book_price=scrapy.Field()
    book_ISBN=scrapy.Field()
    book_score=scrapy.Field()

class DoubanBookComment(scrapy.Item):
    comment_book=scrapy.Field()
    comment_user=scrapy.Field()
    comment_date=scrapy.Field()
    comment_usefulnum=scrapy.Field()
    comment_content=scrapy.Field()