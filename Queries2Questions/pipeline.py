import random
import pandas as pd
import types
import re
from dateutil.parser import parse
from QGenerator import question_template_picker, question_production
from query_reader import queries_data
# from unique_templates import unique_templates
from grammar_corrector import grammar_correction
from endpoint_access import run_online

def sparql_query_corrector(df):
    def replace_not_used_uris(row):
        # print( row["Instances"])
        for v, u in row["Instances"].items():
            if u not in row["Uris_match"].values():
                placeholder = "?" + v.split(":")[-1]
                row["SparqlQuery"] = row["SparqlQuery"].replace("<"+u+">", placeholder)
        return row

    df= df.apply(lambda row: replace_not_used_uris(row),axis=1)
    return df

queries_file_path="./resources/queries_with_results_200.json"

question_templates_path="./resources/Checked_Question_Templates.csv"

data = pd.read_json(queries_file_path, lines=True)
pd.set_option('display.max_columns', None)
# print(data.head())

q_d=queries_data(queries_file_path)
queries_df=q_d.extract_data()
# queries_df = queries_df[queries_df["Q_id"] == "Q46"]
queries_df["Uris_match"]=[{} for _ in range(len(queries_df))]
q_t_p=question_template_picker(question_templates_path)
print(queries_df.head())
df_question_templates=q_t_p.question_template_production(queries_df)
#leave out every query that does not even one question template
# df_question_templates=df_question_templates[df_question_templates.astype(str)["Questions_templates"]!='[]']
print(df_question_templates.head())
q_p=question_production(df_question_templates)
question_df=q_p.produce_questions()

question_df = sparql_query_corrector(question_df)
question_df["Corrected Questions"]= question_df.apply(lambda row: grammar_correction(row["Questions"]), axis=1 )

# Take the answers
question_df["answers"]= question_df.apply(lambda row: run_online(row["SparqlQuery"], 1), axis=1 )

# Save results
question_df.to_csv("./generated_questions/new_generated_questions200.csv")
