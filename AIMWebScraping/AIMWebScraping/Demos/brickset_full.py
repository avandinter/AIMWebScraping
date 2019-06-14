import random
from bs4 import BeautifulSoup as bs
import scrapy
from scrapy.crawler import CrawlerRunner, CrawlerProcess
from decimal import *
from urllib.parse import urlparse, urljoin
from scrapy.selector import Selector
import sqlite3
import time
import json
import requests
from scrapy.http import HtmlResponse
from scrapy_splash import SplashRequest
import datetime

#Selenium
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import chromedriver_binary
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

DATABASE = 'AIMWebScraping/data/fullscrape/brickset.db'
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'
WEBHOOK_URL = "https://outlook.office.com/webhook/dd2566ec-1cc8-45c8-a06a-bc898263f53b@833b2b67-7fd5-4644-a0a2-4b89f0bebe77/IncomingWebhook/9ff35e8854cd49819bef89c764981cb5/fcba8add-659a-4606-84d4-298bc00ddc4c"

class LegoSet(scrapy.Item):
    number = scrapy.Field()
    name = scrapy.Field()
    link = scrapy.Field()
    year = scrapy.Field()
    image_url = scrapy.Field()
    new_current_min = scrapy.Field()
    new_current_avg = scrapy.Field()
    used_current_min = scrapy.Field()
    used_current_avg = scrapy.Field()

class TransformationPipeline(object):
    def convert_to_decmial(self, item, field_name):
        val = item[field_name]
        if val is not None and val != "-":
            val = val.replace("US $", "")
            val = Decimal(val)
        else:
            val = 0
        item[field_name] = val

    def process_item(self, item, spider):
        self.convert_to_decmial(item, "new_current_min")
        self.convert_to_decmial(item, "new_current_avg")
        self.convert_to_decmial(item, "used_current_min")
        self.convert_to_decmial(item, "used_current_avg")
        item['year'] = int(item['year']);
        return item

class NotificationPipeline(object):
    def create_teams_message(self, item, is_new):
        return {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "themeColor": "0076D7",
                "summary": "A Lego Set Has a Lower than Average Price",
                "sections": [{
                    "activityTitle": "A Lego Set Has a Lower than Average Price",
                    "activitySubtitle":  datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "activityImage": item["image_url"],
                    "facts": [{
                        "name": "Set Number",
                        "value": item["number"]
                    }, {
                        "name": "Set Name",
                        "value": item["name"]
                    }, {
                        "name": "Condition",
                        "value": "New" if is_new else "Used"
                    },{
                        "name": "Year",
                        "value": item["year"]
                    }, {
                        "name": "Min Price",
                        "value": str(item["new_current_min"] if is_new else item["used_current_min"])
                    },{
                        "name": "Avg Price",
                        "value": str(item["new_current_avg"] if is_new else item["used_current_avg"])
                    },{
                        "name": "Url",
                        "value": "[BrickLink %s](%s)" % (item["number"], item["link"])
                    }],
                    "markdown": True
                }]
            }

    def compare_and_notify(self, item, is_new):
        min_field_name = "new_current_min" if is_new else "used_current_min"
        avg_field_name = "new_current_avg" if is_new else "used_current_avg"

        if item[avg_field_name] * Decimal(.80) > item[min_field_name]:
            response = requests.post(
                WEBHOOK_URL, data=json.dumps(self.create_teams_message(item, is_new)),
                headers={'Content-Type': 'application/json'}
            )

    def process_item(self, item, spider):
        self.compare_and_notify(item, True)
        self.compare_and_notify(item, False)
        return item

class SaverPipeline(object):
    def open_spider(self, spider):
        self.file = open('AIMWebScraping/data/fullscrape/brickset_%s.json' % spider.running_year, 'w')

    def process_item(self, item, spider):
        if item is not None:
            items = dict(item)
            for field in items:
                items[field] = str(item[field])

            line = json.dumps(items) + "\n"
            self.file.write(line)
        return item

    def close_spider(self, spider):
        self.file.close()



