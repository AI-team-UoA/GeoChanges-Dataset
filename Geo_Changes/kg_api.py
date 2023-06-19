#!/usr/bin/env python
# encoding: utf-8
import json

from flask import Flask, jsonify, request

from rdf_loader import load_graph, get_default_graph

from threading import Thread
import functools

app = Flask(__name__)

g = load_graph()

global res

timeout_bool= True
timeout_sec=10

# custom thread class
class CustomThread(Thread):
    def __init__(self,sparql_query, placeholders):
        Thread.__init__(self)
        self.sparql_query = sparql_query
        self.placeholders = placeholders
    # override the run function
    def run(self):
        global res
        #qres = g.query(self.sparql_query)
        qres=(g.query(self.sparql_query))
        for row in qres:
            res.append({placeholder: row[placeholder.replace("?", "")] for placeholder in self.placeholders})
        print(res)
        

@app.route('/query', methods=['POST'])
def query():
    sparql_query = json.loads(request.data)["sparql_query"]
    placeholders = json.loads(request.data)["placeholders"]

    print(sparql_query)
    print(placeholders)

    global res
    #p = multiprocessing.Process(target=query_func, args=(sparql_query, qres))
    # try:
    res = []
    if timeout_bool:
        t = CustomThread(sparql_query, placeholders)
        t.daemon = True
        # p.start()
        # p.join(10)
        t.start()
        t.join(timeout_sec)
        print("APOTELESMATA:")
    else:
        qres = g.query(sparql_query)
        for row in qres:
            print(row)
            res.append({placeholder: row[placeholder.replace("?", "")] for placeholder in placeholders})
    
    print(res)
    
    
    return jsonify({'res': res})



app.run()
