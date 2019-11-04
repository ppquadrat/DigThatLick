""" convert downloaded sqlite with Lord metadata to RDF
    Polina Proutskova
    July 2019
"""

##############################################################

DBfile = "DATA/2019.07.17_disco_all_linked.sqlite"
RDFfile = "TTL/Lord_RDF.ttl"
RDF_temp_file = "TTL/Lord_RDF_temp.ttl"

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
g_temp = dtlutil.create_graph('Ill1000GraphID_temp')
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

from dtlutil import append_and_clear_temp_graph as append_and_clear
from dtlutil import write_rdf_with_temp

def add(triple):
        g.add(triple)
        g_temp.add(triple)

def set(triple):
    g.set(triple)
    g_temp.set(triple)

def set_status(entity):
    add( (statusURI, DTL.status_processed, Literal(entity)) )

def get_status(entity):
    return (statusURI, DTL.status_processed, Literal(entity)) 

def clear_status():
    g.remove( (statusURI, None, None) )
    write_rdf_with_temp(g, RDFfile, RDF_temp_file)

def create_uri(forWhat, uid):
    uri = "http://www.DTL.org/DISCOGRAPHY/" + forWhat +"/" + str(uid)
    return URIRef(uri)

def find_by_id(forWhat, uid):
    return create_uri(forWhat, uid)

def find_session_performances(sessionURI):
    return g.objects(sessionURI, EVENT.sub_event)

def find_medium_by_release(releaseURI):
    return g.value(releaseURI, MO.record)
    

###########################################################
# create entities, attributes and properties expressed directly in the tables

# sessions
def process_sessions():
    session_ids = sessions_table.full_id
    logging.info("\ncreating %i sessions", len(session_ids))
    for counter, session_id in enumerate(session_ids):
    #    logging.debug(str(counter))
        sessionURI = create_uri("sessions", session_id)
        add( (sessionURI, RDF.type, MO.Performance) )
        add( (sessionURI, DTL.lord_id, Literal(session_id)) )
    logging.debug("sessions created")

# releases
def process_releases():
    release_ids = releases_table.full_id
    release_titles = releases_table.title
    release_label_id_strs = releases_table.label_id_str
    release_notes = releases_table.notes_str
    logging.info("\ncreating %i releases", len(release_ids))
    for release_id, release_title, label_id_str, note in \
            zip(release_ids, release_titles, release_label_id_strs, release_notes):
    #    logging.debug("creating release %s", release_title)
        releaseURI = create_uri("releases", release_id)
        add( (releaseURI, RDF.type, MO.Release) )
        add( (releaseURI, DC.title, Literal(release_title)) )
        add( (releaseURI, DTL.lord_label_id_str, Literal(label_id_str)) )
        add( (releaseURI, DTL.lord_release_notes, Literal(note)) )
        add( (releaseURI, DTL.lord_id, Literal(release_id)) )
        #label_id_str? notes_str?
    logging.debug("releases created")

# bands
###### band or leader? mo:MusicGroup or mo:MusicArtist?
def process_bands():
    leader_ids = leaders_table.id
    leader_names = leaders_table.name
    logging.info("\ncreating %i bands", len(leader_ids))
    for leader_id, name in zip(leader_ids, leader_names):
    #    logging.debug("creating band %s", name)
        bandURI = create_uri("bands", leader_id)
        add( (bandURI, RDF.type, MO.MusicGroup) )
        add( (bandURI, FOAF.name, Literal(name)) )
        add( (bandURI, DTL.lord_id, Literal(leader_id)) )
    logging.debug("bands created")

# musicians
def process_musicians():
    musician_ids = musicians_table.id
    musician_names = musicians_table.name
    logging.info("\ncreating %i musicians", len(musician_ids))
    for musician_id, name in zip(musician_ids, musician_names):
    #    logging.debug("creating musician %s", name)
        musicianURI = create_uri("artists", musician_id)
        add( (musicianURI, RDF.type, MO.MusicArtist) )
        add( (musicianURI, FOAF.name, Literal(name)) )
        add( (musicianURI, DTL.lord_id, Literal(musician_id)) )
    logging.debug("musicians created")

# tunes
def process_tunes():
    tune_ids = tunes_table.id
    tune_titles = tunes_table.name
    logging.info("\ncreating %i tunes", len(tune_ids))
    for tune_id, title in zip(tune_ids, tune_titles):
    #    logging.debug("creating tune %s", title)
        tuneURI = create_uri("tunes", tune_id)
        add( (tuneURI, RDF.type, MO.MusicalWork) )
        add( (tuneURI, DC.title, Literal(title)) )
        add( (tuneURI, DTL.lord_id, Literal(tune_id)) )
    logging.debug("tunes created")

