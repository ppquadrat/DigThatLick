# Python3

""" implementing instruments as objects and matching them on their title strings in JE
    Polina Proutskova
    August 2019
"""

##############################################################
# paths
RDFfile = "TTL/JE_PyRDF_complete_fs.ttl"
RDFnewfile = "TTL/JE_PyRDF_inst0.ttl"


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

from dtlutil import create_uri

def exists_instrument(inst):
    return find_instrument(inst) != None

def find_instrument(inst):
    for inst_object in g.subjects(RDF.type, MO.Instrument):
#        print(str(g.value(inst_object, RDFS.label)))
        if str(g.value(inst_object, DTL.je_inst_label)) == str(inst):
            return inst_object
    return None
                
#########################################################################
# main

import uuid

"""for all performers:
        get stored instrument string
        check if there is an instrument object
        if yes:
            get instrument object
            relate to performer
            delete string object
        else:
            create instrument object
            relate to performer
            delete string object
    save rdf
"""

for performer in g.subjects(RDF.type, DTL.Performer):
    inst_string = str(g.value(performer, DTL.instrument))
    inst_string = inst_string.strip(" ,.")
    logging.debug(inst_string)
    g.remove( (performer, DTL.instrument, Literal(inst_string)) )
    if exists_instrument(inst_string):
        instrumentURI = find_instrument(inst_string)
    else:
        instrumentURI = create_uri("instruments", uuid.uuid4())
        g.add( (instrumentURI, RDF.type, MO.Instrument) )
        g.add( (instrumentURI, DTL.je_inst_label, Literal(inst_string)) )
        logging.debug("object created")
    g.set( (performer, DTL.instrument, instrumentURI) )
    

dtlutil.write_rdf(g, RDFnewfile)


        