class BricksetSpider(scrapy.Spider):
    name = "brick set"
    allowed_domains = ["brickset.com", "bricklink.com"]
    running_year = ""

    def parse_price_page(self, response):
        url = response.url

        if not url.endswith("#T=P"):
            url = url.split("#", 1)[0] + "#T=P"
        self.driver.get(url)

        item = response.meta['item']
        item["link"] = str(response.url)
        try:
            summary_table = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH, "//table[contains(@class, 'pcipgSummaryTable')]")))
            new_table = self.driver.find_element_by_xpath("(//table[contains(@class, 'pcipgSummaryTable')])[3]")
            used_table = summary_table.find_element_by_xpath("(//table[contains(@class, 'pcipgSummaryTable')])[4]")

            min_price_xpath = ".//tbody/tr/td[text()='Min Price:']/following-sibling::*/b"
            avg_price_xpath = ".//tbody/tr/td[text()='Avg Price:']/following-sibling::*/b"

            if new_table is not None:
                item["new_current_min"] = new_table.find_element_by_xpath(min_price_xpath).text
                item["new_current_avg"] = new_table.find_element_by_xpath(avg_price_xpath).text

            if used_table is not None:
                item["used_current_min"] = used_table.find_element_by_xpath(min_price_xpath).text
                item["used_current_avg"] = used_table.find_element_by_xpath(avg_price_xpath).text

            print(str(response.url))
            print(str(item["new_current_min"]))
            print(str(item["used_current_min"]))
            print("==============================")

        except TimeoutException:
            print("driver timed out")

        yield item

    def parse_set_page(self, response):
        item = response.meta['item']
        price_link = response.xpath("///dt[text()='Current value']/following-sibling::*/a/@href").get()
        item["year"] = self.running_year
        item["number"] = response.xpath("//dt[text()='Set number']/following-sibling::*/text()").get()
        item["name"] = response.xpath("//dt[text()='Name']/following-sibling::*/text()").get()
        item["image_url"] = urljoin("https://images.brickset.com/sets/images/", item["number"] + ".jpg")

        if price_link is not None:
            request = scrapy.Request(price_link, callback=self.parse_price_page)
            request.meta["item"] = item
            yield request
        else:
            yield item


    def parse(self, response):
        parsed_uri = urlparse(response.request.url)
        root_url = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)[:-1]
        for set_href in response.xpath('//article[contains(@class,"set")]/div[contains(@class,"meta")]/h1/a'):
            set_full_url = urljoin(root_url, set_href.xpath('@href').get())
            request = scrapy.Request(set_full_url, callback=self.parse_set_page)
            item = LegoSet()
            item.setdefault("new_current_min", "0.00")
            item.setdefault("new_current_avg", "0.00")
            item.setdefault("used_current_min", "0.00")
            item.setdefault("used_current_avg", "0.00")
            request.meta["item"] = item
            yield request

        next_page = response.css('li.next a::attr("href")').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
        else:
            yield None

    def spider_closed(self, spider):
        self.driver.quit()

    def __init__(self, begin_url = '', begin_year = '', *args, **kwargs):
        self.start_urls = [begin_url]
        self.running_year = begin_year
        options = Options()
        options.headless = True
        self.driver = webdriver.Chrome(chrome_options=options)
        super(BricksetSpider, self).__init__(*args, **kwargs)

class brickset_full(object):

    def begin_scraping(self):
        process = CrawlerProcess({
        'USER_AGENT': USER_AGENT,
        'LOG_LEVEL': 'ERROR',
        'CONCURRENT_REQUESTS' : 1,
        'DOWNLOAD_DELAY' : 5,
        'ROBOTSTXT_OBEY' : False,
        #'TELNETCONSOLE_PORT': None,
        'ITEM_PIPELINES': { 'AIMWebScraping.Demos.brickset_full.TransformationPipeline': 100, 
                           'AIMWebScraping.Demos.brickset_full.NotificationPipeline': 200, 
                           'AIMWebScraping.Demos.brickset_full.SaverPipeline': 300 }
        })

        response = requests.get("https://brickset.com/browse/sets")
        page = bs(response.content, 'html.parser')
        
        year_container = page.find('h1', text="Years").parent.parent

        for col in year_container.find_all("div", class_='col'):
            if col is not None:
                for year_url in col.find_all('a'):
                    #print(year_url.text)
                    if year_url.text == '2018':
                        process.crawl(BricksetSpider(), begin_url = urljoin("https://brickset.com/", year_url["href"]), begin_year = year_url.text)
        process.start()