# Python3

""" adding solo fragments and their performers to RDF for the Illinois subset
    of the 1000 tracks dataset
    Polina Proutskova
    August 2019
"""

##############################################################
# paths
from os.path import join
DATA_CSV = "DATA/solo_extract_meta.csv"
RDFfile = "TTL/ILL_inst.ttl"
RDFnewfile = "TTL/ILL_solos.ttl"
NO_MUSICIANS_FILE = "PyLOG/Ill_no_musicians_found.json"
NO_MATCHING_INSTRUMENT_FILE = "PyLOG/Ill_no_matching_instrument_found.json"
MULTIPLE_MUSICIANS_FILE = "PyLOG/Ill_multiple_musicians_found.json"


import dtlutil

# logging
import logging
MIN_LEVEL = logging.WARNING
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
g = dtlutil.create_graph()
dtlutil.read_in_rdf(g, RDFfile)

####################################################################

from dtlutil import *

def create_uri(forWhat, uid):
    uri = "http://www.DTL.org/Ill/" + forWhat +"/" + str(uid)
    return URIRef(uri)

def exists_fingerprint(fprint):
    return Literal(fprint) in g.objects(predicate=DTL.fingerprint_short)

def find_signal_by_fingerprint(fprint):
    return g.value(subject=None, predicate=DTL.fingerprint_short, object=Literal(fprint), default=None, any=False)

def find_performance(signalURI):
    return g.value(subject=signalURI, predicate=DTL.captures, object=None, default=None, any=False)

def exists_instrument(inst):
    return find_instrument(inst) != None

def find_instrument(inst):
    return g.value(subject=None, predicate=DTL.dtl_inst_label, object=inst, default=None, any=False)


def create_time_interval(start, end, timeline=TL.UniversalTimeline):
    eventnode = rdflib.BNode()
    g.add( (eventnode, RDF.type, TL.Interval) )
    g.add( (eventnode, TL.beginsAt, Literal(start)) )
    g.add( (eventnode, TL.endsAt, Literal(end)) )
    g.add( (eventnode, TL.onTimeLine, timeline) )
    return eventnode
                
#########################################################################
# main

import uuid
import csv

