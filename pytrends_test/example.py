from pytrends.pyGTrends import pyGTrends
import time
from random import randint
import json
import pymongo
from SPARQLWrapper import SPARQLWrapper, JSON

def get_all_freebase_genres():


    sparql = SPARQLWrapper("http://lod.openlinksw.com/sparql")
    sparql.setQuery("""
        PREFIX ns: <http://rdf.freebase.com/ns/>
        select * where {
        ?genre ns:common.topic.notable_types ns:m.0kpytn
        } 
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results

    

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
    results=get_all_freebase_genres()
    # print results
    count=0
    print len(results["results"]["bindings"])
    for result in results["results"]["bindings"]:
        count+=1
        print count
        fid=(result["genre"]["value"])[26:].replace('.','/')
        print fid

        client = pymongo.MongoClient('localhost', 27017)
        db = client['googletrends']
        collection=db['genre_query_history']

        google_username = "email"
        google_password = "password"
        path = ""

        # connect to Google
        connector = pyGTrends(google_username, google_password)

        # make request
        connector.request_report(fid,geo='US')
        print 
        res_json=csv2json(connector.decode_data.split('\n'))
        res_json['freebase_id']=fid
        if collection.find_one({'query_title': fid}) == None:
            collection.insert_one(res_json)
        
        # wait a random amount of time between requests to avoid bot detection
        time.sleep(randint(5, 10))









    # download file
    # connector.save_csv(path, "name")

    # get suggestions for keywords
    # keyword = "milk substitute"
    # data = connector.get_suggestions(keyword)
    # print(data)
