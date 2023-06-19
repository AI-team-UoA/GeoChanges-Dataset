from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef


class TSN(DefinedNamespace):
    """
     Territorial Statistical Nomenclature Change Ontology
    Generated from: http://lig-tdcge.imag.fr/tsnchange/index.html
    """

    # TODO: Add other classes and properties

    _fail = True

    # http://www.w3.org/1999/02/22-rdf-syntax-ns#Property
    hasAcronym: URIRef
    hasIdentifier: URIRef
    hasName: URIRef
    hasVersion: URIRef
    isVersionOf: URIRef
    referencePeriod: URIRef

    # http://www.w3.org/2000/01/rdf-schema#Class

    _NS = Namespace("http://purl.org/net/tsn#")
