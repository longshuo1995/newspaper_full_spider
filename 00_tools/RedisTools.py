from redis import StrictRedis


class RedisTool(object):
    def __init__(self):
        self.sr = StrictRedis(host='192.168.1.193', port=6379, password='Duba_zkfr#redis_123.com')
        self.back_key = "0000_black_name"

    def delete_key(self, key_name):
        self.sr.delete(key_name)

    def spop_value(self, key_name):
        return self.sr.spop(key_name)

    def sismember_value(self, key_name, value):
        value = self.value_filter(value)
        return self.sr.sismember(key_name, value)

    def set_val(self, key_name, value):
        return self.sr.set(key_name, value)

    def sadd_value(self, key_name, value):
        """
        :rtype:
        """
        value = self.value_filter(value)
        return self.sr.sadd(key_name, value)

    def value_filter(self, value):
        index = value.find("?")
        if index > 0:
            return value[: index]
        return value

    def smembers(self, key_name):
        return self.sr.smembers(key_name)

    def sadd_iterable(self, key_name, iterable_values):
        for value in iterable_values:
            self.sadd_value(key_name, value)

    def get_val(self, key):
        try:
            url = self.sr.get(key)
        except:
            url = self.spop_value(key)
            self.set_val(key, url)
        return url.decode()


if __name__ == '__main__':
    tool = RedisTool()
    res = tool.sadd_value("0000_black_name", "www.g312.com")
    # res = tool.sismember_value("0000_black_name", "wwsw.g312.com")
    print(res)
    # tool.set_val("001", "3333")
    # res = tool.get_val("001")
    # print(res.decode())
