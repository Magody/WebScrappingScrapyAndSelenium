import scrapy
from tutorial_project.items import ProductoFybeca
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst

class SpiderFybeca(scrapy.Spider):
    name = 'spider_fybeca'
    urls = [
        'https://www.fybeca.com/medicinas/hombre/'
    ]

    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url=url)  # como await

    def parse(self, response):
        productos = response.xpath('//div[contains(@class,"product-tile")]')

        for producto in productos:
            # Instancia para cargar las propiedades del Item
            producto_loader = ItemLoader( 
                item = ProductoFybeca(), # Clase item
                selector = producto # Selector por defecto
            )

            producto_loader.default_output_processor = TakeFirst() # No guardar el arreglo

            producto_loader.add_css(
                'titulo', # Nombre propiedad del item
                'div.product-tile div.pdp-link > a::text' # Css para obtener el dato
            )
            
            producto_loader.add_xpath(
                'imagen',  # Nombre propiedad del item
                './/img[contains(@class,"tile-image")]/@src'  # Xpath para obtener el dato
            ) # ../../images/thumbnail/294930.jpg
            yield producto_loader.load_item()