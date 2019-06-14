import json
import AIMWebScraping.lego_price_scraper.settings as settings

class SaverPipeline(object):
    def open_spider(self, spider):
        self.file = open(settings.LOG_LOCATION + 'notifications_setyear_%s.json' % spider.running_year, 'w')

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
