import json
from lxml import etree
import time
import Configs
import re

# 服务器需要改的。


class GeneralSpider(object):
    def __init__(self, base_url):
        # 配置数据库信息
        # 查询字段，并赋值到本地变量。
        base_url = base_url.strip()
        Configs.ToolsObjManager.redis_tool.delete_key('nav_%s' % Configs.ToolsObjManager.str_tool.convert_url2key(base_url))
        self.pattern_space = re.compile('\s')

        self.mongo_rules = Configs.MongoConfigs.col_site_rule.find_one({'base_url': base_url})

        self.source_spider = self.mongo_rules['source_spider']
        self.base_url = base_url
        rule_site = self.mongo_rules['site_pattern']
        if not self.mongo_rules.get('forbidden_site_pattern', ''):
            self.mongo_rules['forbidden_site_pattern'] = []
        if not self.mongo_rules.get('detail_url_pattern', ''):
            self.mongo_rules['detail_url_pattern'] = ['\d{6}', ]
        self.pattern_site = Configs.ToolsObjManager.re_tool.re_compiler_list(Configs.ToolsObjManager.str_tool.convert_json_list(rule_site))
        rule_article = Configs.ToolsObjManager.str_tool.convert_json_list(self.mongo_rules.get('detail_url_pattern', []))
        self.pattern_article = Configs.ToolsObjManager.re_tool.re_compiler_list(rule_article)
        rule_exit = Configs.ToolsObjManager.str_tool.convert_json_list(self.mongo_rules.get('forbidden_site_pattern', []))
        self.pattern_exit = Configs.ToolsObjManager.re_tool.re_compiler_list(rule_exit)
        try:
            self.xpath_list_article = Configs.ToolsObjManager.str_tool.convert_json_list(self.mongo_rules.get('xpath_list_article', '[]'))
        except:
            self.xpath_list_article = []
        self.end = False
        #
        # self.xpath_createtime = self.mongo_rules['xpath_createtime']
        # self.xpath_title = self.mongo_rules['xpath_title']

    def start(self):
        self.run(self.base_url)
        while not self.end:
            try:
                self.next_url()
            except Exception as e:
                print(e)

    def push_href(self, url, html, ready_put_exit):
        try:
            xhtml = etree.HTML(html)
            hrefs = xhtml.xpath('//a/@href')
        except:
            return
        try:
            end = url.index('/', 8)
            front_href = url[:end]
        except:
            front_href = url
        after_hrefs = set([Configs.ToolsObjManager.str_tool.deal_relative_href(front_href, h) for h in hrefs])
        for after_href in after_hrefs:
            # 加入到
            if ready_put_exit:
                if Configs.ToolsObjManager.re_tool.href_accord_listpattern(after_href, self.pattern_article) and \
                        Configs.ToolsObjManager.re_tool.href_accord_listpattern(after_href, self.pattern_site):
                    have_detail_href = True
            # 查询是否重复，不重复的才加入到redis的队列中。
            is_valid = Configs.ToolsObjManager.str_tool.is_valid_url(after_href)
            if is_valid:
                repeat = Configs.ToolsObjManager.redis_tool.sismember_value(Configs.ToolsObjManager.str_tool.convert_url2key(self.base_url), after_href)
                if not repeat:
                    Configs.ToolsObjManager.redis_tool.sadd_value(Configs.ToolsObjManager.str_tool.convert_url2key(self.base_url), after_href)
        # return after_hrefs

    def next_url(self):
        url = Configs.ToolsObjManager.redis_tool.spop_value(Configs.ToolsObjManager.str_tool.convert_url2key(self.base_url))
        if url:
            self.run(url)
        else:
            self.end = True

    def save_url(self, url):
        '''
        查重， 抽取数据，存储到mongodb库  加入重复
        :param url:
        :return:html
        '''
        harvest = Configs.ToolsObjManager.extract_tool.extract(url)
        if not harvest['article']:
            return ''
            # raise Exception('未取到正文')
        # self.tool.print_log('准备存入数据')
        # Configs.MongoConfigs.db_web.web_data_snapshoot.insert_one({
        #     'url': url,
        #     'snap_shot': harvest['html']
        # })

        crawling_time = str(int(time.time() * 1000))
        create_time = str(harvest['create_time'] * 1000)
        if len(create_time) < 5:
            create_time = crawling_time
        shrink_url = Configs.ToolsObjManager.str_tool.shrink_url(url)
        Configs.MongoConfigs.db_web.web_data.insert_one(
            {
                'by_xpath': 4,
                'url': shrink_url,
                'original_url': url,
                'title': harvest['title'],
                'crawling_time': crawling_time,
                'create_time': create_time,
                'article': harvest['article'],
                'source_spider': self.source_spider
            }
        )
        Configs.MongoConfigs.db_web.url_map.insert_one({
            'url': shrink_url,
            'original_url': url
        })
        Configs.ToolsObjManager.general_tool.print_log('成功存入数据')
        return harvest['html']

    def run(self, url, level):
        if isinstance(url, bytes):
            url = url.decode()

        if self.pattern_space.search(url):
            return

        # 判断是否退出。
        if Configs.ToolsObjManager.re_tool.href_accord_listpattern(url, self.pattern_exit):
            return
        is_nav = Configs.ToolsObjManager.re_tool.href_accord_listpattern(url, self.pattern_site)

        # 是否是详情页面， 是--》抽取正文，存储，去重加入
        for detail_pattern in self.pattern_article:
            if detail_pattern.search(url) and is_nav:
                # 去重
                # repeat = requests.post('http://127.0.0.1:8883/url_sismember', data={'url': url}).text
                html = self.save_url(url)
                if not html:
                    20*1000*1000
                    return
                self.push_href(url, html, False)
                # requests.post('http://127.0.0.1:8883/url_add', data={'url': url}).text
                Configs.ToolsObjManager.redis_tool.sadd_value(Configs.Configs.redis_key_general_spider, url)

        # 是导航页面：抽取href，
        if is_nav:
            if not Configs.ToolsObjManager.redis_tool.sadd_value('nav_%s' % self.base_url, url):
                return
            html = Configs.ToolsObjManager.extract_tool.extract_html(url)[0]
            self.push_href(url, html, True)
            return
        # 加入重复
        # requests.post('http://127.0.0.1:8883/url_add', data={'url': url}).text
        Configs.ToolsObjManager.redis_tool.sadd_value(Configs.Configs.redis_key_general_spider, url)
