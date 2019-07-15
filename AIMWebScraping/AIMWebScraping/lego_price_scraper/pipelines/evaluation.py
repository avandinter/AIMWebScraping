from decimal import *
import AIMWebScraping.lego_price_scraper.settings as settings
from AIMWebScraping.lego_price_scraper.items import Condition

class EvaluationPipeline(object):
    def compare(self, item):
        item["condition"] = Condition.NA
        notify = False

        if item["new_current_avg"] * Decimal(settings.NOTIFICATION_PRICE_THRESHOLD) > item["new_current_min"]:
            notify = True
            item["condition"] = Condition.NEW_ONLY

        if item["used_current_avg"] * Decimal(settings.NOTIFICATION_PRICE_THRESHOLD) > item["used_current_min"]:
            notify = True
            item["condition"] = Condition.BOTH if item["condition"] is Condition.NEW_ONLY else Condition.USED_ONLY

        return notify

    def process_item(self, item, spider):
        if item is not None:
            print("Evaluating {}".format(item["name"]))
            notify = self.compare(item)
            item = item if notify else None
        return item

