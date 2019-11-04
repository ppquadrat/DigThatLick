# -*- coding: utf-8 -*-
# Python3

TESTFILE = "DATA/JEmusiciansInstruments.csv"

# general import
from musiciansInstrumentsParser import MusiciansInstrumentsParser
import csv

# logging
import dtlutil
import logging
MIN_LEVEL = logging.DEBUG
dtlutil.setup_log(MIN_LEVEL)


#####################################################


weirdlist = ["George Mitchell (c), Kid Ory (tb), Omer Simeon (cl), Jelly-Roll Morton (p, a), Johnny St. Cyr (bj), John Lindsay (sb), Andrew Hilaire (d).",
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
        """Dizzy Gillespie (as "B. Bopstein" on label) (t),""",
        """Dizzy Gillespie (as "Izzie Goldberg" on label) (t),""",
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
        "Sam Jones (sb, vc -1), Al McKibbon (sb -2), "]

##parser = MusiciansInstrumentsParser()
##line = """Count Basie (p, dir): Clark Terry (t), Buck Clayton (t), two unknown (cl, as)."""
##sessionParticipants, live, venue, unparsed = parser.parse_musicians_instruments(line)
                              
##for count, string in enumerate(weirdlist):
##     logging.info("\nline %i",count)
##     parser = MusiciansInstrumentsParser()
##     parser.parse_musicians_instruments(string)
                    
with open(TESTFILE, 'r') as f:
    for count, line in enumerate(f):
        if len(line.strip()) > 0:
            logging.info("\nline %i",count)
            print(line)
            line = line.strip("\n\" ")
            parser = MusiciansInstrumentsParser()
            parser.parse_musicians_instruments(line)

    
