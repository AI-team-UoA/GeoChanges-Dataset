from datetime import datetime
import sys
sys.path.append("..")  # Append parent directory to the import path

from kg_api_access import query

#{'res': [{'?rel': 'http://www.opengis.net/ont/geosparql#sfOverlaps'}, {'?rel': 'http://www.opengis.net/ont/geosparql#sfIntersects'}, 
# {'?rel': 'http://www.opengis.net/ont/geosparql#sfContains'}, {'?rel': 'http://www.opengis.net/ont/geosparql#sfCovers'}, 
# {'?rel': 'http://www.opengis.net/ont/geosparql#sfTouches'}]}

sparql_query='''PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX sem: <http://semanticweb.cs.vu.nl/2009/11/sem/>
PREFIX tsn: <http://purl.org/net/tsn#>
PREFIX tsnchange: <http://purl.org/net/tsnchange#>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX hgc: <http://www.semanticweb.org/savtr/ontologies/2022/1/HistoricGeoChanges-23/>

SELECT DISTINCT ?c {
 ?c a hgc:County.
} ORDER BY RAND()'''

#BIND(?x3 AS ?year)
current_time = datetime.now().strftime("%H:%M:%S")
print("Current Time =", current_time)

# extract select variable names
select_placeholders = [placeholder for placeholder in sparql_query.split("SELECT", 1)[1].split("{", 1)[0].split(" ") if
                       placeholder.startswith("?")]
    
print(sparql_query)
res = query(sparql_query)

print(res)
current_time = datetime.now().strftime("%H:%M:%S")
print("Current Time =", current_time)