# Python 3.7.3

""" Match musicians from Jazz Encyclopedia repository to those collected by LinkedJazz.
    The match is done by name
    
    Polina Proutskova, October 2019
"""

##############################################################
# paths
RDFfile = "TTL/ILL1000_styles.ttl"
NTfile = "DATA/LJpeople.nt"
RDFnewfile = "TTL/ILL1000_LODpeople.ttl"


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
from rdflib.namespace import RDF, FOAF, RDFS, DC, XSD, OWL

MO, TL, EVENT, OLO, DTL, initNs = dtlutil.init_namespaces()
DBP, REL, LJ = dtlutil.LOD_namespaces()

g = dtlutil.create_graph()
dtlutil.read_in_rdf(g, RDFfile)

ljg = dtlutil.create_graph("LJgraph")
dtlutil.read_in_rdf(ljg, NTfile, myformat = "nt")

##############################################################

mcount = 0
lodcount = 0
for musician in g.subjects(RDF.type, MO.MusicArtist):
    name = g.value(musician, FOAF.name)
    mcount +=1
    for LODmusician in ljg.subjects(predicate=FOAF.name, object=Literal(name, lang = "en")):
        logging.info("found match for musician %s in DB: %s", name, LODmusician)
        g.add( (musician, OWL.sameAs, LODmusician) )
        lodcount +=1

################################################
logging.info("\nSTATS")
logging.info("%i LOD musicians associated of %i musicians", lodcount, mcount)


dtlutil.write_rdf(g, RDFnewfile)
