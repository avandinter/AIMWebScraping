from decimal import *
import AIMWebScraping.lego_price_scraper.settings as settings
from AIMWebScraping.lego_price_scraper.items import LegoSet
from bs4 import BeautifulSoup as bs
import chromedriver_binary
import scrapy
from scrapy.crawler import CrawlerRunner, CrawlerProcess
from scrapy.http import HtmlResponse
from scrapy.selector import Selector
from urllib.parse import urlparse, urljoin
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

class LegoSpider(scrapy.Spider):
    name = settings.SPIDER_NAME
    allowed_domains = settings.ALLOWED_DOMAINS
    running_year = ""

    def parse_price_page(self, response):
        url = response.url

        if not url.endswith("#T=P"):
            url = url.split("#", 1)[0] + "#T=P"
        self.driver.get(url)

        item = response.meta['item']
        item["bricklink_url"] = str(url)
        try:
            summary_table = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH, "//table[contains(@class, 'pcipgSummaryTable')]")))
            sold_new_table = self.driver.find_element_by_xpath("(//table[contains(@class, 'pcipgSummaryTable')])[1]")
            sold_used_table = summary_table.find_element_by_xpath("(//table[contains(@class, 'pcipgSummaryTable')])[2]")
            current_new_table = self.driver.find_element_by_xpath("(//table[contains(@class, 'pcipgSummaryTable')])[3]")
            current_used_table = summary_table.find_element_by_xpath("(//table[contains(@class, 'pcipgSummaryTable')])[4]")

            min_price_xpath = ".//tbody/tr/td[text()='Min Price:']/following-sibling::*/b"
            avg_price_xpath = ".//tbody/tr/td[text()='Avg Price:']/following-sibling::*/b"

            if current_new_table is not None:
                item["new_current_min"] = current_new_table.find_element_by_xpath(min_price_xpath).text
                item["new_current_avg"] = sold_new_table.find_element_by_xpath(avg_price_xpath).text

            if current_used_table is not None:
                item["used_current_min"] = current_used_table.find_element_by_xpath(min_price_xpath).text
                item["used_current_avg"] = sold_used_table.find_element_by_xpath(avg_price_xpath).text
        except TimeoutException:
            print("driver timed out")

        yield item

    def parse_set_page(self, response):
        item = response.meta['item']
        item["brickset_url"] = response.url
        price_link = response.xpath('//dt[text()="Current value"]/following-sibling::dd/a[contains(@href,"bricklink.com")]/@href').get()
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
        super(LegoSpider, self).__init__(*args, **kwargs)
