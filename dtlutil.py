


##############################################################
# logging

from os.path import join
#from kitchen.text.converters import getwriter
import sys
import logging
import time   
import os 

PATH_LOG = "PyLOG/"
SCRIPT_NAME = os.path.splitext(os.path.basename(sys.argv[0]))[0]

now = time.strftime("%y-%m-%d_%H:%M:%S", time.gmtime())
logfilename = "LOG_" + SCRIPT_NAME + "_" + now + ".txt"
logfilename = join(PATH_LOG, logfilename)

##UTF8Writer = getwriter("utf8")
##sys.stdout = UTF8Writer(sys.stdout)

#logging.basicConfig(filename=logfilename, format='%(levelname)s:%(message)s', level=logging.DEBUG)
#logging.getLogger().addHandler(logging.StreamHandler())

class LogFilter(logging.Filter):
    """Filters (lets through) all messages with level < LEVEL"""
    def __init__(self, level):
        self.level = level
    def filter(self, record):
        return record.levelno < self.level

def setup_log(MIN_LEVEL = logging.DEBUG):
    # messages lower than WARNING go to stdout
    # messages >= WARNING (and >= STDOUT_LOG_LEVEL) go to stderr
    stdout_hdlr = logging.StreamHandler(sys.stdout)
    stderr_hdlr = logging.StreamHandler(sys.stderr)
    log_filter = LogFilter(logging.WARNING)
    stdout_hdlr.addFilter(log_filter)
    stdout_hdlr.setLevel(MIN_LEVEL)
    stderr_hdlr.setLevel(max(MIN_LEVEL, logging.WARNING))
    stdout_formatter = logging.Formatter("%(message)s")
    stdout_hdlr.setFormatter(stdout_formatter)
    stderr_formatter = logging.Formatter("%(levelname)s - %(message)s")
    stderr_hdlr.setFormatter(stderr_formatter)

    # log to file
    file_hdlr_std = logging.FileHandler(logfilename)
    file_hdlr_std.addFilter(log_filter)
    file_hdlr_std.setLevel(MIN_LEVEL)
    file_hdlr_err = logging.FileHandler(logfilename)
    file_hdlr_err.setLevel(max(MIN_LEVEL, logging.WARNING))
    file_formatter_std = logging.Formatter("%(message)s")
    file_hdlr_std.setFormatter(file_formatter_std)
    file_formatter_err = logging.Formatter("%(levelname)s - %(message)s")
    file_hdlr_err.setFormatter(file_formatter_err)

    rootLogger = logging.getLogger()
    rootLogger.handlers.clear()        #SD added to prevent duplicate entries
    rootLogger.addHandler(stdout_hdlr)
    rootLogger.addHandler(stderr_hdlr)
    rootLogger.addHandler(file_hdlr_std)
    rootLogger.addHandler(file_hdlr_err)
    logger = logging.getLogger(__name__)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

##############################################################

# create rdf graph

import rdflib
from rdflib.graph import Graph, Store, URIRef, Literal, BNode
from rdflib.namespace import Namespace, RDFS
from rdflib import plugin
from rdflib.plugins import sparql
from rdflib import Namespace
from rdflib.namespace import RDF, FOAF, RDFS, DC, XSD, OWL

MO = Namespace("http://purl.org/ontology/mo/")  #MusicOntology
TL = Namespace("http://purl.org/NET/c4dm/timeline.owl#")    #Timeline
EVENT = Namespace("http://purl.org/NET/c4dm/event.owl#")
OLO = Namespace("http://purl.org/ontology/olo/core#")   #Ordered List Ontology
DTL = Namespace("http://www.DTL.org/schema/properties/") #DigThatLick fake

DBP = Namespace("http://dbpedia.org/resource/")  #DBpedia
REL = Namespace("http://purl.org/vocab/relationship/")
LJ = Namespace("http://linkedjazz.org/ontology/")


initNs = { "RDF": RDF, "DC": DC, "MO": MO, "TL": TL, "EVENT": EVENT, 
      "DTL": DTL, "XSD": XSD, "FOAF": FOAF, "OLO": OLO, "DBP": DBP, "REL": REL, "LJ": LJ}

# create name spaces
def init_namespaces():
    return MO, TL, EVENT, OLO, DTL, initNs

def LOD_namespaces():
    return DBP, REL, LJ

