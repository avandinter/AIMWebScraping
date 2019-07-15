from scrapy.crawler import CrawlerRunner, CrawlerProcess, Settings, reactor
from bs4 import BeautifulSoup as bs
import requests
from urllib.parse import urlparse, urljoin

from AIMWebScraping.lego_price_scraper.spider import LegoSpider
import AIMWebScraping.lego_price_scraper.settings as settings

class LegoPriceScraper(object):
    def begin_scraping(self):
        response = requests.get("https://brickset.com/browse/sets")
        page = bs(response.content, 'html.parser')
        
        year_container = page.find('h1', text="Years").parent.parent

        crawler_settings = Settings()
        crawler_settings['ITEM_PIPELINES'][settings.TRANSFORMATION_PIPELINE] = 100
        crawler_settings['ITEM_PIPELINES'][settings.EVALUATION_PIPELINE] = 200
        crawler_settings['ITEM_PIPELINES'][settings.NOTIFICATION_PIPELINE] = 300
        crawler_settings['ITEM_PIPELINES'][settings.SAVER_PIPELINE] = 400
        crawler_settings['CONCURRENT_REQUESTS'] = settings.CONCURRENT_REQUESTS
        crawler_settings['DOWNLOAD_DELAY'] = settings.DOWNLOAD_DELAY

        runner = CrawlerRunner(crawler_settings)

        for col in year_container.find_all("div", class_='col'):
            if col is not None:
                for year_url in col.find_all('a'):
                    if year_url.text in settings.YEARS_TO_RUN:
                        runner.crawl(LegoSpider, begin_url = urljoin("https://brickset.com/", year_url["href"]), begin_year = year_url.text)

        d = runner.join()
        d.addBoth(lambda _: reactor.stop())
        reactor.run()
