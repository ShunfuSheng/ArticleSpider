# -*- coding: utf-8 -*-
import hashlib


def get_md5(url):
    # 判断是否为unicode编码的字符串，python2和python3最大的区别就是编码问题
    if isinstance(url, str):
        url = url.encode('utf-8')
    m = hashlib.md5(url)
    m.update(url)
    return m.hexdigest()