# instruments
def process_instruments():
    instrument_ids = instruments_table.id
    instrument_titles = instruments_table.name
    logging.info("\ncreating %i instruments", len(instrument_ids))
    for instrument_id, title in zip(instrument_ids, instrument_titles):
    #    logging.debug("creating instrument %s", title)
        instrumentURI = create_uri("instruments", instrument_id)
        add( (instrumentURI, RDF.type, MO.Instrument) )
        add( (instrumentURI, DTL.lord_inst_label, Literal(title)) )
        add( (instrumentURI, DTL.orig_inst_label, Literal(title)) )
        add( (instrumentURI, DTL.lord_id, Literal(instrument_id)) )
        ######## are these lord uids?
    logging.debug("instruments created")

# tracks
def process_tracks():
    track_ids = tracks_table.id
    track_titles = tracks_table.name
    track_numbers = tracks_table.track_nr
    logging.info("\ncreating %i tracks", len(track_ids))
    for track_id, title, tnum in zip(track_ids, track_titles, track_numbers):
#        logging.debug("creating track %s", title)
        trackURI = create_uri("track", track_id)
        add( (trackURI, RDF.type, MO.Track) )
        add( (trackURI, DC.title, Literal(title)) )
        add( (trackURI, MO.track_number, Literal(str(tnum))) )
        add( (trackURI, DTL.lord_id, Literal(track_id)) )
        ######## are these lord uids?
    logging.debug("tracks created")

# relate bands to sessions
def process_bands_sessions():
    session_idxs = session_leader_table.sessionId
    leader_ids = session_leader_table.leaderId
    logging.info("\relating %i sessions to bands", len(session_idxs))
    for session_idx, leader_id in zip(session_idxs, leader_ids):
        print(session_idx)
        print(leader_id)
        session = sessions_table.loc[sessions_table.id == session_idx]
        print(session)
        session_id = session.full_id
        print(session_id)
        sessionURI = find_by_id("sessions", session_id)
        bandURI = find_by_id("bands", leader_id)
        logging.debug("relating session %s to band %s", session_id, g.value(bandURI, FOAF.name))
        add( (sessionURI, MO.performer, bandURI) )
    logging.debug("\nbands and sessions connected")

###########################################################
# create virtual entities

# medium for each release
def process_media():
    release_ids = releases_table.full_id
    logging.info("\ncreating %i mediums", len(release_ids))

    for counter, release_id in enumerate(release_ids):
        mediumURI = create_uri("mediums", uuid.uuid4())
        releaseURI = find_by_id("releases", release_id)
#        logging.debug("%i: creating medium for release %s", counter, g.value(releaseURI, DC.title))
        add( (mediumURI, RDF.type, MO.Record) )
        add( (releaseURI, MO.record, mediumURI))
    
    logging.debug("\nmedia created")


# relate track to session and to release, create signal, performace
def process_tracks_sessions_releases():
    session_idxs = session_track_table.sessionId
    # sessions: id == ful|_id, idx == id
    track_ids = session_track_table.trackId
    logging.info("\nrelating %i tracks to %i sessions and to releases", len(track_ids), len(session_idxs))

    for session_idx, track_id in zip(session_idxs, track_ids):
        logging.debug("relating track %s to session %s", track_id, session_idx)
        session = sessions_table.loc[sessions_table.id == session_idx]
        session_id = session.full_id
        sessionURI = find_by_id("sessions", session_id)
        trackURI = find_by_id("tracks", track_id)

        # create signal for the track
        signalURI = create_uri("signals", uuid.uuid4())
        add( (signalURI, RDF.type, MO.Signal) )
        add( (signalURI, MO.published_as, trackURI) )
        logging.debug("signal created")

        # create performance
        performanceURI = create_uri("performances", uuid.uuid4())
        add( (performanceURI, RDF.type, MO.Performance) )
        add( (signalURI, DTL.captures, performanceURI) )
        add( (sessionURI, EVENT.sub_event, performanceURI) )
        track = tracks_table.loc[tracks_table.id == track_id]
        track_title = track.name
        add(performanceURI, DC.title, track_title)
        logging.debug("performance %s created", track_title)

        # get release for the session
        releasesession = release_session_table.loc[release_session_table.sessionId == session_idx]
        release_idx = releasesession.releaseId
        release = releases_table.loc[releases_table.id == release_idx]
        release_id = release.full_id
        releaseURI = find_by_id("releases", release_id)

        # relate track to release through medium
        logging.debug("relating track %s to release %s", g.value(trackURI, DC.title), g.value(releaseURI, DC.title))
        mediumURI = find_medium_by_release(releaseURI)
        add( (mediumURI, MO.track, trackURI) )

    logging.debug("\ntracks - sessions - releases connected")
    
    
