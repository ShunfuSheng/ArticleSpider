# -*-  coding:utf-8 -*-
import time
import pickle
import scrapy
from selenium import webdriver


class ZhihuSpider(scrapy.Spider):
    name = "zhihu_sel"
    allowed_domains = ["www.zhihu.com"]
    start_urls = ['https://www.zhihu.com/']

    def parse(self, response):
        pass

    def start_requests(self):
        browser = webdriver.Chrome(executable_path="E:/python-env/py3/chromedriver.exe")

        browser.get("https://www.zhihu.com/signin")
        browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(
            "13328975330")
        browser.find_element_by_css_selector(".SignFlow-password input").send_keys(
            "a2332123456")
        browser.find_element_by_css_selector(
            ".Button.SignFlow-submitButton").click()

        time.sleep(10)

        Cookies = browser.get_cookies()
        cookie_dict = {}
        for cookie in Cookies:
            # 写入文件
            f = open('E:/Python-File/ArticleSpider/cookies/zhihu/' + cookie['name'] + '.txt', 'wb')
            pickle.dump(cookie, f)
            f.close()
            cookie_dict[cookie['name']] = cookie['value']
        browser.close()
        return [scrapy.Request(url=self.start_urls[0], dont_filter=True, cookies=cookie_dict)]