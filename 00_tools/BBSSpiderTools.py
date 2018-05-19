import time
import re


class BBSSpiderTools(object):
    def __init__(self):
        self.time_xpath = "//div[@class='authi']//span/@title"
        self.real_time_xpath = "//div[@class='authi']/em/text()"
        self.pattern_date = re.compile('(\d+)\D*(\d+)\D*(\d+)\D*(\d+)\D*(\d+)\D*(\d*)')
        self.dic_count = {'今': 0, '半': -0.5, '昨': -1, '前天': -2, '两': -2, '一': -1}
        self.dic_unit = {'秒': 's', '分钟': 'm', '小时': 'h', '天': 'd', '周': 'w', '月': 'M'}

        self.digital_pattern = re.compile('\d{1,2}')
        self.hour_minute_pattern = re.compile('(\d{2}):(\d{2})')

    def relative_time_convert(self, tm):
        localtime = time.localtime(time.time())
        dic_unit_time = {
            's': localtime.tm_sec,
            'm': localtime.tm_min,
            'h': localtime.tm_hour,
            'd': localtime.tm_mday,
            'M': localtime.tm_mon,
        }
        count = 0
        for c in self.dic_count.keys():
            if tm.find(c) >= 0:
                count = self.dic_count[c]
                break
        if count == 0:
            search_digital = self.digital_pattern.search(tm)
            # errorlog 入库
            count = -int(search_digital.group(0))
        unit = 0
        for u in self.dic_unit.keys():
            if tm.find(u) >= 0:
                unit = self.dic_unit[u]
                break

        if count == -0.5:
            if unit == 'h':
                count = -30
                unit = 'm'
        if unit == 'w':
            count *= 7
            unit = 'd'
        dic_unit_time[unit] += count
        if unit == 'd':
            hour_minute = self.hour_minute_pattern.search(tm)
            if hour_minute:
                dic_unit_time['h'] = int(hour_minute.group(1))
                dic_unit_time['m'] = int(hour_minute.group(2))

        # 处理相减负数问题
        time_lists = [localtime.tm_year, dic_unit_time['M'], dic_unit_time['d'], dic_unit_time['h'], dic_unit_time['m'], dic_unit_time['s']]
        time_lists = [int(i) for i in time_lists]
        # s
        time_lists = self.dealwith(time_lists, 60, 5)
        # m
        time_lists = self.dealwith(time_lists, 60, 4)
        # h
        time_lists = self.dealwith(time_lists, 24, 3)
        # d
        time_lists = self.dealwith(time_lists, 28, 2)
        # M
        time_lists = self.dealwith(time_lists, 12, 1)
        real_time = '%s-%s-%s %s:%s:%s' % tuple(time_lists)
        return self.time_convert(real_time)

    def dealwith(self, l_time, base, i):
        back_result = self.back_count(l_time[i], base)
        if back_result[1]:
            l_time[i] = back_result[0]
            l_time[i-1] -= 1
        return l_time

    def back_count(self, num, base):
        if num < 0:
            num += base
            return [num, True]
        else:
            return [num, False]

    def impurity_time_converter(self, row_data):
        if not row_data:
            return ''
        if not isinstance(row_data, str):
            return ''
        res = self.pattern_date.search(row_data)
        if res:
            second = 0
            if res.group(6):
                second = res.group(6)
            format_time = '%s-%s-%s %s:%s:%s' % (res.group(1), res.group(2), res.group(3), res.group(4), res.group(5), second)
            return self.time_convert(format_time)
        return ''

    def time_convert(self, tm):
        try:
            time_array = time.strptime(tm, '%Y-%m-%d %H:%M:%S')
            return str(int(time.mktime(time_array)) * 1000)
        except:
            time_array = time.strptime(tm, '%Y-%m-%d %H:%M')
            return str(int(time.mktime(time_array)) * 1000)

    def extract_article(self, row_article):
        if not row_article:
            return ''
        if row_article.find('亲，快登录吧，能够浏览更多精彩内容哦！') > 0:
            index = row_article.find('\r\n\r\nx\r\n') + 5
            res = row_article[index:].strip()[:-40].strip()
            index = res.find('\n\n\n')
            res = res[index:]
        else:
            fun_index = row_article.find('function')
            index = row_article[fun_index:].find('\r\n\r\n')+6
            res = row_article[index:].strip()
        noise = '吧，能够浏览更多精彩内容哦！\n您需要 登录 才可以下载或查看，没有帐号？注册\n\n\n\n\n\n\nx'
        return res.replace(noise, '')

    def extract_time(self, detail_xhtml):
        try:
            tm = detail_xhtml.xpath(self.time_xpath)[0]
        except:
            tm = detail_xhtml.xpath(self.real_time_xpath)[0]
            index = tm.index(' ')
            tm = tm[index + 1:]
        return self.time_convert(tm)


if __name__ == '__main__':
    tool = BBSSpiderTools()
    # str_timestack = tool.relative_time_convert('半小时前')
    # Configs.ToolsObjManager.general_tool.print_log(str_timestack)
    res = tool.impurity_time_converter('前天')
    print(res)

