""" convert downloaded sqlite with Lord metadata to RDF
    Polina Proutskova
    July 2019
"""

##############################################################

DBfile = "DATA/2019.07.17_disco_all_linked.sqlite"
RDFfile = "TTL/Lord_RDF_nc.ttl"

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


#########################################################
# read in sqlite tables

logging.info("Reading tables from %s", DBfile)

import sqlite3
import pandas as pd
pd.set_option("display.max_rows", 5)
# Create your connection.
cnx = sqlite3.connect(DBfile)

sessions_table = pd.read_sql_query("SELECT * FROM sessions", cnx)
#sessions_table.head()
releases_table = pd.read_sql_query("SELECT * FROM releases", cnx)
leaders_table = pd.read_sql_query("SELECT * FROM leaders", cnx)
musicians_table = pd.read_sql_query("SELECT * FROM musicians", cnx)
tunes_table = pd.read_sql_query("SELECT * FROM tunes", cnx)
instruments_table = pd.read_sql_query("SELECT * FROM instruments", cnx)
tracks_table = pd.read_sql_query("SELECT * FROM tracks", cnx)

release_session_table = pd.read_sql_query("SELECT * FROM releasesession", cnx)
##session_instrument_table = pd.read_sql_query("SELECT * FROM sessioninstrument", cnx)
session_musician_table = pd.read_sql_query("SELECT * FROM sessionmusician", cnx)
session_tune_table = pd.read_sql_query("SELECT * FROM sessiontune", cnx)
##tune_instrument_table = pd.read_sql_query("SELECT * FROM tuneinstrument", cnx)
##tune_musician_table = pd.read_sql_query("SELECT * FROM tunemusician", cnx)
##tune_release_table = pd.read_sql_query("SELECT * FROM tunerelease", cnx)
session_leader_table = pd.read_sql_query("SELECT * FROM sessionleader", cnx)
session_track_table = pd.read_sql_query("SELECT * FROM sessiontrack", cnx)
track_musicianinstr_table = pd.read_sql_query("SELECT * FROM trackmusicianinstr", cnx)
musician_instrument_table = pd.read_sql_query("SELECT * FROM musicianinstrs", cnx)

logging.debug("done")

###########################################################
# functions

def create_uri(forWhat, uid):
    uri = "http://www.DTL.org/DISCOGRAPHY/" + forWhat +"/" + str(uid)
    return URIRef(uri)

def find_by_id(forWhat, uid):
    return create_uri(forWhat, uid)

def find_session_performances(sessionURI):
    return g.objects(sessionURI, EVENT.sub_event)

def find_medium_by_release(releaseURI):
    return g.value(releaseURI, MO.record)

def find_track_performance(trackURI):
    signalURI = g.value(subject=None, predicate=MO.published_as, object=trackURI)
    performanceURI = g.value(signalURI, DTL.captures)
    return performanceURI

def get_session_id_by_idx(session_idx):
        # sessions: id == ful|_id, idx == id
        # get the line in which id==idx, from it the column full_id
##        session = sessions_table.loc[sessions_table.id == session_idx, 'full_id']
        # get the content of the one-cell frame
##        session_id = session.iloc[0]
    return sessions_table.loc[sessions_table.id == session_idx, 'full_id'].iloc[0]

def get_track_title_by_track_id(track_id):
    return tracks_table.loc[tracks_table.id == track_id, 'name'].iloc[0]

def get_musician_instrument_ids(musicianinstr_id):
    musicianinstr_line = musician_instrument_table.loc[musician_instrument_table.id == musicianinstr_id]
    musician_id = musicianinstr_line.musician_id.iloc[0]
    instrument_id = musicianinstr_line.instrument_id.iloc[0]
    return musician_id, instrument_id

def get_release_idx_for_session(session_idx):
    releasesession = release_session_table.loc[release_session_table.sessionId == session_idx]
    if len(releasesession) > 0:
        release_idx = releasesession.releaseId.iloc[0]
    else:
        release_idx = None
    return release_idx

def get_release_id_by_idx(release_idx):
    if release_idx != None:
        return releases_table.loc[releases_table.id == release_idx, 'full_id'].iloc[0]
    else:
        return None

###########################################################
# create entities, attributes and properties expressed directly in the tables

