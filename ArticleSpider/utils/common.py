# -*- coding: utf-8 -*-
import hashlib
import re
from datetime import datetime


def get_md5(url):
    # 判断是否为unicode编码的字符串，python2和python3最大的区别就是编码问题
    if isinstance(url, str):
        url = url.encode('utf-8')
    m = hashlib.md5(url)
    m.update(url)
    return m.hexdigest()


# 格式化时间
def date_convert(value):
    try:
        create_date = datetime.strptime(value, "%Y/%m/%d").date()
    except Exception as e:
        create_date = datetime.now().date()
    return create_date


# 提取数字
def get_nums(value):
    match_re = re.match(".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums


# 去掉tag中提取的评论
def remove_comment_tags(value):
    if "评论" in value:
        return ""
    else:
        return value
