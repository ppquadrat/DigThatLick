# Python 3.7.3
"""
    adding dtl:orig_inst_label property copying content from either
    dtl:je_inst_label or dtl:lord_inst_label
"""


##############################################################
# paths
PROPERTY_PREFIX = "lord"  # 'je', 'lord'

if PROPERTY_PREFIX == "je":
    RDFfile = "TTL/JE_PyRDF_rel_fs.ttl"
    RDFnewfile = "TTL/JE_PyRDF_rel_fs_orig_inst.ttl"
else: # lord
    RDFfile = "TTL/ILL1000_inst.ttl"
    RDFnewfile = "TTL/ILL1000_inst_orig.ttl"


##############################################################
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



##############################################################

if PROPERTY_PREFIX == "lord":
    PROPERTY = DTL.lord_inst_label
elif PROPERTY_PREFIX == "je":
    PROPERTY = DTL.je_inst_label
else:
    raise Exception

for instrumentURI in g.subjects(RDF.type, MO.Instrument):
    orig_label = g.value(instrumentURI, PROPERTY)
    g.add( (instrumentURI, DTL.orig_inst_label, Literal(orig_label)) )

dtlutil.write_rdf(g, RDFnewfile)
