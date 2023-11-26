import random
import sys
sys.path.append("..")
import networkx as nx

from model.rule import Rule
from ontology_loader import get_random_instance

from configuration import not_existing_node_types, not_allowed_uri_nodes, types_for_temp_filters, spatial_filter_relations, county_dates_changes, rule_type
import pandas as pd
from simple_endpoint_access import run_online

class SPARQLQueryGraph:

    def __init__(self, rule: Rule = None, rule_graph: nx.Graph = None, node_types: dict = None, select_node=None,
                 uri_nodes=None, other_nodes=None, edges=None):
        self.rule = rule
        self.rule_graph = rule_graph
        if rule_graph:
            self.rule_graph_edges = rule_graph.edges(data=True)

        self.node_types = node_types or dict()
        self.select_node = select_node
        self.uri_nodes = uri_nodes or set()
        self.other_nodes = other_nodes or set()
        self.edges = edges or set()
        self.uri_node_uris = {}
        self.filters = set()
        self.bindings = set()
        self.placeholders = dict()
        self.results = []
        self.rule_graph = rule_graph
        if rule_graph:
            self.rule_graph_edges = rule_graph.edges(data=True)
        self.sparql_query = None
        self.random_uri_node = None
        self.random_uri_node_instance = None
        self.county_relation = None
        self.random_county = None
    

    def create_ask_online_query(self, prefix_dict):
        geo_rel_lst = random.sample(spatial_filter_relations, len(spatial_filter_relations))
        counties_data = pd.read_csv(county_dates_changes)
        weights = counties_data['ch_type'].apply(lambda x: 0.3 if x == 'http://purl.org/net/tsnchange#Change' else 1.0)
        rand_counties = counties_data.sample(2, replace=False, weights=weights)
        c1, c2 = rand_counties.iloc[0], rand_counties.iloc[1]

        for g_rel in geo_rel_lst:
            if rule_type == "county":
                geo_query_search = "ASK  WHERE { <"+c1["county"]+"> tsn:hasCountyVersion ?cv1. ?cv1 geo:hasGeometry ?g1 . ?g1 geo:asWKT ?wkt1 . <"+c2["county"]+"> tsn:hasCountyVersion ?cv2. ?cv2 geo:hasGeometry ?g2 . ?g2 geo:asWKT ?wkt2 . FILTER("+g_rel+"(?wkt1, ?wkt2 )) .} "
            elif rule_type == "state":
                geo_query_search = "ASK  WHERE { <"+c1["state"]+"> tsn:hasStateVersion ?cv1. ?cv1 geo:hasGeometry ?g1 . ?g1 geo:asWKT ?wkt1 . <"+c2["state"]+"> tsn:hasStateVersion ?cv2. ?cv2 geo:hasGeometry ?g2 . ?g2 geo:asWKT ?wkt2 . FILTER("+g_rel+"(?wkt1, ?wkt2 )) .} "
            
            sparql_query = add_prefixes(geo_query_search, prefix_dict)
            result = run_online(sparql_query)
            if result:
                break

        return rand_counties, g_rel

    def create_random_sparql_query(self, prefix_dict, online):
        # create placeholders
        placeholder_index = 1
        placeholders = dict()
        placeholders[self.select_node] = "?x0"

        
        if self.random_county:
            for node in self.uri_nodes:
                if self.node_types[node] == "hgc:County":
                    placeholders[node] = "<"+self.random_county["county"]+">"
                    self.uri_node_uris[node] = self.random_county["county"]
                    self.uri_nodes.remove(node)
                    break

        for node in self.other_nodes:
            placeholders[node] = "?x" + str(placeholder_index)
            placeholder_index += 1
        placeholder_index = 0
        for node in self.uri_nodes:
            placeholders[node] = "?s" + str(placeholder_index)
            placeholder_index += 1

        print("EDGES:")
        print(self.edges)
        # select query
        sparql_query = "SELECT DISTINCT " + " ".join([placeholders[node] for node in self.uri_nodes]) + " { " + "\n"
        # type conditions
        for node in [self.select_node] + self.other_nodes + self.uri_nodes:
            node_type = self.node_types[node]
            if node_type in not_existing_node_types:
                continue
            sparql_query += " " + placeholders[node] + " a " + node_type + " .\n"

        # non-equality conditions
        done_pairs = set()
        for node1 in [self.select_node] + self.other_nodes + self.uri_nodes:
            for node2 in [node for node in [self.select_node] + self.other_nodes + self.uri_nodes if node != node1]:
                node_pair_id = ' '.join(sorted([node1, node2]))
                if node_pair_id not in done_pairs:
                    if self.node_types[node1] == self.node_types[node2]:
                        node_type = self.node_types[node1]
                        if node_type in ['time:Interval', 'time:Instant', 'xsd:date', 'tsnchange:Change','ChangeType', 'ChangeDate', 'WKT_Geo']:
                            continue
                        sparql_query += " FILTER(" + placeholders[node1] + " != " + placeholders[node2] + ") .\n"
                    done_pairs.add(node_pair_id)
        if len(done_pairs) > 0:
            sparql_query += "\n"

        print("-------------PLACE HOLDERS-------------")
        print(placeholders)

        # conditions
        for edge in self.edges:
            edge_property = edge[1]
            if edge_property == "<http://www.opengis.net/ont/geosparql#asWKT>" and not online:       #locally we do not have geometry values skip those edges
                continue
            sparql_query += " " + placeholders[edge[0]] + " " + edge_property + " " + placeholders[edge[2]] + " .\n"
        sparql_query += "\n"

        # filters
        for filter_condition in self.filters:
            if filter_condition[-1]=="temporal":
                filter_str= filter_condition[0].replace(filter_condition[1], placeholders[filter_condition[1]])
            elif filter_condition[-1]=="spatial":
                if online:
                    filter_str= filter_condition[0].replace(filter_condition[1], placeholders[filter_condition[1]])
                    filter_str= filter_str.replace(filter_condition[3], placeholders[filter_condition[3]])
                else:
                    continue
            sparql_query += " FILTER(" + filter_str + ") .\n"
        if online:
            sparql_query += "}"
        else:
            sparql_query += "} ORDER BY RAND() LIMIT 30"
        sparql_query = add_prefixes(sparql_query, prefix_dict)
        # sparql_query = sparql_query.replace("PREFIX time: <http://www.w3.org/2006/time#>",
        #                                     "PREFIX time: <https://www.w3.org/2006/time#>")

        return sparql_query, placeholders


    def create_sparql_query(self, prefix_dict):
        # create placeholders
        placeholder_index = 1
        self.placeholders = dict()
        self.placeholders[self.select_node] = "?x0"
        # for node in self.other_nodes:
        #     self.placeholders[node] = "?x" + str(placeholder_index)
        #     placeholder_index += 1
        
        for n, t in self.node_types.items():
            if n in self.other_nodes or t in types_for_temp_filters:
                self.placeholders[n] = "?x" + str(placeholder_index)
                placeholder_index += 1

        print("-----------Place holdes-----------")
        print(self.placeholders)
        if self.node_types[self.select_node] == "geo:Geometry" and random.random() < 0.45: #probability to ask about area not geometry
            # select area
            sparql_query = "SELECT DISTINCT (strdf:area(" + " " + self.placeholders["GeoValue_"+str(self.select_node).split("_")[1]] + ") as ?area) { " + "\n"
            self.placeholders["Area_0"]="?area"
            self.node_types["Area_0"]="area"
        else:
            # normal select query
            sparql_query = "SELECT DISTINCT " + " " + self.placeholders[self.select_node] + " { " + "\n"

        # type conditions
        for node in [self.select_node] + self.other_nodes:
            node_type = self.node_types[node]
            if node_type in not_existing_node_types:
                continue
            sparql_query += " " + self.placeholders[node] + " a " + node_type + " .\n"
        sparql_query += "\n"

        # conditions
        for edge in self.edges:
            edge_property = edge[1]
            uri_nodes = self.uri_node_uris.keys()
            if edge[0] in uri_nodes and self.node_types[edge[0]] not in types_for_temp_filters:     #ignore the uri if it is not allowed to be used
                subject = "<" + self.uri_node_uris[edge[0]] + ">"
            else:
                subject = self.placeholders[edge[0]]

            if edge[2] in uri_nodes and self.node_types[edge[2]] not in types_for_temp_filters:
                object = "<" + self.uri_node_uris[edge[2]] + ">"
            else:
                object = self.placeholders[edge[2]]

            sparql_query += " " + subject + " " + edge_property + " " + object + " .\n"

        #leave only the truly uris that can be given to each query
        temp_uri_nodes=[x for x in self.uri_nodes if self.node_types[x] not in types_for_temp_filters]
        print("TEMP URI:")
        print(temp_uri_nodes)
        self.uri_nodes=temp_uri_nodes

        # filters
        for filter_condition in self.filters:
            if filter_condition[-1]=="temporal":
                filter_str= filter_condition[0].replace(filter_condition[1], self.placeholders[filter_condition[1]])
            elif filter_condition[-1]=="spatial":
                filter_str= filter_condition[0].replace(filter_condition[1], self.placeholders[filter_condition[1]])
                filter_str= filter_str.replace(filter_condition[3], self.placeholders[filter_condition[3]])
            sparql_query += " FILTER(" + filter_str + ") .\n"
        sparql_query += "}"
        sparql_query = add_prefixes(sparql_query, prefix_dict)
        # sparql_query = sparql_query.replace("PREFIX time: <https://www.w3.org/2006/time#>",
        #                                     "PREFIX time: <http://www.w3.org/2006/time#>")  # TODO Only required to fix http/https error (remove when fixed)

        return sparql_query