# create graph
def create_graph(graph_id = URIRef(SCRIPT_NAME + '_GraphID')):
    memory_store = plugin.get('IOMemory', Store)()
    g = Graph(store=memory_store, identifier=graph_id)
    
    g.bind('mo', MO) 
    g.bind('tl', TL)
    g.bind('event', EVENT) 
    g.bind('dtl', DTL)
    g.bind('dc', DC)
    g.bind('xsd', XSD)
    g.bind('foaf', FOAF)
    g.bind('olo', OLO)
    g.bind('dbp', DBP)
    g.bind('rel', REL)
    g.bind('lj', LJ)

    return g

# read in existing turtle
def read_in_rdf(g, RDFfile, exists=False, myformat = 'turtle'):
    logging.info("Reading rdf from %s ...", RDFfile)
    from os.path import isfile
    if isfile(RDFfile):
        g.parse(RDFfile, format = myformat)
        logging.debug("done")
    else:
        if exists:
            logging.error("No rdf file %s found", RDFfile)
        else:
            logging.warning("No rdf file %s found", RDFfile)
    return g

####################################################################

def create_uri(forWhat, uid):
    uri = "http://www.DTL.org/JE/" + forWhat +"/" + str(uid)
    return URIRef(uri)

def find_class(query):
    result = self.g.query (query)
    if len(result) == 0:
        return None
    elif len(result) > 1:
        raise MultipleRDFfoundWarning(query, result)
    for row in result:
        logging.debug(row)
        return row[0]

def get_id(uri):
    """ getting uid from URIs of the form : "http://www.DTL.org/JE/sessions/08ba77c8-5618-4827-b013-027af2b7cd90"
    """
    return uri.split("/")[-1]

def get_class_name(uri):
    """ getting class name "sessions" from URIs of the form : "http://www.DTL.org/JE/sessions/08ba77c8-5618-4827-b013-027af2b7cd90"
    """
    return uri.split("/")[-2]


######################################################################
# JE info

RELEASE_TITLE = "The Encyclopedia of Jazz: The World's Greatest Jazz Collection"
RELEASE_DATE = "2008-10-24"
ALBUM_TITLES = ["The Encyclopedia of Jazz, Part 1: Classic Jazz - From New Orleans to Harlem", \
                "The Encyclopedia of Jazz, Part 2: Swing Time - The Heyday of Jazz", \
                "The Encyclopedia of Jazz, Part 3: Big Bands - The Giants of the Swing Big Band Era", \
                "The Encyclopedia of Jazz, Part 4: Bebop Story - A Musical Revolution That Radically Changed the Road of Jazz",
                "The Encyclopedia of Jazz, Part 5: Modern Jazz - Cool Jazz"]

def get_JE_release_title():
    return RELEASE_TITLE

def get_JE_release_date():
    return RELEASE_DATE

def get_JE_parts():
    return ALBUM_TITLES

def get_JE_part(number):
    return ALBUM_TITLES[number - 1]


######################################################################

import json
def write_json(data, jsonfile):
    with open(jsonfile, mode='tw+') as mmfile:
        try:
            logging.info("writing to %s", jsonfile)
            json.dump(data, mmfile)
            logging.debug("done")
        except Exception:
            logging.error("cannot write to %s", jsonfile)

