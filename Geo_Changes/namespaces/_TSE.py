from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef


class TSE(DefinedNamespace):
    # TODO: Add other classes and properties

    _fail = True

    # http://www.w3.org/1999/02/22-rdf-syntax-ns#Property
    startDate: URIRef
    isCausedBy: URIRef
    coexisted: URIRef

    # http://www.w3.org/2000/01/rdf-schema#Class
    CountyVersion: URIRef

    _NS = Namespace("http://time-space-event.com/ontology/")
