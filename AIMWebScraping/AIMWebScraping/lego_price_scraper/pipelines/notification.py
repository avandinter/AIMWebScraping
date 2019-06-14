import json
import requests
import datetime
import AIMWebScraping.lego_price_scraper.settings as settings
from AIMWebScraping.lego_price_scraper.items import Condition

class NotificationPipeline(object):
    def format_price_message(self, item, is_new):
        message = ""
        if is_new:
            if item["condition"] is Condition.USED_ONLY:
                message = "Min Price : $%s USD \n\n Avg Price : $%s USD" % (item["new_current_min"], item["new_current_avg"])
            else:
                message = "Min Price : **$%s USD** \n\n Avg Price : $%s USD" % (item["new_current_min"], item["new_current_avg"])
        else:
            if item["condition"] is Condition.NEW_ONLY:
                message = "Min Price : $%s USD \n\n Avg Price : $%s USD" % (item["used_current_min"], item["used_current_avg"])
            else:
                message = "Min Price : **$%s USD** \n\n Avg Price : $%s USD" % (item["used_current_min"], item["used_current_avg"])
        return message


    def create_teams_message(self, item):
        return {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "themeColor": "0076D7",
                "summary": "A Lego Set Has a Lower than Average Price",
                "sections": [{
                    "activityTitle": "#%s" % item["name"],
                    "activitySubtitle":  datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "facts": [{
                        "name": "Set Name",
                        "value": item["name"]
                    },{
                        "name": "Set Number",
                        "value": item["number"]
                    },{
                        "name": "Year",
                        "value": item["year"]
                    },{
                        "name": "New",
                        "value": self.format_price_message(item, True)
                    },{
                        "name": "Used",
                        "value": self.format_price_message(item, False)
                    },{
                        "name": "Url",
                        "value": "- [BrickLink](%s) \r- [BrickSet](%s) \r" % (item["bricklink_url"], item["brickset_url"])
                    }],
                    "text": '[<img style="max-width:300px;" src="%s" alt="%s"></img>](%s)' % (item["image_url"], item["name"], item["bricklink_url"]),
                    "markdown": True
                }]
            }

    def process_item(self, item, spider):
        if item is not None:
            data = self.create_teams_message(item)
            response = requests.post(
                    settings.WEBHOOK_URL, data=json.dumps(data),
                    headers={'Content-Type': 'application/json'}
                )
        return item
