import networkx as nx



test_graph = nx.DiGraph() 

test_graph.add_node(0)
test_graph.add_node(1)
test_graph.add_edges_from([(0, 1)], uris="normal")
test_graph.add_edges_from([(0, 1)], uris_inverted="normal_inverted")
# test_graph.add_node(1)
test_graph.add_node(2)
test_graph.add_edges_from([(2, 1)], uris="normal")
test_graph.add_node(3)
test_graph.add_edges_from([(3, 4)], uris="normal")
print(test_graph.edges(data=True))

ex_list=[["one", "two"], ["three", "four"]]

for l in ex_list:
    l[1]="hello"
    
print(ex_list)