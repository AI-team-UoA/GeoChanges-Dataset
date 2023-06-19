import networkx as nx
import itertools

from ontology_loader import get_ontology

G, data_type_properties, dependency_constraints = get_ontology(directed=False)


all_connected_subgraphs = []
# here we ask for all connected subgraphs that have at least 2 nodes AND have less nodes than the input graph
for nb_nodes in range(2, min(G.number_of_nodes(),6)):
    print("Subgraphs of size",nb_nodes)
    for SG in (G.subgraph(selected_nodes) for selected_nodes in itertools.combinations(G, nb_nodes)):
        if nx.is_connected(SG):

            # if a sub graph only contains, e.g., County_1, replace it with County_0
            node_dict={}
            for node in SG.nodes:
                node_id = node.split("_")[0]
                node_count = node.split("_")[1]
                if node_id not in node_dict:
                    node_dict[node_id] = []
                node_dict[node_id].append(int(node_count))

            valid = True
            for node_id, node_counts in node_dict.items():
                if len(node_counts) == 1 and 0 not in node_counts:
                    valid = False

            if valid:
                all_connected_subgraphs.append(SG)


all_connected_subgraphs_with_properties = []

graph_ids=set()
for subgraph in all_connected_subgraphs:

    # check dependencies
    invalid=False
    for a, b in dependency_constraints.items():
        if a in subgraph.nodes() and b not in subgraph.nodes():
            invalid = True
            break
    if invalid:
        continue

    node_ids=[]
    for a in subgraph.nodes():
        node_ids.append("-"+a.split("_")[0])
    for a in subgraph.edges():
        node_ids.append(a[0].split("_")[0]+"_"+"--"+a[1].split("_")[0])

    graph_id = "-".join(sorted(node_ids))

    if graph_id in graph_ids:
        continue
    graph_ids.add(graph_id)

    all_connected_subgraphs_with_properties.append(subgraph)

for subgraph in all_connected_subgraphs_with_properties:

    print(subgraph)
    for node in subgraph.nodes():
        print(" ",node)
    for edge in subgraph.edges(data=True):
        print(" ",edge[0],"->",edge[1],"("+str(G.get_edge_data(edge[0],edge[1])["uris"])+")")
    print("")