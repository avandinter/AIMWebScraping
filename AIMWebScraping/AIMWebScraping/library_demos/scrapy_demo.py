import scrapy
from scrapy.crawler import CrawlerRunner, CrawlerProcess
import scrapy
from scrapy.http import HtmlResponse
from scrapy.selector import Selector
import requests
from bs4 import BeautifulSoup, SoupStrainer
import time
import json 

class TableItem(scrapy.Item):
        table = scrapy.Field()
        year = scrapy.Field()
        quarter = scrapy.Field()
        product = scrapy.Field()
        items = scrapy.Field()
        amount = scrapy.Field()

class SaverPipeline(object):
    def open_spider(self, spider):
        timestr = time.strftime("%Y%m%d-%H%M%S")
        self.start_time = time.time()
        self.item_count = 0
        self.file = open('AIMWebScraping/data/{}{}{}.json'.format( "products", "_",timestr), 'w')

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        self.item_count += 1
        return item

    def close_spider(self, spider):
        self.file.close()
        print("found " + str(self.item_count) + " total sets in " + str(time.time() - self.start_time) + " seconds")

class DemoSpider(scrapy.Spider):
    name = "crawler"
    allowed_domains = ["testing-ground.scraping.pro"]

    def parse(self, response):
        params = response.url.split("?")[1]

        table = response.xpath("//div[@id='case_table']/table")[0]
        header_row = table.xpath("thead/tr")[0]

        product_lookup = {}
        current_index = 0
        for header in header_row.xpath("th"):
            colspan = header.xpath("@colspan").extract_first()
            text = header.xpath("text()").extract_first()
            if colspan is None:
                colspan = 1
            
            for num in range(0, int(colspan), 1):
                current_index += 1
                product_lookup[current_index] = text



        current_year = ""
        for row in table.xpath('tbody/tr'):
            current_cell_index = 0
            quarter = ''
            for cell in row.xpath("td"):
                colspan = cell.xpath("@colspan").extract_first()
                text = cell.xpath('text()').extract_first()

                if text is None:
                    text = cell.xpath('center/text()').extract_first()

                if text is None or "Toatal for" in text:
                    break

                if colspan is None:
                    colspan = 1
                current_cell_index += int(colspan)

                if (int(colspan) == len(product_lookup)):
                    current_year = text
                    break

                header = product_lookup[current_cell_index]

                if header == 'Quarter':
                    quarter = text
                    continue
                elif header == "Total Amount":
                    continue

                item = TableItem()
                item["quarter"] = quarter
                item["product"] = header
                item["year"] = current_year

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
        'ITEM_PIPELINES': { 'AIMWebScraping.library_demos.scrapy_demo.SaverPipeline': 100 }
        })
        for anchor in all_anchors:
            process.crawl(DemoSpider(), link = "http://testing-ground.scraping.pro" + anchor['href'])
        process.start()
