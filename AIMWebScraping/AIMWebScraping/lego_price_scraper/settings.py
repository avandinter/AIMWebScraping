#RUN SETTINGS
YEARS_TO_RUN = ["2018"]
NOTIFICATION_PRICE_THRESHOLD = .80

#CRAWLER SETTING
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36"
LOG_LEVEL = "ERROR"
CONCURRENT_REQUESTS = 5
DOWNLOAD_DELAY = 5
ALLOWED_DOMAINS = ["brickset.com", "bricklink.com"]
SPIDER_NAME = "Lego Spider"

#PIPELINES
TRANSFORMATION_PIPELINE = "AIMWebScraping.lego_price_scraper.pipelines.transformation.TransformationPipeline"
EVALUATION_PIPELINE = "AIMWebScraping.lego_price_scraper.pipelines.evaluation.EvaluationPipeline"
NOTIFICATION_PIPELINE = "AIMWebScraping.lego_price_scraper.pipelines.notification.NotificationPipeline"
SAVER_PIPELINE = "AIMWebScraping.lego_price_scraper.pipelines.save.SaverPipeline"

#NOTIFICATION SETTINGS
WEBHOOK_URL = "https://outlook.office.com/webhook/dd2566ec-1cc8-45c8-a06a-bc898263f53b@833b2b67-7fd5-4644-a0a2-4b89f0bebe77/IncomingWebhook/9ff35e8854cd49819bef89c764981cb5/fcba8add-659a-4606-84d4-298bc00ddc4c"
LOG_LOCATION = 'AIMWebScraping/lego_price_scraper/logs/'