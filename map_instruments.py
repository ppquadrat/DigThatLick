# Python3

""" mapping original instrument labels to DTL canonical labels
    also adding a generic dtl:orig_inst_label property 
    Polina Proutskova
    August 2019
"""

##############################################################
# paths
PROPERTY_PREFIX = "lord"  # 'je', 'lord, 'orig'

if PROPERTY_PREFIX == "je":
    RDFfile = "TTL/JE_PyRDF_fs.ttl"
    RDFnewfile = "TTL/JE_PyRDF_191031_inst.ttl"
else:
    RDFfile = "TTL/ILL1000_191101_session.ttl"
    RDFnewfile = "TTL/ILL1000_191101_inst.ttl"
    
INST_LABELS = "DATA/orig2DTL_instruments.csv"


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

import csv

INSTRUMENT_LABELS = {}

with open(INST_LABELS, 'r') as csvfile:
    logging.info("\nInstrument labels from file: %s", INST_LABELS)
    instcsvreader = csv.reader(csvfile, delimiter=',')
    instcsvreader.__next__()
    for row in instcsvreader:
        DTLlabel = row[1]
        logging.debug("dtl label %s to be mapped to:", DTLlabel)
        for x in range(1,len(row)-1):
            """ NB the canonical acronyms are also in the dict """
            if len(row[x]) > 0:
                orig_label = row[x]
                logging.debug(orig_label)
                INSTRUMENT_LABELS[orig_label] = DTLlabel


def map_inst_label(orig_label):
    if orig_label in INSTRUMENT_LABELS.keys():
        return INSTRUMENT_LABELS[orig_label]
    else:
        return "other"
    
                
#########################################################################
# main


"""for all instrument objects:
        get label
        map to dtl acronym
        add dtl label
    save rdf
"""

if PROPERTY_PREFIX == "lord":
    PROPERTY = DTL.lord_inst_label
elif PROPERTY_PREFIX == "je":
    PROPERTY = DTL.je_inst_label
else:
    PROPERTY = DTL.orig_inst_label

for instrumentURI in g.subjects(RDF.type, MO.Instrument):
    orig_label = str(g.value(instrumentURI, PROPERTY))
    logging.debug("original label: %s", orig_label)
    DTLlabel = map_inst_label(orig_label.strip(" ,."))
    logging.debug("mapped to: %s", DTLlabel)
    g.add( (instrumentURI, DTL.dtl_inst_label, Literal(DTLlabel)) )

    g.add( (instrumentURI, DTL.orig_inst_label, Literal(orig_label)) )


dtlutil.write_rdf(g, RDFnewfile)


        

