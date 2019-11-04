""" convert downloaded sqlite with Lord metadata to RDF
    Polina Proutskova
    July 2019
"""

##############################################################

DBfile = "DATA/2019.07.17_disco_all_linked.sqlite"
RDFfile = "TTL/ILL1000_191101.ttl"
RDFnewfile = "TTL/ILL1000_191101_bands.ttl"

DATAPATH = "DATA/DTL1000_1960-2020_json_v0/"
JSON = ["1960s.csv_110_musinstr_1date.json", "1970s.csv_110_musinstr_1date.json", \
        "1980s.csv_110_musinstr_1date.json", "1990s.csv_110_musinstr_1date.json", \
        "2000s.csv_110_musinstr_1date.json", "2010s.csv_110_musinstr_1date.json"]


##############################################################

import uuid
import time
import os
from os.path import join
from shutil import copyfile
import sys
import re
import logging


import dtlutil

# logging
import logging
MIN_LEVEL = logging.DEBUG
dtlutil.setup_log(MIN_LEVEL)


##############################################################
# create rdf graph

import rdflib
from rdflib.graph import Graph, Store, URIRef, Literal, BNode
from rdflib.namespace import Namespace, RDFS
from rdflib import plugin
from rdflib.plugins import sparql
from rdflib import Namespace
from rdflib.namespace import RDF, FOAF, RDFS, DC, XSD

MO, TL, EVENT, OLO, DTL, initNs = dtlutil.init_namespaces()

g = dtlutil.create_graph('Ill1000GraphID')
dtlutil.read_in_rdf(g, RDFfile)

#########################################################
# read in sqlite tables

logging.info("Reading tables from %s", DBfile)

import sqlite3
import pandas as pd
pd.set_option("display.max_rows", 5)
# Create your connection.
cnx = sqlite3.connect(DBfile)

sessions_table = pd.read_sql_query("SELECT * FROM sessions", cnx)
leaders_table = pd.read_sql_query("SELECT * FROM leaders", cnx)

session_leader_table = pd.read_sql_query("SELECT * FROM sessionleader", cnx)

logging.debug("done")

####################################################################
# read in json

import json

def readjson(filename):
    with open(filename) as jsn:
        x = json.load(jsn)
    return x[0]



###########################################################
# functions

def create_uri(forWhat, uid):
    uri = "http://www.DTL.org/Ill/" + forWhat +"/" + str(uid)
    return URIRef(uri)

def find_by_id(forWhat, uid):
    return create_uri(forWhat, uid)

def find_session_performances(sessionURI):
    return g.objects(sessionURI, EVENT.sub_event)

def create_band(band_str):
    bandURI = create_uri("bands", uuid.uuid4())
    g.add( (bandURI, RDF.type, MO.MusicGroup) )
    g.add( (bandURI, FOAF.name, Literal(band_str)) )
    return bandURI

def find_band(bandname):
    for bandURI in g.subjects(RDF.type, MO.MusicGroup):
        if str(g.value(bandURI, FOAF.name)) == bandname:
            return bandURI
    return None

def exists_band(bandname):
    return find_band(bandname) != None

def get_session_id_by_idx(session_idx):
        # sessions: id == ful|_id, idx == id
        # get the line in which id==idx, from it the column full_id
##        session = sessions_table.loc[sessions_table.id == session_idx, 'full_id']
        # get the content of the one-cell frame
##        session_id = session.iloc[0]
    return sessions_table.loc[sessions_table.id == session_idx, 'full_id'].iloc[0]

def get_session_idx_by_id(session_full_id):
    return sessions_table.loc[sessions_table.full_id == session_full_id, 'id'].iloc[0]

def get_leader(session_full_id):
    session_idx = get_session_idx_by_id(session_full_id)
    leader_id = session_leader_table.loc[session_leader_table.sessionId == session_idx, "leaderId"].iloc[0]
    return leaders_table.loc[leaders_table.id == leader_id, "name"].iloc[0]


####################################################################
# main

import os.path
import uuid


processed = 0
bands_added = 0

for filename in JSON:
    filename = os.path.join(DATAPATH, filename)
    logging.info("\n###############################################\nimporting data from %s", filename)
    jsondict = readjson(filename)

    for count, key in enumerate(jsondict.keys()):
        entry = jsondict[key]
        logging.info("\n%i: %s, session: %s", count, key, entry['session_full_id'])

        sessionURI = find_by_id("sessions", entry['session_full_id'])
        if g.value(sessionURI, MO.performer) == None:
            processed += 1
            # band
            band_str = get_leader(entry['session_full_id'])
            if exists_band(band_str):
                bandURI = find_band(band_str)
            else:
                bandURI = create_band(band_str)
                bands_added += 1
                logging.debug("band %s added", band_str)
            g.add( (sessionURI, MO.performer, bandURI) )
            logging.debug("band: %s linked to session: %s", band_str, entry['session_full_id'])

            

##################################################################
# STATS
logging.info("\n##############\nSTATS")
logging.info("Processed %i sessions", processed)
logging.info("Added %i bands", bands_added)
logging.info("##############\n")


dtlutil.write_rdf(g, RDFnewfile)