# sessions
def process_sessions():
    session_ids = sessions_table.full_id
    logging.info("\ncreating %i sessions", len(session_ids))
    for counter, session_id in enumerate(session_ids):
        logging.debug(str(counter))
        sessionURI = create_uri("sessions", session_id)
        g.add( (sessionURI, RDF.type, MO.Performance) )
        g.add( (sessionURI, RDF.type, DTL.Session) )
        g.add( (sessionURI, DTL.lord_id, Literal(session_id)) )
    logging.info("sessions created")

# releases
def process_releases():
    release_ids = releases_table.full_id
    release_titles = releases_table.title
    release_label_id_strs = releases_table.label_id_str
    release_notes = releases_table.notes_str
    logging.info("\ncreating %i releases", len(release_ids))
    for release_id, release_title, label_id_str, note in \
            zip(release_ids, release_titles, release_label_id_strs, release_notes):
        logging.debug("creating release %s", release_title)
        releaseURI = create_uri("releases", release_id)
        g.add( (releaseURI, RDF.type, MO.Release) )
        g.add( (releaseURI, DC.title, Literal(release_title)) )
        g.add( (releaseURI, DTL.lord_label_id_str, Literal(label_id_str)) )
        g.add( (releaseURI, DTL.lord_release_notes, Literal(note)) )
        g.add( (releaseURI, DTL.lord_id, Literal(release_id)) )
        #label_id_str? notes_str?
    logging.info("releases created")

# bands
###### band or leader? mo:MusicGroup or mo:MusicArtist?
def process_bands():
    leader_ids = leaders_table.id
    leader_names = leaders_table.name
    logging.info("\ncreating %i bands", len(leader_ids))
    for leader_id, name in zip(leader_ids, leader_names):
        logging.debug("creating band %s", name)
        bandURI = create_uri("bands", leader_id)
        g.add( (bandURI, RDF.type, MO.MusicGroup) )
        g.add( (bandURI, FOAF.name, Literal(name)) )
        g.add( (bandURI, DTL.lord_id, Literal(leader_id)) )
    logging.info("bands created")

# musicians
def process_musicians():
    musician_ids = musicians_table.id
    musician_names = musicians_table.name
    logging.info("\ncreating %i musicians", len(musician_ids))
    for musician_id, name in zip(musician_ids, musician_names):
        logging.debug("creating musician %s", name)
        musicianURI = create_uri("musicians", musician_id)
        g.add( (musicianURI, RDF.type, MO.MusicArtist) )
        g.add( (musicianURI, FOAF.name, Literal(name)) )
        g.add( (musicianURI, DTL.lord_id, Literal(musician_id)) )
    logging.info("musicians created")

# tunes
def process_tunes():
    tune_ids = tunes_table.id
    tune_titles = tunes_table.name
    logging.info("\ncreating %i tunes", len(tune_ids))
    for tune_id, title in zip(tune_ids, tune_titles):
        logging.debug("creating tune %s", title)
        tuneURI = create_uri("tunes", tune_id)
        g.add( (tuneURI, RDF.type, MO.MusicalWork) )
        g.add( (tuneURI, DC.title, Literal(title)) )
        g.add( (tuneURI, DTL.lord_id, Literal(tune_id)) )
    logging.info("tunes created")

# instruments
def process_instruments():
    instrument_ids = instruments_table.id
    instrument_titles = instruments_table.name
    logging.info("\ncreating %i instruments", len(instrument_ids))
    for instrument_id, title in zip(instrument_ids, instrument_titles):
        logging.debug("creating instrument %s", title)
        instrumentURI = create_uri("instruments", instrument_id)
        g.add( (instrumentURI, RDF.type, MO.Instrument) )
        g.add( (instrumentURI, DTL.lord_inst_label, Literal(title)) )
        g.add( (instrumentURI, DTL.orig_inst_label, Literal(title)) )
        g.add( (instrumentURI, DTL.lord_id, Literal(instrument_id)) )
        ######## are these lord uids?
    logging.info("instruments created")

# tracks
def process_tracks():
    track_ids = tracks_table.id
    track_titles = tracks_table.name
    track_numbers = tracks_table.track_nr
    logging.info("\ncreating %i tracks", len(track_ids))
    for track_id, title, tnum in zip(track_ids, track_titles, track_numbers):
        logging.debug("creating track %s with number %s", title, tnum)
        trackURI = create_uri("tracks", track_id)
        g.add( (trackURI, RDF.type, MO.Track) )
        g.add( (trackURI, DC.title, Literal(title)) )
        g.add( (trackURI, MO.track_number, Literal(str(tnum))) )
        g.add( (trackURI, DTL.lord_id, Literal(track_id)) )
        ######## are these lord uids?
    logging.info("tracks created")

