from scrapy.exceptions import DropItem # DropItem

class TransformarTituloAMayusculas(object):

    def process_item(self, item, spider):
        titulo = item['titulo']
        titulo = titulo.replace("\n", "").strip()        
        item['titulo'] = titulo.upper()
        return item
    
class SoloCapsulasPipeline(object):

    def process_item(self, item, spider):
        titulo = item['titulo']
        if 'CAJA' not in titulo:
            raise DropItem('No tiene caja')
        else:
            return item



class TutorialProjectPipeline(object):
    def process_item(self, item, spider):
        return item
