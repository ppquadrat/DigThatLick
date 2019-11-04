# Python3


###########################################################
# Data paths

RDFfile = "TTL/JE_PyRDF_191031_LODpeople.ttl"
RDFnewfile = "TTL/JE_PyRDF_191031_session.ttl"

###########################################################

import dtlutil

# logging
import logging
MIN_LEVEL = logging.DEBUG
dtlutil.setup_log(MIN_LEVEL)

##############################################################
# read in rdf graph

import rdflib
from rdflib.graph import Graph, Store, URIRef, Literal, BNode
from rdflib.namespace import Namespace, RDFS
from rdflib import plugin
from rdflib.plugins import sparql
from rdflib import Namespace
from rdflib.namespace import RDF, FOAF, RDFS, DC, XSD

MO, TL, EVENT, OLO, DTL, initNs = dtlutil.init_namespaces()

g = dtlutil.create_graph()
dtlutil.read_in_rdf(g, RDFfile)

logging.debug("\ngraph has %i triples", len(g))

##############################################################

for band in g.subjects(RDF.type, MO.MusicGroup):
    for sessionURI in g.subjects(MO.performer, band):
        triple = (sessionURI, RDF.type, DTL.Session)
        if not triple in g:
            g.add(triple)
            

logging.debug("\ngraph has %i triples", len(g))
dtlutil.write_rdf(g, RDFnewfile)
