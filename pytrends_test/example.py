from pytrends.pyGTrends import pyGTrends
import time
from random import randint
import json
import pymongo

def csv2json(data):
    output={}
    sign=0
    for d in data:
        print d
        if d.startswith('Web Search interest:'):
            output['query_title']=d.split(': ')[1]
            # print output
            continue
        if d.startswith('Interest over time'):
            output['query_overtime']=[]
            continue
        if (' - ' in d) and d.startswith('20'):
            # print d
            if ',' in d:
                query_time_info={}
                d_time,d_querycount=d.split(',')[0],d.split(',')[1]
                query_time_info['starttime']=d_time.split(' - ')[0]
                query_time_info['endtime']=d_time.split(' - ')[1]
                query_time_info['querycount']=d_querycount
                output['query_overtime'].append(query_time_info)
            # break
        if sign is 1:
            sign=2
            output['query_regions']=[]
            continue
        if d.startswith('Top regions') or d.startswith('Top metros'):
            sign=1
        if sign is 2:
            if d=='':
                sign = 0
                break
            query_regioin_info={}
            query_regioin_info['region']=d.split(',')[0]
            query_regioin_info['querycount']=d.split(',')[1]
            output['query_regions'].append(query_regioin_info)
    return output

if __name__ == '__main__':
    
    # of=open('t.json','w')

    client = pymongo.MongoClient('localhost', 27017)
    db = client['googletrends']
    collection=db['genre_query_history']

    google_username = "gaochang23@gmail.com"
    google_password = "GcXx19840912"
    path = ""

    # connect to Google
    connector = pyGTrends(google_username, google_password)

    # make request
    fid = "/m/02822"
    connector.request_report(fid,geo='US')

    # print connector.decode_data.split('\n')#[:500]
    print 
    res_json=csv2json(connector.decode_data.split('\n'))
    res_json['freebase_id']=fid
    if collection.find_one({'query_title': mid}) == None:
        collection.insert_one(res_json)
    # json.dump(res_json,of)
    # of.write('\n')
    # print res_json
    # wait a random amount of time between requests to avoid bot detection
    time.sleep(randint(5, 10))

    # download file
    # connector.save_csv(path, "pizza")

    # get suggestions for keywords
    # keyword = "milk substitute"
    # data = connector.get_suggestions(keyword)
    # print(data)
