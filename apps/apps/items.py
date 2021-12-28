# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ItemApp(scrapy.Item):
    title = scrapy.Field()
    company = scrapy.Field()
    category = scrapy.Field()
    pegi = scrapy.Field()
    contain_ads = scrapy.Field()
    contain_purchases = scrapy.Field()
    description = scrapy.Field()
    price = scrapy.Field()
    rating = scrapy.Field()
    votes = scrapy.Field()
    installs = scrapy.Field()
    size = scrapy.Field()
    date_updated = scrapy.Field()
    inn_app_products = scrapy.Field()
    
    
    def __str__(self):
        return ""
    
    