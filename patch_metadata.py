# Python 3.7.3

""" patching solo musicians and instruments
    
    Polina Proutskova, November 2019
"""

##############################################################
# paths
RDFfile = "TTL/JE_ILL_merged.ttl"
RDFnewfile = "TTL/JE_ILL_patched.ttl"
PatchMetadataFile = "DATA/missing_performer.csv"
IRI = "http://www.DTL.org/DTL/"


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

g = dtlutil.create_graph()
dtlutil.read_in_rdf(g, RDFfile)

logging.debug("\ngraph has %i triples", len(g))

##############################################################

import uuid

def create_uri(forWhat, uid):
    uri = IRI + forWhat + "/" + str(uid)
    return URIRef(uri)

def create_artist(artistName):
    # create artist URI 
    artistURI = create_uri("artists", uuid.uuid4())
    # add artist metadata
    g.add( (artistURI, RDF.type, MO.MusicArtist) )
    g.add( (artistURI, FOAF.name, Literal(artistName)) )
    logging.debug("Artist %s created", artistName)
    return artistURI

def create_instrument(inst_label):
    # create instrument URI 
    instrumentURI = create_uri("instruments", uuid.uuid4())
    # add instrument metadata
    g.add( (instrumentURI, RDF.type, MO.Instrument) )
    g.add( (instrumentURI, DTL.orig_inst_label, Literal(inst_label)) )
    g.add( (instrumentURI, DTL.dtl_inst_label, Literal(inst_label)) )
    logging.debug("Instrument %s created", inst_label)
    return instrumentURI

def create_performer(musicianURI, instrumentURI):
    performerURI = create_uri("performers", uuid.uuid4())
    g.add( (performerURI, RDF.type, DTL.Performer) )
    g.add( (performerURI, DTL.musician, musicianURI) )
    g.add( (performerURI, DTL.instrument, instrumentURI) )
    logging.debug("Performer %s playing %s created", \
                  g.value(musicianURI, FOAF.name), g.value(instrumentURI, DTL.dtl_inst_label) )
    return performerURI

##############################################################

import csv

logging.info("\nReading metadata from %s", PatchMetadataFile)
with open(PatchMetadataFile, 'r') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',')
    csvreader.__next__()
    count = 0
    for row in csvreader:
        if len(row) > 0:
            solo_id = row[0]
            instrument = row[6]
            if len(row[9]) > 0:
                instrument = row[9]
            musician = row[8]
            track_title = row[4]

            logging.info("\nPatching solo performance for track %s, band %s, date %s", row[4], row[2], row[7])

            if ',' in musician:
                logging.warning("too many musicians given: %s", musician)
                logging.warning("skipping")
            else:

                # get solo performance
                solo_performance_uri = g.value(subject=None, predicate=DTL.solo_id, \
                                    object=Literal(solo_id), default=None, any=False)

                if solo_performance_uri == None:
                    logging.warning("Solo id %s not found for track %s", solo_id, str(row))
                else:
                    logging.debug("found solo for id %s", solo_id)
                    
                    # get performance
                    performanceURI = g.value(subject=None, predicate=EVENT.sub_event, \
                                    object=solo_performance_uri, default=None, any=False)

                    if performanceURI == None:
                        logging.warning("Can't find performance for solo id %s", solo_id)
                    else:
                        perf_title = str(g.value(performanceURI, DC.title))
                        logging.debug("found performance with title: %s", perf_title)
                        if perf_title != track_title:
                            logging.warning("patch track title %s differs from found performance title %s", track_title, perf_title)
            
                        # get musician
                        musicianURI = g.value(subject=None, predicate=FOAF.name, \
                                    object=Literal(musician), default=None, any=True)
                        if musicianURI == None:
                             musicianURI = create_artist(musician)
                        else:
                            logging.debug("found musician %s", musician)

                        # get instrument
                        instrumentURI = g.value(subject=None, predicate=DTL.orig_inst_label, \
                                    object=Literal(instrument), default=None, any=False)
                        if instrumentURI == None:
                            instrumentURI = create_instrument(instrument)
                        else:
                            logging.debug("found instrument %s", instrument)

                        # create new performer
                        perfomerURI = None
                        for performer in g.objects(performanceURI, MO.performer):
                            perf_mus = g.value(performer, DTL.musician)
                            perf_inst = g.value(performer, DTL.instrument)
                            if perf_mus == musicianURI and perf_inst == instrumentURI:
                                performerURI = performer
                                break

                        if perfomerURI != None:
                            logging.warning("performer %s playing %s already exists for this performance", \
                                            g.value(perf_mus, FOAF.name), g.value(perf_inst, DTL.dtl_inst_label) )

                        else:
                            performerURI = create_performer(musicianURI, instrumentURI)

                        # check solo instrument
                        solo_instrument = g.value(solo_performance_uri, DTL.solo_instrument)
                        solo_inst_label = g.value(solo_instrument, DTL.dtl_inst_label)
                        if solo_instrument != instrumentURI:
                            logging.warning("solo instrument in the repository is %s, in the patchfile it is %s -- patching", \
                                            solo_inst_label, instrument)
                            g.set( (solo_performance_uri, DTL.solo_instrument, instrumentURI) )

                        # add solo performer
                        solo_performer = g.value(solo_performance_uri, DTL.solo_performer)
                        if solo_performer != None:
                            solo_musician = g.value(solo_performer, DTL.musician)
                            soloist_name = g.value(solo_musician, FOAF.name)
                            logging.warning("solo performer %s is set for this solo performance -- deleting", soloist_name)
                            # delete this solo performer
                            g.remove( (solo_performance_uri, DTL.solo_performer, solo_performer) )
                            
                        logging.debug("adding solo performer %s playing %s", musician, instrument)
                        g.add( (solo_performance_uri, DTL.solo_performer, performerURI) )
                                        
################################################          

logging.debug("\ngraph has %i triples", len(g))
dtlutil.write_rdf(g, RDFnewfile)
