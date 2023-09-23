import csv
from collections import OrderedDict

from model.rule import Rule

from configuration import question_template_path, rules_path

# target_types_dict = {"DATE": TIME.Interval, "COUNTY": TSN.County, "GEOMETRY": GEO.Geometry, "CHANGE": TSN.Change,
#                     "EVENT": SEM.Event, "STATE": TSN.State}
target_types_dict = {"DATE": "time:Interval", "COUNTY": "tsnchange:County", "GEOMETRY": "Geo:Geometry",
                     "CHANGE": "tsnchange:Change",
                     "EVENT": "sem:Event", "STATE": "tsnchange:State"}

# Loads the rules from the given file
# Returns a dictionary with Rule items
def get_rules():
    tsv_file = open(rules_path)
    question_templates_file = open(question_template_path)

    read_tsv = csv.reader(tsv_file, delimiter="\t")
    question_templates_csv = csv.reader(question_templates_file, delimiter=",")

    headers = next(read_tsv)
    rule_graph = None
    rule_graphs = OrderedDict()

    for row in read_tsv:
        if row[0]:
            rule_id = row[0]
            rule_graph = Rule(rule_id)
            rule_graphs[rule_id] = rule_graph
            if len(row) > 7 and row[7]:
                rule_graph.rule1 = row[7]
            if len(row) > 8 and row[8]:
                rule_graph.rule2 = row[8]

        path = []
        rule_graph.paths.append(path)
        for i in range(1, min(6, len(row))):
            if len(row) > i and row[i]:
                path.append(row[i])

    next(question_templates_csv, None)  # skip header
    # add target types (what we ask for) to each rule
    for question_template in question_templates_csv:
        rule_id = question_template[0]
        if rule_id not in rule_graphs.keys():
            continue
        rule_graph = rule_graphs[rule_id]
        if question_template[1] in target_types_dict:
            rule_graph.target_types.add(target_types_dict[question_template[1]])
        else:
            pass
            # print("missing target type:", question_template[1])

    rule_graphs_filtered = {}
    for rule_graph in rule_graphs.values():

        if len(rule_graph.target_types) == 0:
            print("Error with", rule_graph.id, "(no query or no valid target types in the question templates)")
            continue

        rule_graphs_filtered[rule_graph.id] = rule_graph

        rule_graph.create_edges()
        rule_graph.create_query()

    return rule_graphs_filtered


