# -*- coding: utf-8 -*-
# Python3

"""
parse musicians and instrument from Jazz Encyclopedia csv file

use:
from musiciansInstrumentsParser import MusiciansInstrumentsParser
parser = MusiciansInstrumentsParser()
parser.parse_session_participants(string)

returns:

 - a list of triples: artist, instrument, confidence
         confidence is boolean, usually means there was a "?"; an unknown artist does not trigger confidence=0
 - live: a boolean set to 1 if there was a 'live' qualifier
 - venue: a string if a venue was given, otherwise None
 - unparsed: symbols after the last ')' - the string is expected to end with ')'


Examples:
        "George Mitchell (c), Kid Ory (tb), Omer Simeon (cl), Jelly-Roll Morton (p, a), Johnny St. Cyr (bj), John Lindsay (sb), Andrew Hilaire (d).",
        "Ed Allen, ?Ed Anderson (c),",
        "Memphis (comb),",
        "Ray Bowling, unknown (t), unknown (tb), (as), (ts), Jelly Roll Morton (p), Clay Jefferson (d).",
        "unknown (as, bar, bsx),",
        "Ray Miller (dir):",
        "Walter Pichon (v, p), acc. by Henry ‚ÄòRed‚Äô Allen (t), Teddy Bunn (g).",
        "Earl Hines (p) solo.",
        "Lonnie Johnson & Eddie Lang (g-duet).",
        "unknown (Wingy Manone?) (t),",
        "Fats Waller, Bennie Paine (p) duet.",
        "James P. Johnson (p-solo).",
        "Bob Conselman (d?, vib).",
        "Elmer Chambers, poss. Joe Smith (c), ? George Brashear (tb), Don Redman & another (cl, sax), Fletcher Henderson (p), prob. Charlie Dixon (bj).",
        "Louis Armstrong (c or t)¬†,",
        " Fred Longshaw (or, p)",
        "Butterbeans & Susie (v)",
        "Bix Beiderbecke (?) (c)",
        "Duke Ellington & Billy Strayhorn (p),",
        "Count Basie (as 'Prince Charming') (p)",
        "One or two (t), (tb), one or two (s), (p), (g), (sb), (d).",
        "Billy Banks (v) acc. by (t), 2 (as), (ts), (p), (g), (sb), (d) from regular MBRB personnel.",
        "Billy Banks (v) acc. by Bill Coleman (t), (tb), (cl, as), (as), (ts), Edgar Hayes (p), Bill Johnson (g), Pops Foster (sb), Joseph Smith (d), from regular MBRB personnel.",
        "Dizzy Gillespie & unknown (t),",
        "Charlie Parker, unaccompanied (as)",
        "Dizzy Gillespie (as "B. Bopstein" on label) (t),",
        "Dizzy Gillespie (as "Izzie Goldberg" on label) (t),",
        "Neal Hefti (a, cond):",
        "Unknown personnel, including: Joe Swanson (tb), Buddy Collette (as, fl), Wardell Gray(ts), Gerald Wiggins (p), Joe Comfort (sb).",
        "Live, Confucius Restaurant: Lee Konitz (as), Lennie Tristano (p), Gene Ramey (sb), Arthur Taylor (d).",
        "Live, ‚ÄúStoryville Club‚Äù: Stan Getz (ts), Al Haig (p), Jimmy Raney (g), Teddy Kotick (sb), Tony Kahn (d).",
        "Live, ‚ÄúThe Lighthouse‚Äù: Chet Baker, Rolf Ericson (t), Bud Shank (as, bar), Bob Cooper (ts), Claude Williamson (p), Howard Rumsey (sb),",
        "unknown or Jack Roth (2nd p)",
        "Unknown (as or Cm or ts)",
        "Possibly: Fletcher Henderson (p, dir): Elmer Chambers, Joe Smith, Louis Armstrong  (t),",
        "poss. Ed Cuffee (tb),",
        "possibly Albert Nicholas (cl, as),",
        "Joe Smith (t, poss. mel),",
        "Poss. Mert Oliver (sb),",
        "Paul Desmond (as), Dave Brubeck (p), Ron Crotty (sb), Joe Dodge (d).  Live, ‚ÄúCollege of the Pacific‚Äù",
        "Erroll Garner (p), Eddie Calhoun (sb), Denzil Best (d). Live concert",
        "Bud Powell (p), Charles Mingus (sb), Max Roach (d). Live, Massey Hall",
        "Live, Poss. Crescendo Club:",
        "Julian ‚ÄúCannonball‚Äù Adderley (as) acc. by large orchestra incl. strings. Richard Hayman (a, cond.).",
        "Sam Jones (sb, vc -1), Al McKibbon (sb -2), "

Polina Proutskova
March 2019

"""

# general import
from os.path import join
import re
import logging


