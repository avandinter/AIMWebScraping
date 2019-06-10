import uuid
import random
from bs4 import BeautifulSoup as bs
import scrapy
from scrapy.crawler import CrawlerRunner, CrawlerProcess
import time
import json
import requests
from urllib.parse import urlparse, urljoin

class LegoSet(scrapy.Item):
    number = scrapy.Field()
    name = scrapy.Field()
    link = scrapy.Field()
    year = scrapy.Field()
    current_value = scrapy.Field()

class TransformationPipeline(object):
    def process_item(self, item, spider):
        print(item['year'] + " -- " + item['name'])
        val = item['current_value']
        if val is not None and "~" in val:
            item['current_value'] = val.replace("~", "")

        return item

class SaverPipeline(object):
    def open_spider(self, spider):
        timestr = time.strftime("%Y%m%d-%H%M%S")
        self.start_time = time.time()
        self.file = open('AIMWebScraping/data/fullscrape/{}{}{}{}.json'.format( "brickset", spider.running_year, "_full_",timestr), 'w')

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item

    def close_spider(self, spider):
        self.file.close()

class BricksetSpider(scrapy.Spider):
    name = "brick set"
    allowed_domains = ["brickset.com"]
    running_year = ""

    def parse(self, response):
        parsed_uri = urlparse(response.request.url)
        root_url = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)[:-1]
        for set_href in response.xpath('//article[contains(@class,"set")]/div[contains(@class,"meta")]/h1/a'):
            set_full_url = urljoin(root_url, set_href.xpath('@href').get())
            set_response = requests.get(set_full_url)
            
            if set_response is not None:
                set = LegoSet()
                set_page = bs(set_response.content, 'html.parser')
                set["link"] = str(set_full_url)
                set["number"] = set_page.find("dt", string='Set number').find_next_sibling('dd').text
                set["name"] = set_page.find("dt", string='Name').find_next_sibling('dd').text
                set["year"] = set_page.find("dt", string='Year released').find_next_sibling('dd').text
                set["current_value"] = set_page.find("dt", string='Current value').find_next_sibling('dd').text

                yield set

        next_page = response.css('li.next a::attr("href")').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
        else:
            yield None

    def __init__(self, begin_url = '', begin_year = '', *args, **kwargs):
        self.start_urls = [begin_url]
        self.running_year = begin_year
        super(BricksetSpider, self).__init__(*args, **kwargs)

class brickset_full(object):
    USER_AGENTS = [
        ('Mozilla/5.0 (X11; Linux x86_64) '
         'AppleWebKit/537.36 (KHTML, like Gecko) '
         'Chrome/57.0.2987.110 '
         'Safari/537.36'),
        ('Mozilla/5.0 (X11; Linux x86_64) '
         'AppleWebKit/537.36 (KHTML, like Gecko) '
         'Chrome/61.0.3163.79 '
         'Safari/537.36'),
        ('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) '
         'Gecko/20100101 '
         'Firefox/55.0')
    ]

    def begin_scraping(self):
        process = CrawlerProcess({
        'USER_AGENT': random.choice(self.USER_AGENTS),
        'LOG_LEVEL': 'ERROR',
        #'CONCURRENT_REQUESTS' : 5,
        'ITEM_PIPELINES': { 'AIMWebScraping.Demos.brickset_full.TransformationPipeline': 100, 'AIMWebScraping.Demos.brickset_full.SaverPipeline': 200 }
        })

        response = requests.get("https://brickset.com/browse/sets")
        page = bs(response.content, 'html.parser')
        
        year_container = page.find('h1', text="Years").parent.parent

        for col in year_container.find_all("div", class_='col'):
            if col is not None:
                for year_url in col.find_all('a'):
                    process.crawl(BricksetSpider(), begin_url = urljoin("https://brickset.com/", year_url["href"]), begin_year = year_url.text)
        process.start()