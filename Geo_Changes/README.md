# GeoChangesQA

Question Answering over a knowledge graph of geo changes

## Pre-processing

- `subgraphs_creator.py`: Create a set of connected components in the upper ontology networkx graph.

## Query Generation

The following files are included:

- Rules (`resources/rules.tsv`): A list of semi-manually created rules.
- Invalid rules (`invalid_rules.json`): A dictionary saying which rules are invalid.
- Questions (`resources/question_templates.csv`): A list of semi-manually created questions per rule.
- Type triples (`resources/rdf_types`): A folder containing several RDF files using the "rdf:type" property.

The following process needs to be run to create queries:

- **!** `pipeline.py`: Creates queries. Use the parameters `number_of_queries_per_rule`
  and `number_of_queries_to_generate` to configure how many results to get. The output is found in `
  generated_queries/queries_with_results.txt`

### Helper classes

- `ontology_loader.py`: Load the upper ontology from `resources/ontology/HistoricGeoChanges_upper_with_states.owl`
  into a networkx graph.
- `rules_reader.py`: Reads the manually defined rules in `resources/rules.tsv`
- `query_creator_from_rules.py`: Takes the ontology from `ontology_loader.py` and the rules from `rules_reader.py` to
  create a set of random queries.
