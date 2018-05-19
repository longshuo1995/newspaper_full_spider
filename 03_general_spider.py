from FullSpider import FullSpider
import Configs
import gevent


if __name__ == '__main__':

    while True:
        res = Configs.MongoConfigs.col_site_rule.find()
        spawn_list = []
        for i in res:
            g = FullSpider(i['base_href'])
            spawn_list.append(gevent.spawn(g.start))
        gevent.joinall(spawn_list)
