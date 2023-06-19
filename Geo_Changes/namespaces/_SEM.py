from rdflib.term import URIRef
from rdflib.namespace import DefinedNamespace, Namespace


class SEM(DefinedNamespace):

    """
    The Simple Event Model Ontology (SEM)
    Generated from: https://semanticweb.cs.vu.nl/2009/11/sem/#
    """

    _fail = True

    # http://www.w3.org/1999/02/22-rdf-syntax-ns#Property
    hasActor: URIRef

    # http://www.w3.org/2000/01/rdf-schema#Class
    Event: URIRef  # Events are things that happen. This comprises everything from historical events to web site sessions and mythical journeys. Event is the central class of SEM.
    Place: URIRef

    _NS = Namespace("http://semanticweb.cs.vu.nl/2009/11/sem/")