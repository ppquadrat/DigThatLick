# Python 3.7.3

""" adds musician relationships to the JE rdf repository
    
    Polina Proutskova, October 2019
"""

##############################################################
# paths
RDFfile = "TTL/JE_PyRDF_musicians_leaders_LOD.ttl"
RDFnewfile = "TTL/JE_PyRDF_relationships.ttl"


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

##############################################################

for sessionURI in g.subjects(EVENT.place, None):
    """ get band, bandname
        get leader, leader name (opt)
        for performances in session:
            get performer
            collect musicians
        for each musician:
            lj:bandmember
            lj:bandLeaderOf
            with each other musician:
                rel:knowsOf
                rel:hasMet
                mo:collaborated_with
                lj:inBandTogether
                lj:playedTogether
        
    """
    bandURI = g.value(sessionURI, MO.performer)
    bandname = g.value(bandURI, FOAF.name)
    leaderURI = g.value(bandURI, DTL.has_leader)

    for performanceURI in g.objects(sessionURI, EVENT.sub_event):
        musicians = []
        for performerURI in g.objects(performanceURI, MO.performer):
            musicianURI = g.value(performerURI, DTL.musician)
            musicians.append(musicianURI)
        for musician in musicians:
            mname = g.value(musician, FOAF.name)
            triple = (musician, LJ.bandmember, bandURI)
            if not triple in g:
                g.add(triple)
                logging.debug("%s band member of %s", mname, bandname)
            if leaderURI != None:
                triple = (leaderURI, LJ.bandLeaderOf, musician)
                if not triple in g:
                    g.add(triple)
                    logging.debug("%s band leader of %s", g.value(leaderURI, FOAF.name), mname)
            for musician1 in musicians:
                if musician1 != musician:
                    m1name = g.value(musician1, FOAF.name)
                    triple = (musician, REL.knowsOf, musician1)
                    if not triple in g:
                        g.add(triple)
                        logging.debug("%s knows of %s", mname, m1name)
                    triple = (musician, REL.hasMet, musician1)
                    if not triple in g:
                        g.add(triple)
                        logging.debug("%s has met %s", mname, m1name)
                    triple = (musician, MO.collaborated_with, musician1)
                    if not triple in g:
                        g.add(triple)
                        logging.debug("%s collaborated with %s", mname, m1name)
                    triple = (musician, LJ.inBandTogether, musician1)
                    if not triple in g:
                        g.add(triple)
                        logging.debug("%s in band together with %s", mname, m1name)
                    triple = (musician, LJ.playedTogether, musician1)
                    if not triple in g:
                        g.add(triple)
                        logging.debug("%s played together %s", mname, m1name)
                    
            

dtlutil.write_rdf(g, RDFnewfile)
        
