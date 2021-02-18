#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 31 15:50:54 2021

@author: polinap
"""

#%%

RDFfile_merged = "TTL/JE_ILL_patched.ttl"
DTL100json = "DATA/dtl_1000.json"


import dtlutil

# logging
import logging
MIN_LEVEL = logging.DEBUG
dtlutil.setup_log(MIN_LEVEL)

##############################################################
#%% read in rdf graph

import rdflib
from rdflib.graph import Graph, Store, URIRef, Literal, BNode
from rdflib.namespace import Namespace, RDFS
from rdflib import plugin
from rdflib.plugins import sparql
from rdflib import Namespace
from rdflib.namespace import RDF, FOAF, RDFS, DC, XSD

MO, TL, EVENT, OLO, DTL, initNs = dtlutil.init_namespaces()
DBP, REL, LJ = dtlutil.LOD_namespaces()

g_merged = dtlutil.create_graph()
dtlutil.read_in_rdf(g_merged, RDFfile_merged)

gDTL1000 = dtlutil.create_graph()
#dtlutil.read_in_rdf(gDTL1000, RDFfile_merged)

##############################################################
#%% read in json file
import json
with open(DTL100json, 'r') as jsonfile:
    dtl100list = json.load(jsonfile)
 
fprints = []
for dict in dtl100list:
    fprints.append(dict['file'])

##############################################################
#%% collect subgraph (all connected instances) for an instance
# this can run into infinite cycles!!!

def get_subgraph(g, uri):
    # from subject to object
    logging.debug("collecting objects for instance %s of type %s", \
                  g.value(uri,DC.title), g.value(uri,RDF.type))
        
    g1 = Graph()
    g1 += g.triples( (uri, None, None) ) # this will be immutable
    g11 = Graph()
    g11 = g1 # here connected triples will be added
    for o in g1.objects():
        if not isinstance(o,Literal):
            g11 += get_subgraph(g, o)
        
    # from object to subject
    g2 = Graph()
    g2 += g.triples( (None, None, uri) ) # this will be immutable
    g22 = Graph()
    g22 = g2 # here connected triples will be added
    for o in g2.subjects():
        if not isinstance(o,Literal):
            g22 += get_subgraph(g, o)
        
    return g11 + g22
    
##############################################################
#%%  

logging.debug("merged graph has %i triples", len(g_merged))

for fprint in fprints:
    signalURI = g_merged.value(subject=None, predicate=DTL.fingerprint_short, \
                                object=Literal(fprint), default=None, any=True)
    if signalURI != None:
        signalgraph = get_subgraph(g_merged, signalURI)
        gDTL1000 += signalgraph
