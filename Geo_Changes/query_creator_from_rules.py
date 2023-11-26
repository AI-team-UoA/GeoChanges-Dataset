import copy
import json
import random
import jsons
import time

import matplotlib.pyplot as plt
import networkx as nx
import matplotlib.pyplot as plt

import pandas as pd
import ontology_loader
import rules_reader
from kg_api_access import query
from model.sparql_query_graph import SPARQLQueryGraph
from query_filter_adder import add_geo_relation, add_temporal_filters, add_spatial_filters, random_online_date, node_properties
from configuration import allowed_select_node_types, not_allowed_uri_nodes, select_exception_rule_ids, online_exceptions, rule_type, experiment_path, counties_dates_path, types_for_temp_filters, rules_with_start_end
from simple_endpoint_access import run_online
class IndexedClass:


    def __init__(self, index, rdf_class):
        self.index = index
        self.rdf_class = rdf_class

# A tool to generate 
class QueryGeneratorFromRules:


    def __init__(self, online=False, class_instances=None):
        self.G = None
        self.rules = None
        self.forbidden_queries = []
        self.rules_with_valid_queries = None
        self.queries_without_result = set()
        self.online = online
        self.class_instances = class_instances

    # Returns a dictionary for each edge between 2 counties versions, checks if they come from the same or different county
    def versions_of_same_county(self, rule):       
        same_county_node_versions={}
        if rule_type == "state":
            entity_type = "State"
        else:
            entity_type = "County"
        county1=None
        county2=None

        for edge in rule.edges:
            if edge[0].split("_")[0] == "hgc:"+entity_type+"Version" and edge[1].split("_")[0] == "hgc:"+entity_type+"Version":
                for n1,n2 in rule.edges:
                    if n1 == edge[0] and n2.split("_")[0] == "hgc:"+entity_type:
                        county1 = n2
                    elif n2 == edge[0] and n1.split("_")[0] == "hgc:"+entity_type:
                        county2 = n1
                    if n1 == edge[1] and n2.split("_")[0] == "hgc:"+entity_type:
                        county2 = n2
                    elif n2 == edge[1] and n1.split("_")[0] == "hgc:"+entity_type:
                        county2 = n1
                if county1 == county2:            #if the county versions are from the same county its true 
                    same_county_node_versions[tuple(edge)] = True
                else:                           #from county versions from different county its false
                    same_county_node_versions[tuple(edge)] = False

        return same_county_node_versions


    # Identifies is the two county versions belong to the same county
    # Pick the corresponding predicate between the 2 county versions
    def filter_cnt_ver_predicates(self, edge, same_county_node_versions):
        predicates_to_be_removed=[]
        if rule_type == "state":
            entity_type = "State"
        else:
            entity_type = "County"
        if tuple(edge) in list(same_county_node_versions.keys()):
            if same_county_node_versions[tuple(edge)]:
                predicates_to_be_removed=['sem:geospatialProperty']
            else:
                predicates_to_be_removed=['tse:hasNext'+entity_type+'Version', 'tse:hasPrevious'+entity_type+'Version']

        return predicates_to_be_removed

    # For every rule item creates the corresponding graph
    def create_rule_graphs(self):
        self.rules = rules_reader.get_rules()  #create rule object for every different Q subgraph
        _, self.prefix_dict = ontology_loader.get_default_graph()
        self.G, _, _ = ontology_loader.get_ontology()
        to_remove = set()
        ### Load rule graphs
        for rule in self.rules.values():
            if self.rules_with_valid_queries and rule.id not in self.rules_with_valid_queries:
                to_remove.add(rule)
                continue

            # if rule.id != "Q1": # not in ["Q1","Q3","Q4","Q7", "Q12", "Q13"] :  # Q40 #Q17 #Q34
            #     continue
            rule.graph = nx.DiGraph(id=rule.id)       #Need to be DirectionalyGraph
            same_county_node_versions=self.versions_of_same_county(rule)
            print(rule.id)

            for edge in rule.edges:                 ####### prints na doyme ti ginetai edv
                found_edge = False
                if self.G.get_edge_data(edge[0], edge[1]):
                    rule.graph.add_node(edge[0])
                    rule.graph.add_node(edge[1])
                    predicates_to_be_removed = self.filter_cnt_ver_predicates(edge, same_county_node_versions)
                    rule.graph.add_edge(edge[0], edge[1], uris=list(set(self.G.get_edge_data(edge[0], edge[1])["uris"]) - set(predicates_to_be_removed)))
                    found_edge = True
                # inverted
                if self.G.get_edge_data(edge[1], edge[0]):
                    rule.graph.add_node(edge[0])
                    rule.graph.add_node(edge[1])
                    predicates_to_be_removed = self.filter_cnt_ver_predicates(edge, same_county_node_versions)
                    rule.graph.add_edge(edge[0], edge[1], uris_inverted=list(set(self.G.get_edge_data(edge[1], edge[0])["uris"]) - set(predicates_to_be_removed)))
                    found_edge = True
                print("(((((((((((((( Edges ))))))))))))))")
                print(rule.graph.edges(data=True))
                if not found_edge:
                    print("ERROR in rule graph:", rule.id, "->", edge[0], edge[1])
                    to_remove.add(rule)
        # remove invalid rules
        self.rules = {rule.id: rule for rule in self.rules.values() if rule not in to_remove}

        return to_remove


    def load_forbidden_queries(self, path):
        with open(path) as json_file:
            json_validity = json.load(json_file)["rules"]
            self.rules_with_valid_queries = set([query_json["rule"] for query_json in json_validity if
                                                 "valid" in query_json and query_json["valid"]])
        print("Valid rules:", self.rules_with_valid_queries)


