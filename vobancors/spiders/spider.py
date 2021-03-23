import scrapy

from scrapy.loader import ItemLoader
from ..items import VobancorsItem
from itemloaders.processors import TakeFirst

import requests

url = "https://www.voban.co.rs/novosti"

payload={}
headers = {
  'Cookie': 'TS0115e612=01b1345703b12cb7449697da4c8d611eb89b96aa426e522208d60265a3bcc6308924269475e7b57ed0e057c1dfec35f9825d881041; TSe9f90f69029=08857329b6ab280004f5eb05abe66138d22deb86750f1f0ab6e3ab9a045003b9cc36c349aee8d1c2753f203062bd474e'
}


class VobancorsSpider(scrapy.Spider):
	name = 'vobancors'
	start_urls = ['https://www.voban.co.rs/novosti']

	def parse(self, response):
		data = requests.request("GET", url, headers=headers, data=payload)
		raw_data = scrapy.Selector(text=data.text)

		year_links = raw_data.xpath('//div[@class="inner-menu"]//a/@href').getall()
		yield from response.follow_all(year_links, self.parse_year)

	def parse_year(self, response):
		data = requests.request("GET", response.url, headers=headers, data=payload)
		raw_data = scrapy.Selector(text=data.text)

		post_links = raw_data.xpath('//div[@class="articlepreview"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = raw_data.xpath('//ul[@id="paging"]/li/a/@href').getall()
		yield from response.follow_all(next_page, self.parse_year)

	def parse_post(self, response):
		data = requests.request("GET", response.url, headers=headers, data=payload)
		raw_data = scrapy.Selector(text=data.text)

		title = raw_data.xpath('//h1/text()').get()
		description = raw_data.xpath('//div[@class="text"]/p/text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()
		date = raw_data.xpath('//div[@class="text"]/text()[normalize-space()]').get()

		item = ItemLoader(item=VobancorsItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
