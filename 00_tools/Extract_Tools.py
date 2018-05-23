import socket
from newspaper import Article
import time
import re
from bs4 import BeautifulSoup
from pymongo import MongoClient
from lxml import etree
import requests
from gevent import monkey
monkey.patch_all()


class ExtractTools(object):
    def extract_absolute_url(self, html, from_url):
        xhtml = etree.HTML(html)

    def extract_html_by_count(self, url, min_length):
        html = ''
        while len(html) <= min_length:
            html = self.extract_html(url)[0]
        return html

    def sougou_get_html(self, url):
        if url.find('weixin.sogou') > 0:
            html = requests.get(url, headers=self.headers).text
            # while html.find('txt-box') < 0:

            while html.find('swz2') < 0:
                print(url)
                print('again...')
                html = requests.get(url, headers=self.headers).text
            return [html, url]
        else:
            html = requests.get(url, headers=self.headers).text
            return [html, url]

    def __init__(self):
        # 重复代码  设计问题， 改动则需要修改大量代码， 暂时忍受
        port = 38228
        username = 'zhfr_mongodb_root'
        password = 'zkfr_DUBA@0406mgdb#com'
        conn = MongoClient(host='122.115.46.176', port=port, username=username,
                           password=password)
        self.statistic_collection = conn.statistic.requests_counts
        self.pattern_create_tm_after = re.compile('(\D|^)(20\d{2})\D(\d{1,2})\D(\d{1,2})\D{1,4}(\d{1,2})\D(\d{1,2})($|\D)')
        self.pattern_create_tm = re.compile('((:|>|\\s)?20[0-9]{2}(-|/|\\.|\\u5e74)\\d{1,2}(-|/|\\.|\\u6708)\\d{1,2}(\\u65e5)?\\s?\\d{1,2}(:|\\u65f6)\\d{2}((:|\\u5206)\\d{2})?|(:|>|\\s)?[0-9]{2}\\u5e74\\d{1,2}\\u6708\\d{1,2}(\\u65e5)?\\s?\\d{1,2}(:|\\u65f6)\\d{2}((:|\\u5206)\\d{2})?)')
        self.bs4_xpath_index_pattern = re.compile('\[(-?\d*)\]')
        self.headers = {
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Win64; x64; Trident/4.0)'
        }
        self.pattern_xpath = re.compile('【(.*?)】')
        self.url_pattern = "URL='(.*?)'\">"
        self.pattern_property = re.compile('【(.*)】')
        self.current_date = time.strftime("%Y/%m/%d")
        self.host = socket.gethostname()

    def weibo_time_converter(self, s, timestamp):
        res = s.split('天')

    def statistics(self):
        if True:
            return
        dic = {
            'host': self.host,
            'date': self.current_date
        }
        res = self.statistic_collection.find_one(dic)
        if res:
            res['count'] += 1
            self.statistic_collection.update({
                '_id': res['_id'],
            }, res)
        else:
            dic['count'] = 1
            self.statistic_collection.insert_one(dic)

    def my_xpath(self, xhtml, xpath):
        xpath_lists = self.pattern_xpath.findall(xpath)
        if xpath_lists:
            for item_xpath in xpath_lists:
                result = xhtml.xpath(item_xpath)
                if result:
                    return result
            return ''
        else:
            return xhtml.xpath(xpath)

    def extract_time_str(self, html, dt):
        default = True if dt else False
        try:
            try:
                if not dt:
                    tm = self.pattern_create_tm.search(html)
                    tm = self.pattern_create_tm_after.search(tm.group(0))
                    dt = "%s-%s-%s %s:%s" % (tm.group(2), tm.group(3), tm.group(4), tm.group(5), tm.group(6))
            except:
                pass
            time_array = time.strptime(dt, '%Y-%m-%d %H:%M')
            result = int(time.mktime(time_array))
            if result > time.time():
                if default:
                    result = self.extract_time_str(html, None)
                else:
                    result = 1000000000
            return result
        except:
            return 0

    def convert_day2timestamp(self, date_day):
        timeArray = time.strptime("%s 00:00:01" % date_day, "%Y-%m-%d %H:%M:%S")
        time_stamp = int(time.mktime(timeArray))


        return time_stamp

    def extract(self, url):
        print(url)
        try:
            a = Article(url, language='zh')
            a.download()
            a.parse()
            html = a.html
            after_url = url
            pattern_source = re.compile("[\u4e00-\u9fa5][\w\u4e00-\u9fa5]*")
            start_index = html.find("来源")
            source_from = ''
            if start_index > 0:
                after_source = html[start_index + 2:]
                source = pattern_source.search(after_source)
                source_from = source.group(0) if source else ''

            try:
                row_t = str(a.publish_date)[0:16]
                if not row_t.startswith('201'):
                    row_t = ''
                create_time = self.extract_time_str(html, row_t)
            except Exception as e:
                create_time = 1000000000
            # url = self.url_pattern.search(html).group(1)
            if create_time > time.time():
                create_time = 1000000000
            d_r = {
                'title': a.title,
                'source_from': source_from,
                'article': [i.strip() for i in a.text.split('\n') if i.strip()],
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
        # 加入统计
        # 同一站点的编码识别缓存
        # 针对IP封锁机制的代理和不使用代理重复发送请求
        self.statistics()
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

    def index_filter(self, group_index, row_list):
        if group_index:
            return row_list[int(group_index.group(1))]
        return row_list

    def bs4_special_rule(self, soup, rule):
        if rule == 'ROW':
            return soup
        if rule.find('|') > 0:
            rules = rule.split('|')
        else:
            rules = [rule]
        for item in rules:
            try:
                g = self.pattern_property.search(item)
                group_index = self.bs4_xpath_index_pattern.search(item)
                if group_index:
                    item = item.replace(group_index.group(0), '')
                    index = int(group_index.group(1))
                else:
                    index = 0
                if g:
                    item = item.replace(g.group(0), '')
                    res = soup.select(item)[index][g.group(1)].strip()
                else:
                    res = soup.select(item)[index].text.strip()
                if not res:
                    return ''
                return res
            except:
                pass

    def extract_by_bs4(self, detail_url, save_field):
        html = self.extract_html(detail_url)[0]
        soup = BeautifulSoup(html)
        res = {'title': soup.title.text}
        for field in save_field:
            if isinstance(save_field[field], str):
                res[field] = self.bs4_special_rule(soup, save_field[field])

            elif isinstance(save_field[field], list):
                parent = soup.select(save_field[field][0])
                res[field] = res.get(field, [])
                for item in parent:
                    # 临时的 准备加入
                    temp_list = []
                    try:
                        for item_xpath in save_field[field][1]:
                            temp_list.append(self.bs4_special_rule(item, item_xpath))
                        if temp_list:
                            res[field].append(temp_list)
                    except:
                        # 这里的异常不需要处理， 筛选掉不合法的元素
                        pass
        return [res, html]


if __name__ == '__main__':
    url = 'http://www.qqhrit.com/index.php/home/index/view/id/25997.html'
    extract = ExtractTools()
    res = extract.extract(url)
    for i in res['article']:
        print(i)
        print("*"*11)
