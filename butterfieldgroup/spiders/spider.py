import re

import scrapy

from scrapy.loader import ItemLoader
from ..items import ButterfieldgroupItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class ButterfieldgroupSpider(scrapy.Spider):
	name = 'butterfieldgroup'
	start_urls = ['https://www.bm.butterfieldgroup.com/News/Pages/default.aspx?Year=2021']

	def parse(self, response):
		post_links = response.xpath('//tr[@class="newsRowWrap clearfix"]//a/@href').getall()
		yield from response.follow_all(post_links, self.parse_links)

	def parse_links(self, response):
		links = response.xpath('//li[@class="dfwp-item"]')
		for link in links:
			date = link.xpath('.//tr/td[2]/text()').get()
			url = link.xpath('.//a/@href').get()
			yield response.follow(url, self.parse_post, cb_kwargs=dict(date=date))


	def parse_post(self, response,date):

		title = response.xpath('//h1//text() | //p[@class="ms-rteFontSize-3"]//text() | //span[contains(@style,"font-size:")]//text() | //div[@class="ms-rteFontSize-3"]//strong/text() | //font[@size="3"]//text() | //h4//text() | //b/span[@lang="EN-GB"]//text() | //div[@class="ms-rteFontSize-2"]/strong/text() | //div[@style="font-size:14pt;margin:0in 0in 0pt;color:#660033;line-height:150%"]//strong//text()').get().strip()
		content = response.xpath('//div[contains(@webpartid,"")]//td//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))


		item = ItemLoader(item=ButterfieldgroupItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		return item.load_item()
