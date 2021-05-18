#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 31 21:15:40 2021

Compares the number of solos in rdf and in json for each track which is 
in both files

@author: polinap
"""


#%%

RDFfile_merged = "TTL/JE_ILL_patched.ttl"
DTL1000json = "DATA/dtl_1000.json"



import dtlutil
import copy

# logging
import logging
MIN_LEVEL = logging.DEBUG
dtlutil.setup_log(MIN_LEVEL)

##############################################################
#%% read in rdf graph

import rdflib
from rdflib.graph import Graph, Store, URIRef, Literal, BNode
from rdflib.namespace import RDF, FOAF, DC

MO, TL, EVENT, OLO, DTL, initNs = dtlutil.init_namespaces()
DBP, REL, LJ = dtlutil.LOD_namespaces()

g = dtlutil.create_graph()
dtlutil.read_in_rdf(g, RDFfile_merged)

##############################################################
#%% read in json file
import json
with open(DTL1000json, 'r') as jsonfile:
    dtl1000list = json.load(jsonfile)
 
dtl1000_fprints = []
for dict in dtl1000list:
    dtl1000_fprints.append(dict['file'])
    
##############################################################
#%% compare the number of solos in rdf and in json
count = 1
for fprint in dtl1000_fprints:
    for signal in g.subjects(DTL.fingerprint_short, Literal(fprint)):
        performance = g.value(signal,DTL.captures)
        solos = list(g.objects(performance, EVENT.sub_event))
        for dict in dtl1000list:
            if dict['file'] == fprint:
                json_solos = []
                if "solo_#metadata_full_compressed_v7_csv" in dict.keys():
                    json_solos = dict["solo_#metadata_full_compressed_v7_csv"]
                    if len(solos)!=len(json_solos):
                        print("%i: fingerprint %s, rdf has %i solos, json has %i solos" %(count, fprint, len(solos), len(json_solos)))
                        count +=1
                else:
                    if len(solos) > 0:
                        print("%i: fingerprint %s, rdf has %i solos, json has %i solos" %(count, fprint, len(solos), len(json_solos)))
                        count +=1
                break