#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 31 21:15:40 2021

@author: polinap
"""


#%%

RDFfile_merged = "TTL/JE_ILL_patched.ttl"
DTL1000json = "DATA/dtl_1000.json"
RDFnewfile = "TTL/dtl1000.ttl"


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

gDTL1000 = dtlutil.create_graph()
#%%
gDTL1000 = copy.deepcopy(g)

##############################################################
#%% read in json file
import json
with open(DTL1000json, 'r') as jsonfile:
    dtl1000list = json.load(jsonfile)
 
dtl1000_fprints = []
for dict in dtl1000list:
    dtl1000_fprints.append(dict['file'])

##############################################################
#%% for a uri get the list of connected fingerprints

def get_signal_fprints(signallist):
    fprintlist = [str(g.value(x, DTL.fingerprint_short)) for x in signallist]
    return fprintlist

def get_performance_fprints(uri):
    fprints = []
    for signal in g.subjects(DTL.captures, uri):
        fprint = g.value(signal, DTL.fingerprint_short)
        if fprint is not None:
            fprints.append(str(g.value(signal, DTL.fingerprint_short)))
    return(list(set(fprints)))

def get_performer_fprints(uri):
    fprints = []
    for performance in g.subjects(MO.performer, uri):
        fprints = fprints + get_performance_fprints(performance)
    return(list(set(fprints)))
    
def get_musician_fprints(uri):
    fprints = []
    for performer in g.subjects(DTL.musician, uri):
        fprints = fprints + get_performer_fprints(performer)
    for tune in g.subjects(MO.composed_by, uri):
        fprints = fprints + get_tune_fprints(tune)
    for tune in g.subjects(MO.arranged_by, uri):
        fprints = fprints + get_tune_fprints(tune)
    return(list(set(fprints)))

def get_instrument_fprints(uri):
    fprints = []
    for performer in g.subjects(DTL.instrument, uri):
        fprints = fprints + get_performer_fprints(performer)
    for soloperformance in g.subjects(DTL.solo_instrument, uri):
        fprints = fprints + get_soloperformance_fprints(soloperformance)
    return(list(set(fprints))) 

def get_soloperformance_fprints(uri):
    fprints = []
    for performance in g.subjects(EVENT.sub_event, uri):
        fprints = fprints + get_performance_fprints(performance)
    return(list(set(fprints)))

def get_tune_fprints(uri):
    fprints = []
    for performance in g.objects(uri, MO.performed_in):
        fprints = fprints + get_performance_fprints(performance)
    return(list(set(fprints)))

def get_session_fprints(uri):
    fprints = []
    for performance in g.objects(uri, EVENT.sub_event):
        fprints = fprints + get_performance_fprints(performance)
    return(list(set(fprints)))

def get_band_fprints(uri):
    fprints = []
    for session in g.subjects(MO.performer, uri):
        fprints = fprints + get_session_fprints(session)
    return(list(set(fprints)))

def get_track_fprints(uri):
    fprints = []
    for signal in g.subjects(MO.published_as, uri):
        fprint = g.value(signal, DTL.fingerprint_short)
        if fprint is not None:
            fprints.append(str(g.value(signal, DTL.fingerprint_short)))
    return(list(set(fprints)))

def get_medium_fprints(uri):
    fprints = []
    for track in g.objects(uri, MO.track):
        fprints = fprints + get_track_fprints(track)
    return(list(set(fprints)))

def get_release_fprints(uri):
    fprints = []
    for medium in g.objects(uri, MO.record):
        fprints = fprints + get_medium_fprints(medium)
    return(list(set(fprints)))

def get_album_fprints(uri):
    fprints = []
    for release in g.objects(uri, MO.published_as):
        fprints = fprints + get_release_fprints(release)
    return(list(set(fprints)))

def get_releaseevent_fprints(uri):
    fprints = []
    for release in g.objects(uri, MO.release):
        fprints = fprints + get_release_fprints(release)
    return(list(set(fprints)))

def get_label_fprints(uri):
    fprints = []
    for releaseevent in g.objects(uri, MO.published):
        fprints = fprints + get_releaseevent_fprints(releaseevent)       
    return(list(set(fprints)))

##############################################################
#%% for each class, if their fprint list does not overlap with dtl1000_fprints
# remove their subgraphs from the graph 

logging.debug("original merged graph has %i triples", len(g))

oldnumber = len(set(list(g.subjects(RDF.type,MO.label)))) 
logging.debug("removing from %i labels", oldnumber)
count = 0
for labelURI in g.subjects(RDF.type, MO.label):
    label_fprints = get_label_fprints(labelURI)
    if len(set(label_fprints) & set(dtl1000_fprints)) == 0:
        gDTL1000 -= g.triples( (labelURI, None, None) )
        count+=1
newnumber = len(set(list(gDTL1000.subjects(RDF.type,MO.label))))
logging.debug("removed %i labels, remaining %i", count, newnumber)      
if newnumber != oldnumber - count:
    logging.warning("numbers don't add up!!!")

oldnumber = len(set(list(g.subjects(RDF.type,MO.ReleaseEvent)))) 
logging.debug("removing from %i release events", oldnumber)  
count = 0      
for releaseeventURI in g.subjects(RDF.type, MO.ReleaseEvent):
    revent_fprints = get_releaseevent_fprints(releaseeventURI)
    if len(set(revent_fprints) & set(dtl1000_fprints)) == 0:
        gDTL1000 -= g.triples( (releaseeventURI, None, None) )
        count+=1
newnumber = len(set(list(gDTL1000.subjects(RDF.type,MO.ReleaseEvent)))) 
logging.debug("removed %i release events, remaining %i", count, newnumber)      
if newnumber != oldnumber - count:
    logging.warning("numbers don't add up!!!")

oldnumber = len(set(list(g.subjects(RDF.type,MO.SignalGroup)))) 
logging.debug("removing from %i albums", oldnumber)      
count = 0  
for albumURI in g.subjects(RDF.type, MO.SignalGroup):
    album_fprints = get_album_fprints(albumURI)
    if len(set(album_fprints) & set(dtl1000_fprints)) == 0:
        gDTL1000 -= g.triples( (albumURI, None, None) )
        count+=1
newnumber = len(set(list(gDTL1000.subjects(RDF.type,MO.SignalGroup)))) 
logging.debug("removed %i albums, remaining %i", count, newnumber)      
if newnumber != oldnumber - count:
    logging.warning("numbers don't add up!!!")

oldnumber = len(set(list(g.subjects(RDF.type,MO.Release)))) 
logging.debug("removing from %i releases", oldnumber) 
count = 0       
for releaseURI in g.subjects(RDF.type, MO.Release):
    release_fprints = get_release_fprints(releaseURI)
    if len(set(release_fprints) & set(dtl1000_fprints)) == 0:
        gDTL1000 -= g.triples( (releaseURI, None, None) )
        count+=1
newnumber = len(set(list(gDTL1000.subjects(RDF.type,MO.Release)))) 
logging.debug("removed %i releases, remaining %i", count, newnumber)      
if newnumber != oldnumber - count:
    logging.warning("numbers don't add up!!!")

oldnumber = len(set(list(g.subjects(RDF.type,MO.Record)))) 
logging.debug("removing from %i media", oldnumber)  
count = 0      
for mediumURI in g.subjects(RDF.type, MO.Record):
    medium_fprints = get_medium_fprints(mediumURI)
    if len(set(medium_fprints) & set(dtl1000_fprints)) == 0:
        gDTL1000 -= g.triples( (mediumURI, None, None) )
        count+=1
newnumber = len(set(list(gDTL1000.subjects(RDF.type,MO.Record)))) 
logging.debug("removed %i media, remaining %i", count, newnumber)      
if newnumber != oldnumber - count:
    logging.warning("numbers don't add up!!!")

oldnumber = len(set(list(g.subjects(RDF.type,MO.Track)))) 
logging.debug("removing from %i tracks", oldnumber)   
count = 0     
for trackURI in g.subjects(RDF.type, MO.Track):
    track_fprints = get_track_fprints(trackURI)
    if len(set(track_fprints) & set(dtl1000_fprints)) == 0:
        gDTL1000 -= g.triples( (trackURI, None, None) )
        count+=1
newnumber = len(set(list(gDTL1000.subjects(RDF.type,MO.Track)))) 
logging.debug("removed %i tracks, remaining %i", count, newnumber)      
if newnumber != oldnumber - count:
    logging.warning("numbers don't add up!!!")


oldnumber = len(set(list(g.subjects(RDF.type,MO.MusicGroup)))) 
logging.debug("removing from %i bands", oldnumber)
count = 0
for bandURI in g.subjects(RDF.type, MO.MusicGroup):
    band_fprints = get_band_fprints(bandURI)
    if len(set(band_fprints) & set(dtl1000_fprints)) == 0:
        gDTL1000 -= g.triples( (bandURI, None, None) )
        gDTL1000 -= g.triples( (None, None, bandURI) )
        count+=1
newnumber = len(set(list(gDTL1000.subjects(RDF.type,MO.MusicGroup)))) 
logging.debug("removed %i bands, remaining %i", count, newnumber)      
if newnumber != oldnumber - count:
    logging.warning("numbers don't add up!!!")

oldnumber = len(set(list(g.subjects(RDF.type,DTL.Session)))) 
logging.debug("removing from %i sessions", oldnumber)  
count = 0      
for sessionURI in g.subjects(RDF.type, DTL.Session):
    session_fprints = get_session_fprints(sessionURI)
    if len(set(session_fprints) & set(dtl1000_fprints)) == 0:
        gDTL1000 -= g.triples( (sessionURI, None, None) )
        count+=1
newnumber = len(set(list(gDTL1000.subjects(RDF.type,DTL.Session)))) 
logging.debug("removed %i sessions, remaining %i", count, newnumber)      
if newnumber != oldnumber - count:
    logging.warning("numbers don't add up!!!")

oldnumber = len(set(list(g.subjects(RDF.type,MO.Instrument)))) 
logging.debug("removing from %i instruments", oldnumber)  
count = 0      
for instrumentURI in g.subjects(RDF.type, MO.Instrument):
    instrument_fprints = get_instrument_fprints(instrumentURI)
    if len(set(instrument_fprints) & set(dtl1000_fprints)) == 0:
        gDTL1000 -= g.triples( (instrumentURI, None, None) )
        gDTL1000 -= g.triples( (None, None, instrumentURI) )
        count+=1
newnumber = len(set(list(gDTL1000.subjects(RDF.type,MO.Instrument)))) 
logging.debug("removed %i instruments, remaining %i", count, newnumber)      
if newnumber != oldnumber - count:
    logging.warning("numbers don't add up!!!")

oldnumber = len(set(list(g.subjects(RDF.type,MO.MusicArtist)))) 
logging.debug("removing from %i musicians", oldnumber)      
count = 0  
for musicianURI in g.subjects(RDF.type, MO.MusicArtist):
    musician_fprints = get_musician_fprints(musicianURI)
    if len(set(musician_fprints) & set(dtl1000_fprints)) == 0:
        gDTL1000 -= g.triples( (musicianURI, None, None) )
        gDTL1000 -= g.triples( (None, None, musicianURI) )
        count+=1
newnumber = len(set(list(gDTL1000.subjects(RDF.type,MO.MusicArtist)))) 
logging.debug("removed %i musicians, remaining %i", count, newnumber)      
if newnumber != oldnumber - count:
    logging.warning("numbers don't add up!!!")

oldnumber = len(set(list(g.subjects(RDF.type,DTL.Performer))))       
logging.debug("removing from %i performers", oldnumber)  
count = 0      
for performerURI in g.subjects(RDF.type, DTL.Performer):
    performer_fprints = get_performer_fprints(performerURI)
    if len(set(performer_fprints) & set(dtl1000_fprints)) == 0:
        gDTL1000 -= g.triples( (performerURI, None, None) )
        gDTL1000 -= g.triples( (None, None, performerURI) )
        count+=1
newnumber = len(set(list(gDTL1000.subjects(RDF.type,DTL.Performer)))) 
logging.debug("removed %i performers, remaining %i", count, newnumber)      
if newnumber != oldnumber - count:
    logging.warning("numbers don't add up!!!")

oldnumber = len(set(list(g.subjects(RDF.type,DTL.SoloPerformance)))) 
logging.debug("removing from %i solos", oldnumber)   
count = 0 
for soloURI in g.subjects(RDF.type, DTL.SoloPerformance):
    solo_fprints = get_soloperformance_fprints(soloURI)
    if len(set(solo_fprints) & set(dtl1000_fprints)) == 0:
        gDTL1000 -= g.triples( (soloURI, None, None) )
        gDTL1000 -= g.triples( (None, None, soloURI) )
        count+=1
newnumber = len(set(list(gDTL1000.subjects(RDF.type,DTL.SoloPerformance)))) 
logging.debug("removed %i solos, remaining %i", count, newnumber)      
if newnumber != oldnumber - count:
    logging.warning("numbers don't add up!!!")

oldnumber = len(set(list(g.subjects(RDF.type,MO.MusicalWork)))) 
logging.debug("removing from %i tunes", oldnumber)       
count = 0 
for tuneURI in g.subjects(RDF.type, MO.MusicalWork):
    tune_fprints = get_tune_fprints(tuneURI)
    if len(set(tune_fprints) & set(dtl1000_fprints)) == 0:
        gDTL1000 -= g.triples( (tuneURI, None, None) )
        gDTL1000 -= g.triples( (None, None, tuneURI) )
        count+=1
newnumber = len(set(list(gDTL1000.subjects(RDF.type,MO.MusicalWork)))) 
logging.debug("removed %i tunes, remaining %i", count, newnumber)      
if newnumber != oldnumber - count:
    logging.warning("numbers don't add up!!!")

oldnumber = len(set(list(g.subjects(RDF.type,MO.Performance)))) 
logging.debug("removing from %i performances", oldnumber) 
count = 0       
for performanceURI in g.subjects(RDF.type, MO.Performance):
    performance_fprints = get_performance_fprints(performanceURI)
    if len(set(performance_fprints) & set(dtl1000_fprints)) == 0:
        gDTL1000 -= g.triples( (performanceURI, None, None) )
        gDTL1000 -= g.triples( (None, None, performanceURI) )
        count+=1
newnumber = len(set(list(gDTL1000.subjects(RDF.type,MO.Performance)))) 
logging.debug("removed %i performances, remaining %i", count, newnumber)      
if newnumber != oldnumber - count:
    logging.warning("numbers don't add up!!!")

oldnumber = len(set(list(g.subjects(RDF.type,MO.Signal))))   
logging.debug("removing from %i signals", oldnumber)       
count = 0 
for signalURI in g.subjects(RDF.type, MO.Signal):
    signal_fprint = g.value(signalURI, DTL.fingerprint_short)
    if dtl1000_fprints.count(str(signal_fprint)) == 0:
        gDTL1000 -= g.triples( (signalURI, None, None) )
        count+=1
newnumber = len(set(list(gDTL1000.subjects(RDF.type,MO.Signal)))) 
logging.debug("removed %i signals, remaining %i", count, newnumber)      
if newnumber != oldnumber - count:
    logging.warning("numbers don't add up!!!")

##############################################################
#%%

logging.debug("#########################")
logging.info("graph originally had %i triples, dtl1000 graph has %i triples", len(g), len(gDTL1000))

logging.info("dtl1000 graph has %i Signals", len(list(gDTL1000.subjects(RDF.type, MO.Signal))))


dtlutil.write_rdf(gDTL1000, RDFnewfile)


                
            