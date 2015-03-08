# -*- coding: utf-8 -*-
import json

from scrapy import Spider
from scrapy.http import Request
from scrapy.selector import Selector

from elections2013.items import (
    ElectionReturnItemLoader, RaceItemLoader, ResultItemLoader
)

class RapplerSpider(Spider):
    name = "rappler"
    allowed_domains = ["rappler.com"]

    def start_requests(self):
        yield Request('http://election-results.rappler.com/2013/precinct/region/1/')

    def parse(self, response):
        obj = json.loads(response.body)
        sel = Selector(text=obj['option'])
        selections = sel.xpath('//option[not(@value="")]/@value').extract()
        scope = response.meta.get('scope', 'region')
        scopes = ['region', 'province', 'city', 'pcos']
        if scope in scopes[:3]:
            for selection in selections:
                yield Request(
                    'http://election-results.rappler.com/2013/precinct/%s/%s/' % (
                        scopes[scopes.index(scope) + 1],
                        selection
                    ),
                    meta={
                        'scope': scopes[scopes.index(scope) + 1]
                    }
                )
        else:
            for selection in selections:
                yield Request(
                    'http://election-results.rappler.com/2013/precinct/%s' % selection,
                    self.parse_er
                )

    def parse_er(self, response):
        er = ElectionReturnItemLoader(response=response)
        er.add_xpath(
            'clustered_precinct',
            '//h3[text()="Clustered Precinct"]/following-sibling::p[1]/text()'
        )
        er.add_xpath(
            'pcos_id',
            '//h3[text()="PCOS ID"]/following-sibling::p[1]/text()'
        )
        er.add_xpath(
            'province',
            '//h3[text()="Province"]/following-sibling::p[1]/text()'
        )
        er.add_xpath(
            'city',
            '//h3[text()="City-Municipality"]/following-sibling::p[1]/text()'
        )
        er.add_xpath(
            'voters_total',
            '//h3[text()="No. of Registered Voters:"]/following-sibling::p[1]/text()'
        )
        er.add_xpath(
            'voters_voted',
            '//div[@class="span6"]/p/text()',
            re=r'Voted: ([0-9,]+)'
        )

        race_tables = response.xpath(
            '//div[@class="res-wrap"]/table'
        )
        for race_table in race_tables:
            race = RaceItemLoader(selector=race_table)
            race.add_xpath('name', './/thead/tr/th[1]/text()')
            result_lines = race_table.xpath('./tbody/tr')
            for result_line in result_lines:
                result = ResultItemLoader(selector=result_line)
                result.add_xpath('candidate', './td[1]/text()')
                result.add_xpath('votes', './td[2]/text()')
                race.add_value('results', result.load_item())
            er.add_value('races', race.load_item())
        yield er.load_item()
