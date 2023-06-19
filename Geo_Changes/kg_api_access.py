import requests


def query(sparql_query):
    # extract select variable names
    placeholders = [placeholder for placeholder in sparql_query.split("SELECT", 1)[1].split("{", 1)[0].split(" ")
                    if placeholder.startswith("?")]

    dictToSend = {'sparql_query': sparql_query, 'placeholders': placeholders}
    # print("dictToSend", dictToSend)
    res = requests.post('http://127.0.0.1:5000/query', json=dictToSend)
    print('response from server:', res)
    dictFromServer = res.json()
    # print(dictFromServer)

    return dictFromServer
