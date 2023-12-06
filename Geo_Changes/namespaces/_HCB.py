from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef


class HCB(DefinedNamespace):
    """
     Territorial Statistical Nomenclature Change Ontology
    Generated from: http://lig-tdcge.imag.fr/hcb/index.html
    """

    # TODO: Add other classes and properties

    _fail = True

    # http://www.w3.org/1999/02/22-rdf-syntax-ns#Property
    isCausedBy: URIRef
    hasNextVersion: URIRef
    hasPreviousVersion: URIRef
    inputTerritoryVersion: URIRef
    territoryVersionBefore: URIRef
    lowerChange: URIRef
    outputTerritoryVersion: URIRef
    territoryVersionAfter: URIRef
    upperChange: URIRef
    date: URIRef
    label: URIRef

    # http://www.w3.org/2000/01/rdf-schema#Class
    Change: URIRef
    County: URIRef
    State: URIRef
    CountyVersion: URIRef
    StateVersion: URIRef

    _NS = Namespace("http://www.semanticweb.org/savtr/ontologies/2022/1/HistoricGeoChanges-23/")
