# Python3

""" turning jason files imported from Lord to RDF
    Polina Proutskova
    July - September 2019
"""

DATAPATH = "DATA/DTL1000_1960-2020_json_v0/"
JSON = ["1960s.csv_110_musinstr.json", "1970s.csv_110_musinstr.json", \
        "1980s.csv_110_musinstr.json", "1990s.csv_110_musinstr.json", \
        "2000s.csv_110_musinstr.json", "2010s.csv_110_musinstr.json"]

RDFnewfile = "TTL/ILL1000.ttl"


##############################################################
import dtlutil

# logging
import logging
MIN_LEVEL = logging.INFO
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

####################################################################
# read in json

import json

def readjson(filename):
    with open(filename) as jsn:
        x = json.load(jsn)
    return x[0]

####################################################################
# rdf existence check and creation funtions

def create_uri(forWhat, uid):
    uri = "http://www.DTL.org/Ill/" + forWhat +"/" + str(uid)
    return URIRef(uri)

def find_by_id(forWhat, uid):
    return create_uri(forWhat, uid)

def exists_by_id(forWhat, uid):
    uri = create_uri(forWhat, uid)
    return(uri in g.subjects())

def exists_fingerprint(fprint):
    return Literal(fprint) in g.objects(predicate=DTL.fingerprint_short)

def find_signal_by_fingerprint(fprint):
    return g.value(subject=None, predicate=DTL.fingerprint_short, object=Literal(fprint), default=None, any=False)

def find_performance(signalURI):
    return g.value(subject=signalURI, predicate=DTL.captures, object=None, default=None, any=False)

def exists_performance(signalURI):
    return find_performance(signalURI) != None


####################################################################
# date and place

from lordAreaDateParser import LordAreaDateParser 

def add_time_place():
    # parse areadate string
    session_areadate_str = entry['time_location']
    logging.info('add time and place: %s', session_areadate_str)
    parser = LordAreaDateParser()
    areastr, datestr = parser.parse_area_date_str(session_areadate_str)

    # add area and date to sessions    
    logging.info('add place: %s', areastr)
    g.add( (sessionURI, EVENT.place, Literal(areastr)) )
    logging.info('datestr: %s', datestr)
    dtlutil.add_datestr(g, sessionURI, datestr)
    ## area is not further processed, sometimes has venue info, sometimes country (not always), not very consistent

####################################################################
# main

import os.path
import uuid

no_releases = 0
no_tracks = 0
no_performances = 0
no_tunes = 0
no_sessions = 0
no_musicians = 0
no_instruments = 0

