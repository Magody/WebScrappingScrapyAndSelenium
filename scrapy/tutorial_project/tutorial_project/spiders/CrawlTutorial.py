import scrapy
import pandas as pd
import re

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class CrawlSpiderONU(CrawlSpider):
    name = "crawl_un"
    
    base_url = "https://www.un.org"
    
    urls = ["https://www.un.org"]
    
    
         
    
    allowed_domains = [
        'un.org'
    ]
    
    
    rules = (
        Rule(
            LinkExtractor(
                allow_domains=allowed_domains,
                allow = (
                    r"^https:\/\/www\.un\.org\/[A-z_\-\s]+\/about-us\/un-system$"
                ),
                deny = (
                    'zh/about-us', # can be regex too
                )
            ),
            callback = 'parse'
        ),
        Rule(
            LinkExtractor(
                allow_domains=allowed_domains,
                allow = (
                    r'^https:\/\/www\.un\.org\/[A-z_\-]{2}\/[A-z_\-]{2,8}\/[A-z_\-]{2,9}$'
                ),
                deny=(
                    'press', 'content', 'development', 'publications',
                    'collection',
                    'reham-al-farra-memorial-journalism-fellowship',
                    'news', 'coronavirus', 'node', 'sg', 'speeches',
                    'event', 'events', 'observances',
                    'meetings', 'media', 'file',
                    'rss-feeds', 'documents'
                    
                )
            )
        ),
        
        Rule(
            LinkExtractor(
                allow_domains=allowed_domains,
                allow = (
                    r"^https:\/\/www\.un\.org\/?[A-z_\-\s]{2}\/?$"
                )
            )
        ),
    )
        
    def __init__(self, *a, **kw):
        super(CrawlSpiderONU, self).__init__(*a, **kw)
        self.df = pd.DataFrame(columns=["Web", "Name"])
        self.history = []
        self.rejected = []
        
    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url) # , callback=self.hand_url)
    
    def hand_url(self, response):
        for url in response.css("a::attr(href)").getall():
            if "observances" not in url:
                print(f"DUMMY: {self.base_url}{url}")
                yield response.follow(f"{self.base_url}{url}")


    def parse(self, response):
        url = response.request.url
        m = re.match(r"^.*\.un\.org\/([A-z\d_\-\s]{2,3})\/about-us\/un-system$", url)
        
        if not m:
            self.rejected.append(url)
            return
        
        location = m.groups()[0]
        
        for organization in response.xpath('//h3[contains(@class, "horizontal-line-top-drk")]/text()').getall():
                  
            self.df.at[len(self.df), :] = pd.Series(
                data={
                    "Web": location,
                    "Name": organization
                }
            )
    # This function remains as-is.
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=scrapy.signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        # Whatever is here will run when the spider is done.
        self.df.to_csv("onu.csv", index=False)
        
        with open("output.txt", "w") as f_out:
            f_out.write(f"Rejected: {len(self.rejected)}\n")
            f_out.writelines(map(lambda s: s+"\n",self.rejected))
        
        
        

    