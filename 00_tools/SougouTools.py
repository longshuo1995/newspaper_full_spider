from lxml import etree
import time
import requests
import Configs
import re
import json
import gevent
# from gevent import monkey
# monkey.patch_all()


class Public_Wechat(object):
    def __init__(self):
        self.pub_url = 'http://weixin.sogou.com/weixin?type=1&s_from=input&query='
        self.pub_xpath = "//ul[@class='news-list2']//@href"
        self.pattern_js = re.compile("msgList = (.*)")

    def distribute_extract_html(self, url, count, i):
        while not self.html:
            print(i)
            session = requests.session()
            html = session.get(url=url, headers=Configs.ToolsObjManager.extract_tool.headers).text
            print(len(html))
            if len(html) > count:
                self.html = html
                self.session = session
                return

    def search_link(self, base_url, key_word):
        url = base_url + key_word
        self.html = None
        span_list = []

        for i in range(100):
            span_list.append(gevent.spawn(self.distribute_extract_html, url, 6666, i))
        gevent.joinall(span_list)
        print("xxxxx")
        print("x" * 100)
        print("x" * 100)
        print("x" * 100)
        print(len(self.html))
        with open("wechat.html", "w") as f:
            f.write(self.html)
        xhtml = etree.HTML(self.html)
        hrefs = xhtml.xpath("//p[@class='tit']//a/@href")
        # 过滤掉javascript
        hrefs = [Configs.ToolsObjManager.str_tool.deal_relative_href('', href) for href in hrefs]
        hrefs = [href for href in hrefs if href]
        print(hrefs)
        return hrefs

    def get_pub_link(self, pub_code):
        return self.search_link(self.pub_url, pub_code)

    def extract_pub_items(self, href):
        print(href)
        length = 6344
        while length < 7000:
            html = self.session.get(href, headers=Configs.ToolsObjManager.extract_tool.headers).text
            length = len(html)
            print(length)
        print(len(html))
        print("*" * 11)
        with open("detail.html", "w") as f:
            f.write(html)
        data = self.pattern_js.search(html).group(1)
        # 去除末尾的字符（生成json）
        data = data[:-2]
        with open("data.json", "w") as f:
            f.write(data)
        data = json.loads(data)['list']
        data = [item['app_msg_ext_info'] for item in data]
        return data

    def get_current_url(self, pub_code, title):
        hrefs = self.get_pub_link(pub_code)
        for href in hrefs:
            print(href)
            data_list = self.extract_pub_items(href)
            for item in data_list:
                if item['title'].strip() == title.strip():
                    item['content_url'] = Configs.ToolsObjManager.str_tool.html_label_conveter(item['content_url'])
                    return 'https://mp.weixin.qq.com' + item['content_url']


if __name__ == '__main__':
    wechat = Public_Wechat()
    ''' 
    3千 
    2千 
    '''
    res = wechat.get_current_url('oksadamu', '火灾现场的转型宣传手册')
    print(res)


# if __name__ == '__main__':
#     url = 'http://weixin.sogou.com/weixin?type=1&s_from=input&query=%E7%81%AB%E7%81%BE'
#     wechat = Public_Wechat()
#     wechat.repeat_request(url)


