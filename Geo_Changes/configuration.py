rule_type = "county"

allowed_select_node_types = [ "tsnchange:County", "geo:Geometry", "sem:Event", "tsnchange:Change", "ChangeDate", "time:Interval", "tsnchange:State"]  # control select node ChangeType

not_allowed_uri_nodes=["geo:Geometry", "sem:Event","tsnchange:Change"]  #"time:Interval", "ChangeDate"

not_existing_node_types=['time:Interval' ,'time:Instant' ,'xsd:date', 'WKT_Geo', 'ChangeType', 'ChangeDate', "tsnchange:Change"]

types_for_temp_filters = ['time:Interval', "ChangeDate", 'xsd:date']

select_exception_rule_ids=["Q3", "Q7", "Q12", "Q13", "Q26", "Q28","Q34", "Q45", "Q46"]  #, "Q28", "Q37"    #select node is picked automatically

#Geometry relations
spatial_filter_relations = ['strdf:right', 'strdf:below', 'strdf:above', 'strdf:left']
#'geo:sfWithin', 'geo:sfContains', 'geo:sfOverlaps', 'geo:sfIntersects',
#'geo:sfTouches', 'geo:sfCoverdBy', 'geo:sfEquals', 'geo:sfCovers'

spatial_materialised_properties = ['geo:sfTouches', "geo:sfIntersects", "geo:sfContains",
"geo:sfCovers",
"geo:sfOverlaps",
"geo:sfWithin"]   
                                   

#Change Types
change_subclasses = ['tsnchange:Appearance', 'tsnchange:NameChange', 'tsnchange:Expansion',
                     'tsnchange:Contraction']  # Skip 'tsnchange:Fusion', 'tsnchange:Merge', 'tsnchange:Integration', 'tsnchange:Extraction'

rules_with_start_end=["Q1"]
#Nodes with properties
node_properties={
    "tsnchange:Change":[["tsnchange:date", "ChangeDate_"],
                        ["a", "ChangeType_"]
    ],
    # "time:Interval":[["http://www.w3.org/2006/time#hasEnd", "ChangeDate_"],
    #                     ["http://www.w3.org/2006/time#hasBeginning", "ChangeType_"]]
}

online_exceptions = ["Q22", "Q34"]  # "Q28" "Q22"

experiment_path = "test_Q1_cnt_"

question_template_path = "resources/Checked_Question_Templates.csv"
invalid_rules_path = "resources/invalid_rules.json"
rules_path = "resources/rules3.tsv"
counties_dates_path = "resources/county_dates_changedates.csv"
county_dates_changes = "resources/county_date_change_geo_event.csv"