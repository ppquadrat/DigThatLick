# Python3

""" relating bands to leaders:
    each musician whose name occurs in the band name is a leader

    Polina Proutskova
    September 2019
"""

##############################################################
# paths

RDFfile = "TTL/ILL1000_191101_bands.ttl"
RDFnewfile = "TTL/ILL1000_191101_leaders.ttl"


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

def find_band_musicians(bandURI):
    band_name = g.value(subject=bandURI, predicate=FOAF.name, object=None, default=None, any=True)
    sessionURI = g.value(subject=None, predicate=MO.performer, object=bandURI)
    logging.debug("session: %s", str(sessionURI))
    # logging.debug("found musicians:")
    musicianURIs = []
    for performanceURI in g.objects(subject=sessionURI, predicate=EVENT.sub_event):
        for performerURI in g.objects(performanceURI, MO.performer):
            musician = g.value(performerURI, DTL.musician)
            if not musician in musicianURIs:
                musicianURIs.append(musician)
                musicianname = g.value(musician, FOAF.name)
                #logging.debug(musicianname + ", " + str(musician))
    if len(musicianURIs) == 0:
        logging.warning("no musicians found for band %s", band_name)
    return musicianURIs
        

##def find_band_musicians(bandURI):
##    band_name = g.value(subject=bandURI, predicate=FOAF.name, object=None, default=None, any=True)
##    qstr =  """SELECT DISTINCT ?musician 
##            WHERE {
##                ?session MO:performer <%s> .
##                ?session EVENT:sub_event ?performance .
##                ?performance MO:performer ?performer .
##                ?performer DTL:musician ?musician .
##            } """ %bandURI
##    logging.debug(qstr)
##    q = rdflib.plugins.sparql.prepareQuery(qstr, initNs)
##    found = g.query(q)
##    if found == None or len(found) == 0:
##        logging.warning("no musicians found for band %s", band_name)
##        return None
##    else:
##        musicianURIs = []
##        logging.debug("found musicians:")
##        for row in found:
##            musician = row[0]
##            musicianURIs.append(musician)
##            musicianname = g.value(musician, FOAF.name)
##            logging.debug(musicianname)
##        return musicianURIs
        

bands_count = 0
leaders_count = 0
for bandURI in g.subjects(RDF.type, MO.MusicGroup):
    band_name = g.value(bandURI, FOAF.name)
    bands_count += 1
    logging.debug("\n%i: looking for leader of band %s", bands_count, band_name)
    musicianURIs = find_band_musicians(bandURI)
    for musicianURI in musicianURIs:
        musician_name = g.value(musicianURI, FOAF.name)
        logging.debug("musician: %s", musician_name)
        musician_name = musician_name.replace("\'", "")
        if musician_name.lower() in band_name.lower():
            g.add( (bandURI, DTL.has_leader, musicianURI) )
            leaders_count += 1
            logging.info("Leader %s linked to band %s", musician_name, band_name)


####################################################################

logging.info("\n###########################\n%i leaders linked to %i bands", leaders_count, bands_count)

# write rdf
dtlutil.write_rdf(g, RDFnewfile)
        
