import json
import requests
import re
from lxml import etree
import time
from pymongo import MongoClient
'''
DUBa_zkfr#MLGB0406$cat56
'''


class ToutiaoTools(object):
    def __init__(self):
        client = MongoClient('127.0.0.1', 27017)
        self.db = client.portal
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
        }
        self.time_pattern = re.compile("subInfo: {[\s\S]*?time: '(.*?)'")

    def parse_article_url(self, html):
        '''
        通过正则， 解析头条详情页面
        :param url:
        :return:[content, create_time, str_time]
        '''
        content_pattern = re.compile(r"articleInfo[\s\S]*?content(.*?)''\),")
        res = content_pattern.search(html)
        try:
            # clear_html = requests.post('http://192.168.1.193:9997/clearn', data={'d': res.group(1)}).text
            clear_html = etree.HTML(res.group(1)).xpath('string(.)')
            res = etree.HTML(clear_html).xpath('string(.)')
            start = res.index("'")
            end = res.rindex("'")
            content = res[start + 1: end]
            # 匹配发布时间--》转换成时间戳
            str_time = self.time_pattern.search(html).group(1)
            timeArray = time.strptime(str_time, '%Y-%m-%d %H:%M')
            timestamp = time.mktime(timeArray)
            return [content, timestamp, str_time]
        except:
            return []

    def parse_search_page(self, url):
        '''
        通过 首页加载更多--出来的url--提取数据--规范化
        :param url:
        :return: [has_more,[[title, tag_id, content_url],[title, tag_id, content_url]]]
        '''
        html = requests.get(url, self.headers).text
        jhtml = json.loads(html)
        has_more = jhtml.get('has_more', 0)
        news_list = jhtml['data']
        filter_list = []
        for item in news_list:
            title = item.get('title', item.get('abstract', 'None'))
            tag_id = item.get('tag_id', 'None')
            try:
                content_url = item['url']
            except:
                break
            repeat = requests.post('http://127.0.0.1:8886/url_sismember', data={'url': 'sp_'+content_url}).text
            if len(repeat) > 10:
                raise Exception('redis数据库出错')
            elif not repeat:
                filter_list.append([title, tag_id, content_url])
        return [has_more, filter_list]


