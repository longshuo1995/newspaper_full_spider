from pymongo import MongoClient
from Extract_Tools import ExtractTools
from GeneralTools import GeneralTools, KillThread
from SearchSpiderTools import SearchSpiderTools
from redis import StrictRedis
from RedisTools import RedisTool
from StrTools import StrTools, RETools
# from SougouTools import Public_Wechat


class Configs(object):
    host = '127.0.0.1'
    interface_host = 'http://%s' % host
    redis_key_general_spider = 'general_climbed_url_v1_1'


class RedisConfigs(object):
    sr = StrictRedis(port=6370)


class MongoConfigs(object):
    host = Configs.host
    port = 27017
    '''
    db.addUser("zhfr_mongodb_root", "zkfr_DUBA@0406mgdb#com") 
    
    db.createUser(
        { 
            user: "zhfr_mongodb_root", 
            pwd: "zkfr_DUBA@0406mgdb#com", 
            roles: [
                { role: "userAdminAnyDatabase", db: "admin" }, 
                { role: "readWriteAnyDatabase", db: "admin" },
                { role: "userAdminAnyDatabase", db: "admin" },
            ] 
        } 
    )
    
    db.auth("root", "zkfr_duba@MGDB0406$com") 
    '''
    '''
    db.createUser(
      {
        user: "root",
        pwd: "zkfr_duba@MGDB0406$com",
        roles: [ 
                 { role: "dbAdminAnyDatabase", db: "admin" },
                 { role: "readWriteAnyDatabase", db: "admin" },
                 { role: "userAdminAnyDatabase", db: "admin" }
        ]
      }
    )
    '''
    username = 'zhfr_mongodb_root'
    password = 'zkfr_DUBA@0406mgdb#com'
    conn = MongoClient(host='192.168.1.178', port=27017, username=username,
                       password=password)
    sns_web = conn.sns.web_data_tieba
    db_web = conn.portal
    col_data = db_web.web_data
    col_snapshoot = db_web.web_data_snapshoot
    col_error = db_web.errorlog
    db_config = conn.website_config
    col_baidu_forbid_pattern = db_config.baidu_forbid_pattern
    col_site_rule = db_config.website_config
    col_pub_wechat = db_config.pub_webchat


class ToolsObjManager(object):
    extract_tool = ExtractTools()
    general_tool = GeneralTools()
    searchspider_tools = SearchSpiderTools()
    # wechat = Public_Wechat()
    redis_tool = RedisTool()
    str_tool = StrTools()
    re_tool = RETools()
    kill_tool = KillThread()


if __name__ == '__main__':
    MongoConfigs.db_web.source_spider_map.insert_one({
        "source_spider": "百度新闻搜索",
        "type": "新闻",
        "second_type": "新闻"
    })
'''
./mongo -u zhfr_mongodb_root -p zkfr_DUBA@0406mgdb#com localhost:38228/admin
'''

'''
 ./mongodump -h 127.0.0.1:38228/admin -d website_config -o /home/longshuo/mongo_website_config -u zhfr_mongodb_root -p zkfr_DUBA@0406mgdb#com
 ./mongodump -h localhost --port 38228 -u zhfr_mongodb_root -p zkfr_DUBA@0406mgdb#com -d website_config -o /home/longshuo/copy_mongo/ --authenticationDatabase admin 
'''