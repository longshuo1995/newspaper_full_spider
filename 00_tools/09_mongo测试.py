from pymongo import MongoClient

if __name__ == '__main__':
    username = 'zhfr_mongodb_root'
    password = 'zkfr_DUBA@0406mgdb#com'
    conn = MongoClient(host='192.168.1.178', port=27017, username=username,
                       password=password)
    conn.db_test.col_test.insert_one({
        "name": 'sd'
    })
