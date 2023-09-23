import datetime
import json
import urllib.parse
from socket import timeout
from urllib.error import URLError
from urllib.request import urlopen



ENDPOINT_URL = "http://pyravlos2.di.uoa.gr:8080/ushistoricalcounties/Query?view=HTML&handle=download&query=@QUERY@&format=SPARQL/JSON"

def run_online(query:str, limit: int = None):
    #print("Running Query online...")
    # query = edit_query(query)
    limit_str = ""
    if limit:
        limit_str = " LIMIT " + str(limit)

    sparql_query = query + limit_str

    url = ENDPOINT_URL.replace("@QUERY@", urllib.parse.quote_plus(
        sparql_query))

    #print(sparql_query)

    try:
        time1 = datetime.datetime.now()
        output = urlopen(url, timeout=10000)
    except URLError as error:
        print("Error with executing query (URLError):", error)
        return
    except timeout:
        print("Error with executing query (timeout):", timeout)
        return
    time2 = datetime.datetime.now()
    time_diff = time2 - time1

    output = output.read()
    #print(" Done", flush=True)

    json_result = json.loads(output.decode('utf-8'))
    results = []
    for dict_ in json_result["results"]['bindings']:
        results.append({"?"+k: v['value'] for k, v in dict_.items()})

    #print(results)
    return results