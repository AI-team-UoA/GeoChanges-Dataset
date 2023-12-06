import pandas as pd
import numpy as np
import math
import random
import string
import re
import types
from dateutil.parser import parse
from query_reader import queries_data
from random_date_temp import date_string
#  {"original":, "gerund":, "past":, }
#  {"original":, "gerund":, "noun":, "past":, }
synonyms = {
"geo:sfIntersects" : [{"original": "intersect", "gerund":"intersecting", "past":"intersected" }, {"original": "cross", "gerund":"crossing", "past":"crossed" }],
#"geo:sfCoverdBy": [],
"geo:sfContains": [{"original": "contain", "gerund":"containing", "past":"contained" }, {"original": "include", "gerund":"including", "past":"included" }],
"geo:sfCovers": [{"original": "cover", "gerund":"covering", "past":"covered" }, {"original": "overlay", "gerund":"overlaying", "past":"overlaid" }],
"geo:sfTouches": [{"original": "border", "gerund":"bordering", "past":"bordered" }, {"original": "neighbor", "gerund":"neighboring", "past":"neighbored" }],
"geo:sfOverlaps": [{"original": "overlap", "gerund":"overlapping", "past":"overlapped" }],
"geo:sfWithin": [{"original": "is within", "gerund":"being within", "past":"was within" }, {"original": "is inside", "gerund":"being inside", "past":"was inside" }],
'strdf:right': [{"original":"east of"}], 
'strdf:below': [{"original":"south of"}], 
'strdf:above': [{"original":"north of"}], 
'strdf:left': [{"original":"west of"}],
"http://purl.org/net/tsnchange#Contraction": [{"original":"contract", "gerund":"contracting", "noun":"contraction", "past":"contracted"}],
"http://purl.org/net/tsnchange#NameChange": [{"original":"change in name", "gerund":"renaming", "noun":"renaming", "past":"was renamed"}],
"http://purl.org/net/tsnchange#Appearance": [{"original":"change in appearance", "gerund":"appearance changing", "noun":"changing in appearance", "past":"changed in appearance"}],
"http://purl.org/net/tsnchange#Extraction": [{"original":"extract", "gerund":"extracting", "noun":"extraction", "past":"extracted"}],
"http://purl.org/net/tsnchange#Expansion": [{"original":"expand", "gerund":"expanding", "noun":"expansion", "past":"expanded"}],
"http://purl.org/net/tsnchange#Change": [{"original":"change", "gerund":"changing", "noun":"change", "past":"changed"}],
}


Dict_query_type_mapping={
    "hcb:County": "COUNTY",
    "time:Interval": "DATE",
    "geo:Geometry": "GEOMETRY",
    "tsnchange:Change": "CHANGE",
    "sem:Event": "EVENT",
    'hcb:State': "STATE",
    "ChangeType": "CHANGE",
    "ChangeDate": "DATE",
    "area": "AREA",
    "xsd:date": "DATE"
}

Dict_instances_type_mapping={
    "hcb:County":"COUNTY_NAME",
    "time:Interval":"DATE_NAME",
    'hcb:State':"STATE_NAME",
    "ChangeType":"CHANGE_TYPE",
    "GEOSPATIAL":"COUNTY_RELATION",
    #"COUNTY_NAME_2":"hcb:County",
}

Condition_Names=["COUNTY_NAME", "COUNTY_RELATION", "CHANGE_TYPE", "COUNTY_NAME_2", "STATE_NAME", "STATE_NAME_2"]

types_to_uris={
    "COUNTY_NAME":"/",
    "STATE_NAME":'/',
    "CHANGE_TYPE":"#",
    "COUNTY_NAME_2":"/",
     "STATE_NAME_2":'/',
    "COUNTY_RELATION":"sf"
}


