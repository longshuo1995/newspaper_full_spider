import re
import json
import requests
from lxml import etree
from Extract_Tools import ExtractTools
import time
from pymongo import MongoClient
from GeneralTools import GeneralTools
from RedisTools import RedisTool

# //div[@id='viceNav']//a/@href
# //div[@class='box_1_a']//a/text()


class StrTools(object):
    def __init__(self):
        self.pattern_repeat = re.compile(r'(\w{3,5}).*?\1.*?\1')
        self.pattern_space = re.compile('\s')
        self.pattern_datetime = re.compile('(\d+)\D*(\d+)\D*(\d+)\D*(\d+)\D*(\d+)(\D*)?(\d*)?')

        self.extract_tools = ExtractTools()
        port = 38228
        self.redis_tools = RedisTool()
        self.general_tools = GeneralTools()
        self.interface_host = "http://192.168.1.179:5020/"
        username = 'zhfr_mongodb_root'
        password = 'zkfr_duba@MGDB0406$com'
        self.conn = MongoClient(host='122.115.46.176', port=port, username=username,
                           password=password)

    def convert_url2key(self, url):
        res = url.replace(':', '@@')
        return res

    def extract_xpath_list(self, xhtml, xpath_list):
        for xpath in xpath_list:
            res = xhtml.xpath(xpath)
            if res and len(res) > 0:
                return res
        return ''

    def get_current_time_str(self):
        result = str(int(time.time()*1000))
        return result

    def html_label_conveter(self, row):
        html = '''
        <p>%s</p>
        ''' % row
        xhtml = etree.HTML(html)
        return xhtml.xpath("//p/text()")[0]

    def deal_relative_href(self, front_href, h):
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

    def extract_host(self, url):
        try:
            end_index = url.index('/', 8)
            url = url[:end_index]
            index = url.find('#')
            if index > 0:
                return url[:index]
            return url
        except:
            return url

    def convert_json_list(self, row):
        if isinstance(row, list) or isinstance(row, dict):
            return row
        return json.loads(row)

    def is_valid_url(self, url):
        if self.pattern_space.search(url):
            return False
        # 冒号
        if self.pattern_repeat.search(url):
            return False
        if len(url) > 100:
            return False
        count_colon = 0
        # 井号
        count_well = 0
        for c in url:
            if c == ':':
                count_colon += 1
            if count_well == '#':
                count_well += 1
        if count_well > 2 or count_colon > 2:
            return False
        return True

    def convert_row_datetime2str(self, row_data):
        if not row_data:
            return ''
        res = self.pattern_datetime.search(row_data)
        try:
            second = res.group(7)
            if not second:
                second = '00'
        except:
            second = '00'
        format_time = '%s-%s-%s %s:%s:%s' % (
        res.group(1), res.group(2), res.group(3), res.group(4), res.group(5), second)
        return self.convert_formdate_strtime(format_time)

    def convert_formdate_strtime(self, format_time):
        try:
            time_array = time.strptime(format_time, '%Y-%m-%d %H:%M:%S')
            return str(int(time.mktime(time_array))*1000)
        except:
            time_array = time.strptime(format_time, '%Y-%m-%d %H:%M')
            return str(int(time.mktime(time_array)) * 1000)

    def shrink_url(self, ori_url):
        try:
            shrink_url = self.general_tools.article2md5(ori_url)

            # url = self.interface_host+'url_to_dwz/url='+ori_url
            # response_html = requests.get(url).text
            # shrink_url = json.loads(response_html)['dwz']
            self.redis_tools.set_val(shrink_url, ori_url)
            return shrink_url
        except:
            return ori_url

    def shrink_url_(self, ori_url):
        # shrink_url = requests.get("http://suo.im/api.php?url=%s" % ori_url).text
        # url_len = len(shrink_url)
        # if url_len < 16 or url_len > 20:
        #     self.conn.portal.cant_shirnk_url({
        #         'url': ori_url
        #     })
        #     shrink_url = ori_url
        # if url_len < 16 or url_len > 20:
        #     Configs.MongoConfigs.db_web.errorlog.insert_one({
        #         'error_type': 'shrink_url',
        #         'msg': ori_url
        #     })
        try:
            res = requests.post(url='http://dwz.cn/create.php', data={'url': ori_url})
            shrink_url = json.loads(res.text)['tinyurl']
            if 16 < len(shrink_url) < 24:
                return shrink_url
            else:
                shrink_url = self.tim_shrink(ori_url)
                if 15 < len(shrink_url) < 24:
                    return shrink_url
        except:
            try:
                shrink_url = self.tim_shrink(ori_url)
                if 15 < len(shrink_url) < 24:
                    return shrink_url
            except:
                pass
            return ori_url

    def tim_shrink(self, ori_url):
        html = self.extract_tools.extract_html('http://t.tl/?url=%s' % ori_url)[0]
        xhtml = etree.HTML(html)
        result = xhtml.xpath("//span[@id='shortUrl']/text()")
        return str(result[0])


class RETools(object):

    def href_accord_listpattern(self, href, pattern_list):
        for pattern_detail in pattern_list:
            if pattern_detail.search(href):
                return True
        return False

    def re_compiler_dict(self, dic):
        res = dict()
        for k in dic.keys():
            if isinstance(dic[k], str):
                res[k] = re.compile(dic[k])
            else:
                res[k] = self.re_compiler_list(dic[k])
        return res

    def re_compiler_list(self, list_row):
        result = []
        if isinstance(list_row, str):
            return [re.compile(list_row), ]
        for s in list_row:
            result.append(re.compile(s))
        return result


if __name__ == '__main__':
    str_tool = StrTools()
    url = 'zzzhttps://mp.weixin.qq.com/s?src=11&timestamp=1520297719&ver=737&signature=Kn3qZZOkBGpZCHMmgKa6hVU7DWeIuXePoAffdURgDl92TYIq6qOCD8NU6cAzLcn4kocwSRusWluucPY2MT8Oh6R9IvT*4iqPigHTd0B*nbPGfKpDQrFjZO5Z*g*LDKEw&new=1'
    res = str_tool.shrink_url(url)
    print(res)
    '''
    https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&tn=baidu&wd=111&oq=111&rsv_pq=dbb580c500082a31&rsv_t=edf44%2FkrJ4XWK2Zc0j2WkIe5bYjkkXZz%2B6aIyV7SghIhOtWD%2B30uGGHenXc&rqlang=cn&rsv_enter=1&gpc=stf%3D1523344368%2C1523430768%7Cstftype%3D1&tfflag=1&rsv_srlang=cn&sl_lang=cn&rsv_rq=cn
    '''