with open(DATA_CSV) as csvfile:
    logging.info("\nReading data from file: %s", DATA_CSV)
    csvreader = csv.reader(csvfile, delimiter=',')
    csvreader.__next__()

    found = 0
    NO_MUSICIANS = []
    NO_MATCHING_INSTRUMENT = []
    MULTIPLE_MUSICIANS = []

    for count, row in enumerate(csvreader):
        logging.info("\nprocessing row %i:", count + 1)
        soloid = row[0].replace(".csv","")
        fprint = row[1]
        instrument = row[2]
        start = row[3]
        end = row[4]
        logging.info("fprint: %s", fprint)
        logging.info("instrument: %s", instrument)

        if not row[1].startswith("JE-"):
            found += 1
            if str(fprint) != "AQAHB6kSLR9xZRApLce5wy9-4U_QcIUi" and str(fprint) != "AQAIJVQSa-oSfFOCHw9yH8kyPujEOnij"\
               and str(fprint) != "AQAKzkmoZVGihMPzINzgHL2OHw96vDeO" and str(fprint) != "AQALPkqULUqkRBPGeA7c5MF5PEGtIgyl"\
               and str(fprint) != "AQANwUmSaIoeJUmg5cFzpFv14A2-nPjg" and str(fprint) != "AQAUq0kmJk5kPDA-QmV8PE-PTBfOow-8":
                signalURI = find_signal_by_fingerprint(fprint)
                trackURI = g.value(subject=signalURI, predicate=MO.published_as, object=None, default=None, any=False)
                track_title = g.value(subject=trackURI, predicate=DC.title, object=None, default=None, any=False)
                logging.debug("track title: %s", track_title)
                
                performanceURI = find_performance(signalURI)
                
                # create solo performance
                soloperformanceURI = create_uri("solo_performances", soloid)
                g.add( (soloperformanceURI, RDF.type, DTL.SoloPerformance) )
                g.add( (performanceURI, EVENT.sub_event, soloperformanceURI) )
                g.add( (soloperformanceURI, DTL.solo_id, Literal(soloid)) )
                logging.debug("created solo performance for track %s", track_title)

                # add timestamps
                if exists_timeline(g, performanceURI):
                    timelineURI = find_timeline(g, performanceURI)
                else:
                    timelineURI = create_timeline(g, performanceURI)
                logging.debug("timeline uri: %s", timelineURI)
                start_xsd = start.replace(".", ":", 2)
                end_xsd = end.replace(".", ":", 2)
                logging.debug("start: %s, end: %s", start_xsd, end_xsd)
                g.add( (soloperformanceURI, EVENT.time, create_time_interval(start_xsd, end_xsd, timelineURI)) )

                # add solo instrument
                instrumentURI = g.value(subject=None, predicate=DTL.lord_inst_label, object=Literal(instrument), default=None, any=False)
                if instrumentURI == None:
                    # this instrument has not come up in the ILL1000 tracks, creating it
                    logging.debug("new instrument %s created", instrument)
                    instrumentURI = create_uri("instruments", uuid.uuid4())
                    g.add( (instrumentURI, RDF.type, MO.Instrument) )
                    g.add( (instrumentURI, DTL.lord_inst_label, Literal(instrument)) )
                    g.add( (instrumentURI, DTL.dtl_inst_label, Literal(instrument)) )
                    g.add( (instrumentURI, DTL.orig_inst_label, Literal(instrument)) )
                g.add( (soloperformanceURI, DTL.solo_instrument, instrumentURI) )
                logging.debug("connected instrument %s to the solo performance of track %s", instrument, track_title)

                # find performers
                performers = g.objects(performanceURI, MO.performer)
                exist_performers = False
                candidates = []
                for performer in performers:
                    exist_performers = True
                    perf_inst = g.value(subject=performer, predicate=DTL.instrument, object=None, default=None, any=False)
                    perf_inst_label = g.value(subject=perf_inst, predicate=DTL.dtl_inst_label, object=None, default=None, any=False)
                    musician = g.value(subject=performer, predicate=DTL.musician, object=None, default=None, any=False)
                    name = g.value(subject=musician, predicate=FOAF.name, object=None, default=None, any=False)
                    logging.debug("performer: %s, instrument: %s", name, perf_inst_label)

                    if str(perf_inst_label) == str(instrument):
                        candidates.append(performer)
                        logging.debug("performer: %s", name)

                if len(candidates) == 1:
                    # one performer found - relate to solo performance
                    performer = candidates[0]
                    perf_inst = g.value(subject=performer, predicate=DTL.instrument, object=None, default=None, any=False)
                    perf_inst_label = g.value(subject=perf_inst, predicate=DTL.dtl_inst_label, object=None, default=None, any=False)
                    musician = g.value(subject=performer, predicate=DTL.musician, object=None, default=None, any=False)
                    name = g.value(subject=musician, predicate=FOAF.name, object=None, default=None, any=False)
                    g.set( (soloperformanceURI, DTL.solo_instrument, perf_inst) )
                    g.add( (soloperformanceURI, DTL.solo_performer, performer) )
                    logging.debug("added performer %s and instrument %s to the solo performance of track %s", name, perf_inst_label, track_title)
                elif len(candidates) < 1:
                    if not exist_performers:
                        # no performers found
                        NO_MUSICIANS.append( (track_title, fprint, instrument) )
                        logging.warning("No performers found on track %s with fingerprint %s", track_title, fprint)
                    else:
                        # no performers with a matching instrument found
                        NO_MATCHING_INSTRUMENT.append( (track_title, fprint, instrument) )
                        logging.warning("No performers found playing %s on track %s with fingerprint %s", instrument, track_title, fprint)
                elif len(candidates) > 1:
                    # multiple performers found
                    logging.warning("Multiple performers found playing %s on track %s with fingerprint %s:", instrument, track_title, fprint)
                    names_list = []
                    for performer in candidates:
                        musician = g.value(subject=performer, predicate=DTL.musician, object=None, default=None, any=False)
                        name = g.value(subject=musician, predicate=FOAF.name, object=None, default=None, any=False)
                        logging.warning("%s", name)
                        names_list.append(name)
                    MULTIPLE_MUSICIANS.append( (track_title, fprint, instrument, names_list) )
                    # add possible solo performers
                    for performer in candidates:
                        musician = g.value(subject=performer, predicate=DTL.musician, object=None, default=None, any=False)
                        name = g.value(subject=musician, predicate=FOAF.name, object=None, default=None, any=False)
                        g.add( (soloperformanceURI, DTL.possible_solo_performer, performer) )
                        logging.debug("added performer %s as a possible performer to the solo performance of track %s", name, track_title)
                    
                        
        else:
            logging.info("fingerprint not found: %s", fprint)

# stats
logging.info("\n##############\nSTATS")
logging.info("Processed %i fingerprints", found)
logging.info("No performer found: %i (%i%s)", len(NO_MUSICIANS), len(NO_MUSICIANS)/found*100, "%")
logging.info("No matching instrument found: %i (%i%s)", len(NO_MATCHING_INSTRUMENT), len(NO_MATCHING_INSTRUMENT)/found*100, "%")
logging.info("Multiple performers found: %i (%i%s)", len(MULTIPLE_MUSICIANS), len(MULTIPLE_MUSICIANS)/found*100, "%")
logging.info("##############\n")


# write problem cases to files
from dtlutil import write_json
write_json(NO_MUSICIANS, NO_MUSICIANS_FILE)
write_json(NO_MATCHING_INSTRUMENT, NO_MATCHING_INSTRUMENT_FILE)
write_json(MULTIPLE_MUSICIANS, MULTIPLE_MUSICIANS_FILE)

# write rdf
dtlutil.write_rdf(g, RDFnewfile)


        

