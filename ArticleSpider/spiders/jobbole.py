# -*- coding: utf-8 -*-
import scrapy
import re
from datetime import datetime
from scrapy.http import Request
from urllib import parse

from ArticleSpider.items import JobBoleArticleItem, ArticleItemLoader
from ArticleSpider.utils.common import get_md5


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    """
    1.获取文章列表页中的文章url并交给scrapy下载后进行解析
    2.获取下一页的url并交给scrapy进行下载，下载完成后交给scrapy
    """
    def parse(self, response):
        # 解析当前页所有文章的url
        post_nodes = response.css('#archive>div>div.post-thumb>a')
        for post_node in post_nodes:
            post_url = post_node.css('::attr(href)').extract_first('')
            image_url = post_node.css('img::attr(src)').extract_first('')
            yield Request(url=parse.urljoin(response.url, post_url), meta={'front_image_url': image_url}, callback=self.parse_detail)
        # 提取下一页并交给scrapy进行下载
        next_url = response.css('.next.page-numbers::attr(href)').extract_first('')
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    # 提取具体文章的信息
    def parse_detail(self, response):
        # 使用item loader加载item
        front_image_url = response.meta.get('front_image_url', '')  # 文章封面图
        item_loader = ArticleItemLoader(item=JobBoleArticleItem(), response=response)
        item_loader.add_xpath('title', '//*[@class="entry-header"]/h1/text()')
        item_loader.add_value('url', response.url)
        item_loader.add_value('url_object_id', get_md5(response.url))
        item_loader.add_xpath('create_date', '//*[@class="entry-meta"]/p/text()[1]')
        item_loader.add_value('front_image_url', [front_image_url])
        item_loader.add_xpath('praise_nums', '//h10/text()')
        item_loader.add_xpath('collect_nums', '//*[@class="post-adds"]/span[2]/text()')
        item_loader.add_xpath('comment_nums', '//*[@class="post-adds"]/a[1]/span/text()')
        item_loader.add_xpath('content', '//*[@class="entry"]')
        item_loader.add_xpath('tags', '//div[@class="entry-meta"]/p/a/text()')

        article_item = item_loader.load_item()

        yield article_item