class MusiciansInstrumentsParser():
    
    IGNORE = ["acc. by", "unaccompanied", "solo", "duet", "2nd", "Unknown personnel", "including"]
    POSSIBLY = ["poss.", "possibly", "Poss.", "Possibly", "(?)", "?", "prob.", "Prob.", "probably", "Probably"]
    UNKNOWN = ["another", "one or two", "One or two", "two unknown", "two ", "Two ","2 unknown", "2 "]

    def parse_musicians_instruments(self, artistString):
        logging.debug("parsing musicians and instruments:...\n%s", artistString)
        live = 0
        venue = None
        musicians = []

        # venue
        if artistString.startswith("Live"):
            logging.debug("live")
            live = 1
            lst = re.split("[,:]", artistString)
            venue = lst[1].strip()
            logging.debug("Venue: %s", venue)
            artistString = ",".join(lst[2:])
        if re.search(". +Live", artistString) != None:
            logging.debug("live")
            live = 1
            lst = re.split(". +Live", artistString, 1)
            artistString = lst[0]
            if "," in lst[1]:
                venue = lst[1].split(",", 1)[1].strip()
                logging.debug("Venue: %s", venue)
        # inconsistent use of ":"
        for word in self.POSSIBLY:
            if word + ":" in artistString:
                artistString = artistString.replace(word + ":", word)
        artistString = artistString.replace(":", ",")
        # inconsistent use of ","
        artistString = artistString.replace(") acc. by", "),")
        # forms of "unknown"
        for word in self.UNKNOWN:
            if word in artistString:
                artistString = artistString.replace(word, "unknown")

        # split on each ")," into session participants
        lst = artistString.split("),")
        lstend = lst[-1].strip(" .").rsplit(")", 1)
        if len(lstend) == 1 and len(lstend[0]) == 0:
            unparsed = ","
        elif len(lstend) == 1:
            unparsed = lstend[0]
        else:
            lst[-1] = lstend[0]
            unparsed = lstend[1]
        logging.debug("split list: %s, unparsed: %s", lst, unparsed)
        for musicianString in lst:
            musicianString = musicianString.strip()
            logging.debug("session-participant string: %s", musicianString)
            if "(" in musicianString:
                if musicianString.startswith("("):
                    # only instrument given, e.g. "(as),"
                    logging.debug("only instrument given")
                    musicianString = "Unkonwn" + musicianString
                # remove anything after the last ")", like in "(d) from regular MBRB personnel."
                # yet not in "unknown (Eddie Lang or DickMcDonough) (g"
                if ")" in musicianString:                   
                    lastclose = musicianString.rfind(")")
                    lastopen = musicianString.rfind("(")
                    if lastclose > lastopen:
                        musicianString = musicianString.rsplit(")", 1)[0]  # on the last ')', only keep the first bit
                        logging.debug("tail removed: %s", musicianString)
                # split into musicians and instruments on the last "("
                lst2 = musicianString.rsplit("(", 1)
                logging.debug("split: %s", lst2)
                artStr = lst2[0].strip()
                instStr = lst2[1]
                logging.debug("artist string: %s	 instrument string: %s ", artStr, instStr)
                # if several artists listed, separate
                if artStr.count("&") > 0:
                    artList = artStr.split(" & ")
                elif artStr.count(" or ") > 0:
                    artList = artStr.split(" or ")
                    for idx in range(len(artList)):
                        artList[idx] += "?"
                else:
                    artList = artStr.split(", ")
                # if several instruments listed, separate
                if instStr.count(" or ") > 0:
                    instList = instStr.split(" or ")
                    for idx in range(len(instList)):
                        instList[idx] += "?"
                else:
                    instList = instStr.split(", ")
                logging.debug("artists list: %s", artList)
                logging.debug("instruments list: %s", instList)
                # return each combination of artists and instruments
                for artist in artList:
                    artist_confidence = 1
                    for word in self.POSSIBLY:
                        if artist.count(word) > 0:
                            artist = artist.replace(word, "").strip(" -")
                            artist_confidence = 0
                    for word in self.IGNORE:
                            if artist.count(word) > 0:
                                artist = artist.replace(word, "").strip(" -")
                    for instrument in instList:
                        instrument_confidence = 1
                        for word in self.POSSIBLY:
                           if instrument.count(word) > 0:
                                instrument = instrument.replace(word, "").strip(" -")
                                instrument_confidence = 0
                        for word in self.IGNORE:
                            if instrument.count(word) > 0:
                                instrument = instrument.replace(word, "").strip(" -")
                        # add to musicians list
                        if len(artist) > 0 and len(instrument) > 0:        
                            confidence = artist_confidence, instrument_confidence
                            musicians.append( (artist, instrument, confidence) )                  
                            logging.debug("artist: %s, instrument: %s, confidence: %s", artist, instrument, confidence)

            else:
                # no "(" in string - ignore
                logging.debug("ignore")

        if len(unparsed) > 0:
            logging.debug("unparsed: %s", unparsed)

        return musicians, live, venue, unparsed
                              
        

