import random
import pandas as pd
import types
import re
from dateutil.parser import parse
from QGenerator import question_template_picker, question_production
from query_reader import queries_data
from tqdm import tqdm
# from unique_templates import unique_templates
from grammar_corrector import grammar_correction
from endpoint_access import run_online

tqdm.pandas()

def df_clear(data):
    pattern = '|'.join(map(re.escape, ['tsnchange:Fusion', 'tsnchange:Merge', 'tsnchange:Integration']))
    # print(data.head())
    # print(data.shape)
    data = data[~(data["SparqlQuery"].str.contains(pattern)) ]
    data = data.drop_duplicates(subset='SparqlQuery').reset_index(drop=True)
    return data

def remove_date_filters(row):
    if "DATE_NAME" not in row["Uris_match"].keys():
        for f in row["Filters"]:
            if f["f_type"] == "temporal":
                input_str = row["SparqlQuery"]
                d_val = f["v2"]
                pattern = re.compile(f".*{re.escape(d_val)}.*\n")
                # matching_lines = pattern.findall(input_str)
    
                # Remove matching lines from the input string
                result_string = re.sub(pattern, '', input_str)
                row["SparqlQuery"] = result_string
    return row

def remove_change_type(row):
    change_types = ["tsnchange:Contraction","tsnchange:NameChange","tsnchange:Appearance","tsnchange:Extraction","tsnchange:Expansion", "tsnchange:Merge"]
    if "CHANGE_TYPE" not in row["Uris_match"].keys():
        for ct in change_types:
            row["SparqlQuery"] = row["SparqlQuery"].replace(ct, "tsnchange:Change")
    return row

def sparql_query_corrector(df):
    def replace_not_used_uris(row):
        # print( row["Instances"])
        for v, u in row["Instances"].items():
            if u not in row["Uris_match"].values():
                placeholder = "?" + v.split(":")[-1]
                row["SparqlQuery"] = row["SparqlQuery"].replace("<"+u+">", placeholder)
        row = remove_date_filters(row)
        row = remove_change_type(row)
        return row

    df= df.apply(lambda row: replace_not_used_uris(row),axis=1)
    return df

queries_file_path="./resources/Total_final_cnt_stt_dataset.json"
output_file = "./generated_questions/Total_final_cnt_stt_queries_questions.csv"


question_templates_path="./resources/States_Counties_Question_Templates.csv"



# data = pd.read_json(queries_file_path, lines=True)
# data = data[:100]
pd.set_option('display.max_columns', None)
# print(data.head())

q_d = queries_data(queries_file_path)
queries_df = q_d.extract_data()
# queries_df = queries_df[queries_df["Q_id"] == "Q46"]
queries_df["Uris_match"]=[{} for _ in range(len(queries_df))]
q_t_p = question_template_picker(question_templates_path)
print(queries_df.head())
df_question_templates = q_t_p.question_template_production(queries_df)
# leave out every query that does not even one question template
# df_question_templates=df_question_templates[df_question_templates.astype(str)["Questions_templates"]!='[]'].reset_index()
print(df_question_templates.head())
q_p=question_production(df_question_templates)
question_df = q_p.produce_questions()
question_df = df_clear(question_df)
question_df.to_csv(output_file)

print("Making corrections...")
question_df = sparql_query_corrector(question_df)
question_df["Corrected Questions"]= question_df.progress_apply(lambda row: grammar_correction(row["Questions"]), axis=1 )
question_df.to_csv(output_file)

# Take the answers
question_df["answers"]= question_df.progress_apply(lambda row: run_online(row["SparqlQuery"], 1) if "answer" not in row["Answer"][0].keys() else row["Answer"][0]["answer"], axis=1 )
question_df.to_csv(output_file)
