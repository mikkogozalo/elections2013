# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field
from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import (
    TakeFirst, MapCompose, Compose, Join, Identity
)


class ElectionReturnItem(Item):
    clustered_precinct = Field()
    pcos_id = Field()
    province = Field()
    city = Field()
    voters_total = Field()
    voters_voted = Field()
    voters_turnout = Field()
    races = Field()

class RaceItem(Item):
    name = Field()
    results = Field()

class ResultItem(Item):
    candidate = Field()
    votes = Field()

class ElectionReturnItemLoader(ItemLoader):
    default_item_class = ElectionReturnItem

    default_output_processor = TakeFirst()
    clustered_precinct_in = MapCompose(unicode, unicode.strip)
    pcos_id_in = MapCompose(unicode, unicode.strip)
    province_in = MapCompose(unicode, unicode.strip)
    city_in = MapCompose(unicode, unicode.strip, unicode.upper)
    voters_total_in = MapCompose(int)
    voters_voted_in = MapCompose(int)

    races_out = Identity()

class RaceItemLoader(ItemLoader):
    default_item_class = RaceItem

    default_output_processor = TakeFirst()
    name_in = MapCompose(unicode, unicode.strip)
    results_out = Identity()

class ResultItemLoader(ItemLoader):
    default_item_class = ResultItem

    default_output_processor = TakeFirst()
    candidate_in = MapCompose(unicode, unicode.strip)
    votes_in = MapCompose(int)
