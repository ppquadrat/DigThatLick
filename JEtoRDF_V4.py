# Python3

""" Export the Encyclopedia of Jazz metadata into RDF

Adjust the paths and filenames at the beginning of the script

triples are appended to the rdf file

Polina Proutskova
January - June 2019"""

# general import
import rdflib
from rdflib.graph import Graph, Store, URIRef, Literal, BNode
from rdflib.namespace import Namespace, RDFS
from rdflib import plugin
from rdflib.plugins import sparql
from rdflib import Namespace
from rdflib.namespace import RDF, FOAF, RDFS, DC, XSD
import uuid
import time
import os
from os.path import join
from shutil import copyfile
import sys
import re
from dateutil.parser import parse as parsedate
import datetime
import logging
import csv
from dateutil.parser import parserinfo

# import my parsers
from dateParser import DateParser
from musiciansInstrumentsParser import MusiciansInstrumentsParser
from tunesComposersParser import TunesComposersParser

# data paths
##DATA_CSV = "/import/c4dm-datasets/C4DM Music Collection/Jazz Encyclopedia/JECompleteIndex_cleaned.csv"

DATA_CSV = "DATA/JECompleteIndex_cleaned.csv"
#DATA_CSV = "test_JEtoRDF_small.csv"

rdffilename = 'TTL/JE_PyRDF.ttl'
rdffilename_tmp = 'TTL/JE_PyRDF_tmp.ttl'


import dtlutil

# logging
import logging
MIN_LEVEL = logging.INFO
dtlutil.setup_log(MIN_LEVEL)

# album part titles
RELEASE_TITLE = dtlutil.get_JE_release_title()
RELEASE_DATE = dtlutil.get_JE_release_date()
ALBUM_TITLES = dtlutil.get_JE_parts()




##############################################################
# create rdf namespaces

import rdflib
from rdflib.graph import Graph, Store, URIRef, Literal, BNode
from rdflib.namespace import Namespace, RDFS
from rdflib import plugin
from rdflib.plugins import sparql
from rdflib import Namespace
from rdflib.namespace import RDF, FOAF, RDFS, DC, XSD

MO, TL, EVENT, OLO, DTL, initNs = dtlutil.init_namespaces()

##############################################################

from dtlutil import create_date, add_qualified_date

class MultipleRDFfoundWarning(Warning):
    """Raised when a query yields multiple results"""
    
    def __init__(self, query, result):
        self.message = """ query yields '%i' results -- it seems duplicates have been created in the graph: \n \" 
                        "%s" \" \n 
                        ------------- result: \n
                        "%s" \n""" %(len(result), query, result)