def find_string_without_prefix(sparql_words, prefix_val):
    matching_prefixs = [word for word in sparql_words if prefix_val in word]
    return matching_prefixs

def replace_unmatched_prefixs(sparql, matching_prefixs, prefix_val, prefix_k):
    uri_prefix_form = [word.strip("<>").replace(prefix_val,prefix_k+":") for word in matching_prefixs]
    for i in range(len(matching_prefixs)):
        sparql = sparql.replace(matching_prefixs[i], uri_prefix_form[i])
    return sparql


def add_prefixes(sparql_query, prefix_dict):
    extra_prefix_list = {"strdf":"http://strdf.di.uoa.gr/ontology#", "time":"http://www.w3.org/2006/time#",  "hgc":"http://www.semanticweb.org/savtr/ontologies/2022/1/HistoricGeoChanges-23/"}  #'tser': 'http://time-space-event.com/resource/'
    prefix_dict.update(extra_prefix_list)
    sparql_prefix_list = ""
    sparql_words = sparql_query.split()
    # sparql_prefix_list = "PREFIX strdf: <http://strdf.di.uoa.gr/ontology#>\n"+ "PREFIX time: <http://www.w3.org/2006/time#>\n"       #add this prefix as it should be
    for prefix_key, prefix_value in prefix_dict.items():
        if prefix_value in sparql_query:
            unmatched_prefixs = find_string_without_prefix(sparql_words, prefix_value)
            sparql_query = replace_unmatched_prefixs(sparql_query, unmatched_prefixs, prefix_value, prefix_key)
        if prefix_key + ":" in sparql_query:
            sparql_prefix_list += "PREFIX " + prefix_key + ": <" + str(prefix_value) + ">\n"

    return sparql_prefix_list + "\n" + sparql_query