class question_template_picker:
    def __init__(self, question_templates):

        self.unique_templates = pd.read_csv(question_templates)
        # self.unique_templates = self.question_templates.groupby(["Q_type","Answer", "COUNTY_NAME", "DATE_NAME","COUNTY_RELATION", "GEO_RELATION",
        #                                                 "CHANGE_TYPE", "COUNTY_NAME_2","STATE_NAME","TEMP_RELATION", "PREDICATE"]).agg({'Questions Template': list}).reset_index()

    def predicate_filtering(self, questions_temp, row):
        if row["Q_id"] in ["Q7", "Q37", "Q28", "SQ7", "SQ37", "SQ28"]: 
            if "tsnchange:countyVersionAfter" in row["Predicates"] or "tsnchange:stateVersionAfter" in row["Predicates"]:
                questions_temp=questions_temp[questions_temp["PREDICATE"]=="AFTER"]
            elif "tsnchange:countyVersionBefore" in row["Predicates"] or "tsnchange:stateVersionBefore" in row["Predicates"]:
                questions_temp=questions_temp[questions_temp["PREDICATE"]=="BEFORE"]
            # else:
            #     questions_temp=questions_temp[questions_temp["PREDICATE"]=="BOTH"]
        elif row["Q_id"] in ["Q1", "SQ1"]: 
            if "time:hasBeginning" in row["Predicates"]:
                questions_temp=questions_temp[questions_temp["PREDICATE"]=="start_date"]
            elif "time:hasEnd" in row["Predicates"]:
                questions_temp=questions_temp[questions_temp["PREDICATE"]=="end_date"]

        return questions_temp

    def filtering_question_templates(self, questions_temp , row):
        f_list= row['Filters']
        print(f_list)
        used_the_date = False
        # used_geometry = False

        for f in f_list:
            if f["f_type"] == "temporal" and questions_temp["DATE_NAME"]:
                if used_the_date:
                    continue
                used_the_date = True
                # print("MPHKA")
                # questions_temp = questions_temp[questions_temp["DATE_NAME"]]
                date_str = date_string(str(f["v2"]))
                if f["operator"] == "<":
                    row["Uris_match"]["DATE_NAME"]="before " + date_str
                    # print(row["Uris_match"])
                elif f["operator"] == ">":
                    row["Uris_match"]["DATE_NAME"]="after " + date_str
                    # print(row["Uris_match"])
                elif f["operator"] == "=":
                    row["Uris_match"]["DATE_NAME"] = "in " + date_str
                    # print(row["Uris_match"])
            elif f["f_type"] =="spatial" and questions_temp["GEO_RELATION"]:
                # used_geometry = True
                # questions_temp = questions_temp[questions_temp["GEO_RELATION"]]
                row["Uris_match"]["GEO_RELATION"] = f["operator"]

        # if used_the_date == False:
        #     questions_temp = questions_temp[questions_temp["DATE_NAME"]==False]
        # if used_geometry == False:
        #     questions_temp = questions_temp[questions_temp["GEO_RELATION"]==False]
        print(row["Uris_match"])
        return questions_temp  

    def template_picker(self, row):
        # print(row)
        questions_temp1 = self.unique_templates[self.unique_templates["Q_type"] == row["Q_id"]]
        # if row["Q_id"]!="Q7":
        #     return []
        questions_temp2 = questions_temp1[questions_temp1["Answer"] == Dict_query_type_mapping[row["Select_type"]]]
        questions_temp = self.predicate_filtering(questions_temp2, row)
        
        if questions_temp.shape[0] == 0:
            return []
        
        random_index = random.choice(questions_temp.index)
        # random_index = random.randint(0, len(df) - 1)
        random_row = self.unique_templates.iloc[random_index]
        print(random_row[Condition_Names].to_list())
        # Templates that does not have variables are removed in order to avoid duplicates on our results
        if not any(random_row[Condition_Names+["DATE_NAME"]].to_list()): 
            self.unique_templates = self.unique_templates.drop(random_index).reset_index(drop=True)
        
        unique_template = random_row.to_dict()
        unique_template = self.filtering_question_templates(unique_template, row)
        unique_template1 = questions_temp.sample(n=1).reset_index(drop=True).to_dict(orient='records')[0]
        print("++++ PICKED TEMPLATE ++++")
        print(unique_template) 
        #self.I_types = Condition_Names.copy()
        inst_types = [(x.split("_")[0], v) for x, v in row["Instances"].items()]
        for i, _ in inst_types:
            if i not in Dict_instances_type_mapping.keys():
                print("-----------------------Adeio " + i)
                return []

        temp_instances = row["Instances"].copy()

        instance_nodes_counter ={
            "COUNTY_NAME":0,
            "STATE_NAME":0
        }

        for k in row["Instances"].keys():
            instance_node_type, number = k.split("_")
            key_ref = Dict_instances_type_mapping[instance_node_type]
            if key_ref in instance_nodes_counter.keys():
                if instance_nodes_counter[key_ref] == 0:
                    new_key = key_ref
                else:
                    new_key = key_ref +"_"+ str(instance_nodes_counter[key_ref] + 1)
                instance_nodes_counter[key_ref] += 1
            else:
                new_key = key_ref

            temp_instances[new_key] = temp_instances.pop(k)

        print("------ TEMP INSTANCES ------")
        print(temp_instances)

        for col in Condition_Names:
            if unique_template[col]:
                if col in temp_instances.keys():
                    row["Uris_match"][col] = temp_instances[col]
                else:
                    return []
        print("===== URI MATCH =======")
        print(row["Uris_match"])

        # for variable_name, uri in inst_types:     # for every node, uri pair
        #     for k, node_type in Dict_instances_type_mapping.items():         # map the node with the corresponding variable in questions
        #         if node_type == variable_name:
        #             self.I_types.remove(k)
        #             questions_temp=questions_temp[questions_temp[k]]
        #             row["Uris_match"][k]=uri
        #             break
        # questions_temp=self.filtering_question_templates(questions_temp, row)
        # for t in self.I_types:
        #     questions_temp=questions_temp[~questions_temp[t]]

        return eval(unique_template["Questions Templates"])

    def question_template_production(self, querie_df):
        # querie_df = querie_df[querie_df["Q_id"] == "Q7"]
        querie_df["Questions_templates"] = querie_df.apply(lambda row: self.template_picker(row), axis=1)
        # print(querie_df["Questions_templates"])
        return querie_df


