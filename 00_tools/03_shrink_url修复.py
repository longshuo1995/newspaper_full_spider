import Configs

res = Configs.MongoConfigs.db_web.web_data.find({'url': {'$regex': '不符合'}})

Configs.MongoConfigs.db_web.web_data.find({'url': 'http://ww.baidu.com'})

for item in res:
    item['url'] = item['original_url']
    Configs.MongoConfigs.db_web.web_data.update({'_id': item['_id']}, item)
    item.pop('_id')
    Configs.MongoConfigs.db_web.correct_data.insert_one(item)
