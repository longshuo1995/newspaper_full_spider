import Configs
import re
import time
from lxml import etree


class FullSpider(object):
    def __init__(self, base_url):
        base_url = base_url.strip()

        self.nav_set = set()
        self.warehouse_over = False
        self.pattern_space = re.compile('\s')
        self.default_timestamp = "1262275200000"

        self.mongo_rules = Configs.MongoConfigs.col_site_rule.find_one({'base_href': base_url})
        self.source_spider = self.mongo_rules['source_spider']
        self.base_url = base_url
        self.pattern_host = re.compile("http.*?\.(.*?)\.")

        if not self.mongo_rules.get('forbidden_host', ''):
            self.mongo_rules['forbidden_host'] = ['\.exe$', '\.apk$']
        if not self.mongo_rules.get('detail_url_pattern', ''):
            self.mongo_rules['detail_url_pattern'] = ['\d{6}', ]
        if not self.mongo_rules.get('max_level', 0):
            self.mongo_rules['max_level'] = 3
        try:
            self.mongo_rules['host'] = Configs.ToolsObjManager.re_tool.re_compiler_list(
                self.mongo_rules['host'])
        except:
            re_str = self.pattern_host.search(self.mongo_rules['base_href']).group(1)
            self.mongo_rules['host'] = Configs.ToolsObjManager.re_tool.re_compiler_list(re_str)
        self.mongo_rules['detail_url_pattern'] = Configs.ToolsObjManager.re_tool.re_compiler_list(
            self.mongo_rules['detail_url_pattern'])
        self.mongo_rules['forbidden_host'] = Configs.ToolsObjManager.re_tool.re_compiler_list(
            self.mongo_rules['forbidden_host'])
        self.end = False

    def start(self):
        self.nav_set = set()
        self.run(self.base_url, 0)
        while not self.end:
            # self.next_url()
            try:
                self.next_url()
            except Exception as e:
                Configs.ToolsObjManager.general_tool.print_log(e)

    def isvalid_href(self, href):
        if len(href) > 200:
            return False
        if href in self.nav_set:
            return False
        if self.pattern_space.search(href):
            return False
        if Configs.ToolsObjManager.re_tool.href_accord_listpattern(href, self.mongo_rules['forbidden_host']):
            Configs.MongoConfigs.col_error.insert_one({
                'exit_url': href
            })
            return False
        if Configs.ToolsObjManager.re_tool.href_accord_listpattern(href, self.mongo_rules['host']):
            return True
        return False

    def convert_url2table_name(self, url):
        url = Configs.ToolsObjManager.general_tool.article2md5(url)
        return "queue_%s" % url

    def mongo_pop(self, url):
        table_name = self.convert_url2table_name(url)
        r = eval('Configs.MongoConfigs.conn.news_url_queue.%s' % table_name)
        res = r.find_one()
        if not res:
            self.end = True
            return
        r.remove({'url': res['url']})
        return res

    def next_url(self):
        temp = self.mongo_pop(self.base_url)
        if not temp:
            self.end = True
            return
        self.run(temp['url'], temp['level'], temp['from_url'])
        table_name = self.convert_url2table_name(self.base_url)
        r = eval('Configs.MongoConfigs.conn.news_url_queue.%s' % table_name)
        r.remove({'url': temp['url']})

    def mongo_count(self, base_url):
        table_name = self.convert_url2table_name(base_url)
        r = eval('Configs.MongoConfigs.conn.news_url_queue.%s' % table_name)
        return r.count()

    def mongo_insert(self,from_url, base_url, url, level):
        table_name = self.convert_url2table_name(base_url)
        r = eval('Configs.MongoConfigs.conn.news_url_queue.%s' % table_name)
        r.insert_one({
            'url': url,
            'level': level,
            'from_url': from_url
        })

    def push_href(self, url, html, level):
        if self.mongo_count(self.base_url) > 10000:
            self.warehouse_over = True
        if self.warehouse_over:
            return
        try:
            xhtml = etree.HTML(html)
            hrefs = set(xhtml.xpath('//a/@href'))
            index = url.find('/', 8)
            if index < 0:
                host = url
            else:
                host = url[:index]
            for href in hrefs:
                real_href = Configs.ToolsObjManager.str_tool.deal_relative_href(host, href)
                if self.isvalid_href(real_href):
                    repeat = Configs.ToolsObjManager.redis_tool.sismember_value(
                        Configs.Configs.redis_key_general_spider, real_href)
                    if (not real_href in self.nav_set) and (not repeat):
                        self.mongo_insert(url, self.base_url, real_href, level)
        except Exception as e:
            print(e)
            return

    def run(self, url, level, from_url):
        # 这里url全部是通过过滤的。
        # 过滤条件
        is_detail = Configs.ToolsObjManager.re_tool.href_accord_listpattern(url, self.mongo_rules['detail_url_pattern'])
        if is_detail:
            # 加入到去重中
            added = Configs.ToolsObjManager.redis_tool.sadd_value(
                Configs.Configs.redis_key_general_spider, url)
            if added:
                harvest = Configs.ToolsObjManager.extract_tool.extract(url)
                if harvest['article']:
                    # 有东西才存
                    shrink_url = Configs.ToolsObjManager.str_tool.shrink_url(url)
                    md5 = Configs.ToolsObjManager.general_tool.article2md5(harvest['article'])
                    refer_item = Configs.MongoConfigs.db_web.web_data.find_one({'article_md5': md5})
                    refer_article_id = ''
                    if refer_item:
                        harvest['article'] = []
                        refer_article_id = refer_item['_id']
                    crawling_time = str(int(time.time() * 1000))
                    create_time = str(harvest['create_time'] * 1000)
                    if len(create_time) < 5:
                        create_time = self.default_timestamp
                    if create_time > crawling_time:
                        return
                    # 判断是不是已经在  nav_permanent集合
                    added = Configs.ToolsObjManager.redis_tool.sadd_value("nav_permanent", from_url)

                    Configs.MongoConfigs.db_web.web_data.insert_one(
                        {
                            'refer_article_id': refer_article_id,
                            'article_md5': md5,
                            'by_xpath': 5,
                            'url': shrink_url,
                            'original_url': url,
                            'title': harvest['title'],
                            'source_from': harvest['source_from'],
                            'crawling_time': crawling_time,
                            'create_time': create_time,
                            'article': harvest['article'],
                            'source_spider': self.source_spider,
                            'from_url': from_url
                        }
                    )
                    Configs.MongoConfigs.db_web.url_map.insert_one({
                        'url': shrink_url,
                        'original_url': url
                    })

        else:
            html = Configs.ToolsObjManager.extract_tool.extract_html(url)[0]
            self.nav_set.add(url)
            if level >= self.mongo_rules['max_level']:
                return
            level += 1
            self.push_href(url, html, level)