# create performers, relate to musicians and instruments
def process_performers_musicians_instruments():
    track_ids = track_musicianinstr_table.trackID
    musicianinstr_ids = track_musicianinstr_table. musicianinstrId
    logging.info("\nrelating %i tracks to musicians and instruments", len(track_ids))

    for track_id, musicianinstr_id in zip(track_ids, musicianinstr_ids):
        trackURI = find_by_id("track", track_id)
        logging.debug("creating performer for track %s", g.value(trackURI, DC.title))

        # find musician and instrument
        musicianinstr = musician_instrument_table.loc[musician_instrument_table.id == musicianinstr_id]
        musicianURI = find_by_id("musicians", musicianinstr.musician_id)
        instrumentURI = find_by_id("instruments", musicianinstr.instrument_id)

        # create performer
        logging.debug("musician: %s, instrument: %s", g.value(musicianURI, FOAF.name), g.value(instrumentURI, DTL.lord_inst_label))
        performerURI = create_uri("performers", uuid.uuid4())
        add( (performerURI, RDF.type, DTL.Performer) )
        add( (performanceURI, MO.performer, performerURI) )
        add( (performerURI, DTL.musician, musicianURI) )
        add( (performerURI, DTL.instrument, instrumentURI) )
        
    logging.debug("\nperformers - musicians - instruments connected")


# relate performances to tunes
def process_performances_tunes():
    logging.info("\nrelating performances to tunes")

    for row in tracks_table:
        track_id = row.id
        tune_id = row.tune_id
        trackURI = find_by_id("tracks", track_id)

        # find performance for the track
        signalURI = g.value(subject=None, predicate=MO.published_as, object=trackURI)
        performanceURI = g.value(signalURI, DTL.captures)

        # relate performance to tune
        logging.debug("relating performance %s to tune %s", g.value(performanceURI, DC.title), g.value(tuneURI, DC.title))
        add( (tuneURI, MO.performed_in, performanceURI) )
        add( (performanceURI, DTL.performance_of, tuneURI) )
        ###### we don't know about intro, theme, changes, variations, etc

    logging.debug("\nperformances and tunes connected")


############################################################
# date and place

import Lord_time_area_parser

def process_time_area():
    # parse areadate strings
    session_areadate_strings = sessions_table.location_time_str
    logging.info("\nparsing %i area date strings", len(session_areadate_strings))
    session_area_strings = []
    session_date_strings = []
    for session_areadate_str in session_areadate_strings:
        areastr, datestr = Lord_time_area_parser.parse_location_time_str(session_areadate_str)
        logging.debug("area: %s, date: %s", areastr, datestr)
        session_area_strings.append(areastr)
        session_date_strings.append(datestr)
    logging.debug("area - date strings parsed")

    # add area and date to sessions
    session_idxs = sessions_table.sessionId
    logging.info("\nadding areas and dates to %i sessions", len(session_idxs))
    for session_id, session_area_str, session_date_str in zip(session_ids, session_area_strings, session_date_strings):
        sessionURI = find_by_id("sessions", session_id)
        logging.debug('add place: %s', areastr)
        add( (sessionURI, EVENT.place, Literal(areaString)) )
        logging.debug('datestr: %s', datestr)
        dtlutil.add_datestr(sessionURI, datestr)
    logging.debug("\ndates and areas added to sessions")
    ## area is not further processed, sometimes has venue info, sometimes country (not always), not very consistent


##################################################################

CLASSES = ["sessions", "releases", "bands", "tunes", "musicians", "instruments", "tracks", "media"]

CONNECTIONS = ["bands_sessions", "tracks_sessions_releases", "performers_musicians_instruments", \
               "performances_tunes"]

ATTRIBUTES = ["time_area"]

# this main outer cycle takes care of securely appending RDF for each entity to the resulting file
# and keeping track of what has already been processed. If the process is interrupted it can be
# resumed without the need to reprocess everything from the start

# create the status triple, it will keep track of what data has been entered into the graph
statusURI = create_uri("status", "status_temp")

for entity in CLASSES + CONNECTIONS + ATTRIBUTES:
    if not get_status(entity) in g:
        # convert table(s) to RDF
        globals()['process_' + entity]()
        # set status done for this entity
        set_status(entity)
        # # append the temporary graph to the rdf file, clear the temporary graph
        g_temp = append_and_clear(g_temp, RDFfile, RDF_temp_file)
    else:
        logging.debug("\n%s already processed, skipping", entity)

# remove status triples from the graph and save
clear_status()
logging.info("\nSUCCESS --- all tables processed, RDF created successfully")


