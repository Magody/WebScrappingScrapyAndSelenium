import scrapy
import pandas as pd

class SpiderTutorial(scrapy.Spider):
    name = "spider_quotes"
    urls = ['http://quotes.toscrape.com/']
    
    def start_requests(self): 
        for url in self.urls: 
            yield scrapy.Request(url=url) 

    def parse(self, response):
        
        df = pd.DataFrame(columns=["Author", "Cite"])
        
        for quote in response.xpath('//div[@class="quote"]'):
            # 
            # ./span[@class="text"]
            
            df.at[len(df), :] = pd.Series(
                data={
                    "Author": quote.xpath('.//small[@class="author"]/text()').get(),
                    "Cite": quote.css('span.text::text').get()
                }
            )
        
        df.to_csv("test.csv", index=False)
        
        

    