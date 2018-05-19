import re
from lxml import etree
import requests
import time
import datetime
from A1_MongoConfigs import MongoConfig


class StrTools:
    def __init__(self):
        self.pattern_host = re.compile("\.(.*?)\..*?/")
        self.pattern_repeat = re.compile(r'(\w{3,5}).*?\1.*?\1')
        self.pattern_space = re.compile('\s')
        self.pattern_datetime = re.compile('(\d+)\D*(\d+)\D*(\d+)\D*(\d+)\D*(\d+)(\D*)?(\d*)?')
        self.mongo_conf = MongoConfig()
        self.headers = {
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Win64; x64; Trident/4.0)'
        }
        self.key_words = {
            "新闻", "网", "站", "吧", "论坛", "百科"
        }
        self.name_pattern = re.compile("[a-zA-Z0-9\u4e00-\u9fa5]*")
        self.fobid_host = {
            "com", "cn", "org", "net", "cc", "gov", "people"
        }
        # 处理时间戳相关的数据
        space = "[年月日时分秒 ：\- :]"
        self.pattern_time = re.compile("(((20)?\d{2})(%s{1,2}\d{2}){2,5})" % space)
        self.pattern_digital = re.compile("\d*")

    def site2host(self, site_name):
        # 查询
        pass

    def str_contains(self, row, keywords):
        '''
        row 中是否包含  keywords中的一个对象（用做噪音判定）
        :param row:
        :param keywords:
        :return:
        '''
        for keyword in keywords:
            if keyword in row:
                return True
        return False

    def site_name_filter(self, name):
        names = self.name_pattern.findall(name)
        names = [i for i in names if i]

        # 包含关键词的搜索， 则按顺序直接返回
        for item in names:
            if self.str_contains(item, self.key_words):
                return item
        # 长度>=3  再按照长度排序
        names3 = [name for name in names if len(name) > 2]
        if names3:
            names = names3
        names.sort(key=lambda name: len(name))
        if not names:
            return ""
        return names[0]

    def get_url_seach_patition(self, url):
        '''
        切割， 将url切割掉前后缀
        :param url:
        :return:
        '''
        index = url.find("/", 9)
        start_index = url.find("//") + 2
        host = url
        if index > 0:
            host = host[: index]
        if start_index > 2:
            host = host[start_index:]
        return host

    def host2site(self, url):
        '''
        将host 转换成 站点名字
        :param url:  url（切割后的）
        :return: 站点名称
        '''
        host = self.get_url_seach_patition(url)
        # 查询Mongodb 是否有作数据缓存
        cache = self.mongo_conf.col_site_host.find_one({
            "host": host
        })
        print(cache)
        if cache:
            return cache['site_name']
        print("*" * 11)
        print(host)
        baidu_search = "http://www.baidu.com/s?wd=%s" % host
        print(baidu_search)
        try:
            html = requests.get(baidu_search, headers=self.headers, verify=False).text

        except Exception as e:
            print(e)
            return self.host2site(url)
        xhtml = etree.HTML(html)
        try:
            site_name = ''.join(xhtml.xpath("//h3//a")[0].xpath(".//text()"))
        except:
            return ""
        site_name = self.site_name_filter(site_name)
        self.mongo_conf.col_site_host.insert_one({
            "host": host,
            'site_name': site_name
        })
        return site_name

    def get_host(self, url):
        first_index = url.find("/") + 2
        end_index = url.find("/", first_index)
        if end_index == -1:
            end_index = len(url)
        url = url[first_index: end_index]
        for host in url.split(".")[::-1]:
            if host not in self.fobid_host:
                return host
        return None

    def extract_host_url(self, url):
        try:
            end_index = url.index('/', 8)
            url = url[:end_index]
            index = url.find('#')
            if index > 0:
                return url[:index]
            return url
        except:
            return url

    def deal_relative_href(self, from_url, h):
        front_href = self.extract_host_url(from_url)
        exit_set = ('#', '', '/')
        if h.startswith('java') or (h in exit_set):
            return ''
        if h.startswith('//'):
            if front_href.startswith('https'):
                return 'https:' + h
            return 'http:' + h
        if self.pattern_space.search(h):
            return ''
        if not h.startswith('http'):
            if h.startswith('/'):
                return front_href + h
            else:
                return front_href+'/'+h
        else:
            return h

    def convert_time_format2stamp(self, time_format):
        time_tuple = self.pattern_digital.findall(time_format)
        time_tuple = list(filter(lambda i: i, time_tuple))
        time_tuple += ["00", "00", "00"]
        time_array = time.strptime("%s-%s-%s %s:%s:%s" % tuple(time_tuple[:6]), "%Y-%m-%d %H:%M:%S")
        return int(time.mktime(time_array))

    def extract_timestamp(self, html):
        '''
        从一段字符串（HTML）源码中， 提取最接近的 timestamp
        :param html:
        :return:
        '''
        time_tuple = self.pattern_time.findall(html)
        lengths = [len(i[0]) for i in time_tuple]
        max_length = max(lengths)
        precise_time_tuple = [i for i in time_tuple if len(i[0]) >= max_length-3]
        time_stamp_list = []
        current_timestamp = time.time()
        print(precise_time_tuple)
        for time_item in precise_time_tuple:
            if not time_item[1]:
                stamp_result = self.convert_time_format2stamp("%s-%s" % (datetime.datetime.now().year, time_item[0]))
            elif len(time_item[1]) == 2:
                stamp_result = self.convert_time_format2stamp("20%s-%s" % (datetime.datetime.now().year, time_item[0]))
            else:
                stamp_result = self.convert_time_format2stamp(time_item[0])
            if stamp_result < current_timestamp:
                time_stamp_list.append(stamp_result)
        time_stamp_list.sort()
        return time_stamp_list[len(time_stamp_list)//2]

    def extract_source_spider(self, html):
        '''
        从一段字符串（html）之类的里面查找source_spider 属性
        :param html:
        :return:
        '''
        pattern_source = re.compile("[\u4e00-\u9fa5][\w\u4e00-\u9fa5]*")
        start_index = html.find("来源")
        source_from = ''
        if start_index > 0:
            after_source = html[start_index + 2:]
            source = pattern_source.search(after_source)
            source_from = source.group(0) if source else ''
        return source_from


if __name__ == '__main__':
    url = "http://www.thepaper.cn/system/2018/04/10/011948296.shtml"
    tool = StrTools()
    res = tool.host2site(url)
    print(res)

