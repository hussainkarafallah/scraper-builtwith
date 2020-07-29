# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import  Field,Item


class metaItem(Item):
    site = Field()
    spent = Field()

class techItem(Item):
    site = Field()
    domain = Field()
    tech = Field()

class techinfoItem(Item):
    tech = Field()
    site = Field()
    desc = Field()



