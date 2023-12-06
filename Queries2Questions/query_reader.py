import pandas as pd
import numpy as np
import math
import random
import string
import re
import types
from dateutil.parser import parse



class queries_data:
    def __init__(self,query_file):
        self.processed_df = pd.DataFrame(data = None, 
                               columns = ['Q_id','Instances','Select_type', 'Predicates', "Filters", "SparqlQuery", "Answer"],
                              )
        self.original_dataframe=pd.read_json(query_file, lines=True)  #nrows=1
        # self.original_dataframe=self.original_dataframe.iloc[9:12]
    
    def extract_select_type(self, select_node, node_types):
        #type_list=[node_types[x] for x in select_node]
        if "Area_0" in node_types.keys():
            return "area"
        return node_types[select_node]

    def uri_2_name(self, uri):
        return uri.split("/")[-1].title().replace("_"," ")

    def extract_instances(self, row):
        instance_list={} #Needs to be a list because you are going to have many instances
        #Now Simon has only one instance
        for x in row["uri_nodes"]:
            instance_list[x] = row["uri_node_uris"][x]
        
        if row["county_relation"] != None and str(row["county_relation"])!='nan':
            instance_list["GEOSPATIAL_PROPERTY"] = row["county_relation"]
        # d={}
        # d["type"]=row["seed_node_type"]
        # d_value=row["uri_changes"][0]["uri"]
        # if d['type']=="hcb:County" or d['type']=="hcb:State":
        #     d_value=self.uri_2_name(d_value)
        # d['value']=d_value
        # instance_list.append(d)
        return instance_list
    
    def extract_predicates(self, row):
        predicates=[]
        for x in row["edges"]:
            predicates.append(x[1])
        return predicates

    def extract_filter(self, row):
        filters=[]
        for f in row["filters"]:
            d={}
            d["f_type"]=f[4] #take the filter type
            # d["f_text"]="FILTER(" +f[0] +")"
            if d["f_type"]=="temporal":
                #d["filter_str"]= f[0]
                d["v1"]=f[1].strip()
                d["operator"]=f[2].strip()
                d["v2"]=f[3].strip()
            elif d["f_type"]=="spatial":
                d["v1"]=f[1].strip()
                d["operator"]=f[2].strip()
                d["v2"]=f[3].strip()             
            filters.append(d)
        return filters 

    def extract_data(self):
        # self.original_dataframe=pd.read_json(self.query_file)
        print(self.original_dataframe.columns)
        self.processed_df['Q_id']= self.original_dataframe["rule"].apply(lambda x: x["id"])
        self.processed_df['Select_type']= self.original_dataframe.apply(lambda x: self.extract_select_type(x["select_node"],x["node_types"]), axis=1)
        self.processed_df['Instances']= self.original_dataframe.apply(lambda row: self.extract_instances(row),axis=1)
        self.processed_df['Predicates']= self.original_dataframe.apply(lambda row: self.extract_predicates(row),axis=1)
        self.processed_df['Filters']= self.original_dataframe.apply(lambda row: self.extract_filter(row),axis=1)
        self.processed_df['SparqlQuery']= self.original_dataframe["sparql_query"]
        self.processed_df['Answer']= self.original_dataframe["results"]

        # self.processed_df = self.processed_df[self.processed_df["Q_id"] == "SQ28"]
        return self.processed_df
        # print(original_dataframe.head())