import scrapy
import pandas as pd
import re

class SpiderONU(scrapy.Spider):
    name = "spider_onu"
    urls = ['https://www.un.org/fr/about-us/un-system']
    
    df = None
    
    
    
    def start_requests(self):
        self.df = pd.DataFrame(columns=["Web", "Name"])
        
        for url in self.urls: 
            yield scrapy.Request(url=url)
            

    def parse(self, response):
        
        url = response.request.url
        m = re.match(r".*//www.un.org/([A-z\d_\-\s]+)/.*", url)
        
        location = url
        if m:
            location = m.groups()[0]
        
        for organization in response.xpath('//h3[contains(@class, "horizontal-line-top-drk")]/text()').getall():
            # print(organization)        
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
        
        
        
        
        

    