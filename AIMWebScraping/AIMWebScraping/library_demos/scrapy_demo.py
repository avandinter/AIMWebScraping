import scrapy
from scrapy.crawler import CrawlerRunner, CrawlerProcess
import requests
from bs4 import BeautifulSoup, SoupStrainer
import time

class TableItem(scrapy.Item):
        table = scrapy.Field()
        year = scrapy.Field()
        quarter = scrapy.Field()
        product = scrapy.Field()
        items = scrapy.Field()
        amount = scrapy.Field()

class LegoSetPipeline(object):
    def open_spider(self, spider):
        print("open spider")
        timestr = time.strftime("%Y%m%d-%H%M%S")
        self.start_time = time.time()
        self.item_count = 0
        self.file = open('AIMWebScraping/data/{}{}{}{}.json'.format( "products", spider.running_year, "_",timestr), 'w')

    def process_item(self, item, spider):
        print("Process Item")
        # This is normally where you would be running your post extraction logic and save to a database
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        self.item_count += 1
        return item

    def close_spider(self, spider):
        self.file.close()
        print("found " + str(self.item_count) + " total sets in " + str(time.time() - self.start_time) + " seconds")

class DemoSpider(scrapy.Spider):
    name = "crawler"
    allowed_domains = ["brickset.com"]
    running_year = ""

    def parse(self, response):
        params = response.url.split("?")[1]

        table = response.xpath("//div[@id='case_table']/table")[0]

        product_lookup = {}
        current_index = 0
        for header in table.xpath("th"):
            colspan = header.xpath("@colspan").get()
            text = header.text
            if colspan is None:
                colspan = 1
            
            for num in range(1,colspan, 1):
                current_index += 1
                product_lookup[current_index] = text
                print(text)



        for row in table.xpath('tr'):
            current_cell_index = 0
            quarter = ''
            for cell in row.xpath("td"):
                colspan = header.xpath("@colspan").get()
                text = header.xpath('text()').get()
                if colspan is None:
                    colspan = 1
                current_cell_index += colspan
                    

                header = product_lookup[current_cell_index]

                if header == 'Quarter':
                    quarter = text
                    continue
                elif header == "Total Amount":
                    continue
                
                
                item = TableItem()
                item.quarter = quarter
                item.product = header

                yield item


    def __init__(self, link = '', *args, **kwargs):
        self.start_urls = [link]
        super(DemoSpider, self).__init__(*args, **kwargs)

class ScrapyDemo(object):
    def begin_scraping(self):
        response = requests.get("http://testing-ground.scraping.pro/table")
        soup = BeautifulSoup(response.content, 'html.parser', parse_only=SoupStrainer("ul"))

        all_anchors = soup.find_all("a", href = True)

        process = CrawlerProcess({
        'LOG_LEVEL': 'ERROR',
        'ITEM_PIPELINES': { 'AIMWebScraping.Demos.webscraping_demo.LegoSetPipeline': 100 }
        })
        for anchor in all_anchors:
            process.crawl(DemoSpider(), link = "http://testing-ground.scraping.pro" + anchor['href'])
        process.start()
