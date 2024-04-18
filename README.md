# GeoChanges-Dataset
We introduce GeoChanges QA Dataset. This dataset was semi-automatically created. The manual work involves the generation of a set of subgraphs and their corresponding natural language questions. The Dataset generation was based on HCB-Ontology and HCB-KG


# HCB-Ontology
![image](https://github.com/AI-team-UoA/GeoChanges-Dataset/assets/58078938/31f35bb0-7792-42c1-bd88-f3bfa2745e80)

The ontology file is presented here [ontology](https://github.com/AI-team-UoA/GeoChanges-Dataset/blob/main/Geo_Changes/resources/ontology/hcb_ontology.rdf)

# HCB-Knowledge Graph
The KG followed the HBC-Ontollogy and was populated using The Atlas Historical County Boundaries Dataset (https://digital.newberry.org/ahcb/downloads/states.html)
Publicly available [rdf_dump](https://drive.google.com/drive/folders/1HFWT9dvkB8LRkhOxoLfFum8RRrIzkHQg?usp=sharing) files

# QA Generation Pipeline
![Question Generation Pipeline](https://github.com/AI-team-UoA/GeoChanges-Dataset/assets/58078938/f32927b3-1b70-475f-a5eb-5fd5f5f477f1)


The dataset production is based on 2 components the Geo-changes(Random SPARQL Query Generator) and the Queries2Questions.

- **Random SPARQL Query Generator**: This component takes as input the set of subgraphs and based on them produces random SPARQL queries.
- **Queries2Questions**: The second component takes the randomly produced queries and generates the corresponding natural language question utilizing the previously mentioned templates.

# Random SPARQL Query Generator
The first component is inside Geo_Changes directory. For the given subgraphs the target node is selected. We create a generic query to retrieve a valid combination of instances for our final query. The chosen instances will be used to create a SPARQL query that will return at least one result.
To run the generic query more efficiently we create locally a simpler endpoint that will not have the volume and the complexity of the original. In this way, we make more efficient the process of retrieving results from the generic query. To build the local endpoint create a folder /resources/rdf_dump and place there all the .nt files (link). Also, create folder /resources/rdf_dump where the ontology should be placed (link).

For the local endpoint creation:

    python kg_api.py

Now that we have the running endpoint locally we can generate our queries

    python pipeline.py

The configuration can be modified through configuration.py file. There are 2 main modes, regarding the rule_type, county or state, depending on what type of subgraphs we want to produce.
Other variables to be modified inside configuration:

 - allowed_select_node_types: Not every node can take the role of a target node. We define the ones that can.
 - not_allowed_uri_nodes: Usually intermediate nodes that does not make sence to be replaced by an instance.
 - types_for_temp_filters: The variety of filters that can be formed
 - select_exception_rule_ids: A set of subgraph ids where the select node is picked automatically (subgraphs that include Geometry or Event nodes usually has them as target node)
 - spatial_filter_relations: The functions that can be used inside geospatial filter
 - spatial_materialised_properties: The materialized functions
 - change_subclasses: The different change types.
 - rules_with_start_end: rules that make use of start and end date of county/state
 - node_properties: A dictioanry of external properties that may be used
 - online_exceptions: Are the subgraph types that make use of geospatial filter. We avoid to run those queries to online endpoint due to the compleexity of them.
 - experiment_path: Where the prefix of the created file with the generated SPARQL Queries
 - question_template_path: THe question template path
 - invalid_rules_path: A dictionary with invalid rules
 - rules_path: The subgraphs representations
 - county_dates_changes: External info that is used for the creation of queries with geospatial filter


# Queries2Questions
This component makes the mapping between subgraphs and question templates, and produces natural language questions. The generated sparql queries will be given as input, along with the question templates and will give an output file with the questions, queries and one sample answer.
    
    python pipeline.py

# Useful links
Paper: (link)

We created a QA dataset with 5700 such examples(DOI: 10.5281/zenodo.10257310). 

All the produced SPARQL queries can run to our endpoint in:
[HCB-KG endpoint](https://hcbkg.l3s.uni-hannover.de/sparql)

[Ontology](https://github.com/AI-team-UoA/GeoChanges-Dataset/blob/main/Geo_Changes/resources/ontology/hcb_ontology.rdf)

# License
Copyright 2024, AI Team, University of Athens

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
   