import csv
def write_csv(data, csvfile):
    with open(csvfile, 'w+', newline='') as f:
        writer = csv.writer(f, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        logging.info("writing to %s", csvfile)
        for row in data:
            writer.writerow(row)
    logging.debug("done")
    

def write_rdf(g, RDFnewfile):
#    with open(RDFnewfile, mode='tw') as newrdf:
    try:
        logging.info("\nwriting rdf to %s", RDFnewfile)
        g.serialize(destination = RDFnewfile, format = 'turtle')
        logging.debug("done")
    except Exception:
        logging.error('cannot write RDF triples to file %s', RDFnewfile)

from os.path import isfile
from shutil import copyfile

def write_rdf_with_temp(g, rdffilename, rdffilename_tmp):
    if isfile(rdffilename):
        copyfile(rdffilename, rdffilename_tmp)
    write_rdf(g, rdffilename)

def append_rdf_with_temp(g_temp, rdffilename, rdffilename_tmp):
    if isfile(rdffilename):
        copyfile(rdffilename, rdffilename_tmp)
    with open(rdffilename, mode='ta', newline="\n") as rdf:
        logging.info("Appending RDF to %s", rdffilename)
        try:
            gstring = g_temp.serialize(format='turtle', encoding="utf-8").decode('utf-8')
            rdf.write(gstring)
        except Exception:
            logging.error('cannot append RDF triples to %s', rdffilename)
    logging.debug("done")

def append_and_clear_temp_graph(g_temp, rdffilename, rdffilename_tmp):
# append the temporary graph to the rdf file
#    logging.debug("\nTemporary graph: \n%s", str(self.g_temp.serialize(format="turtle")))
    append_rdf_with_temp(g_temp, rdffilename, rdffilename_tmp)
    # clear temporary graph
    g_temp.remove( (None, None, None) )
#    logging.debug("\ng_temp cleared: \n%s", str(g_temp.serialize(format="turtle")))
    return g_temp


######################################################################
# dates

import re
import datetime
from dateutil.parser import parse as parsedate
from dateutil.parser import parserinfo
from dateParser import DateParser

class MyParserInfo(parserinfo):
    def convertyear(self, year, *args, **kwargs):
        if year < 100:
            year += 1900
        return year 


def create_date(g, date):
    eventnode = rdflib.BNode()
    g.add( (eventnode, RDF.type, TL.Instant) )
    g.add( (eventnode, TL.at, Literal(date)) ) 
    g.add( (eventnode, TL.timelime, TL.universaltimeline) )
    return eventnode
#         event:time [
#         a tl:Instant;
#         tl:at "2007-10-15T12:00:00"^^xsd:dateTime;
#         ];
def create_time_interval(g, start, end):
    eventnode = rdflib.BNode()
    g.add( (eventnode, RDF.type, TL.Interval) )
    g.add( (eventnode, TL.at, Literal(start)) )
    g.add( (eventnode, TL.duration, Literal(str(end-start)) ) )
    g.add( (eventnode, TL.timelime, TL.universaltimeline) )
    return eventnode


def create_qualified_date(g, freetext_date, startdate, enddate, is_apprx = True, apprxq = None):
    if startdate != enddate:
        timespan_node = create_time_interval(g, startdate, enddate)
        g.add( (timespan_node, RDF.type, DTL.QualifiedDateInterval) )
    else:
        timespan_node = create_date(g, startdate)
        g.add( (timespan_node, RDF.type, DTL.QualifiedDateInstant) )
    g.add( (timespan_node, DTL.freetext_timespan, Literal(freetext_date)) )
    g.add( (timespan_node, DTL.is_approximate, Literal(str(int(is_apprx)))) )
    if apprxq != None:
        g.add( (timespan_node, DTL.approximation_qualifier, Literal(apprxq)) )
#    logging.debug("Qualified date created")
    return timespan_node


def add_qualified_date(g, sessionURI, freetext_date, datekwargs):
    """
    kwresults['startdate'] = startdate
    kwresults['enddate'] = enddate
    kwresults['is_approximate'] = self.IS_APPROXIMATE
    kwresults['apprx'] = self.MYAPPRX
    kwresults['period_list'] = self.MYPERIOD
    kwresults['season_list'] = self.MYSEASON

     - startdate as datetime
     - enddate, same as startdate for single dates
     - IS_APPROXIMATE boolean; any date with a approximation qualifier or if month, season, year \
             are given but not a day; "between ... and ..." as well as "from ... to ..." also considered
             approximate
     - approximation qualifier, "" if no qualifier present
    """
    # unpack kwargs
    startdate = datekwargs["startdate"]
    enddate = datekwargs["enddate"]
    is_apprx = datekwargs["is_approximate"]
    apprxq = datekwargs["apprx"]
    if len(apprxq) == 0:
        apprxq = None
    # create a bnode
    timespan_node = create_qualified_date(g, freetext_date, startdate, enddate, is_apprx, apprxq)
    # connect bnode to Session
    g.add( (sessionURI, EVENT.time, timespan_node) )


def add_datestr(g, sessionURI, freetext_date):       
    myparserinfo = MyParserInfo()
    dates_parser = DateParser(myparserinfo, 1900, 2019)
    
    datekwargs = dates_parser.parse_freetext_date(freetext_date)
    if len(datekwargs) > 0:
        add_qualified_date(g, sessionURI, freetext_date, datekwargs)
            
#######################################################
# timelines

def create_timeline(g, uri):
    # e.g. performance timeline to place solos
    uid = get_id(uri)
    classname = get_class_name(uri)
    timelineURI = create_uri(classname + "_timelines", uid)
    g.add( (timelineURI, RDF.type, TL.RelativeTimeLine) )
    g.add( (uri, TL.onTimeLine, timelineURI) )
    return timelineURI

def find_timeline(g, uri):
    uid = get_id(uri)
    classname = get_class_name(uri)
    timelineURI = create_uri(classname + "_timelines", uid)
    if timelineURI in g.objects(uri, TL.onTimeLine):
        return timelineURI
    return None

def exists_timeline(g, uri):
    return find_timeline(g, uri) != None
