# Python3

""" adding solo fragments and their performers to RDF
    Polina Proutskova
    August 2019
"""

##############################################################
# paths
DATA_CSV = "DATA/solo_extract_meta.csv"
RDFfile = "TTL/JE_inst.ttl"
RDFnewfile = "TTL/JE_solos.ttl"
INST_LABELS = "DATA/DTLtoJE_instruments.csv"
NO_MUSICIANS_FILE = "PyLOG/JE_no_musicians_found.json"
NO_MATCHING_INSTRUMENT_FILE = "PyLOG/JE_no_matching_instrument_found.json"
MULTIPLE_MUSICIANS_FILE = "PyLOG/JE_multiple_musicians_found.json"


##############################################################
import dtlutil

# logging
import logging
MIN_LEVEL = logging.INFO
dtlutil.setup_log(MIN_LEVEL)

# create rdf graph
import rdflib
from rdflib.graph import Graph, Store, URIRef, Literal, BNode
from rdflib import plugin
from rdflib.plugins import sparql
from rdflib.namespace import RDF, FOAF, RDFS, DC, XSD

MO, TL, EVENT, OLO, DTL, initNs = dtlutil.init_namespaces()
g = dtlutil.create_graph()
dtlutil.read_in_rdf(g, RDFfile)

####################################################################

from dtlutil import *

def exists_instrument(inst):
    return find_instrument(inst) != None

def find_instrument(inst):
    return g.value(subject=None, predicate=DTL.dtl_inst_label, object=inst, default=None, any=False)

ALBUM_TITLES = dtlutil.get_JE_parts()

# no longer needed as tracks are identified by fprint
def find_performance_from_JEid(JEid):
    # parse JE id
    # example JE id: JE-4-077-18
    idlst = JEid.split("-")
    part = int(idlst[1])
    cdnum = int(idlst[2])
    tnum = int(idlst[3])
    release_title = dtlutil.get_JE_part(part)
    qstr =  """SELECT ?performance ?trackt
        WHERE {
            ?release RDF:type MO:Release .
            ?release DC:title "%s" .
            ?release MO:record ?medium .
            ?medium MO:record_number "%i" .
            ?medium MO:track ?track .
            ?track MO:track_number "%i" .
            ?track DC:title ?trackt .
            ?signal MO:published_as ?track .
            ?signal DTL:captures ?performance .
        } """ %(release_title, cdnum, tnum)
    logging.debug(qstr)
    q = rdflib.plugins.sparql.prepareQuery(qstr, initNs)
    found = g.query(q)
   # found = self.find_class(q)
    if found == None or len(found) == 0:
        logging.warning("no RDF found for id %s", JEid)
        return '', ''
    elif len(found) > 1:
        logging.warning("Multiple performances found for id %s:", JEid)
        for row in found:
            logging.warning(row)
        return '',''
    else:
        for row in found:
            performanceURI = row[0]
            track_title = row[1]
            logging.debug("performance found for track %s: %s", track_title, performanceURI)
            return (performanceURI, track_title)
                                    
def find_signal_by_fingerprint(fprint):
    return g.value(subject=None, predicate=DTL.fingerprint_short, object=Literal(fprint), default=None, any=False)

def find_performance(signalURI):
    return g.value(subject=signalURI, predicate=DTL.captures, object=None, default=None, any=False)


def create_time_interval(start, end, timeline=TL.UniversalTimeline):
    eventnode = rdflib.BNode()
    g.add( (eventnode, RDF.type, TL.Interval) )
    g.add( (eventnode, TL.beginsAt, Literal(start)) )
    g.add( (eventnode, TL.endsAt, Literal(end)) )
    g.add( (eventnode, TL.onTimeLine, timeline) )
    return eventnode
    

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
        orig_label = row[2]
        logging.debug(orig_label)
        INSTRUMENT_LABELS[DTLlabel] = orig_label

                
#########################################################################
# main

import uuid
import datetime


with open(DATA_CSV) as csvfile:
    logging.info("\nReading data from file: %s", DATA_CSV)
    csvreader = csv.reader(csvfile, delimiter=',')
    csvreader.__next__()

    found = 0
    solos_count = 0
    NO_MUSICIANS = []
    NO_MATCHING_INSTRUMENT = []
    MULTIPLE_MUSICIANS = []

    for count, row in enumerate(csvreader):
        logging.info("\nprocessing row %i:", count + 1)

		#if row[1].startswith("JE-"):
        fprint = row[1]
        soloid = row[0].replace(".csv","")
        instrument = row[2]
        start = row[3]
        end = row[4]
        logging.info("fprint: %s", fprint)
        logging.info("instrument: %s", instrument)
        signalURI = find_signal_by_fingerprint(fprint)

        if signalURI is not None:
            # find performance
            #performanceURI, track_title = find_performance_from_JEid(JEid)
            trackURI = g.value(subject=signalURI, predicate=MO.published_as, object=None, default=None, any=False)
            track_title = g.value(subject=trackURI, predicate=DC.title, object=None, default=None, any=False)
            logging.debug("track title: %s", track_title)
            performanceURI = find_performance(signalURI)

            if len(str(performanceURI)) > 0:
                found +=1
            
                # create solo performance
                soloperformanceURI = create_uri("solo_performances", soloid)
                g.add( (soloperformanceURI, RDF.type, DTL.SoloPerformance) )
                g.add( (performanceURI, EVENT.sub_event, soloperformanceURI) )
                g.add( (soloperformanceURI, DTL.solo_id, Literal(soloid)) )
                solos_count += 1
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
                je_inst_label = INSTRUMENT_LABELS[instrument]
                instrumentURI = g.value(subject=None, predicate=DTL.je_inst_label, object=Literal(je_inst_label), default=None, any=False)
                if instrumentURI != None:
                    g.add( (soloperformanceURI, DTL.solo_instrument, instrumentURI) )
                    logging.debug("connected instrument %s to the solo performance of track %s", instrument, track_title)
                else:
                    logging.warning("no instrument found for instrument label %s", instrument)
                
                # find performers
                performers = g.objects(performanceURI, MO.performer)
                candidates = []
                exist_performers = False
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
                    perf_inst_label = g.value(subject=perf_inst, predicate=DTL.je_inst_label, object=None, default=None, any=False)
                    musician = g.value(subject=performer, predicate=DTL.musician, object=None, default=None, any=False)
                    name = g.value(subject=musician, predicate=FOAF.name, object=None, default=None, any=False)
                    g.add( (soloperformanceURI, DTL.solo_performer, performer) )
                    g.set( (soloperformanceURI, DTL.solo_instrument, perf_inst) )
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
                    logging.warning("Multiple performers found playing %s on track %s with id %s:", instrument, track_title, fprint)
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
            logging.debug("non JE id, skipping row")
                

# stats
logging.info("\n##############\nSTATS")
logging.info("Processed %i tracks", found)
logging.info("Created %i solos", solos_count)
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



        

