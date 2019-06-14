from scrapy.crawler import CrawlerRunner, CrawlerProcess
from bs4 import BeautifulSoup as bs
import requests
from urllib.parse import urlparse, urljoin

from AIMWebScraping.lego_price_scraper.spider import LegoSpider
import AIMWebScraping.lego_price_scraper.settings as settings

class LegoPriceScraper(object):
    def begin_scraping(self):
        process = CrawlerProcess({
        'USER_AGENT': settings.USER_AGENT,
        'LOG_LEVEL': settings.LOG_LEVEL,
        'CONCURRENT_REQUESTS' : settings.CONCURRENT_REQUESTS,
        'DOWNLOAD_DELAY' : settings.DOWNLOAD_DELAY,
        'ITEM_PIPELINES': { 
            settings.TRANSFORMATION_PIPELINE : 100, 
            settings.EVALUATION_PIPELINE : 200, 
            settings.NOTIFICATION_PIPELINE: 300,
            settings.SAVER_PIPELINE : 400
        }})

        response = requests.get("https://brickset.com/browse/sets")
        page = bs(response.content, 'html.parser')
        
        year_container = page.find('h1', text="Years").parent.parent

        for col in year_container.find_all("div", class_='col'):
            if col is not None:
                for year_url in col.find_all('a'):
                    if year_url.text in settings.YEARS_TO_RUN:
                        process.crawl(LegoSpider(), begin_url = urljoin("https://brickset.com/", year_url["href"]), begin_year = year_url.text)
        process.start()
