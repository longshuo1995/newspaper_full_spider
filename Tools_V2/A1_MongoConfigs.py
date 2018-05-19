from pymongo import MongoClient
from A0_ServerConfig import ServerConfig


class MongoConfig:
    def __init__(self):
        self.conn = MongoClient(host=ServerConfig.mongodb_data_host, port=ServerConfig.mongodb_data_port,
                           username=ServerConfig.mongodb_data_username,
                           password=ServerConfig.mongodb_data_password)

        self.db_portal = self.conn.portal
        self.db_sns = self.conn.sns
        self.db_wechat = self.conn.wechat
        self.db_config = self.conn.website_config
        self.db_statistics = self.conn.statistics
        self.db_error = self.conn.db_error

        self.col_sites = self.db_config.website_config
        self.col_map = self.db_portal.source_spider_map
        self.col_crawl_conf = self.db_config.crawlconf
        self.col_statistics_hourly = self.db_statistics.statistics
        self.col_error_log = self.db_error.error_log
        self.col_site_host = self.db_portal.site_host_map


if __name__ == '__main__':
    mongo_config = MongoConfig()
    # mongo_config.db_portal.source_spider_map.insert_one({
    #     "source_spider": "微博搜索",
    #     "type": "微博",
    #     "second_type": "新闻"
    # })
    res = mongo_config.db_portal.web_data.find_one()
    print(res)