# relate bands to sessions
def process_bands_sessions():
    session_idxs = session_leader_table.sessionId
    leader_ids = session_leader_table.leaderId
    logging.info("\nrelating %i sessions to bands", len(session_idxs))
    for session_idx, leader_id in zip(session_idxs, leader_ids):
        session_id = get_session_id_by_idx(session_idx)
        sessionURI = find_by_id("sessions", session_id)
        bandURI = find_by_id("bands", leader_id)
        logging.debug("relating session %s to band %s", session_id, g.value(bandURI, FOAF.name))
        g.add( (sessionURI, MO.performer, bandURI) )
    logging.info("bands and sessions connected")

###########################################################
# create virtual entities

# medium for each release
def process_media():
    release_ids = releases_table.full_id
    logging.info("\ncreating %i media", len(release_ids))

    for counter, release_id in enumerate(release_ids):
        mediumURI = create_uri("mediums", uuid.uuid4())
        releaseURI = find_by_id("releases", release_id)
        logging.debug("%i: creating medium for release %s", counter, g.value(releaseURI, DC.title))
        g.add( (mediumURI, RDF.type, MO.Record) )
        g.add( (releaseURI, MO.record, mediumURI))
    
    logging.info("media created")

# create signal and performance for each track
def process_signals_performances():
    track_ids = tracks_table.id
    logging.info("\ncreating signals and performances for %i tracks", len(track_ids))
    for track_id in track_ids:
        trackURI = find_by_id("tracks", track_id)
        
        # create signal for the track
        signalURI = create_uri("signals", uuid.uuid4())
        g.add( (signalURI, RDF.type, MO.Signal) )
        g.add( (signalURI, MO.published_as, trackURI) )
        logging.debug("signal created")

        # create performance
        performanceURI = create_uri("performances", uuid.uuid4())
        g.add( (performanceURI, RDF.type, MO.Performance) )
        g.add( (signalURI, DTL.captures, performanceURI) )
        track_title = g.value(trackURI, DC.title)
        g.add( (performanceURI, DC.title, Literal(track_title)) ) 
        logging.debug("performance %s created", track_title)

    logging.info("signals and performances created")

# relate track to session and to release
def process_tracks_sessions_releases():
    session_idxs = session_track_table.sessionId
    # sessions: id == ful|_id, idx == id
    track_ids = session_track_table.trackId
    logging.info("\nrelating %i tracks to sessions and to releases", len(track_ids))

    no_release_counter = 0
    for session_idx, track_id in zip(session_idxs, track_ids):
        
        session_id = get_session_id_by_idx(session_idx)
        logging.debug("relating track %s to session %s", track_id, session_id)
        sessionURI = find_by_id("sessions", session_id)
        trackURI = find_by_id("tracks", track_id)
        performanceURI = find_track_performance(trackURI)
        g.add( (sessionURI, EVENT.sub_event, performanceURI) )
        
        # get release for the session
        release_idx = get_release_idx_for_session(session_idx)
        release_id = get_release_id_by_idx(release_idx)
        if release_id != None:
            # some sessions are not found in the session_track_table, in that case no connection is created
            releaseURI = find_by_id("releases", release_id)

            # relate track to release through medium
            logging.debug("relating track %s to release %s", g.value(trackURI, DC.title), g.value(releaseURI, DC.title))
            mediumURI = find_medium_by_release(releaseURI)
            g.add( (mediumURI, MO.track, trackURI) )
        else:
            no_release_counter += 1
            logging.warning("no release found for session %s, track %s", session_id, track_title)

    logging.info("tracks - sessions - releases connected")
    logging.info("no release was found for %i of %i tracks (%i%s)", no_release_counter, len(track_ids),\
                 no_release_counter/len(track_ids)*100, "%")
    
    
