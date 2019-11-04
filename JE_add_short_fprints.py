# Python3

""" Import short audio fingerprints for JE into RDF

    Polina Proutskova, August-Seeptember 2019
"""

###########################################################
# Data paths

RDFfile = "TTL/JE_PyRDF_musicians_leaders.ttl"
RDFnewfile = "TTL/JE_PyRDF_fs.ttl"
FPRINTfile = "DATA/id_dtl1000_idonly.csv"

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

logging.info("\nReading fingerprints from %s", FPRINTfile)
with open(FPRINTfile, 'r') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',')
    count = 0
    for row in csvreader:
        if len(row) > 0 and row[0].startswith(".."):
            filename = row[0].split("/")[3]
            
            if filename.startswith("JE"):
                count +=1
            
                fsplit = re.split("[-\.]", filename)
                part = int(fsplit[1])
                part_title = dtlutil.get_JE_part(part)
                cd = int(fsplit[2])
                tnum = int(fsplit[3])
                fingerprint = row[1]


                # find signal
                qstr =  """SELECT ?trackt ?signal
                        WHERE {
                            ?track RDF:type MO:Track .
                            ?track DC:title ?trackt .
                            ?track MO:track_number "%i" .
                            ?medium MO:track ?track .
                            ?medium DC:title ?mediumt .
                            ?medium MO:record_number "%i" .
                            ?release MO:record ?medium .
                            ?release DC:title "%s" .
                            ?signal MO:published_as ?track .
                        } 
                        """  %(tnum, cd, part_title)
                q = rdflib.plugins.sparql.prepareQuery(qstr, initNs)
                found = g.query(q)
                for row in found:
                    print(count, row[0], row[1])
                    g.add( (row[1], DTL.fingerprint_short, Literal(fingerprint)) )

logging.debug("\ngraph has %i triples", len(g))
dtlutil.write_rdf(g, RDFnewfile)