def extract_word_forms(sentence, keyword):
    # Split the sentence into individual words
    words = sentence.split()

    # Iterate over the words to find the word and its surrounding substring
    for i in range(len(words)):
        if keyword+"." in words[i]:
            return words[i]
        elif keyword in words[i]:
            return keyword

    # If the word is not found, return None or an appropriate value
    return ""


def camel_to_words(camel_string):
    # Use regular expression to find all occurrences of uppercase letters
    words = re.findall(r'[A-Z][a-z]*', camel_string)
    
    # Join the found words into a single string with spaces
    words_with_spaces = ' '.join(words)
    
    return words_with_spaces


class question_production:
    def __init__(self, df_picked_templates):
        self.df_questions=df_picked_templates.copy()

    def clear_uri(self, k, uri, title_form):
        if "COUNTY_NAME" in k:
            s = uri.split(types_to_uris[k])[-3].title().replace("_", " ")
        else:
            s=""
        if title_form:
            return (uri.split(types_to_uris[k])[-1].title()).replace("_", " ") + ", "+ s
        else:
            return camel_to_words(uri.split(types_to_uris[k])[-1].replace("_", " ")).lower()

    def replace_variables(self, row):
        if not row["Questions_templates"]:
            return " "
        question=random.choice(row["Questions_templates"])
        print(row["Uris_match"].items())
        for k,v in row["Uris_match"].items():
            type_with_version = extract_word_forms(question, k)
            temp_v = v
            type_with_version = type_with_version.replace("?","")
            type_with_version = type_with_version.replace(",","")
            split_type_version = type_with_version.split(".")
            if len(split_type_version) >= 2:
                type_, version = split_type_version[0], split_type_version[1]   
            else:
                type_, version = split_type_version[0],""
            if v in synonyms.keys():
                if version == "":
                    temp_v = random.choice([item["original"] for item in synonyms[v]])
                else:
                    temp_v = random.choice([item[version] for item in synonyms[v]])
                # print(temp_v)
            elif k != "DATE_NAME":
                temp_v = self.clear_uri(k, v, k == "COUNTY_NAME" or k == "STATE_NAME" or k == "COUNTY_NAME_2" or k == "STATE_NAME_2")
            question = question.replace(type_with_version, temp_v, 1)
        return question

    def produce_questions(self):
        self.df_questions["Questions"] = self.df_questions.apply(lambda row: self.replace_variables(row), axis=1)
        return self.df_questions