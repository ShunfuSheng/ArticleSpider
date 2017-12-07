# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
import logging
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import CsvItemExporter
import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi


# 处理结果写入json文件
class JsonWithEncodingPipeline(object):
    def __init__(self):
        self.file = codecs.open('article.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + '\n'
        self.file.write(lines)
        return item

    def close_spider(self, spider):
        self.file.close()


# 使用内置导出模块导出csv文件
class CsvExporterPipeline(object):
    def __init__(self):
        self.file = open('article_export.csv', 'wb')
        self.exporter = CsvItemExporter(self.file)

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

    def close_spider(self, spider):
        self.file.close()


# 重写图片下载处理管道
class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        for ok, value in results:
            image_file_path = value['path']
            item['front_image_path'] = image_file_path
        return item


# 采用同步的机制写入mysql
class MysqlPipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect('localhost', 'root', '123456', 'article_spider', charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = 'INSERT INTO jobbole_article(title, url, create_date, collect_nums) \
                     VALUES (%s, %s, %s, %s)'
        self.cursor.execute(insert_sql, (item['title'], item['url'], item['create_date'], item['collect_nums']))
        self.conn.commit()


# 采用异步的机制写入mysql
class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWORD'],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbparms)
        return cls(dbpool)

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error) # 处理异常

    def handle_error(self, failure):
        logging.error(failure)

    def do_insert(self, cursor, item):
        insert_sql = 'INSERT INTO jobbole_article(title, url, create_date, collect_nums) \
                             VALUES (%s, %s, %s, %s)'
        cursor.execute(insert_sql, (item['title'], item['url'], item['create_date'], item['collect_nums']))
