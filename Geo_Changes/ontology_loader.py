import copy
import os
import random

import networkx as nx
from rdflib import Graph, OWL, RDF, BNode, TIME, Namespace

from namespaces import SEM, TSN, TSE, GEO, TSNCHANGE, HCB


class LabelGenerator:

    def __init__(self):
        self.literal_idx = 1

    def get_label(self, g, uri, is_prop: bool):
        suffix = ""
        if not is_prop:
            suffix = "_0"
        # if uri == RDFS.Literal:
        # uri += str(self.literal_idx)
        # self.literal_idx += 1
        uri = uri.replace("https", "http")
        for ns_prefix, namespace in g.namespaces():
            namespace = namespace.replace("https", "http")
            if uri.startswith(namespace):
                return uri.replace(namespace, ns_prefix + ":") + suffix
        return uri + suffix


def get_default_graph():
    g = Graph()

    TIME._NS = Namespace("http://www.w3.org/2006/time#")

    g.bind("tse", TSE)
    g.bind("sem", SEM)
    g.bind("tsn", TSN)
    g.bind("tsnchange", TSNCHANGE)
    g.bind("geo", GEO)
    g.bind("time", TIME)
    g.bind("rdf", RDF)
    g.bind("hcb", HCB)

    prefixes = {}
    for prefix, namespace in g.namespace_manager.store.namespaces():
        prefixes[prefix] = namespace

    return g, prefixes


def load_graph():
    g, _ = get_default_graph()
    file_name = 'resources/ontology/HistoricGeoChanges_upper_with_states2.owl'

    # load RDF dumps
    print("Parse", file_name)
    g.parse(file_name)
    return g


def get_random_instance(class_instances: dict, rdf_class: str):
    print(rdf_class)
    print(class_instances.keys())

    print(len(class_instances[rdf_class]))
    return random.choice(class_instances[rdf_class])


def get_ontology(directed=True):
    g = load_graph()
    print("Graph Building...")
    lbl_gen = LabelGenerator()

    if directed:
        G = nx.DiGraph()
    else:
        G = nx.Graph()

    for s, _, _ in g.triples((None, RDF.type, OWL.Class)):
        if type(s) != BNode:
            G.add_node(lbl_gen.get_label(g, s, False))

    query = "SELECT ?p ?range ?domain WHERE { ?p rdf:type* owl:ObjectProperty. ?p rdfs:range/(owl:unionOf/rdf:rest*/rdf:first)* ?range ; rdfs:domain/(owl:unionOf/rdf:rest*/rdf:first)* ?domain . }"
    qres = g.query(query)
    for row in qres:
        domain_uri = row.domain
        range_uri = row.range
        if type(domain_uri) != BNode and type(range_uri) != BNode:
            src = lbl_gen.get_label(g, domain_uri, False)
            print(src)
            dst = lbl_gen.get_label(g, range_uri, False)
            uris = []
            if ((src, dst) in G.edges):
                uris = G.get_edge_data(src, dst)["uris"]
            # print("LAB:", row.p, lbl_gen.get_label(g, row.p, True))
            uris.append(lbl_gen.get_label(g, row.p, True))
            if ((src == "hcb:CountyVersion_0" and dst == "hcb:StateVersion_0") or (dst == "hcb:CountyVersion_0" and src == "hcb:StateVersion_0")) and "sem:geospatialProperty" in uris:
                uris.remove("sem:geospatialProperty")
            print(src, " -- ",dst," -- ", uris)
            G.add_edge(src, dst, uris=uris)

    data_type_properties = {}
    query = """
            SELECT DISTINCT ?p ?range ?domain WHERE {
                 ?p rdf:type* owl:DatatypeProperty.
                 ?p rdfs:range/(owl:unionOf/rdf:rest*/rdf:first)* ?range ; rdfs:domain/(owl:unionOf/rdf:rest*/rdf:first)* ?domain .
             }
            """
    qres = g.query(query)

    for row in qres:
        # print(row)
        domain_uri = row.domain
        range_uri = row.range
        if type(domain_uri) != BNode and type(range_uri) != BNode:
            domain_uri_lbl = lbl_gen.get_label(g, domain_uri, False).split("_")[0]
            if domain_uri_lbl not in data_type_properties:
                data_type_properties[domain_uri_lbl] = []
            data_type_properties[domain_uri_lbl].append(lbl_gen.get_label(g, row.p, True))

    dependencies = {TIME.Interval: HCB.CountyVersion, GEO.Geometry: HCB.CountyVersion}
    groups = [[TIME.Interval, GEO.Geometry, HCB.CountyVersion], [SEM.Event], [HCB.State],
              [HCB.County], [TSNCHANGE.Change], [HCB.State], [HCB.StateVersion]]
    number_of_repetitions = 2
    dependency_constraints = dict()

    for repetition in [0, number_of_repetitions - 1]:
        for a, b in dependencies.items():
            dependency_constraints[
                lbl_gen.get_label(g, a, False).replace("_0", "_" + str(repetition))] = lbl_gen.get_label(g, b,
                                                                                                         False).replace(
                "_0", "_" + str(repetition))

    for group in groups:
        for repetition in [1, number_of_repetitions - 1]:
            # duplicate nodes
            group_new = dict()
            for node in group:
                node_lbl = lbl_gen.get_label(g, node, False)
                new_node = node_lbl.replace("_0", "_" + str(repetition))
                group_new[node_lbl] = new_node
                G.add_node(new_node)
            old_edges = copy.deepcopy(G.edges())
            for edge in old_edges:
                new_src = group_new.get(edge[0])
                new_dst = group_new.get(edge[1])
                if new_src is None and new_dst is None:
                    continue
                if new_src is None:
                    new_src = edge[0]
                if new_dst is None:
                    new_dst = edge[1]
                G.add_edge(new_src, new_dst, uris=G.get_edge_data(edge[0], edge[1])["uris"])
    # Replace self loops
    old_G = G.copy()
    
    for edge in old_G.edges:
        if edge[0] == edge[1]:
            for repetition1 in [0, number_of_repetitions - 1]:
                for repetition2 in [0, number_of_repetitions - 1]:
                    if repetition1 == repetition2:
                        continue
                    G.add_edge(edge[0][:-1] + str(repetition1), edge[1][:-1] + str(repetition2),
                               uris=old_G.get_edge_data(edge[0], edge[1])["uris"])
            G.remove_edge(edge[0], edge[1])

    return G, data_type_properties, dependency_constraints
# nx.draw_circular(G, with_labels = True)

# plt.show(figsize=(300,300))
