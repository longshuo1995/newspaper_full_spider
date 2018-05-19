from pymysql import connect
import json
lists = [
            [['百度'], ['it']],
            [['烤肉'], ['']],
            [['百度科技有限公司'], ['']],
            [['金华银行'], ['']],
            [['阿里巴巴公司', '阿里巴巴'], ['']],
            [['中工信环宇', '中工信环宇(北京)网络科技有限公司', '中工信环宇网络科技'], ['电竞', '棋牌', '游戏', '钱', '']],
            [['上海浦东发展银行'], ['']],
            [['中信银行'], ['']],
            [['中国农业银行'], ['']],
            [['中国建设银行'], ['']],
            [['中国邮政储蓄银行'], ['']],
            [['交行', '交通银行'], ['']],
            [['兴业银行'], ['']],
            [['北京银行'], ['']],
            [['华夏银行'], ['']],
            [['工商银行', '工行'], ['']],
            [['广发银行'], ['']],
            [['恒丰银行'], ['']],
            [['民生银行'], ['']],
            [['浦发银行'], ['']],
        ]

conn = connect(host='192.168.1.193', port=3306, user='root', password='Zkfr_duba@0623.', database='zkdp',
               charset='utf8')
# sql = "insert into key_word(words, and_words) VALUES('aaa', 'bbb')"
# cur = conn.cursor()
# cur.execute(sql)
for collection in lists:
    sql = "insert into key_word(words, and_words) VALUES('%s', '%s')" % (json.dumps(collection[0], ensure_ascii=False), json.dumps(collection[1], ensure_ascii=False))
    print(sql)
    cur = conn.cursor()
    cur.execute(sql)
conn.commit()