# Adds to the query the triple with the geometry value if needed
    def add_geometry_values(self, query: SPARQLQueryGraph):
        new_edges = set()

        for node, node_type in copy.deepcopy(query.node_types).items():
            if node_type == "geo:Geometry":
                geo_value = 'GeoValue_' + node.split("_")[1]
                new_edge=(node, '<http://www.opengis.net/ont/geosparql#asWKT>', geo_value)
                query.other_nodes.append(geo_value)
                query.node_types[geo_value] = "WKT_Geo"
                query.edges.add(new_edge)

        for new_edge in new_edges:
            query.edges.add(new_edge)

        return query


    def add_properties(self, leaf_nodes, query: SPARQLQueryGraph):
        new_edges = set()

        for node, node_type in copy.deepcopy(query.node_types).items():
            if node_type in node_properties.keys():
                prop_pairs = node_properties[node_type]

                for p, o in prop_pairs:
                    prop_value = o + node.split("_")[1]
                    new_edge=(node, p, prop_value)
                    leaf_nodes.add(prop_value)
                    query.node_types[prop_value] = prop_value.split("_")[0]
                    query.edges.add(new_edge)

        for new_edge in new_edges:
            query.edges.add(new_edge)

        return query


    def generate_query(self, rule_graph_id, print_info: bool = False):
        sparql_query_graph = self.create_sparql_query_graph(rule_graph_id, print_info)
        sparql_query_graph = self.add_geometry_values(sparql_query_graph)
        if not self.online:
            sparql_query_graph = self.add_filters(sparql_query_graph)
        sparql_query_graph = self.replace_uri_nodes(sparql_query_graph)

        return sparql_query_graph


    def add_filters(self, sparql_query_graph):
        sparql_query_graph = add_geo_relation(sparql_query_graph)
        sparql_query_graph = add_temporal_filters(sparql_query_graph) 
        sparql_query_graph = add_spatial_filters(sparql_query_graph) 

        return sparql_query_graph


    def create_sparql_query_graph(self, rule_graph_id, print_info: bool = False):
        # Select rule and rule graph
        rule = self.rules[rule_graph_id]
        random_graph = copy.deepcopy(rule.graph)
        if print_info:
            print("random_graph:", random_graph)
        created_query = SPARQLQueryGraph(rule=rule, rule_graph=random_graph)
        nodes = set()

        for node in random_graph.nodes():
            nodes.add(node)
            node_type = node.split("_")[0]
            # if node_type=="tsnchange:Change":
            #     created_query.node_types[node] = node_type
            # else:
            created_query.node_types[node] = node_type
        # identify leaf nodes
        leaf_nodes = nodes.copy()
        in_nodes = set()
        out_nodes = set()
        edges = random_graph.edges()

        for edge in edges:
            in_nodes.add(edge[0])
            out_nodes.add(edge[1])

        for node in in_nodes:
            if node in out_nodes:
                leaf_nodes.remove(node)

        if created_query.rule.id in online_exceptions:
            county_names_df = pd.read_csv(counties_dates_path)
            # get a random row using sample()
            random_row = county_names_df.sample()

            # get the value of the 'name' column in the random row
            created_query.random_county = {"county":random_row['county'].values[0], "date":random_row['date'].values[0], "change_date":random_row['change_date'].values[0] }  #county,date,change_date

            # random_county_name = county_names_df["counties"].sample(n=1).values[0]
            print("RANDOM COUNTY NAME PICKED: "+ str(created_query.random_county))
        

        created_query.other_nodes = []
        created_query = self.add_properties(leaf_nodes, created_query)
        # randomly select select node
        if rule.id in select_exception_rule_ids:
            for n, t in created_query.node_types.items():      #always ask for geometries or events when it comes to some subgraphs
                if t=="geo:Geometry":
                    created_query.select_node = n
                if t=="sem:Event":
                    created_query.select_node = n
                    break
        else:
            a_select_nodes_t = allowed_select_node_types.copy()

            if rule.id in rules_with_start_end:
                a_select_nodes_t = a_select_nodes_t + ['xsd:date']
            elif rule.id in ["Q42"]:
                a_select_nodes_t.remove("hgc:State")
            elif rule.id in ["Q43"]:
                a_select_nodes_t.remove("hgc:County")
                
            created_query.select_node = random.choice(
            [node for node in list(leaf_nodes) + created_query.other_nodes if created_query.node_types[node] in a_select_nodes_t])
        created_query.select_node = created_query.select_node.split("_")[0]+"_0"
        # remaining leaf nodes are URI nodes
        created_query.uri_nodes = [node for node in leaf_nodes if node != created_query.select_node and created_query.node_types[node] not in not_allowed_uri_nodes]  #created_query.node_types[node] not in not_allowed_uri_nodes

        created_query.other_nodes = [node for node in nodes if node not in created_query.uri_nodes and node != created_query.select_node]

        if print_info:
            print("leaf_nodes", leaf_nodes)
            print("select_node", created_query.select_node)
            print("uri_nodes", created_query.uri_nodes)
            print("other_nodes", created_query.other_nodes)
        # for each edge, select one property
        same_county_node_versions=self.versions_of_same_county(rule)
        print(same_county_node_versions)
        print(random_graph.edges(data=True))
        print("PREDICATES")
        for edge in random_graph.edges(data=True):
            uris = []
            uris_inverted = []
            print(edge)

            if "uris" in edge[2].keys():
                uris = edge[2]["uris"]
            if "uris_inverted" in edge[2].keys():
                uris_inverted = edge[2]["uris_inverted"]  

            random_uri_index = random.randrange(len(uris) + len(uris_inverted))
            print("Uris: " + str(uris))
            print("Uris Inverted: " + str(uris_inverted))
            # print(uris_inverted)
            if len(uris) > 0 and random_uri_index <= len(uris):
                uri = random.choice(uris)
                created_query.edges.add((edge[0], uri, edge[1]))
            else:
                uri = random.choice(uris_inverted)
                created_query.edges.add((edge[1], uri, edge[0]))
        if print_info:
            print("edges", created_query.edges)

        return created_query
    
    @staticmethod
    def choose_random_change_type( results):
        filteres_results = [res for res in results if 'http://purl.org/net/tsnchange#Change' not in res.values()]
        
        if filteres_results != []:
            results = filteres_results
            
        return results

    # query results
    def replace_uri_nodes(self, sparql_query_graph: SPARQLQueryGraph):
        if sparql_query_graph.rule.id in online_exceptions:
            online = True
        else:
            online = False
        if online:

            counties, g_rel = sparql_query_graph.create_ask_online_query(self.prefix_dict)
            sparql_query_graph = add_spatial_filters(sparql_query_graph, g_rel)


            r_operator = random.choice([" < ", " > "])
            if r_operator == " < ":
                r_date = random_online_date(max(counties.iloc[0]["date"], counties.iloc[1]["date"]), r_operator)
            else:
                r_date = random_online_date(min(counties.iloc[0]["date"], counties.iloc[1]["date"]), r_operator)
            sparql_query_graph = add_temporal_filters(sparql_query_graph, r_date, r_operator) 
            types_names = {
                 "hgc:County":"county",
                 "ChangeType":"ch_type",
                 "hgc:State":"state",
            }

            for uri_node in sparql_query_graph.uri_nodes:
                n_type, n_num = uri_node.split("_")
                if n_type in types_names.keys():
                    sparql_query_graph.uri_node_uris[uri_node] = counties.iloc[int(n_num)][types_names[n_type]]
                elif n_type in types_for_temp_filters:
                    sparql_query_graph.uri_node_uris[uri_node] = r_date
            
            s_type, s_num = sparql_query_graph.select_node.split("_")
            if s_type in types_names.keys():
                sparql_query_graph.results.append({"answer":counties.iloc[int(s_num)][types_names[s_type]]})
            elif s_type in types_for_temp_filters:
                sparql_query_graph.results.append({"answer":counties.iloc[int(s_num)]["date"]})
            elif s_type == "geo:Geometry":
                sparql_query_graph.results.append({"answer":counties.iloc[int(s_num)]["geo"]})
            elif s_type == "sem:Event":
                sparql_query_graph.results.append({"answer":counties.iloc[int(s_num)]["event"]})

            return sparql_query_graph
        
        random_sparql_query, placeholders = sparql_query_graph.create_random_sparql_query(self.prefix_dict, online)
        #print the query that runs locally
        print("##############RANDOM SPARQL QUERY###################")
        print(random_sparql_query)
        jsonStr = jsons.dumps(sparql_query_graph)
        print(jsonStr)
        

        if random_sparql_query in self.queries_without_result:
            return None
        #Query with at least one result
        print("Run query locally..")
        # time.sleep(5)
        if online:
            #print(random_sparql_query)
            results = run_online(random_sparql_query, 1)
        else:
            results = query(random_sparql_query)["res"]    #RUN LOCAL KG
        print(results)

        if not results:
            self.queries_without_result.add(random_sparql_query)
            output_file = open("generated_queries/"+experiment_path+"_queries_without_local_results.json", "a")
            sparql_query_graph.sparql_query = random_sparql_query
            output_file.write(jsons.dumps(sparql_query_graph) + "\n")
            output_file.flush()
            output_file.close()
            return None
        print("RESULTS:")

        if "tsnchange:Change" in sparql_query_graph.node_types.values() and random.random() > 0.2:
            results = QueryGeneratorFromRules.choose_random_change_type(results)
            
        uris_combination = random.choice(results)
        print(uris_combination)
        print(sparql_query_graph.uri_nodes)
        print(placeholders)
        for uri_node in sparql_query_graph.uri_nodes:
            sparql_query_graph.uri_node_uris[uri_node] = uris_combination[placeholders[uri_node]]


        return sparql_query_graph
