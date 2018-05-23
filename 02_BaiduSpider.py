from lxml import etree
import time
import Configs
import re
import gevent
'''
1. 来源站点   
    泛化的解决方案： 
        通过来源定位位置 来源  
        a标签 href的抽取  的查找 
2. 176数据库丢失的全站网站的Config数据， 迁移 
3. 可视化配置界面 
4. 短网址，修复， 通过redis映射来 
5. 微信的链接处理（实时爬取）

转载来源处理
'''


class BaiduSpider(object):
    def __init__(self):
        self.final_count = 10
        self.repeat_remain = self.final_count
        res = Configs.MongoConfigs.col_baidu_forbid_pattern.find()
        self.forbid_pattern = []
        for pattern in res:
            self.forbid_pattern.append(re.compile(pattern['pattern']))

    def append(self, word1, word2):
        res = ''
        if word1:
            res += word1
        if word2:
            res += ' ' + word2
        return res

    def run(self, base_url, keywords, offset, href_xpath, max_index, filter_before=True, index=0, sourse_spider=''):
        '''
        执行方法。
        :param base_url:
        :param key_word:
        :param offset:
        :param href_xpath:
        :param col:
        :param filter_before: 首页抽取的url是否能在进入之前进行去重判断
        :param index:
        :return:
        '''
        self.keywords = keywords
        self.source_spider = sourse_spider
        item = self.append(keywords[0], keywords[1])
        self.key_word = item
        end = False
        while not end:
            url = base_url % (item, index)
            url = url.replace("__", "%")
            index += offset
            if index > max_index:
                break
            list_html = Configs.ToolsObjManager.extract_tool.extract_html(url)[0]
            list_xhtml = etree.HTML(list_html)
            detail_hrefs = list_xhtml.xpath(href_xpath)
            for detail_href in detail_hrefs:
                # try:
                    if filter_before:
                        repeat = Configs.ToolsObjManager.redis_tool.sismember_value('real_baidu', detail_href)
                        if not repeat:
                            harvest = Configs.ToolsObjManager.extract_tool.extract(detail_href)
                            self.save_harvest(harvest)
                    else:
                        harvest = Configs.ToolsObjManager.extract_tool.extract(detail_href)
                        repeat = Configs.ToolsObjManager.redis_tool.sismember_value('real_baidu', harvest['url'])
                        if not repeat:
                            self.save_harvest(harvest)
                # except Exception as e:
                #     print(e)
                #     pass

    def contains_key(self, row, word):
        if word == '':
            return True
        if isinstance(row, list):
            row = ''.join(row)
        if row.find(word) > 0:
            return True

    def save_harvest(self, harvest):
        crawling_time = str(int(time.time() * 1000))
        # 进行关键词查询
        # contains1 = self.contains_key(harvest['article'], self.keywords[0])
        # contains2 = self.contains_key(harvest['article'], self.keywords[1])
        # if contains1 and contains2:
        if True:
            harvest['create_time'] = str(int(harvest['create_time'] * 1000))
            if len(harvest['create_time']) < 10:
                harvest['create_time'] = crawling_time
            Configs.ToolsObjManager.redis_tool.sadd_value('real_baidu', harvest['url'])
            url = Configs.ToolsObjManager.str_tool.shrink_url(harvest['url'])
            print(harvest['url'])
            print(url)
            if harvest['article']:
                md5 = Configs.ToolsObjManager.general_tool.article2md5(harvest['article'])
                refer_item = Configs.MongoConfigs.db_web.web_data.find_one({'article_md5': md5})
                refer_article_id = ''
                if refer_item:
                    harvest['article'] = []
                    refer_article_id = refer_item['_id']
                Configs.MongoConfigs.db_web.web_data.insert_one({
                    'refer_article_id': refer_article_id,
                    'article_md5': md5,
                    'source_spider': self.source_spider,
                    'title': harvest['title'],
                    'source_from': harvest['source_from'],
                    'article': harvest['article'],
                    'crawling_time': crawling_time,
                    'create_time': harvest['create_time'],
                    'url': url,
                    'original_url': harvest['url'],
                    'key_word': self.key_word
                })
                Configs.MongoConfigs.db_web.url_map.insert_one({
                    'url': url,
                    'original_url': harvest['url']
                })


if __name__ == '__main__':
    while True:
        span_list = []
        start_time = time.time()
        Configs.MongoConfigs.db_web.start_log.insert_one({
            'start_time': start_time
        })
        keywords = Configs.ToolsObjManager.searchspider_tools.get_key_word()

        # keywords = [["火灾", "基站"], ["火灾", ""], [["起火", "机房"]]]

        tm = int(time.time())
        print(keywords)
        for keyword in keywords:
            spider = BaiduSpider()
            url = "https://www.baidu.com/s?wd=%s&pn=%s"
            span_list.append(gevent.spawn(spider.run, 'https://www.baidu.com/s?wd=%s&gpc=stf__3D'+str(tm-24*60*60)+'__2C' + str(tm)+'__7Cstftype__3D1&pn=%s', keywords=keyword, offset=10,
                       href_xpath='//h3/a/@href', max_index=100, filter_before=False, sourse_spider='百度搜索'))
            # span_list.append(gevent.spawn(spider.run, url, keywords=keyword, offset=10,
            #            href_xpath='//h3/a/@href', max_index=500, filter_before=False, sourse_spider='百度搜索'))
            spider = BaiduSpider()
            span_list.append(
                gevent.spawn(spider.run, 'http://news.baidu.com/ns?word=%s&pn=%s', keywords=keyword, offset=20,
                             href_xpath='//h3/a/@href', max_index=500, filter_before=True, sourse_spider='百度新闻'))
            # spider.run('https://www.baidu.com/s?wd=%s&pn=%s', keywords=keyword, offset=10,
            #            href_xpath='//h3/a/@href', max_index=100, filter_before=False, sourse_spider='百度搜索')
            # spider.run('http://news.baidu.com/ns?word=%s&pn=%s', keywords=keyword, offset=20,
            #            href_xpath='//h3/a/@href', max_index=100, filter_before=True, sourse_spider='百度新闻')
        gevent.joinall(span_list)
