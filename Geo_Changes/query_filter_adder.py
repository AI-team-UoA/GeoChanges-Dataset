import copy
import random
import time
from datetime import datetime as dt
import datetime

from rdflib import Namespace

from model.sparql_query_graph import SPARQLQueryGraph

from configuration import spatial_filter_relations, spatial_materialised_properties, change_subclasses, node_properties, rules_with_start_end, spatial_filter_relations, types_for_temp_filters

EX = Namespace("https://www.example.org/")


temporal_filter_relations = [EX.after]

FILTER_TYPE_SPATIAL = "spatial"
FILTER_TYPE_TEMPORAL = "temporal"
FILTER_CARDINALITY_UNARY = "unary"
FILTER_CARDINALITY_BINARY = "binary"

GEOSPATIAL_PROPERTY = "sem:geospatialProperty"
TEMPORAL_PROPERTY = "sem:temporalProperty"

MIN_YEAR = "1629-01-01"
MAX_YEAR = "2000-01-01"



def add_interval_values(query: SPARQLQueryGraph, new_edges, interval_index, interval):
    
    random_par=random.random() if query.rule.id in rules_with_start_end else 0

    if random_par <.5:
        interval_start = 'IntervalStart_' + str(interval_index)
        interval_value = 'IntervalStartValue_' + str(interval_index)
        new_edges.add((interval, 'time:hasBeginning', interval_start))
        new_edges.add((interval_start, 'time:inXSDDate', interval_value))
        query.other_nodes.append(interval_start)
        query.node_types[interval_start] = 'time:Instant'
        query.other_nodes.append(interval_value)
        query.node_types[interval_value] = 'xsd:date'
    else:
        interval_end = 'IntervalEnd_' + str(interval_index)
        interval_value = 'IntervalEndValue_' + str(interval_index)
        new_edges.add((interval, 'time:hasEnd', interval_end))
        new_edges.add((interval_end, 'time:inXSDDate', interval_value))
        query.other_nodes.append(interval_end)
        query.node_types[interval_end] = 'time:Instant'
        query.other_nodes.append(interval_value)
        query.node_types[interval_value] = 'xsd:date'

    return interval_value



# Picks a random materialized geometry between 2 county versions
def add_geo_relation(query: SPARQLQueryGraph):
    new_edges = set()
    for edge in query.edges:
        if edge[1] == GEOSPATIAL_PROPERTY:
            geo_property = random.choice(spatial_materialised_properties)
            new_edges.add((edge[0], geo_property, edge[2]))
            query.county_relation = geo_property
            # only compare geometries when both county versions/state versions existed at the same time
            # new_edges.add((edge[0], "tse:coexisted", edge[2])) All materialized relations refer to the same time period
        else:
            new_edges.add(edge)
    query.edges = new_edges
    return query


def str_time_prop(start, end, time_format, prop):
    stime = time.mktime(time.strptime(start, time_format))
    etime = time.mktime(time.strptime(end, time_format))

    ptime = stime + prop * (etime - stime)

    return time.strftime(time_format, time.localtime(ptime))


def random_date():
    start_date = dt.strptime(MIN_YEAR, '%Y-%m-%d')
    end_date   = dt.strptime(MAX_YEAR, '%Y-%m-%d')
    num_days   = (end_date - start_date).days
    rand_days   = random.randint(1, num_days)
    random_date = start_date + datetime.timedelta(days=rand_days)
    return str(random_date.date())


def random_online_date(random_d, rand_operator):
    start_date = dt.strptime(MIN_YEAR, '%Y-%m-%d')
    random_date = dt.strptime(random_d.split("^^")[0].replace("\"", ""), '%Y-%m-%d')
    end_date   = dt.strptime(MAX_YEAR, '%Y-%m-%d')
    if rand_operator == " > ":
        num_days   = (random_date - start_date).days
        rand_days   = random.randint(1, num_days)
        random_date = random_date - datetime.timedelta(days=rand_days)
    elif rand_operator == " < ":
        num_days   = (end_date - random_date).days
        rand_days   = random.randint(1, num_days)
        random_date = random_date + datetime.timedelta(days=rand_days)
    return str(random_date.date())


def add_temporal_filters(query: SPARQLQueryGraph):
    # for each interval: in 50% of the cases, add random temporal condition (e.g., start date before 1950)
    new_edges = set()
    
    relation_operators=[" < ", " > "]    #" = "
    rand_operator=random.choice(relation_operators)
    if query.random_county:
        if "ChangeDate" in query.node_types.values():
            random_d = random_online_date(query.random_county["change_date"],rand_operator)
        else:
            random_d = random_online_date(query.random_county["date"],rand_operator)
            
    else:
        random_d = random_date()
        # random_change_d = random_date()
    print("random date:", random_d)
    interval_index=0
    #continue # do not include any information about dates
    if query.node_types[query.select_node]  in types_for_temp_filters:
        return query
    for node, node_type in copy.deepcopy(query.node_types).items():
        if node_type in types_for_temp_filters: # 'time:Interval' or node_type == "ChangeDate":  # skip the case where the select node is time:Interval. We ask about this node we do not want to give extra information
            # if node == query.select_node:
            #     return query
                #continue # do not include any information about dates
            if random.random() < 1: #probability to add temporal filter
                # get interval values
                if node_type == "ChangeDate" or node_type == "xsd:date":
                    interval1_value = node
                else:
                    interval1_value = add_interval_values(query, new_edges, interval_index, node)
                    interval_index+=1
                # if node_type == "ChangeDate":
                #     random_d = random_change_d
                query.filters.add((interval1_value + rand_operator + '"' + random_d + '"^^xsd:date', interval1_value, rand_operator, random_d, "temporal"))

    for new_edge in new_edges:
        query.edges.add(new_edge)

    return query

def add_spatial_filters(query: SPARQLQueryGraph):
    relation_operators= spatial_filter_relations    #" = "
    rand_operator=random.choice(relation_operators)
    geo_nodes_list=[]
    for node, node_type in copy.deepcopy(query.node_types).items():
        if node_type == 'WKT_Geo':  # skip the case where the select node is time:Interval. We ask about this node we do not want to give extra information
            geo_nodes_list.append(node)
    
    if len(geo_nodes_list)<=1:
        return query
    elif len(geo_nodes_list)==2:
        query.filters.add(( rand_operator + "(" + geo_nodes_list[0]  + ", " + geo_nodes_list[1] + " )", geo_nodes_list[0], rand_operator, geo_nodes_list[1], "spatial"))


    return query