for filename in JSON:
    filename = os.path.join(DATAPATH, filename)
    logging.info("\n###############################################\nimporting data from %s", filename)
    jsondict = readjson(filename)

    for count, key in enumerate(jsondict.keys()):
        entry = jsondict[key]
        logging.info("\n%i: %s", count, key)

        # add release (and medium)
        ### is album the same as release in Lord?
        ### mediums? dnum? dcount?
        if not exists_by_id("releases", entry['release_id']):
            releaseURI = create_uri("releases", entry['release_id'])
            g.add( (releaseURI, RDF.type, MO.Release) )
            g.add( (releaseURI, DC.title, Literal(entry['album'])) )
            logging.debug("release %s created: %s", entry['release_id'], entry['album'])
            mediumURI = create_uri("mediums", uuid.uuid4())
            g.add( (mediumURI, RDF.type, MO.Record) )
            g.add( (releaseURI, MO.record, mediumURI))
            no_releases +=1
        else:
            releaseURI = find_by_id("releases", entry['release_id'])
            mediumURI = g.value( releaseURI, MO.record )
            logging.debug("release %s found", entry['release_id'])

        # add track
        # tnum? tcount?
        if not exists_by_id("tracks", entry['track_id']):
            trackURI = create_uri("tracks", entry['track_id'])
            g.add( (trackURI, RDF.type, MO.Track) )
            g.add( (trackURI, DC.title, Literal(entry['trackname'])) )
            logging.debug("track created: %s", entry['trackname'])
            no_tracks += 1
            print(no_tracks)
        else:
            trackURI = find_by_id("tracks", entry['track_id'])
            logging.debug("track found")
        ######### adds 3,377 tracks in 938 cycles - how can that be??

        # relate medium to track
        triple = (mediumURI, MO.track, trackURI)
        if not triple in g:
            g.add(triple)

        # add signal, fingerprint
        if not exists_fingerprint(entry['audioid']):
            signalURI = create_uri("signals", uuid.uuid4())
            g.add( (signalURI, RDF.type, MO.Signal) ) 
            g.add( (signalURI, DTL.fingerprint_short, Literal(entry['audioid'])) )
            logging.debug("signal created for fingerprint %s", entry['audioid'])
        else: 
            signalURI = find_signal_by_fingerprint(entry['audioid'])
            logging.debug("signal found for fingerprint %s", entry['audioid'])

        # relate track to signal
        triple = (signalURI, MO.published_as, trackURI)
        if not triple in g:
            g.add(triple)

        # add session and performance, relate to signal
        if not exists_by_id("sessions", entry['session_full_id']):
            sessionURI = create_uri("sessions", entry['session_full_id'])
            g.add( (sessionURI, RDF.type, MO.Performance) )
            g.add( (sessionURI, RDF.type, DTL.Session) )
            logging.debug("session created: %s", entry['session_full_id'])
            no_sessions += 1
            ##### band and leader are not given in JSON, retrieved via different scripts
            performanceURI = create_uri("performances", uuid.uuid4())
            g.add( (performanceURI, RDF.type, MO.Performance) )
            g.add( (performanceURI, DC.title, Literal(entry['trackname'])) )
            g.add( (sessionURI, EVENT.sub_event, performanceURI) )
            g.add( (signalURI, DTL.captures, performanceURI) )
            logging.debug("performance created: %s", entry['trackname'])
            no_performances += 1
            # add time and place
            add_time_place()

        else:
            sessionURI = find_by_id("sessions", entry['session_full_id'])
            logging.debug("session found: %s", entry['session_full_id'])
            #check if signal has performance
            if exists_performance(signalURI):
                performanceURI = find_performance(signalURI)
                logging.debug("performance found: %s", entry['trackname'])
                triple = (sessionURI, EVENT.sub_event, performanceURI)
                if not triple in g:
                    g.add(triple)
            else:
                ### could that be a new signal of an existing performance? e.g. remastered?
                performanceURI = create_uri("performances", uuid.uuid4())
                g.add( (performanceURI, RDF.type, MO.Performance) )
                g.add( (performanceURI, DC.title, Literal(entry['trackname'])) )
                g.add( (signalURI, DTL.captures, performanceURI) )
                g.add( (sessionURI, EVENT.sub_event, performanceURI) )
                logging.debug("performance created: %s", entry['trackname'])
                no_performances += 1

        # add tune
        if not exists_by_id("tunes", entry['tune_id']):
            tuneURI = create_uri("tunes", entry['tune_id'])
            g.add( (tuneURI, RDF.type, MO.MusicalWork) )
            g.add( (tuneURI, DC.title, Literal(entry['title'])) )
            logging.debug("tune %s created: %s", entry['tune_id'], entry['title'])
            no_tunes += 1
        else:
            tuneURI = find_by_id("tunes", entry['tune_id'])
            logging.debug("tune %s found: %s", entry['tune_id'], entry['title'])

        # relate tune to performance
        triple = (tuneURI, MO.performed_in, performanceURI)
        if not triple in g:
            g.add(triple)

        # add musicians and instruments
        musicians_list = entry['musician_instrument']
        for mus_inst in musicians_list:
            # add musician
            if not exists_by_id("artists", mus_inst['musician_id']):
                musicianURI = create_uri("artists", mus_inst['musician_id'])
                g.add( (musicianURI, RDF.type, MO.MusicArtist) )
                g.add( (musicianURI, FOAF.name, Literal(mus_inst['musician_name'])) )
                logging.debug("musician %s created: %s", mus_inst['musician_id'], mus_inst['musician_name'])
                no_musicians += 1
            else:
                musicianURI = find_by_id("artists", mus_inst['musician_id'])
                logging.debug("musician %s found: %s", mus_inst['musician_id'], mus_inst['musician_name'])
            # add instrument
            if not exists_by_id("instruments", mus_inst['instrument_id']):
                instrumentURI = create_uri("instruments", mus_inst['instrument_id'])
                g.add( (instrumentURI, RDF.type, MO.Instrument) )
                g.add( (instrumentURI, DTL.lord_inst_label, Literal(mus_inst['instrument_name'])) )
                logging.debug("instrument %s created: %s", mus_inst['instrument_id'], mus_inst['instrument_name'])
                no_instruments += 1
            else:
                instrumentURI = find_by_id("instruments", mus_inst['instrument_id'])
                logging.debug("instrument %s found: %s", mus_inst['instrument_id'], mus_inst['instrument_name'])
            # check if performer exists for the performance with the given musician and instrument
            performerURI = None
            for performer in g.objects(performanceURI, MO.performer):
                if musicianURI == g.value(performer, DTL.musician) and \
                instrumentURI == g.value(performer, DTL.instrument):
                    performerURI = performer
                    logging.debug("performer found")
                    break
            # otherwise create and relate
            if performerURI == None:
                performerURI = create_uri("performers", uuid.uuid4())
                g.add( (performerURI, RDF.type, DTL.Performer) )
                g.add( (performanceURI, MO.performer, performerURI) )
                g.add( (performerURI, DTL.musician, musicianURI) )
                g.add( (performerURI, DTL.instrument, instrumentURI) )
                logging.debug("performer created")
            

#################################
logging.info("\n#################### STATS")
logging.info("created %i releases", no_releases)
logging.info("created %i performances", no_performances)
logging.info("created %i tunes", no_tunes)
logging.info("created %i sessions", no_sessions)
logging.info("created %i musicians", no_musicians)
logging.info("created %i instruments", no_instruments)


dtlutil.write_rdf(g, RDFnewfile)


