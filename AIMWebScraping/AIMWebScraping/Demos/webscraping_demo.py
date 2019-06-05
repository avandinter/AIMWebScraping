#import requests
from bs4 import BeautifulSoup as bs
import scrapy
from scrapy.crawler import CrawlerRunner, CrawlerProcess
import time
import requests

class webscraping_demo(object):
    base_brickset_url = "https://brickset.com/sets/"
    year_url = ""

    def __get_brickset(self, page = 1):
        url = self.year_url + "/page-" + str(page)
        print(url)
        return requests.get(url)

    def requests_brickset(self):
        response = self.__get_brickset()

        result = "URL : " + self.year_url
        result += "Status Code : " + str(response.status_code)
        result += "HTML : " + response.text
        return result

    def bs4_brickset(self):
        response = self.__get_brickset()
        page = bs(response.content, 'html.parser')
        results = ''

        for lego_set in page.find_all('article', class_="set"):
            set_link = lego_set.find('div', {'class':'meta'}).h1.a

            results += "-----------------------------<br />"
            results += "Set: " + set_link.text
            results += '<br />' 
            results += "URL: " + set_link['href']
            results += '<br />'

        return results

    def all_pages_brickset(self):
        start_time = time.time()
        total_sets = 0
        page_number = 1
        while True:
            response = self.__get_brickset(page_number)
            if response.status_code != 200:
                break

            page = bs(response.content, 'html.parser')

            if not page.find('article', class_="set"):
                break

            for lego_set in page.find_all('article', class_="set"):
                total_sets += 1
            page_number += 1

        elapsed_time = time.time() - start_time

        return str(page_number) + " pages scanned, finding " + str(total_sets) + " total sets in " + str(elapsed_time) + " seconds"

    def __init__(self, year):
        self.year_url = self.base_brickset_url + "/year-" + year

class LegoSet(scrapy.Item):
        name = scrapy.Field()
        link = scrapy.Field()

class LegoSetPipeline(object):
    items = []
    start_time = None
    def open_spider(self, spider):
        self.start_time = time.time()

    def process_item(self, item, spider):
        # This is normally where you would be running your database/save logic
        self.items.append(item)
        return item

    def close_spider(self, spider):
        print("found " + str(len(self.items)) + " total sets in " + str(time.time() - self.start_time) + " seconds")

class ScrapySpider(scrapy.Spider):
    name = "crawler"
    #allowed_domains = ["https://brickset.com/"]
    start_urls = ['https://brickset.com/sets/year-' + '2018']

    def parse(self, response):
        for set_link in response.xpath('//article[contains(@class,"set")]/div[contains(@class,"meta")]/h1/a'):
            yield LegoSet(name = set_link.xpath('text()').extract(), link = set_link.xpath('@href').extract())

        next_page = response.css('li.next a::attr("href")').get()
        print(next_page)
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)



class ScrapyExample(object):
    def begin_scraping(self):
        process = CrawlerProcess({
        'USER_AGENT': 'scrapy',
        'LOG_LEVEL': 'ERROR',
        'ITEM_PIPELINES': { 'AIMWebScraping.Demos.webscraping_demo.LegoSetPipeline': 100 }
        })

        results = process.crawl(ScrapySpider)
        process.start()
