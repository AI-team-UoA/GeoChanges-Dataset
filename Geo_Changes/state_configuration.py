rule_type = "state"

allowed_select_node_types = [ "hgc:County", "geo:Geometry", "sem:Event", "tsnchange:Change", "ChangeDate", "time:Interval", "hgc:State"]  # control select node ChangeType

not_allowed_uri_nodes=["geo:Geometry", "sem:Event","tsnchange:Change"]  #"time:Interval", "ChangeDate"

not_existing_node_types=['time:Interval' ,'time:Instant' ,'xsd:date', 'WKT_Geo', 'ChangeType', 'ChangeDate', "tsnchange:Change"]

types_for_temp_filters = ['time:Interval', "ChangeDate", 'xsd:date']

select_exception_rule_ids=["SQ3", "SQ7", "SQ12", "SQ13", "SQ26", "SQ28", "SQ34"]  #, "Q28", "Q37"    #select node is picked automatically

#Geometry relations
spatial_filter_relations = ['strdf:right', 'strdf:below', 'strdf:above', 'strdf:left']
#'geo:sfWithin', 'geo:sfContains', 'geo:sfOverlaps', 'geo:sfIntersects',
#'geo:sfTouches', 'geo:sfCoverdBy', 'geo:sfEquals', 'geo:sfCovers'

spatial_materialised_properties = ['geo:sfTouches', "geo:sfIntersects", "geo:sfCoverdBy",
"geo:sfOverlaps",
"geo:sfWithin"]   
                                   

#Change Types
change_subclasses = ['tsnchange:Appearance', 'tsnchange:NameChange', 'tsnchange:Expansion',
                     'tsnchange:Contraction', 'tsnchange:Extraction']  # Skip 'tsnchange:Fusion', 'tsnchange:Merge', 'tsnchange:Integration'

rules_with_start_end=["SQ1"]
#Nodes with properties
node_properties={
    "tsnchange:Change":[["tsnchange:date", "ChangeDate_"],
                        ["a", "ChangeType_"]
    ],
    # "time:Interval":[["http://www.w3.org/2006/time#hasEnd", "ChangeDate_"],
    #                     ["http://www.w3.org/2006/time#hasBeginning", "ChangeType_"]]
}

online_exceptions = ["SQ22", "SQ34"]

experiment_path = "final_28_stt"

question_template_path = "./resources/state_question_templates.csv"
invalid_rules_path = "./resources/state_invalid_rules.json"
rules_path = "resources/state_rules.tsv"
counties_dates_path = "resources/county_dates_changedates.csv"
county_dates_changes = "resources/state_date_change_geo_event.csv"