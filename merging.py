# Python 3.7.3

""" merging JE and ILL
    
    Polina Proutskova, November 2019
"""

##############################################################
# paths
RDFfile_JE = "TTL/JE_LODpeople.ttl"
RDFfile_ILL = "TTL/ILL_LODpeople.ttl"
RDFnewfile = "TTL/JE_ILL_merged.ttl"


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
DBP, REL, LJ = dtlutil.LOD_namespaces()

gJE = dtlutil.create_graph()
dtlutil.read_in_rdf(gJE, RDFfile_JE)

gILL = dtlutil.create_graph()
dtlutil.read_in_rdf(gILL, RDFfile_ILL)

##############################################################

def merge(uri_JE, uri_ILL):

    for s,p,o in gILL.triples( (uri_ILL, None, None) ):
        #logging.debug("\nremoving: (%s, %s, %s)", str(s), str(p), str(o))
        g_merge.remove( (s,p,o) )
        if not (uri_JE, p, o) in g_merge:
            #logging.debug("adding: (%s, %s, %s)", str(uri_JE), str(p), str(o))
            g_merge.add( (uri_JE, p, o) )

    for s,p,o in gILL.triples( (None, None, uri_ILL) ):
        #logging.debug("\nremoving: (%s, %s, %s)", str(s), str(p), str(o))
        g_merge.remove( (s,p,o) )
        if not (s, p, uri_JE) in g_merge:
            #logging.debug("adding: (%s, %s, %s)", str(s), str(p), str(uri_JE))
            g_merge.add( (s, p, uri_JE) )

def same_instruments(instrumentURI_JE, instrumentURI_ILL):
    labelJE = gJE.value(instrumentURI_JE, DTL.orig_inst_label)
    labelILL = gILL.value(instrumentURI_ILL, DTL.orig_inst_label)
    return labelJE == labelILL

def same_bands(uri_JE, uri_ILL):
    labelJE = gJE.value(uri_JE, FOAF.name)
    labelILL = gILL.value(uri_ILL, FOAF.name)
    return labelJE == labelILL

def same_musicians(uri_JE, uri_ILL):
    labelJE = gJE.value(uri_JE, FOAF.name)
    labelILL = gILL.value(uri_ILL, FOAF.name)
    return labelJE == labelILL

def same_tunes(uri_JE, uri_ILL):
    labelJE = gJE.value(uri_JE, DC.title)
    labelILL = gILL.value(uri_ILL, DC.title)
    return labelJE == labelILL

##############################################################

g_merge = gJE + gILL
logging.debug("JE has %i triples", len(gJE))
logging.debug("ILL has %i triples", len (gILL))
len_orig = len(g_merge)
count_merged = 0
count_merged_all = 0

# merge instruments
logging.info("\nmerging instruments")
for instrumentURI_JE in gJE.subjects(RDF.type, MO.Instrument):
    for instrumentURI_ILL in gILL.subjects(RDF.type, MO.Instrument):
        if same_instruments(instrumentURI_JE, instrumentURI_ILL):
            logging.debug("merging instruments: %s   and   %s", gJE.value(instrumentURI_JE, DTL.orig_inst_label), gILL.value(instrumentURI_ILL, DTL.orig_inst_label))
            merge(instrumentURI_JE, instrumentURI_ILL)
            count_merged += 1
logging.info("instruments merged, found %i matches", count_merged)
logging.debug("merged graph has %i triples", len(g_merge))

count_merged_all += count_merged
count_merged = 0

# merge bands
logging.info("\nmerging bands")
for uri_JE in gJE.subjects(RDF.type, MO.MusicGroup):
    for uri_ILL in gILL.subjects(RDF.type, MO.MusicGroup):
        if same_bands(uri_JE, uri_ILL):
            logging.debug("merging bands: %s   and   %s", gJE.value(uri_JE, FOAF.name), gILL.value(uri_ILL, FOAF.name))
            merge(uri_JE, uri_ILL)
            count_merged += 1
logging.info("bands merged, found %i matches", count_merged)
logging.debug("merged graph has %i triples", len(g_merge))

count_merged_all += count_merged
count_merged = 0

# merge musicians
logging.info("\nmerging musicians")
for uri_JE in gJE.subjects(RDF.type, MO.MusicArtist):
    if not (uri_JE, RDF.type, MO.MusicGroup) in gJE:
        for uri_ILL in gILL.subjects(RDF.type, MO.MusicArtist):
            if not (uri_ILL, RDF.type, MO.MusicGroup) in gILL:
                if same_musicians(uri_JE, uri_ILL):
                    logging.debug("merging musicians: %s   and   %s", gJE.value(uri_JE, FOAF.name), gILL.value(uri_ILL, FOAF.name))
                    merge(uri_JE, uri_ILL)
                    count_merged += 1
logging.info("musicians merged, found %i matches", count_merged)
logging.debug("merged graph has %i triples", len(g_merge))

count_merged_all += count_merged
count_merged = 0

# merge tunes
logging.info("\nmerging tunes")
for uri_JE in gJE.subjects(RDF.type, MO.MusicalWork):
    for uri_ILL in gILL.subjects(RDF.type, MO.MusicalWork):
        if same_tunes(uri_JE, uri_ILL):
            logging.debug("merging tunes: %s   and   %s", gJE.value(uri_JE, DC.title), gILL.value(uri_ILL, DC.title))
            merge(uri_JE, uri_ILL)
            count_merged += 1
logging.info("tunes merged, found %i matches", count_merged)
logging.debug("merged graph has %i triples", len(g_merge))

count_merged_all += count_merged
count_merged = 0
                            

##############################################################

logging.debug("#########################")
logging.info("\nmerged: found %i matches", count_merged_all)
logging.debug("merged graph originally had %i triples, now has %i triples", len_orig, len(g_merge))

dtlutil.write_rdf(g_merge, RDFnewfile)
        
