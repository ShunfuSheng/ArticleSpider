# -*- coding: utf-8 -*-
from selenium import webdriver
from scrapy.selector import Selector

browser = webdriver.Chrome(executable_path='E:/python-env/py3/chromedriver.exe')
browser.get('https://detail.tmall.com/item.htm?spm=a222t.7786574.tabs.27.721a79d6Nax1xP&acm=lb-zebra-21014-276839.1003.4.1662890&id=537351011986&scm=1003.4.lb-zebra-21014-276839.ITEM_537351011986_1662890&skuId=3208290075326')

t_select = Selector(text=browser.page_source)
print(t_select.css('.tm-happy11-panel .tm-price::text').extract())

browser.quit()
