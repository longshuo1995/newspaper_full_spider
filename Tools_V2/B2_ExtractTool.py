import requests
import re
import time
from newspaper import Article
from B1_StrTools import StrTools
from lxml import etree


class ExtractTools:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Win64; x64; Trident/4.0)'
        }
        self.bs4_pattern = re.compile("【(.*?)\|(.*?)】")
        self.fobidden_list = ["图片来源", "文|", "返回搜狐"]
        self.pattern_datetime = re.compile('(\d{2,4})?\D(\d{1,2})\D(\d{1,2})\D(\d\d?)\D(\d\d?)(\D)?(\d\d?)?')
        self.pattern_redirect_url = re.compile('window\.location\.replace\("(.*?)"\)\}')
        self.str_tool = StrTools()

    def get_before_redirect(self, url):
        r = requests.get(url, allow_redirects=False)
        if r.headers.get("Location"):
            after_url = r.headers.get("Location")
        else:
            after_url = self.pattern_redirect_url.search(r.text).group(1)
        if after_url.startswith("/"):
            after_url = "http://www.baidu.com"+after_url
            after_url = self.get_before_redirect(after_url)
        return after_url

    def extract(self, url):
        try:
            a = Article(url, language='zh')
            a.download()
            a.parse()
            html = a.html
            after_url = a.url
            article = [i.strip() for i in a.text.split("\n") if i.strip()]
            start_index = html.find(a.title)
            end_index = html.find(article[0])
            create_time = ''
            source_from = ''
            # son_html 判断，
            if (start_index > 0) and (start_index < end_index):
                try:
                    son_html = html[start_index: end_index]
                    source_from = self.str_tool.extract_source_spider(son_html)
                    create_time = self.str_tool.extract_timestamp(son_html)
                except:
                    pass
            if not create_time:
                try:
                    create_time = self.str_tool.extract_timestamp(html)
                except:
                    create_time = 1000000000
                    pass

                # 在全文搜索（忽略掉）
                try:
                    if not source_from:
                        source_from = self.str_tool.extract_source_spider(html)
                except:
                    pass
            if "sohu" in after_url:
                source_from = ''
            d_r = {
                'title': a.title,
                'source_from': source_from,
                'article': article,
                'html': html,
                'create_time': int(create_time),
                'url': after_url
            }
            return d_r
        except Exception as e:
            print(e)
            print('抽取错误！！！')
            print(url)

    def extract_html(self, url):
        '''
        ①解决编码问题， 通过try  exception  获取html源码。
        ②加入Requests Headers
        :param url:
        :return: [html, after_url]
        '''
        # 同一站点的编码识别缓存
        # 针对IP封锁机制的代理和不使用代理重复发送请求
        ori = requests.get(url, headers=self.headers, verify=False)
        b_html = ori.content
        after_url = ori.url
        try:
            html = b_html.decode(encoding='utf-8')
        except:
            try:
                html = b_html.decode(encoding='gbk')
            except:
                html = ori.text
        return [html, after_url]

    def bs4_helper(self, soup, rule):
        pattern = self.bs4_pattern.search(rule)
        if pattern:
            rule = rule.replace(pattern.group(0), '')
            temp = soup.select(rule)
            result = []
            if pattern.group(1) == 'attr' or pattern.group(1) == '':
                for item in temp:
                    result = item[pattern.group(2)]
            return result

        else:
            temp = soup.select(rule)
            result = []
            for item in temp:
                result.append(item.text)
        return result

    def bs4_parse_seed(self, soup, seed):
        result = {}
        if isinstance(seed, dict):
            for k in seed.keys():
                result[k] = self.bs4_helper(soup, seed[k])
            return result
        elif isinstance(seed, list):
            parent_soups = soup.select(seed[0])
            result_list = []
            for son in parent_soups:
                result_list.append(self.bs4_parse_seed(son, seed[1]))
            return result_list


if __name__ == '__main__':
    tool = ExtractTools()
    url = "http://www.baidu.com/baidu.php?sc.Kf0000jA5uApXoP2PM05s8DNF_joLqa2tLLkHw0zIDa1OvJTZ4bn2HmyaMyfxyFQgYXRVvA7-3ELChCRoEb6qOot31KTcmK8Uki14SlJ65xSjviVR8unWf6YR_5aTh82GnLo35mL6hcZ4SwmTGvpp9ylBbU20J-AQU0YrxYMFIXj9-IN5f.7R_NR2Ar5Od669hHTS9a1PT1WkSNengUaeHGw01WkYIDiXajgnl2901WkYID7auhZV6hHalpeMLCHnsqEs88ikeUrPhzEGLIr1W_3v2N9h9meQQn-B6.U1Yk0ZDqEUEPJPQ3YP0-nWjyYQMlEUEPJ0KspynqnfKY5Uve1pWiSPjf0A-V5HczPfKM5yF-TZnk0ZNG5yF9pywd0ZKGujYk0APGujY1P160UgfqnH0krNtknjDLg1nznW9xn1msnfKopHYs0ZFY5iYk0ANGujY0mhbqnW0Yg1DdPfKVm1YLPjRzn1c1rHIxP1fdP1RknWmLg1Dsn-ts0Z7spyfqn0Kkmv-b5H00ThIYmyTqn0K9mWYsg100ugFM5H00TZ0qn0K8IM0qna3snj0snj0sn0KVIZ0qn0KbuAqs5H00ThCqn0KbugmqTAn0uMfqn0KspjYs0Aq15H00mMTqnH00UMfqn0K1XWY0IZN15HTvrHc1n1fdrHf4nW03nH0kPjn0ThNkIjYkPHcvPjf4njbzPWbv0ZPGujdbnvRzn16vPj0snjKBP1NW0AP1UHYYnW9AwWP7rDD3wWRYrjR30A7W5HD0TA3qn0KkUgfqn0KkUgnqn0KlIjYs0AdWgvuzUvYqn7tsg1Kxn0Kbmy4dmhNxTAk9Uh-bT1Ysg1KxnWf4nHDvP-ts0ZK9I7qhUA7M5H00uAPGujYs0ANYpyfqQHD0mgPsmvnqn0KdTA-8mvnqn0KkUymqnHm0uhPdIjYs0AulpjYs0Au9IjYs0ZGsUZN15H00mywhUA7M5HD0UAuW5H00mLFW5HD1nj0Y"
    res = tool.get_before_redirect(url)
    print(res)

