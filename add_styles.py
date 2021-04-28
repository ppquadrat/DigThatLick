# Python3

""" Import styles from csv

    Polina Proutskova, October 2019
"""

###########################################################
# Data paths

RDFfile = "TTL/JE_solos.ttl"
RDFnewfile = "TTL/JE_styles.ttl"
STYLESfile = "DATA/styles.csv"

###########################################################

# general import
import csv
import os
import re
import json



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

logging.info("\nReading styles from %s", STYLESfile)
with open(STYLESfile, 'r') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',')
    count = 0
    for row in csvreader:
        if len(row) > 0:
            fprint = row[0]
            style = row[1]
            signalURI = g.value(subject=None, predicate=DTL.fingerprint_short, \
                                object=Literal(fprint), default=None, any=True)
            if signalURI != None:
                g.add( (signalURI, DTL.style, Literal(style)) )
                track = g.value(signalURI, MO.published_as)
                title = g.value(track, DC.title)
                logging.debug("style %s added to the signal of track %s", style, title)

                

logging.debug("\ngraph has %i triples", len(g))
dtlutil.write_rdf(g, RDFnewfile)
