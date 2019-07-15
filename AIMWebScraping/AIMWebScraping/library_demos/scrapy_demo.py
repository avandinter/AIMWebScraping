import scrapy
from scrapy.crawler import CrawlerRunner, CrawlerProcess, Settings, reactor
import scrapy
from scrapy.http import HtmlResponse
from scrapy.selector import Selector
from scrapy.exporters import JsonLinesItemExporter
import requests
from bs4 import BeautifulSoup, SoupStrainer
import time
import json 
import uuid

class TableItem(scrapy.Item):
        table = scrapy.Field()
        year = scrapy.Field()
        quarter = scrapy.Field()
        product = scrapy.Field()
        items = scrapy.Field()
        amount = scrapy.Field()

class ExporterPipeline(object):
    def open_spider(self, spider):
        self.table_to_exporter = {}

    def close_spider(self, spider):
        for exporter in self.table_to_exporter.values():
            exporter.finish_exporting()
            exporter.file.close()

    def _exporter_for_item(self, item):
        table = item['table']
        if table not in self.table_to_exporter:
            f = open('AIMWebScraping/data/{}.json'.format(table), 'wb')
            exporter = JsonLinesItemExporter(f)
            exporter.start_exporting()
            self.table_to_exporter[table] = exporter
        return self.table_to_exporter[table]

    def process_item(self, item, spider):
        exporter = self._exporter_for_item(item)
        exporter.export_item(item)
        return item

class DemoSpider(scrapy.Spider):
    name = "crawler"
    allowed_domains = ["testing-ground.scraping.pro"]

    def parse(self, response):
        params = response.url.split("?")[1]

        table = response.xpath("//div[@id='case_table']/table")[0]
        header_row = table.xpath("thead/tr")[0]

        product_lookup = {}
        col_by_header = {}
        current_index = 0
        for header in header_row.xpath("th"):
            colspan = header.xpath("@colspan").extract_first()
            text = header.xpath("text()").extract_first()
            if colspan is None:
                colspan = 1
            col_by_header[text] = []
            for num in range(0, int(colspan), 1):
                current_index += 1
                col_by_header[text].append(current_index)
                product_lookup[current_index] = text



        current_year = ""
        for row in table.xpath('tbody/tr'):
            current_cell_index = 0
            cell_data = {}
            for cell in row.xpath("td"):
                
                colspan = cell.xpath("@colspan").extract_first()
                if colspan is None:
                    colspan = 1

                text = cell.xpath('text()').extract_first()
                if text is None:
                    text = cell.xpath('center/text()').extract_first()

                if (int(colspan) == len(product_lookup)):
                    current_year = text
                    break

                for num in range(0, int(colspan), 1):
                    current_cell_index += 1
                    cell_data[current_cell_index] = text

            if (len(cell_data) == 0 ):
                continue

            for header, cols in col_by_header.items():
                if header == 'Quarter' or header == "Total Amount":
                    continue
                elif len(cols) < 2 or len(cell_data) < cols[1]:
                    continue

                quarter = cell_data[col_by_header["Quarter"][0]]
                if quarter is not None:
                    item = TableItem()
                    item["table"] = params
                    item["quarter"] = quarter
                    item["product"] = header
                    item["year"] = current_year
                    item["items"] = cell_data[cols[0]]
                    item["amount"] = cell_data[cols[1]]

                    yield item


    def __init__(self, link = '', *args, **kwargs):
        self.start_urls = [link]
        super(DemoSpider, self).__init__(*args, **kwargs)

class ScrapyDemo(object):
    def begin_scraping(self):
        response = requests.get("http://testing-ground.scraping.pro/table")
        soup = BeautifulSoup(response.content, 'html.parser', parse_only=SoupStrainer("ul"))

        all_anchors = soup.find_all("a", href = True)

        settings = Settings()
        settings['ITEM_PIPELINES']['AIMWebScraping.library_demos.scrapy_demo.ExporterPipeline'] = 100

        runner = CrawlerRunner(settings)

        for anchor in all_anchors:
            runner.crawl(DemoSpider, link = "http://testing-ground.scraping.pro" + anchor['href'])
        d = runner.join()
        d.addBoth(lambda _: reactor.stop())
        reactor.run()
