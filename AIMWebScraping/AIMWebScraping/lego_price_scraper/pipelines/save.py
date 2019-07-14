import json
import AIMWebScraping.lego_price_scraper.settings as settings

class SaverPipeline(object):
    def open_spider(self, spider):
        self.year_to_exporter = {}

    def close_spider(self, spider):
        for exporter in self.year_to_exporter.values():
            exporter.finish_exporting()
            exporter.file.close()

    def _exporter_for_item(self, item):
        year = item['year']
        if table not in self.year_to_exporter:
            f = open('AIMWebScraping/data/fullscrape/{}.json'.format(year), 'wb')
            exporter = JsonLinesItemExporter(f)
            exporter.start_exporting()
            self.year_to_exporter[year] = exporter
        return self.year_to_exporter[year]

    def process_item(self, item, spider):
        exporter = self._exporter_for_item(item)
        exporter.export_item(item)
        return item