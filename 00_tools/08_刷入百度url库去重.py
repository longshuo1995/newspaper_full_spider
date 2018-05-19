import Configs

res = Configs.MongoConfigs.db_web.web_data.find()
for i in res:
    try:
        Configs.ToolsObjManager.redis_tool.sadd_value(Configs.Configs.redis_key_general_spider, i['original_url'])
    except:
        try:
            Configs.ToolsObjManager.redis_tool.sadd_value(Configs.Configs.redis_key_general_spider, i['url'])
        except:
            print(i['url'])

