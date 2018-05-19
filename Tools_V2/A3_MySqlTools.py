from pymysql import connect

'''
insert into map(url, html)VALUES("b0f80dbaa5e0c06b7c2ee977f3fdd5ea", "<!DOCTYPE ()html>")
'''
class MySqlTools:

    def search_snapshoot(self, url):
        sql = "select html from map where url='%s';" % url
        print(sql)
        self.cursor_snapshoot.execute(sql)
        res = self.cursor_snapshoot.fetchone()
        return res[0].replace("@@@@", '"')

    def __init__(self):
        self.conn = connect(host='192.168.1.193', port=3306, user='root', password='Zkfr_duba@0623.', database='zkdp',
                       charset='utf8')
        self.conn_snapshoot = connect(host='192.168.1.193', port=3306, user='root', password='Zkfr_duba@0623.', database='url_html_map',
                       charset='utf8')

        self.sql = 'SELECT * FROM zkdp.keyword;'
        self.cursor_snapshoot = self.conn_snapshoot.cursor()

    def insert_html_map(self, url, html):
        html = html.replace('"', "@@@@")
        sql = 'insert into map(url, html)VALUES("%s", "%s");' % (url, html)
        print(sql)
        self.cursor_snapshoot.execute(sql)
        self.conn_snapshoot.commit()

    def get_keywords(self):
        cur = self.conn.cursor()
        cur.execute(self.sql)
        ress = cur.fetchall()
        result = [self.none_replace(res) for res in ress]
        return [self.append(i[0], i[1]) for i in result]

    def append(self, word1, word2):
        res = ''
        if word1:
            res += word1
        if word2:
            res += ' ' + word2
        return res

    def none_replace(self, row):
        result = ['', '']
        if not row[0]:
            result[0] = ''
        else:
            result[0] = row[0]
        if not row[1]:
            result[1] = ''
        else:
            result[1] = row[1]
        return result


if __name__ == '__main__':
    tool = MySqlTools()
    res = tool.search_snapshoot("d2001e7689de07048f75c0392837d815")
    print(res)

