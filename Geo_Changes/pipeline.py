import ontology_loader
import jsons
from model.rule import Rule
from endpoint_access import run_query_online
from query_creator_from_rules import QueryGeneratorFromRules
import time
import random
from model.sparql_query_graph import SPARQLQueryGraph
from configuration import invalid_rules_path, online_exceptions, experiment_path 


number_of_queries_to_generate = 2000

online_run = False

def create_query(query_rule: Rule):
    created_query = query_generator.generate_query(query_rule.id, print_info=True)
    if not created_query:
        print("=> No results.")
        return None
    else:
        print("=> Results.")
    created_query.sparql_query = created_query.create_sparql_query(prefix_dict)

    return created_query


_, prefix_dict = ontology_loader.get_default_graph()
query_generator = QueryGeneratorFromRules(online = online_run)
query_generator.load_forbidden_queries(path = invalid_rules_path)
query_generator.create_rule_graphs()

# print("(((((((((((((( Edges ))))))))))))))")
# print(query_generator.rules["Q34"].graph.edges())

rules_count = {}
rules_count_without_results = {}
online_rules_count_without_results = {}

for rule in query_generator.rules.values():
    rules_count[rule.id] = 0
    rules_count_without_results[rule.id] = 0
    online_rules_count_without_results[rule.id] = 0

# Load the files for results
f_with_results = open("generated_queries/"+experiment_path+"_queries_dataset.json", "w")
f_without_results = open("generated_queries/"+experiment_path+"_queries_without_results.json", "w")

# Counters for produced queries
total_query_count_with_results = 0
total_query_count_without_results = 0
found_result = False
done = False

# Start counting time
start = time.time()
number_of_queries_per_rule = 5 #int(number_of_queries_to_generate/(len(query_generator.rules.values())-len(online_exceptions)))
for rule in query_generator.rules.values():
    # if online_run:
    #     if rule.id not in online_exceptions:   # ['Q1', 'Q3', 'Q4', 'Q7', 'Q12', 'Q13', 'Q18', 'Q22', 'Q23', 'Q26', 'Q28', 'Q40', 'Q42', 'Q43', 'Q45', 'Q46']
    #             continue
    # else:
    #     if rule.id in online_exceptions:   # ['Q1', 'Q3', 'Q4', 'Q7', 'Q12', 'Q13', 'Q18', 'Q22', 'Q23', 'Q26', 'Q28', 'Q40', 'Q42', 'Q43', 'Q45', 'Q46']
    #             continue

    # if rule.id not in ["Q13"]:   # ['Q1', 'Q3', 'Q4', 'Q7', 'Q12', 'Q13', 'Q18', 'Q22', 'Q23', 'Q26', 'Q28', 'Q40', 'Q42', 'Q43', 'Q45', 'Q46']
    #             continue
    while rules_count[rule.id] < number_of_queries_per_rule:
        
        print("========================================")
        print("Rule", rule.id)
        query = create_query(rule)
        if query:
            if not (online_run and query.results):
                r = run_query_online(query, 1)  # runs the created query against the online endpoint to get online results
            else:
                 print(query.sparql_query)
            if not query.results:
                online_rules_count_without_results[rule.id]+=1
                output_file = f_without_results
                total_query_count_without_results += 1
            else:
                output_file = f_with_results
                rules_count[rule.id] = rules_count[rule.id] + 1
                number_of_queries_to_generate -= 1
                total_query_count_with_results += 1
            # found_result = True
        else:
            output_file = f_without_results
            rules_count_without_results[rule.id] = rules_count_without_results[rule.id] + 1
            total_query_count_without_results += 1
        
        print(" with results:", rules_count)
        print(" without results:", rules_count_without_results)
        print(" without online results:", online_rules_count_without_results)
        print("rule", rule.id, "->", rules_count[rule.id], "/", rules_count_without_results[rule.id], " - total:",
        total_query_count_with_results, "/", total_query_count_without_results, ")")
        if not query:
            continue
        jsonStr = jsons.dumps(query)
        # Write results
        output_file.write(jsonStr + "\n")
        output_file.flush()
        




# while len(query_generator.rules.values()) > 0 and (not number_of_queries_to_generate or number_of_queries_to_generate > 0):
#     to_remove = []

#     for rule in query_generator.rules.values():
#         if rule.id in online_exceptions:# ["SQ22", "SQ28"]:#["Q22", "Q28"] :  #["Q26", "Q13", "Q23", "Q28"] :  #["Q22", "Q28"] # not in ["Q1","Q3","Q4","Q7", "Q12", "Q13"] :  # Q40 #Q17 #Q34
#             continue
#         print("========================================")
#         print("Rule", rule.id)
#         query = create_query(rule)
#         if query:
#             r = run_query_online(query, 1)  # runs the created query against the online endpoint to get online results
#             if not query.results:
#                 online_rules_count_without_results[rule.id]+=1
#                 output_file = f_without_results
#                 total_query_count_without_results += 1
#             else:
#                 output_file = f_with_results
#                 rules_count[rule.id] = rules_count[rule.id] + 1
#                 number_of_queries_to_generate -= 1
#                 total_query_count_with_results += 1
#             # found_result = True
#         else:
#             output_file = f_without_results
#             rules_count_without_results[rule.id] = rules_count_without_results[rule.id] + 1
#             total_query_count_without_results += 1
        
#         print(" with results:", rules_count)
#         print(" without results:", rules_count_without_results)
#         print(" without online results:", online_rules_count_without_results)
#         print("rule", rule.id, "->", rules_count[rule.id], "/", rules_count_without_results[rule.id], " - total:",
#         total_query_count_with_results, "/", total_query_count_without_results, ")")
#         if not query:
#             continue
#         jsonStr = jsons.dumps(query)
#         # Write results
#         output_file.write(jsonStr + "\n")
#         output_file.flush()
#         # Check if we exceed rule's max queries
#         if rules_count[rule.id] >= number_of_queries_per_rule:
#             to_remove.append(rule)
#         if number_of_queries_to_generate <= 0:
#             break
#     if number_of_queries_to_generate <= 0:
#         break
#     # Remove the rules on dictionary in order to not produce more out of them
#     if len(to_remove) > 0:
#         print("Done:", to_remove)
#     query_generator.rules = {rule.id: rule for rule in query_generator.rules.values() if rule not in to_remove}

f_with_results.close()
f_without_results.close()
# Print time
print("Total time: ", time.time()-start)
