# Python3

""" Parser for location / time string from Lord

    Polina Proutskova, July - September 2019
"""

import re
import logging

class LordAreaDateParser():
##    class UnparsableAreaDateStringWarning(Warning):
##        """ raised when the date area string cannot be parsed """
##        def __init__(self, session_areadate_str):
##            self.message = """area-date string   %s    cannot be parsed""" %session_areadate_str


    def parse_area_date_str(self, session_areadate_str):
        MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        SEPARATORS = [", ca. ", "early","late", ", c. "]
        UNKNOWN = ["unidentified", "same", "unknown", "similar", "Unknown", "from this period", \
                   "prob from this period", "prob. from this period", "possibly from the above broadcast",\
                   "concert continues", "prob. same session", "poss. from this period", "details unknown"]
        areastr = None
        datestr = None
        for month in MONTHS:
            if month in session_areadate_str:
                datestartidx = session_areadate_str.index(month)
                areastr = session_areadate_str[0:datestartidx]
                datestr = session_areadate_str[datestartidx:]
                break
        if (areastr == None or datestr == None):
            for exp in UNKNOWN:
                if exp in session_areadate_str:
                    datestartidx = session_areadate_str.index(exp)
                    areastr = session_areadate_str[0:datestartidx]
                    datestr = ""
        if (areastr == None or datestr == None):
            for sep in SEPARATORS:
                if sep in session_areadate_str:
                    datestartidx = session_areadate_str.index(sep)
                    areastr = session_areadate_str[0:datestartidx]
                    datestr = session_areadate_str[datestartidx:]
                    break
        if (areastr == None or datestr == None):
            if session_areadate_str.strip() == "":
                areastr = ""
                datestr = ""
        if (areastr == None or datestr == None):
            datestart = re.search("[0-9]{4}", session_areadate_str)
            if datestart != None :
                datestartidx = datestart.start(0)
                areastr = session_areadate_str[0:datestartidx]
                datestr = session_areadate_str[datestartidx:]
                
        if (datestr == None):
            areastr = session_areadate_str
            datestr = ""
#            raise self.UnparsableAreaDateStringWarning(session_areadate_str)
##            logging.warning("time and area string %s could not be parsed properly", session_areadate_str)
##            areastr = session_areadate_str
##            datestr = ""
    #        raise Exception("date_time_string " + session_areadate_str + " cannot be parsed")
        
        if ", c. " in datestr:
            datestr = datestr.replace(", c. ", ", ca. ")

        return areastr.strip(", "), datestr.strip(", ")