# create performers, relate to musicians and instruments
def process_performers_musicians_instruments():
    track_ids = track_musicianinstr_table.trackId
    musicianinstr_ids = track_musicianinstr_table.musicianinstrId
    logging.info("\nrelating %i tracks to musicians and instruments", len(track_ids))

    for track_id, musicianinstr_id in zip(track_ids, musicianinstr_ids):
        trackURI = find_by_id("tracks", track_id)
        logging.debug("creating performer for track %s", g.value(trackURI, DC.title))
        performanceURI = find_track_performance(trackURI)

        # find musician and instrument
        musician_id, instrument_id = get_musician_instrument_ids(musicianinstr_id)
        musicianURI = find_by_id("musicians", musician_id)
        instrumentURI = find_by_id("instruments", instrument_id)

        # create performer
        logging.debug("musician: %s, instrument: %s", g.value(musicianURI, FOAF.name), g.value(instrumentURI, DTL.lord_inst_label))
        performerURI = create_uri("performers", uuid.uuid4())
        g.add( (performerURI, RDF.type, DTL.Performer) )
        g.add( (performanceURI, MO.performer, performerURI) )
        g.add( (performerURI, DTL.musician, musicianURI) )
        g.add( (performerURI, DTL.instrument, instrumentURI) )
        
    logging.info("\nperformers - musicians - instruments connected")


# relate performances to tunes
def process_performances_tunes():
    logging.info("\nrelating performances to tunes")
    track_ids = tracks_table.id
    for track_id in track_ids:
        tune_id = tracks_table.loc[tracks_table.id == track_id, "tune_id"].iloc[0]
        trackURI = find_by_id("tracks", track_id)
        tuneURI = find_by_id("tunes", tune_id)

        # find performance for the track
        performanceURI = find_track_performance(trackURI)

        # relate performance to tune
        logging.debug("relating performance %s to tune %s", g.value(performanceURI, DC.title), g.value(tuneURI, DC.title))
        g.add( (tuneURI, MO.performed_in, performanceURI) )
        g.add( (performanceURI, DTL.performance_of, tuneURI) )
        ###### we don't know about intro, theme, changes, variations, etc

    logging.info("\nperformances and tunes connected")


############################################################
# date and place

from lordAreaDateParser import LordAreaDateParser

def process_time_area():
    parser = LordAreaDateParser()
    # parse areadate strings
    session_areadate_strings = sessions_table.location_time_str
    logging.info("\nparsing %i area date strings", len(session_areadate_strings))
    session_area_strings = []
    session_date_strings = []
    for session_areadate_str in session_areadate_strings:
        areastr, datestr = parser.parse_area_date_str(session_areadate_str)
##        except parser.UnparsableAreaDateStringWarning as e:
##            logging.warning(e.message)
##            areastr = session_areadate_str
##            datestr = ""
        logging.debug("area: %s, date: %s", areastr, datestr)
        session_area_strings.append(areastr)
        session_date_strings.append(datestr)
    logging.info("area - date strings parsed")

    # g.add area and date to sessions
    from dateParser import DateParser
    
    session_idxs = sessions_table.id
    logging.info("\nadding areas and dates to %i sessions", len(session_idxs))
    for session_idx, session_area_str, session_date_str in zip(session_idxs, session_area_strings, session_date_strings):
        logging.debug("session %i", session_idx)
        session_id = get_session_id_by_idx(session_idx)
        sessionURI = find_by_id("sessions", session_id)
        logging.debug('add place: %s', session_area_str)
        g.add( (sessionURI, EVENT.place, Literal(session_area_str)) )
        g.add( (sessionURI, DTL.orig_date, Literal(session_date_str)) )
        logging.debug('datestr: %s', session_date_str)
        try:
            dtlutil.add_datestr(g, sessionURI, session_date_str)
        except DateParser.UnparsableDateWarning as e0:
            logging.warning(e0.message)
        except DateParser.YearOutOfRangeWarning as e1:
            logging.warning(e1.message)
            
    logging.info("\ndates and areas added to sessions")
    ## area is not further processed, sometimes has venue info, sometimes country (not always), not very consistent


##################################################################

CLASSES = ["sessions", "releases", "bands", "tunes", "musicians", "instruments", "tracks", "media", "signals_performances"]

CONNECTIONS = ["bands_sessions", "tracks_sessions_releases", "performers_musicians_instruments", \
               "performances_tunes"]

ATTRIBUTES = ["time_area"]

dtlutil.read_in_rdf(g, RDFfile)
#for entity in CLASSES + CONNECTIONS + ATTRIBUTES:
for entity in ["performers_musicians_instruments", "bands_sessions", "time_area"]:
    # convert table(s) to RDF
    globals()['process_' + entity]()

dtlutil.write_rdf(g, RDFfile)

logging.info("\nSUCCESS --- all tables processed, RDF created successfully")


