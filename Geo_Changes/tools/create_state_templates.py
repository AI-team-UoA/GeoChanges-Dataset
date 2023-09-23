import pandas as pd
import ast

Q_id_list = ["Q1", "Q2", "Q3", "Q4", "Q7", "Q12", "Q13", "Q17", "Q18", "Q22", "Q23", "Q24", "Q26", "Q28", "Q34", "Q36", "Q37"]
counties_to_states = {"county":"state", "County": "State", "counties":"states", "Counties": "States", "COUNTY_NAME":"STATE_NAME"}

def change_Q_type(row):
    return "S"+row["Q_type"]


def change_answer(row):
    if row["Answer"] == "COUNTY":
        return "STATE"
    else:
        return row["Answer"]


def change_template(row):
    #quest_list = row["Questions Templates"]
    # Converting string to list
    quest_list = ast.literal_eval(row["Questions Templates"])
    state_quests = []
    for q in quest_list:
        new_q = q
        for k, v in counties_to_states.items():
            new_q = new_q.replace(k, v)
        state_quests.append(new_q)
            
    return state_quests

temp_df = pd.read_csv("./resources/Checked_Question_Templates.csv")
temp_df = temp_df[temp_df["Q_type"].isin(Q_id_list)]
temp_df["Questions Templates"] = temp_df.apply(lambda row: change_template(row), axis=1)
temp_df["Q_type"] = temp_df.apply(lambda row: change_Q_type(row), axis=1)
temp_df["Answer"] = temp_df.apply(lambda row: change_answer(row), axis=1)


for column in ["COUNTY_NAME",  "COUNTY_NAME_2", "STATE_NAME",  "STATE_NAME_2"]:
    temp_df[column] = temp_df["Questions Templates"].apply(lambda row: column in row[0])

temp_df.to_csv("./state_question_templates.csv", index=False )
print(temp_df.head())