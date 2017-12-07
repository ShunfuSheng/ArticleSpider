# -*- coding: utf-8 -*-
import scrapy
import re
from datetime import datetime
from scrapy.http import Request
from urllib import parse

from ArticleSpider.items import JobBoleArticleItem
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
        # 初始化items
        article_item = JobBoleArticleItem()
        # 获取上一级url对应的封面图片
        front_image_url = response.meta.get('front_image_url', '')
        # 获取标题
        title = response.xpath('//*[@class="entry-header"]/h1/text()').extract_first()
        # 获取日期
        create_date = response.xpath('//*[@class="entry-meta"]/p/text()[1]').extract_first().strip().replace(' ·', '')
        # 获取点赞数
        praise_nums = response.xpath('//h10/text()').extract_first()
        # 获取收藏数
        result = response.xpath('//*[@class="post-adds"]/span[2]/text()').extract_first()
        regex = re.match('.*?(\d+).*', result)
        if regex:
            collect_nums = int(regex.group(1))
        else:
            collect_nums = 0
        # 获取评论数
        result = response.xpath('//*[@class="post-adds"]/a[1]/span/text()').extract_first()
        regex = re.match('.*?(\d+).*', result)
        if regex:
            comment_nums = int(regex.group(1))
        else:
            comment_nums = 0
        # 获取内容
        content = response.xpath('//*[@class="entry"]').extract_first()
        # 获取文章标签
        tag_list = response.xpath('//div[@class="entry-meta"]/p/a/text()').extract()
        tag_list = [element for element in tag_list if not element.strip().endswith('评论')]
        tags = ','.join(tag_list)
        # 赋值item
        article_item['title'] = title
        article_item['url'] = response.url
        article_item['url_object_id'] = get_md5(response.url)
        try:
            create_date = datetime.strptime(create_date, '%Y/%m/%d').date()
        except Exception as e:
            create_date = datetime.now()
        article_item['create_date'] = create_date
        article_item['front_image_url'] = [front_image_url]
        article_item['praise_nums'] = praise_nums
        article_item['collect_nums'] = collect_nums
        article_item['comment_nums'] = comment_nums
        article_item['content'] = content
        article_item['tags'] = tags
        yield article_item
