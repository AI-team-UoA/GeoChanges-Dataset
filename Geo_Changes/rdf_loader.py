import datetime
import os

from rdflib import Graph

from namespaces import SEM, TSN, TSE, GEO


unused_rdf_files = ["usCountyVerison_without_geometries.nt"]
unused_rdf_geo_files = ["us_counties_version_with_geom.nt"]

unused_rdf_reduced_files = ["us_counties_version_with_geom.nt"]  # ,"materialized_triples_updated2.nt
# "before_after_county_extended.nt" ]

rdf_folder_name = "C:/Users/mikem/Desktop/Work/Dharmen_Eleni_thesis/My_GeoChangesQA/GeoChangesQA/resources/rdf_dump"  # /storage/home/gottschalk/geochanges/rdf_dumps/


class SimpleDate():

    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day


class Change():

    def __init__(self, node, date, text):
        self.node = node
        self.date = date
        self.text = text

        print(date)
        self.simple_date = datetime.datetime.strptime(date, '%a %b %d %X EET %Y').strftime('%Y-%m-%d')

    def __str__(self):
        return str(self.date) + ", " + str(self.text)


def get_default_graph():
    g = Graph(store="Oxigraph")

    g.bind("tse", TSE)
    g.bind("sem", SEM)
    g.bind("tsn", TSN)
    g.bind("geo", GEO)

    return g


def load_graph():
    g = get_default_graph()
    
    # load RDF dumps
    for folder in [x[0] for x in os.walk(rdf_folder_name)]:
        print("Folder", folder)
        print(os.listdir(folder))
        for file in os.listdir(folder):
            if file.endswith(".nt") and file not in unused_rdf_reduced_files:
                file_name = os.path.join(folder, file)
                print(" Parse", file_name, " - ", datetime.datetime.now().strftime("%H:%M:%S"))
                g.parse(file_name)
    return g