class JEtoRDF:
    
    class MyParserInfo(parserinfo):
        def convertyear(self, year, *args, **kwargs):
            if year < 100:
                year += 1900
            return year

    def __init__(self, g, g_temp):
        self.g = g
        self.g_temp = g_temp

    def write_rdf_to_file(self, rdffilename, rdffilename_tmp):
        if os.path.isfile(rdffilename):
            copyfile(rdffilename, rdffilename_tmp)
            # write RDF to file
        with open(rdffilename, mode='tw') as rdf:
            try:
                gstring = self.g.serialize(format='turtle').decode('utf-8')
                print("gstring serialised")
                rdf.write(gstring)
            except Exception:
                logging.error('cannot write RDF triples')

    def append_rdf_to_file(self, rdffilename, rdffilename_tmp):
        if os.path.isfile(rdffilename):
            copyfile(rdffilename, rdffilename_tmp)
            # write RDF to file
        with open(rdffilename, mode='ta', newline="\n") as rdf:
            try:
                gstring = self.g_temp.serialize(format='turtle', encoding="utf-8").decode('utf-8')
                print(type(gstring))
                rdf.write(gstring)
            except Exception:
                logging.error('cannot append RDF triples')
                
    def add(self, triple):
        self.g.add(triple)
        self.g_temp.add(triple)

    def indexx2index(self):
        qstr =  """CONSTRUCT {
                        ?slot OLO:index ?slotindexx .
                    }
                    WHERE {
                        ?medleyTune RDF:type DTL:Medley .
                        ?medleyTune OLO:slot ?slot .
                        ?slot OLO:indexx ?slotindexx .
                    }""" 
        logging.debug(qstr)
        q = rdflib.plugins.sparql.prepareQuery(qstr, initNs)
        result = self.g.query(q)
        for row in result:
            self.g.add(row)
        self.g.remove( (None, OLO.indexx, None) )
    
    def create_uri(self, forWhat, uid):
        uri = "http://www.DTL.org/JE/" + forWhat +"/" + str(uid)
        return URIRef(uri)

    def find_class(self, query):
        result = self.g.query (query)
        if len(result) == 0:
            return None
        elif len(result) > 1:
            raise MultipleRDFfoundWarning(query, result)
        for row in result:
            logging.debug(row)
            return row[0]

    def create_album(self, title):
        # create album URI 
        albumURI = self.create_uri("albums", uuid.uuid4())
        # add album metadata
        self.add( (albumURI, RDF.type, MO.SignalGroup) )
        self.add( (albumURI, DC.title, Literal(title) ))
        self.add( (albumURI, DTL.is_compilation, Literal("1")) )
        self.add( (albumURI, DTL.is_remix, Literal("0") ) )
        self.add( (albumURI, DTL.is_live, Literal("0") ) )
        logging.debug("Album created")
        return albumURI

    def find_album(self, title):
        qstr =  """SELECT ?album 
        WHERE {
            ?album RDF:type MO:SignalGroup .
            ?album DC:title "%s" .
        } """ %title
        logging.debug(qstr)
        q = rdflib.plugins.sparql.prepareQuery(qstr, initNs)
        found = self.find_class(q)
        if found != None:
            logging.debug("Album found: %s", found)
        return found

    def exists_album(self, title):
        return self.find_album(title) != None

    def create_release_event(self, title, date):
        # create uri
        releaseEventURI = self.create_uri("release_events", uuid.uuid4())
        # add metadata
        self.add( (releaseEventURI, RDF.type, MO.ReleaseEvent) )
        self.add( (releaseEventURI, DC.title, Literal(title)) ) 
        # add date 
        self.add( (releaseEventURI, EVENT.time, create_date(g, "2008-10-24")) )
        # add place 
        self.add( (releaseEventURI, EVENT.place, Literal("Germany")) )
        logging.debug("Release event created")
        return releaseEventURI

    def find_releaseEvent(self, title, date):        
        qstr =  """SELECT ?releaseEvent 
        WHERE {
            ?releaseEvent RDF:type MO:ReleaseEvent .
            ?releaseEvent DC:title "%s" .
            ?releaseEvent EVENT:time ?date .
            ?date RDF:type TL:Instant .
            ?date TL:at "%s" .
        } """ %(title, date)
        logging.debug(qstr)
        q = rdflib.plugins.sparql.prepareQuery(qstr, initNs)
        found = self.find_class(q)
        if found != None:
            logging.debug("Release event found: %s", found)
        return found

    def exists_releaseEvent(self, title, date):
        return self.find_releaseEvent(title, date) != None

    def create_label(self, title):
        # create URI
        labelURI = self.create_uri("labels", uuid.uuid4())
        self.add( (labelURI, RDF.type, MO.Label) )
        self.add( (labelURI, DC.title, Literal(title) ))
        logging.debug("Label created")
        return labelURI

    def find_label(self, title):
        qstr =  """SELECT ?label 
        WHERE {
            ?label RDF:type MO:Label .
            ?label DC:title "%s" .
        } """ %title
        logging.debug(qstr)
        q = rdflib.plugins.sparql.prepareQuery(qstr, initNs)
        found = self.find_class(q)
        if found != None:
            logging.debug("Label found: %s", found)
        return found

    def exists_label(self, title):
        return self.find_label(title) != None

    def create_release(self, title, dcount):
        # create release URI 
        releaseURI = self.create_uri("releases", uuid.uuid4())
         # add release metadata
        self.add( (releaseURI, RDF.type, MO.Release) )
        self.add( (releaseURI, DC.title, Literal(title)) ) 
        self.add( (releaseURI, MO.record_count, Literal(str(dcount))) )
        self.add( (releaseURI, DTL.is_remastered, Literal("0") ) )
        logging.debug("Release created")
        return releaseURI

    def find_release(self, title, dcount):
        qstr =  """SELECT ?release 
        WHERE {
            ?release RDF:type MO:Release .
            ?release DC:title "%s" .
            ?release MO:record_count "%i" .
        } """ %(title, dcount)
        logging.debug(qstr)
        q = rdflib.plugins.sparql.prepareQuery(qstr, initNs)
        found = self.find_class(q)
        if found != None:
            logging.debug("Release found: %s", found)
        return found

    def exists_release(self, title, dcount):
        return self.find_release(title, dcount) != None

    def create_medium(self, title, dnum, tcount):
        # create medium URI 
        mediumURI = self.create_uri("mediums", uuid.uuid4())
        ######## should medium uid be defined through release?
        # add medium metadata
        self.add( (mediumURI, RDF.type, MO.Record) )
        self.add( (mediumURI, MO.record_number, Literal(str(dnum))) )
        self.add( (mediumURI, DC.title, Literal(title)) )
        if tcount > 0:
            self.add( (mediumURI, MO.track_count, Literal(str(tcount))) )
        logging.debug("Medium created")
        return mediumURI

    def find_medium(self, mediumTitle, dnum):
        qstr =  """SELECT ?medium 
        WHERE {
            ?medium RDF:type MO:Record .
            ?medium DC:title "%s" .
            ?medium MO:record_number "%i" .
        } """ %(mediumTitle, dnum)
        logging.debug(qstr)
        q = rdflib.plugins.sparql.prepareQuery(qstr, initNs)
        found = self.find_class(q)
        if found != None:
            logging.debug("Medium found: %s", found)
        return found

    def exists_medium(self, mediumTitle, dnum):
        return self.find_medium(mediumTitle, dnum) != None

    def delete_medium(self, mediumURI):
        mediumTitle = self.g.value(mediumURI, DC.title, None)
        
        # collect tracks
        qstr =  """SELECT ?track 
        WHERE {
            ?track RDF:type MO:Track .
            <%s> MO:track ?track .
        } """ %mediumURI
        logging.debug(qstr)
        q = rdflib.plugins.sparql.prepareQuery(qstr, initNs)
        track_list = self.g.query (q)
        logging.debug("track list: %s", track_list)
        
        for track in track_list:
            trackTitle = self.g.value(track, DC.title, None)
            signal = g.value(None, MO.published_as, track)
            performance = g.value(signal, DTL.captures, None)
            performanceTitle = self.g.value(performance, DC.title, None)
            session = g.value(None, EVENT.sub-event, performance)
            # remove performers
            qstr =  """SELECT ?performer 
            WHERE {
                ?performer RDF:type DTL:Performer .
                <%s> MO:performer ?performer .
            } """ %performance
            logging.debug(qstr)
            q = rdflib.plugins.sparql.prepareQuery(qstr, initNs)
            performer_list = self.g.query (q)
            logging.debug("performer list: %s", performer_list)
            for performer in performer_list:
                musician = self.g.value(performer, DTL.musician, None)
                performerName = self.g.value(musician, FOAF.name, None)
                self.g.remove( (performer, None, None) )
                logging.debug("Performer graph removed: %s", performerName)
            # remove performance, session, signal, track
            g.remove( (session, None, None) )
            logging.debug("Session removed")
            g.remove( (performance, None, None) )
            logging.debug("Performance graph removed: %s", performanceTitle)
            g.remove( (signal, None, None) )
            logging.debug("Signal removed")
            g.remove( (track, None, None) )
            logging.debug("Track removed: %s", trackTitle)
            
        g.remove( (mediumURI, None, None) )
        logging.debug("Medium removed: %s", mediumTitle)

    def create_track(self, trackTitle, tnum):
        # create track URI 
        trackURI = self.create_uri("tracks", uuid.uuid4())
        #add track metadata
        self.add( (trackURI, RDF.type, MO.Track) )
        self.add( (trackURI, DC.title, Literal(trackTitle)) ) 
        self.add( (trackURI, MO.track_number, Literal(str(tnum))) )
        logging.debug("Track created")
        return trackURI

    def create_signal(self):
        signalURI = self.create_uri("signals", uuid.uuid4())
        self.add( (signalURI, RDF.type, MO.Signal) )
        logging.debug("Signal created")
        return signalURI
    
    def create_performance(self, trackTitle):
        performanceURI = self.create_uri("performances", uuid.uuid4())
        self.add( (performanceURI, RDF.type, MO.Performance) )
        self.add( (performanceURI,  DC.title, Literal(trackTitle)) )
        logging.debug("Performance created")
        return performanceURI
    
    def create_tune(self, tune_title, composer_list, arranger_list):
        # create tune URI 
        tuneURI = self.create_uri("tunes", uuid.uuid4())
        #add tune metadata
        self.add( (tuneURI, RDF.type, MO.MusicalWork) )
        self.add( (tuneURI, DC.title, Literal(tune_title)) )
        logging.debug("Tune created")
        # add composers
        ################ modularise composer and tune creation, now they are intertwined
        for composer in composer_list:
            if composer != "unknown" and self.exists_composer(composer):
                composerURI = self.find_composer(composer)
            else:
                composerURI = self.create_composer(composer)
            self.add( (tuneURI, DTL.composed_by, composerURI) )
        for arranger in arranger_list:
            if self.exists_arranger(arranger):
                arrangerURI = self.find_arranger(arranger)
            else:
                arrangerURI = self.create_arranger(arranger)
            self.add( (tuneURI, DTL.arranged_by, arrangerURI) )                                   
        return tuneURI

    def find_tune(self, tune_title, composer_list, arranger_list):     
        qstr =  """SELECT ?tune 
                WHERE {
                    ?tune RDF:type MO:MusicalWork .
                    ?tune DC:title "%s" .
                """ %tune_title
        for count, composer in enumerate(composer_list):
            qstr = qstr + """ ?composer%i RDF:type MO:MusicArtist .
                    ?composer%i FOAF:name "%s" .
                    ?tune DTL:composed_by ?composer%i .
                """ %(count, count, composer, count)
        for count, arranger in enumerate(arranger_list):
            qstr = qstr + """ ?arranger%i RDF:type MO:MusicArtist .
                    ?arranger%i FOAF:name "%s" .
                    ?tune DTL:arranged_by ?arranger%i .
                """ %(count, count, arranger, count)
        qstr = qstr + "}"
        logging.debug(qstr)
        q = rdflib.plugins.sparql.prepareQuery(qstr, initNs)
        try:
            found = self.find_class(q)            
            
        except MultipleRDFfoundWarning:
            logging.debug("multiple matching tunes found")
            qlist = self.g.query(q)
            for tuneURI in qlist:
                logging.debug(tuneURI)
            for tuneURI in qlist:
                logging.debug("tune URI %s", tuneURI)
                qstr = """SELECT ?composer 
                WHERE {
                    <%s> DTL:composed_by ?composer .
                }""" %tuneURI
                logging.debug(qstr)
                q = rdflib.plugins.sparql.prepareQuery(qstr, initNs)
                composerURIs = self.g.query(q)
                if len(composer_list) == len(composerURIs):
                    logging.debug("Tune found: %s", tuneURI)
                    return tuneURI[0]
                break
            return None

        else:
            if found != None:
                logging.debug("Tune found: %s", found)
        return found
                
    def exists_tune(self, tune_title, composer_list, arranger_list):
        return self.find_tune(tune_title, composer_list, arranger_list) != None

    def create_composer(self, name):
        # create URI 
        composerURI = self.create_uri("composers", uuid.uuid4())
        #add metadata
        self.add( (composerURI, RDF.type, MO.MusicArtist) )
        self.add( (composerURI, FOAF.name, Literal(name)) )
        logging.debug("Composer created")
        return composerURI

    def find_composer(self, name):
        qstr =  """SELECT DISTINCT ?composer 
        WHERE {
            ?composer RDF:type MO:MusicArtist .
            ?composer FOAF:name "%s" .
            ?tune RDF:type MO:MusicalWork .
            ?tune DTL:composed_by ?composer .
        } """ %(name)
        logging.debug(qstr)
        ############ do I need to check that he composed a tune?
        ############ in fact it would be nice to have one artist for Elligton as performer and as composer
        ############ but checking existence just by name is too weak, can lead to collating different John Smiths together
        ############ probably associate them later, based on all the data
        ######### also, composers are only given a surname
        q = rdflib.plugins.sparql.prepareQuery(qstr, initNs)
        found = self.find_class(q)
        if found != None:
            logging.debug("Composer found: %s", found)
        return found

    def exists_composer(self, name):
        return self.find_composer(name) != None

    def create_arranger(self, name):
        # create URI 
        arrangerURI = self.create_uri("arrangers", uuid.uuid4())
        #add metadata
        self.add( (arrangerURI, RDF.type, MO.MusicArtist) )
        self.add( (arrangerURI, FOAF.name, Literal(name)) )
        logging.debug("Arranger created")
        return arrangerURI

    def find_arranger(self, name):
        qstr =  """SELECT DISTINCT ?arranger 
        WHERE {
            ?arranger RDF:type MO:MusicArtist .
            ?arranger FOAF:name "%s" .
            ?tune RDF:type MO:MusicalWork .
            ?tune DTL:arranged_by ?arranger .
        } """ %(name)
        logging.debug(qstr)
        q = rdflib.plugins.sparql.prepareQuery(qstr, initNs)
        found = self.find_class(q)
        if found != None:
            logging.debug("Arranger found: %s", found)
        return found

    def exists_arranger(self, name):
        return self.find_arranger(name) != None
                   
    def add_area(self, uri, areaString):
        ############# resolve with GeoNames: dump GeoNames, use it to check the correct spelling/disambiguate
        self.add( (uri, EVENT.place, Literal(areaString)) ) 

    def create_band(self, bandName):
        # create URI 
        bandURI = self.create_uri("bands", uuid.uuid4())
        #add metadata
        self.add( (bandURI, RDF.type, MO.MusicGroup) )
        self.add( (bandURI, FOAF.name, Literal(bandName)) )
        logging.debug("Band created")
        return bandURI

    def find_band(self, bandName):
        qstr =  """SELECT ?band 
        WHERE {
            ?band RDF:type MO:MusicGroup .
            ?band FOAF:name "%s" .
        } """ %(bandName)
        logging.debug(qstr)
        q = rdflib.plugins.sparql.prepareQuery(qstr, initNs)
        found = self.find_class(q)
        if found != None:
            logging.debug("Band found: %s", found)
        return found

    def exists_band(self, bandName):
        return self.find_band(bandName) != None       
        
    def create_session(self):
        sessionURI = self.create_uri("sessions", uuid.uuid4())
        self.add( (sessionURI, RDF.type, MO.Performance) )
        logging.debug("Session created")
        return sessionURI

    def session_to_RDF(self, area, band, freetext_date):
        # create URI
        sessionURI = self.create_session()
        # area
        self.add_area(sessionURI, area)
        # band 
        if self.exists_band(band):
            bandURI = self.find_band(band)
        else:
            bandURI = self.create_band(band) 
        self.add( (sessionURI, MO.performer, bandURI) )
        # qualified date
        ############# what to do with missing/unknown dates?
        datekwargs = self.dates_parser.parse_freetext_date(freetext_date)
        if len(datekwargs) > 0:
            add_qualified_date(g, sessionURI, freetext_date, datekwargs)
        # is live
        return sessionURI

    def create_artist(self, artistName):
        # create artist URI 
        artistURI = self.create_uri("artists", uuid.uuid4())
        # add artist metadata
        self.add( (artistURI, RDF.type, MO.MusicArtist) )
        self.add( (artistURI, FOAF.name, Literal(artistName)) )
        logging.debug("Artist created")
        return artistURI

    def find_artist(self, artistName, bandURI):
        # artist is matched on the name + that they recorded with the same band
        ################### is this a good idea?
        qstr =  """SELECT DISTINCT ?artist 
        WHERE {
            ?artist RDF:type MO:MusicArtist .
            ?artist FOAF:name "%s" .
            ?performer DTL:musician ?artist .
            ?performance MO:performer ?performer .
            ?session EVENT:sub_event ?performance .
            ?session MO:performer <%s> .
        } """ %(artistName, bandURI)
            
        logging.debug(qstr)
        q = rdflib.plugins.sparql.prepareQuery(qstr, initNs)
        found = self.find_class(q)
        if found != None:
            logging.debug("Artist found: %s", found)
        return found
    
    def exists_artist(self, artistName, bandURI):
        return self.find_artist(artistName, bandURI) != None

    def create_performer(self, artistURI, instrument, confidence):
        performerURI = self.create_uri("Performers", uuid.uuid4())
        self.add( (performerURI, RDF.type, DTL.Performer) )
        self.add( (performerURI, DTL.musician, artistURI) )
        self.add( (performerURI, DTL.instrument, Literal(instrument)) )
        # confidence 
        confnode = rdflib.BNode()
        self.add( (confnode, RDF.type, DTL.PerformerConfidence) )
        self.add( (confnode, DTL.musician_confidence, Literal(confidence[0])) ) 
        self.add( (confnode, DTL.instrument_confidence, Literal(confidence[1])) ) 
        self.add( (performerURI, DTL.performer_confidence, confnode) )
        logging.debug("Performer created")
        return performerURI

    def tune_to_RDF(self, performanceURI, ptitle_dict, stitle_dict, composer_list):           
        # one Performance, one Tune, not medley
        
        # add attributes to Performance (primary title qualifiers)
        if "part" in list(ptitle_dict.keys()):
            self.add( (performanceURI, DTL.part_number, Literal(str(ptitle_dict["part"]))) )
        if "take" in list(ptitle_dict.keys()):
            self.add( (performanceURI, DTL.take_number, Literal(str(ptitle_dict["take"]))) )
        if "vocal" in list(ptitle_dict.keys()):
            self.add( (performanceURI, DTL.is_vocal, Literal(str(ptitle_dict["vocal"]))) )

        # construct the tune_title
        tune_title = ptitle_dict["title"]
        # recombine primary and secondary titles where secondary title cannot be semantically resolved
        if len(stitle_dict) > 0 and \
           not "aka" in list(stitle_dict.keys()) and not "intro" in list(stitle_dict.keys())\
           and not "theme" in list(stitle_dict.keys()) and not "changes" in list(stitle_dict.keys()):
            secondary_title = stitle_dict["title"]
            # re-introduce quilifiers in the title
            if "part" in list(stitle_dict.keys()):
                secondary_title =  secondary_title + " part " + str(stitle_dict["part"])
            if "take" in list(stitle_dict.keys()):
                secondary_title =  secondary_title + " take " + str(stitle_dict["take"])
            # recombine
            tune_title = ptitle_dict["title"] + " (" + secondary_title + ")"
                       
        # check if the tune exists, retrieve or create it
        composers = []
        arrangers = []
        for composer_dict in composer_list:
            if "arr" in list(composer_dict.keys()):
                arrangers.append(composer_dict["name"])
            else:
                composers.append(composer_dict["name"])
        if self.exists_tune(tune_title, composers, arrangers):
            tuneURI = self.find_tune(tune_title, composers, arrangers)
        elif "aka" in list(stitle_dict.keys()):
            aka_title = stitle_dict["title"]
            if self.exists_tune(aka_title, composers, arrangers):
                tuneURI = self.find_tune(aka_title, composers, arrangers)
                self.add( (tuneURI, DC.title, Literal(tune_title)) )
            else:
                tuneURI = self.create_tune(tune_title, composers, arrangers)
        else:
            tuneURI = self.create_tune(tune_title, composers, arrangers)
        
        # connect Performance and Tune with the appropriate property
        if "intro" in list(ptitle_dict.keys()):
            self.add( (performanceURI, DTL.has_intro, tuneURI) )
        if "theme" in list(ptitle_dict.keys()):
            self.add( (performanceURI, DTL.theme_of, tuneURI) )
        if "changes" in list(ptitle_dict.keys()):
            self.add( (performanceURI, DTL.changes_of, tuneURI) )
        if "variation" in list(ptitle_dict.keys()):
            self.add( (performanceURI, DTL.variations_on, tuneURI) )
        if "cite" in list(ptitle_dict.keys()):
            self.add( (performanceURI, DTL.citation, tuneURI) )
        if not "intro" in list(ptitle_dict.keys()) and not "theme" in list(ptitle_dict.keys()) and \
           not "changes" in list(ptitle_dict.keys()) and not "variation" in list(ptitle_dict.keys()) and \
           not "cite" in list(ptitle_dict.keys()):
            self.add( (performanceURI, DTL.performance_of, tuneURI) )  # captures only proper performances of a tune
        self.add( (tuneURI, MO.performed_in, performanceURI) )         # catches all performances of a tune

        # if secondary title can be resolved semantically
        if "aka" in list(stitle_dict.keys()):
            # add aka title to the Tune
            aka_title = stitle_dict["title"]
            if not self.exists_tune(aka_title, composers, arrangers):
                self.add( (tuneURI, DC.title, Literal(aka_title)) )
        if "intro" in list(stitle_dict.keys()):
            # if the tune has an intro, relate Performance with the intro tune
            intro_title = stitle_dict["title"]
            if self.exists_tune(intro_title, composers, arrangers):
                intro_tuneURI = self.find_tune(intro_title, composers, arrangers)
            else:
                intro_tuneURI = self.create_tune(intro_title, composers, arrangers)
            self.add( (performanceURI, DTL.has_intro, intro_tuneURI) )
        if "theme" in list(stitle_dict.keys()):
            # if the tune is a variation on a theme, relate Performance with the theme tune
            theme_title = stitle_dict["title"]
            if self.exists_tune(theme_title, composers, arrangers):
                theme_tuneURI = self.find_tune(theme_title, composers, arrangers)
            elif self.exists_theme(theme_title):
                theme_tuneURI = self.find_theme(theme_title)
            else:
                theme_tuneURI = self.create_tune(theme_title)               
            self.add( (performanceURI, DTL.same_theme_as, theme_tuneURI) )
        if "changes" in list(stitle_dict.keys()):
            # if the tune has same changes as another tune, relate Performance with the changes tune
            changes_title = stitle_dict["title"]
            if self.exists_tune(changes_title, composers, arrangers):
                changes_tuneURI = self.find_tune(changes_title, composers, arrangers)
            elif self.exists_theme(changes_title):
                changes_tuneURI = self.find_theme(changes_title)
            else:
                theme_tuneURI = self.create_tune(changes_title)               
            self.add( (performanceURI, DTL.same_changes_as, changes_tuneURI) )

        return tuneURI

    def medley_has_intro(self, tunes_composers_list):
        pdict0, sdict0, comp0 = tunes_composers_list[0]
        return "intro" in list(pdict0.keys())

    def medley_has_changes(self, tunes_composers_list):
        pdict1, sdict1, comp1 = tunes_composers_list[1]
        return "changes" in list(pdict1.keys())        

    def is_medley(self, tunes_composers_list, track_qualifiers_dict):
        if len(track_qualifiers_dict) > 0:
            return 1
        if len(tunes_composers_list) > 1:
            return 1
        return 0
            
        
    def medley_to_RDF(self, performanceURI, trackTitle, tunes_composers_list, track_qualifiers_dict):
        """
        unpack the list of tuples of the kind: primary_title_dict, secondary_title_dict, composer_list
        create tunes and composers for each list entry
        
            - primary_title_dict always has a keyword 'title' and can have keywords: part, w, vocal, take, theme, changes
            - secondary_title_dict can be empty; if not, has a keyword 'title' and can have keyqords: part, aka, intro, take, theme
            - composer_list is a list of dictionaries, each of them always has the keyword 'name' and can have a keyword 'arr'; can be empty

        - track_qualifiers_dict contains optional qualifiers related to the whole track such as:
         - part: is a string, can be '1', '2', '1&2', '1 & 2'
         - medley: 1 if the overall_title contains the word 'Medley'
         - variation: 1 if the overall_title contains the word 'Variation'
         - intro: 1 if the overall_title contains the word 'Intro'
         - take: same as part
         - overall_title - the rest of the overall description before the list of tunes with qualifiers removed, e.g. for "Perfume Suite, Part 1" it would be "Perfume Suite" 

     we have properties realting Performance to Tune: performance_of, into, changes_of, theme_of, variations_on, citation
     aka is a property relating a Tune to another Tune
     part_number, take_number, vocal are attributes of a Performance
     Medley is a subclass of Performance; medley_of is a property relating a Performance to its subperformances (of one tune)
        """
            
        if self.is_medley(tunes_composers_list, track_qualifiers_dict):
            # first handle those which are not really a medley (intro, changes)
            if len(tunes_composers_list) == 2 and (self.medley_has_intro(tunes_composers_list) or self.medley_has_changes(tunes_composers_list) ):
                ptitle_dict0, stitle_dict0, composer_list0 = tunes_composers_list[0]
                ptitle_dict1, stitle_dict1, composer_list1 = tunes_composers_list[1]
                tuneURI0 = self.tune_to_RDF(performanceURI, ptitle_dict0, stitle_dict0, composer_list0)
                tuneURI1 = self.tune_to_RDF(performanceURI, ptitle_dict1, stitle_dict1, composer_list1)
            else:
                # real medleys
                # set medley attributes
                if "part" in list(track_qualifiers_dict.keys()):
                    self.add( (performanceURI, DTL.part_number, Literal(str(track_qualifiers_dict["part"]))) )
                if "take" in list(track_qualifiers_dict.keys()):
                    self.add( (ptitle_node, DTL.take_number, Literal(str(track_qualifiers_dict["take"]))) )
                # if there is a medley title, add to performance
                if "overall_title" in  list(track_qualifiers_dict.keys()):
                    medley_title = track_qualifiers_dict["overall_title"]
                    self.add( (performanceURI, DTL.medley_title, Literal(medley_title)) )
                composer_arranger = []
                # create medley tune; composer either empty, or check if the same composer for all tunes
                for ptitle_dict, stitle_dict, composer_list in tunes_composers_list:
                    if len(composer_arranger) == 0:
                        composer_arranger = composer_list
                    else:
                        if composer_arranger != composer_list:
                            composer_arranger = []
                            break
                if len(composer_arranger) == 0:
                    medleyTuneURI = self.create_tune(trackTitle, [], [])
                elif "arr" in list(composer_arranger[0].keys()):
                    medleyTuneURI = self.create_tune(trackTitle, [], composer_arranger)
                else:
                    medleyTuneURI = self.create_tune(trackTitle, composer_arranger, [])
                # create Medley and connect to Performance
                self.add( (medleyTuneURI, RDF.type, DTL.Medley) )
                self.add( (performanceURI, DTL.medley, medleyTuneURI) )
                self.add( (medleyTuneURI, MO.performed_in, performanceURI) )
                ############### ordered list - multiple inheritance: Medley is a DTL.Medley and an OrderedList
                self.add( (medleyTuneURI, RDF.type, OLO.OrderedList) )
                self.add( (medleyTuneURI, OLO.length, Literal(str(len(tunes_composers_list))) ) )
                # iterate over tunes in medley
                for count, (ptitle_dict, stitle_dict, composer_list) in enumerate(tunes_composers_list):
                    tuneURI = self.tune_to_RDF(performanceURI, ptitle_dict, stitle_dict, composer_list)
                    # connect medleyTuneURI with each tune via ordered list ontology
                    oloslot = rdflib.BNode()
                    self.add( (oloslot, OLO.indexx, Literal(str(count)) ) )
                    self.add( (oloslot, OLO.item, tuneURI) )
                    self.add( (medleyTuneURI, OLO.slot, oloslot) )



    def create_rdf(self):

        # create parsers
        myparserinfo = self.MyParserInfo()
        self.dates_parser = DateParser(myparserinfo, 1900, 1959)
        self.musicians_instruments_parser = MusiciansInstrumentsParser()
        self.tunes_composers_parser = TunesComposersParser()
        # create label and release event
        if self.exists_label("Membran International GmbH"):
            labelURI = self.find_label("Membran International GmbH")
        else:
            labelURI = self.create_label("Membran International GmbH")
        if self.exists_releaseEvent(RELEASE_TITLE, RELEASE_DATE):
            releaseEventURI = self.find_releaseEvent(RELEASE_TITLE, RELEASE_DATE)
        else:
            releaseEventURI = self.create_release_event(RELEASE_TITLE, RELEASE_DATE)
        if not (labelURI, DTL.published, releaseEventURI) in self.g:
            self.add( (labelURI, DTL.published, releaseEventURI) )
        
        # read in csv
        ####################### csv module does not handle unicode?
        with open(DATA_CSV) as csvfile:
            logging.info("\nFrom file: %s", DATA_CSV)
            csvreader = csv.reader(csvfile, delimiter=',')
            tcount = -1 # on a CD
            pcount = 0 # parts 1 to 5 a 100 CDs
                        
            for count, row in enumerate(csvreader):
                logging.info("\nprocessing row %i:\n%s", count + 1, row)
                if row[0].startswith("CD"):
                    # a new CD
                    mediumTitle = row[3]
                    dnum = int(row[0].split()[1])                            
                    # create new part                    
                    if dnum == 1:
                        # iterate part
                        pcount = pcount + 1
                        # create album
                        title = ALBUM_TITLES[pcount-1]
                        if self.exists_album(title):
                            albumURI = self.find_album(title)
                        else:
                            albumURI = self.create_album(title)
                        # create release
                        if self.exists_release(title, 100):
                            releaseURI = self.find_release(title, 100)
                        else:
                            releaseURI = self.create_release(title, 100)
                        # connect the above
                        if not (albumURI, MO.published_as, releaseURI) in self.g:
                            self.add( (albumURI, MO.published_as, releaseURI) )
                        if not (releaseEventURI, MO.release, releaseURI) in self.g:
                            self.add( (releaseEventURI, MO.release, releaseURI) )

                    # check if medium exists
                    if self.exists_medium(mediumTitle, dnum):
                        mediumURI = self.find_medium(mediumTitle, dnum)
                        if (mediumURI, MO.track_count, None) in self.g:
                            # this CD is already in graph
                            logging.debug("CD already in graph")
                            tcount = -1
                            continue
                        else:
                            # CD is partly in graph, delete all triples created for this CD
                            logging.debug("CD partly in graph, deleting")
                            self.delete_medium(mediumURI)
                            logging.warning("Erased CD partially in graph, please restart")
                            raise Exception
                           
                    # create medium (track count will be added later)
                    mediumURI = self.create_medium(mediumTitle, dnum, 0)
                    self.add( (mediumURI, DC.title, Literal(row[3])) )
                    # connect medium to release
                    self.add( (releaseURI, MO.record, mediumURI) )
                    # prepare to collect data about the CD: track count, musicians
                    tcount = 0
                    area = ""
                    freetext_date = ""
                    band = ""
                    artistString = ""
                    # check live CD
                    if "live" in mediumTitle or "Live" in mediumTitle:
                        liveCD = True
                    else: liveCD = False
                    
                elif tcount >= 0 and re.match("[0-9]+", row[0]) != None:
                    # default case, row represents a track on a CD
                    tcount = tcount + 1
                    # add track
                    trackTitle = row[3]
                    tnum = row[0]
                    trackURI = self.create_track(trackTitle, tnum)
                    self.add( (mediumURI, MO.track, trackURI) )    
                    # add SoundSignal
                    signalURI = self.create_signal()
                    self.add( (signalURI, MO.published_as, trackURI) )
                    # add performance
                    performanceURI = self.create_performance(trackTitle)
                    self.add( (signalURI, DTL.captures, performanceURI) )
                    # parse tunes and composers
                    composerString = row[4]
                    try:
                        tunes_composers_list, track_qualifiers_dict = self.tunes_composers_parser.parse_tunes_composers(trackTitle, composerString)
                    except self.tunes_composers_parser.NrTunesException:
                        logging.warning("Line %i --- Nr of tunes != nr of composers! \nTrack title: %s\nComposers: %s\n not processing tunes and composers",count + 1, trackTitle, composerString)
                    if self.is_medley(tunes_composers_list, track_qualifiers_dict):
                        self.medley_to_RDF(performanceURI, trackTitle, tunes_composers_list, track_qualifiers_dict)
                    else:
                        ptitle_dict, stitle_dict, composer_list = tunes_composers_list[0]
                        self.tune_to_RDF(performanceURI, ptitle_dict, stitle_dict, composer_list)                                    
                    # session is defined by date, area and band name.
                    # when anything of the above has changed, create new session
                    # if not, just add performance - session link
                    ################# can a band have two distinct sessions on one day in one area? Ask jazz people
                    if tcount == 1:
                        # new CD, create new session
                        new_session = True
                        area = row[6]
                        freetext_date = row[7]
                        band = row[5]
                        sessionURI = self.session_to_RDF(area, band, freetext_date)                      
                    else:
                    ################## the way I am doing it is to check whether anything has changed from the last cycle run. Why not proper existence function?
                        logging.debug("session uri: %s", sessionURI)
                        logging.debug("old area: %s,        new area: %s", area, row[6])
                        logging.debug("old date: %s,        new date: %s", freetext_date, row[7])
                        logging.debug("old band: %s,        new band: %s", band, row[5])
                        new_session = False
                        if row[6] != area:
                            new_session = True
                            area = row[6]
                        if freetext_date != row[7]:
                            new_session = True
                            freetext_date = row[7]
                        if band != row[5]:
                            new_session = True
                            band = row[5]
                        if new_session:
                            sessionURI = self.session_to_RDF(area, band, freetext_date)
                        else:
                            logging.debug("session found")
                    # connect session with performance
                    self.add( (sessionURI, EVENT.sub_event, performanceURI) ) 
                    # parse musicians and instruments
                    artistString = row[8]
                    musicians, live, venue, unparsed = self.musicians_instruments_parser.parse_musicians_instruments(artistString)
                    if len(unparsed) > 0:
                        logging.warning("Line %i --- Unprocessed symbols in musicians/instruments string: %s\n%s", count + 1, unparsed, artistString)
                    bandURI = self.find_band(band)
                    for artist, instrument, confidence in musicians:
                        # find or create artist
                        yes = False
                        try:
                            yes = self.exists_artist(artist, bandURI)
                        except UnicodeDecodeError:
                            # rdflib sparql cannot handle non-ascii characters, therefore the exist/find funcitons
                            # raise an exception. In that case the code creates a new artist each time
                            logging.warning("Line %i --- UnicodeDecodeError! artist name: %s", count + 1, artist)
                            artistURI = self.create_artist(artist)
                        if yes:
                            artistURI = self.find_artist(artist, bandURI)
                        else:
                            artistURI = self.create_artist(artist)
                        # create performer
                        performerURI = self.create_performer(artistURI, instrument, confidence)
                        # connect with Performance
                        self.add( (performanceURI, MO.performer, performerURI) )
                    # set live and venue for Session
                    if int(live) or liveCD:
                        self.add( (sessionURI, DTL.is_live, Literal("1")) )
                    else:
                        self.add( (sessionURI, DTL.is_live, Literal("0")) )
                    if venue != None and len(venue) > 0:
                        ################### DTL.venue or EVENT.place? If latter, how to differentiate from area?
                        self.add( (sessionURI, DTL.venue, Literal(venue) ) )
                    ################# band leader: in Lord leaders and bandnames are the same thing

                elif tcount > 0 and len(row[0]) == 0:
                    # finished processing a CD, empty string
                    # add track count to the medium
                    self.add( (mediumURI, MO.track_count, Literal(tcount)) )
                    tcount = 0
                    # append the temporary graph to the rdf file
                    logging.debug("\nTemporary graph: \n%s", str(self.g_temp.serialize(format="turtle")))
                    logging.info("\nAppending RDF to: %s ...", rdffilename)
                    self.append_rdf_to_file(rdffilename, rdffilename_tmp)
                    logging.info("done")
                    # clear temporary graph
                    self.g_temp.remove( (None, None, None) )
                    logging.debug("\ng_temp cleared: \n%s", str(self.g_temp.serialize(format="turtle")))

                else:
                    # track already in graph
                    logging.info("skipping")


            # clean up at the end
            # correct olo:indexx to olo:index
            logging.info("\nCorrecting olo:indexx to olo:index ...")
            self.indexx2index()
            logging.info("Writing RDF to: %s ...", rdffilename)
            self.write_rdf_to_file(rdffilename, rdffilename_tmp)
            logging.info("done")
            #logging.debug(str(g.serialize(format='turtle')))


# create graphs
g = dtlutil.create_graph('JEGraphID')
g_temp = dtlutil.create_graph('JE_temp_GraphID')
dtlutil.read_in_rdf(g, rdffilename)
 
# create RDF
RDFcreator = JEtoRDF(g, g_temp)
RDFcreator.create_rdf()






        


        

    

    
                    

    
