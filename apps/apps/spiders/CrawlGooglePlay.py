from itemloaders.processors import TakeFirst
import scrapy
import pandas as pd
import re
from scrapy.loader import ItemLoader

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from apps.items import ItemApp

class CrawlGooglePlay(CrawlSpider):
    name = "crawl_google_play"
    
    urls = [
        "https://play.google.com/store/apps",
        "https://play.google.com/store/apps/category/GAME",
        "https://play.google.com/store/apps/category/FAMILY",
        "https://play.google.com/store/apps/editors_choice",
        "https://play.google.com/store/apps/category/BOOKS_AND_REFERENCE",
        "https://play.google.com/store/apps/stream/baselist_featured_arcore",
        "https://play.google.com/store/apps/collection/cluster?clp=ogoKCA0qAggBUgIIAQ%3D%3D:S:ANO1ljJJQho&gsr=Cg2iCgoIDSoCCAFSAggB:S:ANO1ljJDbNY",
        "https://play.google.com/store/apps/top",
        "https://play.google.com/store/apps/new",
        "https://play.google.com/store/apps/stream/vr_top_device_featured_category"
        ]
    
    allowed_domains = [
        'play.google.com'
    ]
    
    
    rules = (
        Rule(
            LinkExtractor(
                allow_domains=allowed_domains,
                allow = (
                    r"^https?\:\/\/play.google.com\/store\/apps\/details.*$"
                )
            ),
            callback = 'parse_app'
        ),
        Rule(
            LinkExtractor(
                allow_domains=allowed_domains,
                allow = (
                    r'^https?\:\/\/play.google.com\/store\/apps\/?.*$'
                )
            )
        )
    )
        
    def __init__(self, *a, **kw):
        super(CrawlGooglePlay, self).__init__(*a, **kw)
        
    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url) # , callback=self.hand_url)
    
    def parse_app(self, response):
        
        
        item_loader = ItemLoader(item=ItemApp(), selector=response)
        item_loader.default_output_processor = TakeFirst()  # no save array
        
        monetization = response.xpath('//div[@class="bSIuKf"]').get()
        monetization = "none" if not monetization else monetization.strip().lower()
        description = response.xpath('//div[@jsname="sngebd"]').get().strip().replace("<br>", ". ").replace("\\", "").replace("*", "").replace("•", "").replace('<div jsname="sngebd">', "").replace('</div>', '')
        button_install = response.xpath('//span[@class="oocvOe"]/button/text()').get()
        button_install = "install" if not button_install else button_install.strip().lower()
        price = 0 if "install" in button_install else float(re.match(r'\$([\d\.]+) buy', button_install).groups()[0])
        rating = response.xpath('//div[@class="BHMmbe"]/text()').get()
        rating = 0 if not rating else float(rating.strip())
        votes = response.xpath('//span[@class="EymY4b"]/span[2]/text()').get()
        votes = 0 if not votes else int(votes.replace(",","").strip())

        in_app = response.xpath('//div[text() = "In-app Products"]/parent::div/span/div/span/text()').get()
        in_app = "none" if not in_app else in_app.strip()

        installs = response.xpath('//div[text() = "Installs"]/parent::div/span/div/span/text()').get()
        installs = 0 if not installs else int(installs.replace(",","").replace("+","")),
        
        item_dict = {
            "title": response.xpath('//h1[@class="AHFaub"]/span/text()').get(),
            "company": response.xpath('//div[@class="qQKdcc"]/span/a/text()').get(),
            "category": response.xpath('//a[@itemprop="genre"]/text()').get(),
            "pegi": response.xpath('//div[@class="KmO8jd"]/text()').get().strip(),
            "contain_ads": 1 if "ads" in monetization else 0,
            "contain_purchases": 1 if "purchases" in monetization else 0,
            "description": description,
            "price": price,
            "rating": rating,
            "votes": votes,
            "installs": installs,
            "size": response.xpath('//div[text() = "Size"]/parent::div/span/div/span/text()').get(),
            "date_updated": response.xpath('//div[text() = "Updated"]/parent::div/span/div/span/text()').get(),
            "inn_app_products": in_app,
        }
        
        for key, value in item_dict.items():
            item_loader.add_value(key, value)
        
        yield item_loader.load_item()
        
        

    