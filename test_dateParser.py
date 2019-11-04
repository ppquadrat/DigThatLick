# Python3

TESTFILE = "DATA/JEdates.csv"


import csv
from dateParser import DateParser
from dateutil.parser import parserinfo

# logging
import dtlutil
import logging
MIN_LEVEL = logging.DEBUG
dtlutil.setup_log(MIN_LEVEL)


#####################################################


class MyParserInfo(parserinfo):
    def convertyear(self, year, *args, **kwargs):
        if year < 100:
            year += 1900
        return year

line = "January 7  and   Portl"
parserinfo = MyParserInfo()
dtprsr = DateParser(parserinfo, 1900, 2019)
dtprsr.parse_freetext_date(line)


### this should throw my exception
##line = "1972 Phi Mu Alpha Jazz Festival, South Shelby & Troy, MO, 1972"
##parserinfo = MyParserInfo()
##dtprsr = DateParser(parserinfo, 1900, 2019)
##dtprsr.parse_freetext_date(line)
                           

##lst =  ["30/10/1923", 
##        "June 1923", 
##        "ca. September 1924", 
##        "17.- 22.1.1924", 
##        "early December 1924", 
##        "January, 1925", 
##        "ca. January, 1927", 
##        "about August, 1928", 
##        "May (8-15), 1923", 
##        "July 28/August 1, 1924", 
##        "about mid November, 1928", 
##        "ca. February 9-14, 1925", 
##        " 23-29. 3. 1955", 
##        "between 27. 2. and 17. 3. 1941", 
##        "March/April 1946", 
##        "(first half of) June 1952", 
##        "08. or 12.03.1946", 
##        "23. & 24.02.1944", 
##        "September 1941/42", 
##        "spring (poss. May 30) 1945", 
##        "January-February  1946", 
##        "late summer 1950", 
##        "ca. fall 1950", 
##        "mid winter 42", 
##        "January 22 or 23, 1952", 
##        "late 1943", 
##        "November 11/12, 1955", 
##        "prob. June 1946", 
##        "end 1946", 
##        "poss. October 1950", 
##        "spring & summer 1953", 
##        "June 11, 1955",
##        "ca. early 1941(?)",
##        "July 24, 25 & 31, 1956",
##        "May 31, June 1, 2 & 3, 1960",
##        "October & November 1981",
##        "January, February & March, 1974",
##        "June 22 & July 11, 1995",
##        "January 29-31 & February 1, 1992",
##        "June 13, 15, 26 & 28, 1995",
##        "March 13, 2003-October 25, 2004",
##        "1950's - 1960s",
##        "early 1960's",
##        "late 1968 - 1969",
##        "late 1960s - early 1970s",
##        "2000 - early 2001",
##        "2001 & winter 2002"]
##
##for count, datestr in enumerate(lst):
##     logging.info("\nline %i",count)
##     parserinfo = MyParserInfo()
##     dtprsr = DateParser(parserinfo, 1900, 2020)
##     dtprsr.parse_freetext_date(datestr)
                    

##with open(TESTFILE, 'r') as f:
##    for count, line in enumerate(f):
##        if len(line.strip()) > 0:
##             logging.info("\nline %i",count)
####             print line
##             line = line.strip("\n\" ")
##             parserinfo = MyParserInfo()
##             dtprsr = DateParser(parserinfo, 1900, 2020)
##             dtprsr.parse_freetext_date(line)
##
    
