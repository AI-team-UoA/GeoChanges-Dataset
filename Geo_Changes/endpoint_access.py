import datetime
import json
import urllib.parse
from socket import timeout
from urllib.error import URLError
from urllib.request import urlopen

from model.sparql_query_graph import SPARQLQueryGraph
from configuration import online_exceptions


ENDPOINT_URL = "http://pyravlos2.di.uoa.gr:8080/ushistoricalcounties/Query?view=HTML&handle=download&query=@QUERY@&format=SPARQL/JSON"


def run_query_online(query: SPARQLQueryGraph, limit: int = None):
    print("Running Query online...")
    # query = edit_query(query)
    limit_str = ""
    if limit:
        limit_str = " LIMIT " + str(limit)

    sparql_query = query.sparql_query + limit_str

    url = ENDPOINT_URL.replace("@QUERY@", urllib.parse.quote_plus(
        sparql_query))

    print(sparql_query)

    if query.rule.id in online_exceptions:
        timeout_threshold = 10000
    else:
        timeout_threshold = 100

    try:
        time1 = datetime.datetime.now()
        output = urlopen(url, timeout = timeout_threshold)
    except URLError as error:
        print("Error with executing query (URLError):", error)
        return
    except timeout:
        print("Error with executing query (timeout):", timeout)
        return
    time2 = datetime.datetime.now()
    time_diff = time2 - time1

    output = output.read()
    print(" Done", flush=True)

    json_result = json.loads(output.decode('utf-8'))

    print(json_result)

    result = []

    placeholders_inv = {v: k for k, v in query.placeholders.items()}

    if "results" in json_result and "bindings" in json_result["results"] and json_result["results"][
        "bindings"]:
        for i in range(0, len(json_result["results"]["bindings"])):
            single_result = {}
            result.append(single_result)
            # print(json_result["results"]["bindings"][i][placeholder])
            for placeholder in json_result["head"]["vars"]:
                placeholder_res = json_result["results"]["bindings"][i][placeholder]

                placeholder_val = placeholder_res["value"]
                literal_data_type = None
                if "datatype" in placeholder_res:
                    literal_data_type = placeholder_res["datatype"]
                    if literal_data_type == 'http://www.w3.org/2001/XMLSchema#string':
                        placeholder_val = "\"" + placeholder_val + "\"^^xsd:string"
                placeholder = "?" + placeholder
                print("NODE_TYPES:", query.node_types)
                print("PC", query.placeholders)
                single_result[placeholder] = {"value": placeholder_val,
                                              "type": query.node_types[placeholders_inv[placeholder]],
                                              "literal_data_type": literal_data_type}
                # print(json_result["results"]["bindings"][0][placeholder]["value"])
            i += 1

    print("Number of results:", len(result))
    


    query.results = result
    query.time_diff = time_diff

    return result




