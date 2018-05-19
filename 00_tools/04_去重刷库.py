import Configs
res = Configs.MongoConfigs.db_web.web_data.find()
for item in res:
    if 'original_url' not in item.keys():
        item['original_url'] = item['url']
        item['url'] = Configs.ToolsObjManager.str_tool.shrink_url(item['original_url'])
    added = Configs.ToolsObjManager.redis_tool.sadd_value('zl_general_crawled_url', item['original_url'])
    if added:
        Configs.MongoConfigs.db_web.web_data_2.insert_one(item)
        Configs.MongoConfigs.db_web.url_map_2.insert_one({
            'url': item['url'],
            'original_url': item['original_url']
        })
