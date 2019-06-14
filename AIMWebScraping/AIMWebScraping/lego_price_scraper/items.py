import scrapy
from enum import Enum

class Condition(Enum):
    NA = 1
    NEW_ONLY = 2
    USED_ONLY = 3
    BOTH = 4

class LegoSet(scrapy.Item):
    number = scrapy.Field()
    name = scrapy.Field()
    bricklink_url = scrapy.Field()
    brickset_url = scrapy.Field()
    year = scrapy.Field()
    image_url = scrapy.Field()
    new_current_min = scrapy.Field()
    new_current_avg = scrapy.Field()
    used_current_min = scrapy.Field()
    used_current_avg = scrapy.Field()
    condition = scrapy.Field()