# Python3

""" parse freetext dates and date spans
Examples of dates that can be parsed:
        "30/10/1923", 
        "June 1923", 
        "ca. September 1924", 
        "17.- 22.1.1924", 
        "early December 1924", 
        "January, 1925", 
        "ca. January, 1927", 
        "about August, 1928", 
        "May (8-15), 1923", 
        "July 28/August 1, 1924", 
        "about mid November, 1928", 
        "ca. February 9-14, 1925", 
        " 23-29. 3. 1955", 
        "between 27. 2. and 17. 3. 1941", 
        "March/April 1946", 
        "(first half of) June 1952", 
        "08. or 12.03.1946", 
        "23. & 24.02.1944", 
        "September 1941/42", 
        "spring (poss. May 30) 1945", 
        "January-February  1946", 
        "late summer 1950", 
        "ca. fall 1950", 
        "mid winter 42", 
        "January 22 or 23, 1952", 
        "late 1943", 
        "November 11/12, 1955", 
        "prob. June 1946", 
        "end 1946", 
        "poss. October 1950", 
        "spring & summer 1953", 
        "June 11, 1955",
        "ca. early 1941(?)",
        "July 24, 25 & 31, 1956"

Call:

    from dateParser import DateParser
    DateParser.parse_freetext_date(datestring)

You can set the century and check that your date is within a given time limit:

             from dateutil.parser import parserinfo
             myparserinfo = MyParserInfo()
             dtprsr = DateParser(myparserinfo, year1, year2)
             dtprsr.parse_freetext_date(datestring)

year1 and year2 are the limits against which the resulting startdate and enddate are checked

Set the century for two digit years through sublassing parserInfo:

    class MyParserInfo(parserinfo):
        def convertyear(self, year, *args, **kwargs):
            if year < 100:
                year += 1900
            return year



Returns:

 - startdate as datetime
 - enddate, same as startdate for single dates
 - IS_APPROXIMATE boolean; any date with a approximation qualifier or if month, season, year \
         are given but not a day; "between ... and ..." as well as "from ... to ..." also considered
         approximate
 - approximation qualifier, "" if no qualifier present
 - a list of period qualifiers, empty if no period is given; if a period is only given to the end date, will be ["", <qualifier>]
 - list of season qualifiers, otherwise empty; if a timespan it is assumed that both start and end have a season
years, months and seasons are resolved to a day; e.g. "winter to spring 1944" is resolved to 1/12/1943 - 31/05/1944, see add_season()
periods are resolved in add_period()
approximation is not resolved


The freetext string can contain following qualifyers:

 approximation: "ca", "Ca", "about", "About", "approximately", "Approximately",\
             "possibly", "Possibly", "poss", "probably", "Probably", "prob"
 periods: "early", "mid", "late", "first half of",\
                  "second half of", "first quarter of", "end"
 seasons: "winter", "spring", "summer", "fall", "Winter", "Spring", "Summer",
                 "Fall", "autumn", "Autumn"
Adjust the qualifiers in the global variables declaration in dateParser's __init__


Following strings are considered as datespan symbols:
         "-", "/", "&", " and ", " to ", " or "
dashes and slashes will indicate a datespan only if they occur once in the string.
                Dots are replaced by spaces

Polina Proutskova
February-May 2019"""

# general import

import re
from dateutil.parser import parse as parsedate
import datetime
from dateutil.relativedelta import relativedelta
from dateutil.parser import parserinfo
from datetime import timedelta
from os.path import join
import logging


class DateParser():

    class UnparsableDateWarning(Warning):
        """ raised when the freetext date cannot be parsed """
        def __init__(self, freetext_date):
            self.message = """date    %s    cannot be parsed""" %freetext_date

    class YearOutOfRangeWarning(Warning):
        """ raised when the year is out of range given to __init__"""
        def __init__(self, freetext_date, date_limit_lower, date_limit_upper):
            self.message = """date    %s    out of given range between %s and %s""" %(freetext_date, date_limit_lower, date_limit_upper)
        

    def __init__(self, parserInfo, date_limit_lower = datetime.MINYEAR, date_limit_upper = datetime.MAXYEAR):

        self.PARSERINFO = parserInfo

        self.DATERANGE = date_limit_lower, date_limit_upper

        self.APPRX = ["ca", "Ca", "about", "About", "approximately", "Approximately",\
             "possibly", "Possibly", "poss", "probably", "Probably", "prob", "unidentified date"]

        self.IS_APPROXIMATE = False

        self.MYAPPRX = ""

        self.SEASONS = ["winter", "spring", "summer", "fall", "Winter", "Spring", "Summer", "Fall", \
                        "autumn", "Autumn"]

        self.HAS_SEASON = False

        self.MYSEASON = [] # season(s) removed from the freetext date

        self.PERIODS = ["early", "mid", "late", "first half of",\
                  "second half of", "first quarter of", "last quarter of", "end"]

        self.HAS_PERIOD = False

        self.MYPERIOD = [] # period(s) removed from the freetext date

        self.TIMESPANS = ["-", "/", "&", " and ", " to ", " or "]

        self.TIMESPANS_APPRX = ["or", "from", "between"]

        self.HAS_TIMESPAN = False

        self.MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",\
                  "November", "December"]
        self.MONTHS_SHORT = ["Jan", "Feb", "Mar", "Apr", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    def is_approximate(self, freetext_date):
        result = False
        for word in self.APPRX:
            if freetext_date.startswith(word):
                self.MYAPPRX = word
                result = True
                break
            elif re.search("\("+word, freetext_date) != None:
                lst = re.split("[\(\)]", freetext_date)
                self.MYAPPRX = lst[1]
                logging.debug("approximation in brackets: %s", self.MYAPPRX)
                break
        for word in self.TIMESPANS_APPRX:
            if freetext_date.count(word) > 0:
                self.MYAPPRX = word
                result = True
                break
        return result

    def remove_approximate(self, freetext_date):
        for string in self.APPRX:
            if re.search("\("+string, freetext_date) != None:
                lst = re.split("[\(\)]", freetext_date)
                freetext_date = lst[0]+lst[2]
            else:
                freetext_date = freetext_date.replace(string, "")
        return freetext_date

    def has_season(self, freetext_date):
        if self.contains_timespan(freetext_date):
            sep = self.find_timespan_symbol(freetext_date)
            season1 = None
            season2 = None
            for word in self.SEASONS:
                if word in freetext_date:
                    if freetext_date.index(word) < freetext_date.index(sep):
                        season1 = word
                        if season2 == None:
                            season2 = ""
                    else:
                        season2 = word
                        if season1 == None:
                            season1 = ""
            if season1 != None:
                self.MYSEASON.append(season1)
                self.MYSEASON.append(season2)
        else:
            # no timespan symbol, max one season
            for word in self.SEASONS:
                if word in freetext_date:
                    self.MYSEASON.append(word)
                    break
        return len(self.MYSEASON) > 0

    def remove_season(self, freetext_date):
        for string in self.MYSEASON:
            freetext_date = freetext_date.replace(string, "")       
        return freetext_date

    def add_season(self, date, season):
        season = season.lower()           
        if season == "winter":
            startdate = datetime.date(date.year-1, 12, 1)
            enddate = datetime.date(date.year, 2, 28)
        elif season == "spring":
            startdate = datetime.date(date.year, 3, 1)
            enddate = datetime.date(date.year, 5, 31)
        elif season == "summer":
            startdate = datetime.date(date.year, 6, 1)
            enddate = datetime.date(date.year, 8, 31)
        elif season == "fall" or season == "autumn":
            startdate = datetime.date(date.year, 9, 1)
            enddate = datetime.date(date.year, 11, 30)
        else:
            logging.warning("unknown season: %s", season)
            raise Warning
        if not date.month == 1 and not date.day == 1:
            if not date.month == 12 and not date.day == 31:
                if date < startdate or date > enddate:
                    logging.warning("parsed date %s outside its season %s", date, season)
                    raise Warning
        return startdate, enddate

    def add_season_start_end(self, startdate, enddate, season1, season2 = None):
        if len(season1) > 0:
            startdate, tmp1 = self.add_season(startdate, season1)
        if season2 != None and len(season2) > 0:
            tmp2, enddate = self.add_season(enddate, season2)
##        if season2 == None:
##            season2 = season1
##        startdate, tmp1 = self.add_season(startdate, season1)
##        tmp2, enddate = self.add_season(enddate, season2)
        return startdate, enddate

    def has_period(self, freetext_date):
        if self.contains_timespan(freetext_date):
            sep = self.find_timespan_symbol(freetext_date)
            period1 = None
            period2 = None
            for word in self.PERIODS:
                if word in freetext_date:
                    if freetext_date.index(word) < freetext_date.index(sep):
                        period1 = word
                        if period2 == None:
                            period2 = ""
                    else:
                        period2 = word
                        if period1 == None:
                            period1 = ""
            if period1 != None:
                self.MYPERIOD.append(period1)
                self.MYPERIOD.append(period2)
        else:
            for word in self.PERIODS:
                if word in freetext_date:
                    self.MYPERIOD.append(word)
                    break
        return len(self.MYPERIOD) > 0

    def remove_period(self, freetext_date):
        for string in self.MYPERIOD:
            freetext_date = freetext_date.replace(string, "")       
        return freetext_date

    def add_period(self, startdate, enddate, period):
        delta = enddate - startdate
        period = period.lower()
        if period == "early":
            enddate = startdate + (delta // 3)
        elif period == "mid":
            startdate = startdate + (delta // 3)
            enddate = enddate - (delta // 3)
        elif period == "late":
            startdate = enddate - (delta // 3)
        elif period == "first half of":
            enddate = enddate - (delta // 2)
        elif period == "second half of":
            startdate = startdate + (delta // 2)
        elif period == "first quarter of":
            enddate = enddate - (delta // 4)
        elif period == "last quarter of":
            startdate = enddate - (delta // 4)
        elif period == "end":
            startdate = enddate - (delta // 6)
        elif period == "":
            pass
        else:
            logging.warning("unknown period: %s", period)
            raise Exception
        return startdate, enddate

    def contains_timespan(self, string):
        for word in self.TIMESPANS:
            if string.count(word) == 1:
                return True
        return False

    def find_timespan_symbol(self, string):
        for word in self.TIMESPANS:
            if string.count(word) == 1:
                return word
        return None

    def adjust_timespan(self, freetext_date):
        for sep in self.TIMESPANS:
            freetext_date = freetext_date.replace(sep, " " + sep + " ")
        if freetext_date.count("from") > 0:
            freetext_date = freetext_date.replace("from", "between")
            freetext_date = freetext_date.replace("to", "and")
        return freetext_date

    def has_alphanumeric(self, string):
        return re.search("[a-zA-Z0-9]+", string) != None

    def list_has_alphanumeric(self, lst):
        return self.has_alphanumeric(" ".join(lst))

    def count_alphanumeric(self, lst):
        count = 0
        for word in lst:
            if self.has_alphanumeric(word):
                count +=1
        return count

    def resolve_three_dates(self, freetext_date):
        # removes the middle date in "July 24, 25 & 31, 1956" case
        if "&" in freetext_date:
            freetext_date = re.sub(", ?[0-9]{1,2},? ?&", " &", freetext_date)
        if " and " in freetext_date:
            freetext_date = re.sub(", ?[0-9]{1,2},? ?and", " and", freetext_date)
        logging.debug("three dates resolved: %s", freetext_date)
        if self.has_three_dates(freetext_date):
            freetext_date = self.resolve_three_dates(freetext_date)
        return freetext_date

    def has_three_dates(self, freetext_date):
        # like in "July 24, 25 & 31, 1956"
        if " and " in freetext_date or " & " in freetext_date:
            if re.search(", ?[0-9]{1,2},? ?&", freetext_date):
                return True
            if re.search(", ?[0-9]{1,2},? ?and", freetext_date):
                return True
        return False
            

    def resolve_long_and_list(self, freetext_date):
        # if the date contains a long 'and' list:
        # like "May 31, June 1 & 3, 1960"
        # January 29-31 & February 1, 1992
        logging.debug("Resolving long list of dates")
        split1 = re.split("&|and", freetext_date)
        logging.debug("%s", split1)
        split2 = re.split("[,-]", split1[0])
        logging.debug("%s", split2)
        date1 = split2[0]
        date2 = split1[1]
        has_month = False
        for month in self.MONTHS:
            if month in date2:
                has_month = True
                break
        if not has_month:
            for month in self.MONTHS:
                if month in split2[-1]:
                    date2 = month + " " + date2
                    break
        logging.debug("date1: %s, date2: %s", date1, date2)
        newdate = date1 + " and " + date2
        (start, end), (before, after) = self.separate2(newdate)
        logging.debug("start: %s, end: %s", start, end)
        return self.separate3(start, end, "", after)

    def has_long_and_list(self, freetext_date):
        # whether the date contains a long 'and' list:
        # like "May 31, June 1, 2 & 3, 1960"
        if " and " in freetext_date or " & " in freetext_date:
            months = []
            for month in self.MONTHS:
                if month in freetext_date:
                    months.append(month)
            if len(months) == 2:
                re_pattern = months[0]+".*[0-9]{1,2} ?[,-].*"+months[1]
                result = re.search(re_pattern, freetext_date)
                if result != None:
                    logging.debug("long list of dates to be resolved")
                    return True
            elif len(months) > 2:
                logging.debug("long list of dates to be resolved")
                return True                
            
        return False
        
        

    def separate2(self, freetext_date):
        sep = self.find_timespan_symbol(freetext_date)
        logging.debug("timespan symbol: %s", sep)
        lst0 = re.split(sep, freetext_date, 1)
        beforestr = lst0[0]
        afterstr = lst0[1]
        if re.search("[1-9][0-9]{3}", beforestr):
            # beforestr ends with a 4-digit year, meaning the separator is between two complete dates
            date1 = beforestr
            date2 = afterstr
            beforestr = ""
            afterstr = ""           
        else:
            # the separator is not between complete dates, e.g. "July 27-August 13 1951"    
            if not "between" in freetext_date:
                before = re.split('(\W+)', beforestr) # list includes non-alphanumeric separators as words
                logging.debug("before: %s", before)
                after = re.split('(\W+)', afterstr)
                logging.debug("after: %s", after)
                # date1 is the chunk of "before" starting with the last alphanumeric
                date1 = ""
                while not self.has_alphanumeric(date1) and len(before) > 0:
                    date1 = before[-1]
                    before = before[:-1]
                logging.debug("date1: %s    before: %s", date1, before)
                # date2 is the chunk of "after" that ends with the first alphnumeric
                date2 = ""
                while not self.has_alphanumeric(date2) and len(after) > 0:
                    date2 = date2 + after[0]
                    after = after[1:]
                logging.debug("date2: %s    after: %s", date2, after)
                # if one of date1 and date2 is a digit and the other is not, like in
                # "27-August", keep adding chunks from before and after until you get
                # "July 27-August 13"
                if re.match('[0-9]+', date1) and not re.search('[0-9]+', date2) or \
                   not re.match('[0-9]+', date1) and re.search('[0-9]+', date2):
                    if len(before) > 0:
                        while len(before) > 0 and not self.has_alphanumeric(before[-1]):
                            date1 = before[-1] + date1
                            before = before[:-1]
                        date1 = before[-1] + date1
                        before = before[:-1]
                        logging.debug("date1: %s    before: %s", date1, before)
                    if len(after) > 0:
                        while len(after) > 0 and not self.has_alphanumeric(after[0]):
                            date2 = date2 + after[0]
                            after = after[1:]
                        date2 = date2 + after[0]
                        after = after[1:]
                        logging.debug("date2: %s    after: %s", date2, after)
                beforestr = "".join(before)
                afterstr = "".join(after)
                logging.debug("afterstr: %s", afterstr)
            else:                    
                # if the freetext date is of the form "... between ... and ... "
                # split in these three strings
                lst1 = re.split("between", beforestr)
                beforestr = lst1[0]  # before the word "between"
                betweenstr = lst1[1]  # str between the words "between" and "and"
                # split on each non-alphanumeric, count alphanumeric words in date1 (which is betweenstr)
                # make date2 have the same number of alphanumeric words
                between = re.split('(\W+)', betweenstr)
                count = self.count_alphanumeric(between)
                logging.debug("between: %s    %i words", between, count)
                after = re.split('(\W+)', afterstr)
                logging.debug("after: %s", after)
                date1 = betweenstr
                date2lst = []
                while not self.count_alphanumeric(date2lst) == count and not len(after) == 0:
                    date2lst.append(after[0])
                    after = after[1:]
                date2 = ''.join(date2lst)
                logging.debug("date2: %s    after: %s", date2, after)
                afterstr = "".join(after)         
                                            
        return (str(date1), str(date2)), (beforestr, afterstr)

    def separate3(self, date1, date2, before, after):
        start = before + date1 + after
        end = before + date2 + after
        return start, end

    def separate(self, freetext_date):           
        # extract start and end dates from the freetext_date
        # freetext_date is assumed to contain a timespan symbol
        (date1, date2), (before, after) = self.separate2(freetext_date)
        return self.separate3(date1, date2, before, after)           

    def parse_start_end(self, start, end, original_date):
        # parse the dates for start and end
        try:
            startdate = parsedate(start, self.PARSERINFO, default=datetime.date(datetime.MINYEAR, 1, 1), dayfirst=True)
##            startdate, tokens = parsedate(start, self.PARSERINFO, default=datetime.date(datetime.MINYEAR, 1, 1), dayfirst=True, fuzzy_with_tokens = True)
        except (ValueError, TypeError):
            raise self.UnparsableDateWarning(original_date)
        else:
##            if self.list_has_alphanumeric(tokens):
##                logging.info("Could not parse tokens %s in separated datestring %s, original datestring %s", tokens, start, original_date)
            try:
                enddate = parsedate(end, self.PARSERINFO, default=datetime.date(datetime.MINYEAR, 12, 31), dayfirst=True)               
##               enddate, tokens = parsedate(end, self.PARSERINFO, default=datetime.date(datetime.MINYEAR, 12, 31), dayfirst=True, fuzzy_with_tokens = True)
            except (ValueError, TypeError):
                raise self.UnparsableDateWarning(original_date)
            else:
##                if self.list_has_alphanumeric(tokens):
##                    logging.info("Could not parse tokens %s in separated datestring %s, original datestring %s", tokens, end, original_date)           
                # check whether the date(s) are exact, like "07/11/1945" or approximate, like "November 1945"
                tmp = parsedate(end, self.PARSERINFO, default=datetime.date(datetime.MINYEAR, 1, 1), dayfirst=True)
                if tmp != enddate:
                    self.IS_APPROXIMATE = True
        return startdate, enddate

    def parse_one_date(self, processed_date, original_date):
        try:
            date = parsedate(processed_date, self.PARSERINFO, default=datetime.date(datetime.MINYEAR, 1, 1), dayfirst=True)
##            date, tokens = parsedate(processed_date, self.PARSERINFO, default=datetime.date(datetime.MINYEAR, 1, 1), dayfirst=True, fuzzy_with_tokens = True)
        except (ValueError, TypeError):
            raise self.UnparsableDateWarning(original_date)
        return date

    def parse_one_date_start_end(self, freetext_date, original_date):
        if self.is_decade(freetext_date):
            # special case like 1950s
            startdate = self.parse_decade(freetext_date)
            enddate = self.parse_decade(freetext_date, end=True)
        else:
            # default: all other cases
            try:
                startdate = parsedate(freetext_date, self.PARSERINFO, default=datetime.date(datetime.MINYEAR, 1, 1), dayfirst=True)
    ##            startdate, tokens = parsedate(freetext_date, self.PARSERINFO, default=datetime.date(datetime.MINYEAR, 1, 1), dayfirst=True, fuzzy_with_tokens = True)
                enddate = parsedate(freetext_date, self.PARSERINFO, default=datetime.date(datetime.MINYEAR, 12, 31),  dayfirst=True)
            except (ValueError, TypeError):
                raise self.UnparsableDateWarning(original_date)
        logging.debug("parsed: %s  :  %s", startdate, enddate)
##            if self.list_has_alphanumeric(tokens):
##                logging.info("Could not parse tokens %s in original datestring %s", tokens, original_date)
        return startdate, enddate

        

    def parse_one_date_with_period_season(self, freetext_date, original_date, season=None, period=None):
        if period!=None and len(period) > 0:
            freetext_date = freetext_date.replace(period, "")
            logging.debug("period removed: %s", freetext_date)
        if season!=None and len(season) > 0:
            freetext_date = freetext_date.replace(season, "")
            logging.debug("season removed: %s", freetext_date)
        startdate, enddate = self.parse_one_date_start_end(freetext_date, original_date)
        if season != None and len(season) > 0:
            startdate, enddate = self.add_season_start_end(startdate, enddate, season)
            logging.debug("season added: %s  :  %s", startdate, enddate)
        if period != None and len(period) > 0:
            startdate, enddate = self.add_period(startdate, enddate, period)
            logging.debug("period added: %s  :  %s", startdate, enddate)
        return startdate, enddate


    def adjust_date_to_include_period(self, date1, date2, before, after):
        if not date1 in self.MYPERIOD and not date1 in self.MYPERIOD: 
            period1 = self.MYPERIOD[0]
            if len(self.MYPERIOD) > 1:
                period2 = self.MYPERIOD[1]
                if period2 in date2 and len(after) > 0:
                    afterlst = after.split(None, 1)
                    date2 = date2 + " " + afterlst[0]
                    after = afterlst[-1]
            else:
                self.MYPERIOD.append("")
            if period1 in before:
                beforelst = re.split(period1, before, 1)
                before = beforelst[0].strip()
                date1 = period1 + beforelst[-1] + " " + date1
            elif period1 in date2 and len(after) > 0:
                afterlst = after.split(None, 1)
                date2 = date2 + " " + afterlst[0]
                after = afterlst[-1]
                self.MYPERIOD[1] = self.MYPERIOD[0]
                self.MYPERIOD[0] = ""

        date1 = before + " " + date1 + " " + after
        date2 = before + " " + date2 + " " + after
        logging.debug("adjusted: date1: %s    date2:  %s", date1, date2)
        return date1, date2


    def is_decade(self, freetext_date):
        return re.search("[0-9]{3}0'?s", freetext_date)

    def parse_decade(self, freetext_date, end=False):
        # decade like 1950s or 1950's
        freetext_date = freetext_date.strip("\'s ")
        try:
            date = parsedate(freetext_date, self.PARSERINFO, default=datetime.date(datetime.MINYEAR, 1, 1), dayfirst=True)
        except (ValueError, TypeError):
            raise self.UnparsableDateWarning(freetext_date)
        if end:
            year = timedelta(days=365)
            delta = 10*year + timedelta(days=1)
            date = date + delta
        return date

  
    def parse_freetext_date2(self, freetext_date, original_date):

        self.HAS_SEASON = False
        self.MYSEASON = []
        if self.has_season(freetext_date):
            self.HAS_SEASON = True
            self.IS_APPROXIMATE = True
        logging.debug("has season: %s", self.HAS_SEASON)
        if self.HAS_SEASON:
            logging.debug("%s", self.MYSEASON)

        self.HAS_PERIOD = False
        self.MYPERIOD = []
        if self.has_period(freetext_date):
            self.HAS_PERIOD = True
            self.IS_APPROXIMATE = True
        logging.debug("has period: %s", self.HAS_PERIOD)
        if self.HAS_PERIOD:
            logging.debug("%s", self.MYPERIOD)

        self.HAS_TIMESPAN = False
        if self.contains_timespan(freetext_date):
            self.HAS_TIMESPAN = True
            freetext_date = self.adjust_timespan(freetext_date)
        logging.debug("has timespan: %s", self.HAS_TIMESPAN)

        if self.HAS_SEASON and not self.HAS_PERIOD:
            if self.HAS_TIMESPAN: # assuming the timespan is between two seasons
                logging.debug("season: yes, period: no, timespan: yes")
                start, end = self.separate(freetext_date)
                logging.debug("separated: %s  :  %s", start, end)
                start = self.remove_season(start)
                end = self.remove_season(end)
                logging.debug("season removed: %s  :  %s", start, end)
                startdate, enddate = self.parse_start_end(start, end, original_date)
                logging.debug("parsed: %s  :  %s", startdate, enddate)
                startdate, enddate = self.add_season_start_end(startdate, enddate, self.MYSEASON[0], self.MYSEASON[1])
                logging.debug("season added: %s  :  %s", startdate, enddate)
            else: # no timespan, just one season
                logging.debug("season: yes, period: no, timespan: no")
                processed_date = self.remove_season(freetext_date)
                logging.debug("season removed: %s", processed_date)
                date = self.parse_one_date(processed_date, original_date)
                logging.debug("parsed: %s", date)
                startdate, enddate = self.add_season(date, self.MYSEASON[0])
                logging.debug("season added: %s  :  %s", startdate, enddate)

        elif self.HAS_SEASON and self.HAS_PERIOD:
            if self.HAS_TIMESPAN:
                logging.debug("season: yes, period: yes, timespan: yes")
                ((date1, date2), (before, after)) = self.separate2(freetext_date)
                date1, date2 = self.adjust_date_to_include_period(date1, date2, before, after)

                startdate, tmpend = self.parse_one_date_with_period_season(date1, original_date, self.MYSEASON[0], self.MYPERIOD[0])
                tmpstart, enddate = self.parse_one_date_with_period_season(date2, original_date, self.MYSEASON[1], self.MYPERIOD[1])
                logging.debug("parsed: %s  :  %s", startdate, enddate)

            else: # no timespan, just one period and one season
                logging.debug("season: yes, period: yes, timespan: no")
                processed_date = self.remove_period(freetext_date)
                logging.debug("period removed: %s", processed_date)
                processed_date = self.remove_season(processed_date)
                logging.debug("season removed: %s", processed_date)
                date = self.parse_one_date(processed_date, original_date)
                logging.debug("parsed: %s", date)
                startdate, enddate = self.add_season(date, self.MYSEASON[0])
                logging.debug("season added: %s  :  %s", startdate, enddate)
                startdate, enddate = self.add_period(startdate, enddate, self.MYPERIOD[0])
                logging.debug("period added: %s  :  %s", startdate, enddate)

        elif not self.HAS_PERIOD: # no season, no peroid
            if self.HAS_TIMESPAN:
                logging.debug("season: no, period: no, timespan: yes")
                if self.is_decade(freetext_date):
                    lst = freetext_date.split("-")
                    startdate = self.parse_decade(lst[0])
                    enddate = self.parse_decade(lst[1], end=True)
                else:  #default
                    if self.has_long_and_list(freetext_date):
                        start, end = self.resolve_long_and_list(freetext_date)
                    else:
                        start, end = self.separate(freetext_date)
                        logging.debug("separated: %s  :  %s", start, end)
                    startdate, enddate = self.parse_start_end(start, end, original_date)
                logging.debug("parsed: %s  :  %s", startdate, enddate)
            else: # no season, no period, no timespan
                # should actually has been dealt with already
                logging.debug("season: no, period: no, timespan: no")                   
                startdate, enddate = self.parse_one_date_start_end(freetext_date, original_date)
                
        else: # with period, no season
            if not self.HAS_TIMESPAN:
                logging.debug("season: no, period: yes, timespan: no")
                startdate, enddate = self.parse_one_date_with_period_season(freetext_date, original_date, None, self.MYPERIOD[0])
            else: # period and timespan
                logging.debug("season: no, period: yes, timespan: yes")
                # separate at the timespan symbol
                ((date1, date2), (before, after)) = self.separate2(freetext_date)
                logging.debug("separated: date1: %s    date2:  %s    before: %s    after: %s", date1, date2, before, after)
                date1, date2 = self.adjust_date_to_include_period(date1, date2, before, after)

                startdate, tmpend = self.parse_one_date_with_period_season(date1, original_date, None, self.MYPERIOD[0])
                tmpstart, enddate = self.parse_one_date_with_period_season(date2, original_date, None, self.MYPERIOD[1])
             
        return startdate, enddate
                    
    def parse_freetext_date(self, original_date):
        logging.debug("Original date: %s", original_date)

        if len(original_date) == 0:
            return {}
        
        freetext_date = original_date.strip()

        # remove approximation qualifier
        self.MYAPPRX = ""
        self.IS_APPROXIMATE = False
        if self.is_approximate(freetext_date):
            self.IS_APPROXIMATE = True
            logging.debug("is approximate: %s", self.IS_APPROXIMATE)
        freetext_date = self.remove_approximate(freetext_date)
        logging.debug("approximation removed: %s", freetext_date)

        # preprocessing the date string
        # remove "?"
        freetext_date = freetext_date.replace("?", "")
        # replace all . by whitespace
        freetext_date = freetext_date.replace(".", " ")
        # remove brackets
        freetext_date = re.sub("[\[\]\(\)]", "", freetext_date)
        logging.debug("preprocessed: %s", freetext_date)

        PARSED = False

        # if there is just one timespan symbol, move to complex parsing
        for word in self.TIMESPANS:
            if freetext_date.count(word) == 1:
                # these cannot be parsed as is, due to a bug in dateutil
                # dates like "February 9-14, 1925", "November 11/12, 1955", "January 22 or 23, 1952" fail
                # therefore we send all strings with a single timespan symbol straight to the complex parsing
                logging.debug("Has a timespan symbol %s, moving to complex parsing", word)
                if self.has_three_dates(freetext_date):
                    freetext_date = self.resolve_three_dates(freetext_date)
                startdate, enddate = self.parse_freetext_date2(freetext_date, original_date)
                PARSED = True
                break
            
        if not PARSED:
            # no single timepan symbols: either no timespan or multiple like "30/12/1926" or "6-9-45"
            # try to parse as is assuming it is a simple date like "30/10/1923"
            # if it fails or start and end are not the same, move to complex parsing
            logging.debug("parsing as is")
            try:
                startdate = parsedate(freetext_date, self.PARSERINFO, default=datetime.date(datetime.MINYEAR, 1, 1), dayfirst=True)
##                startdate, tokens = parsedate(freetext_date, self.PARSERINFO, default=datetime.date(datetime.MINYEAR, 1, 1), dayfirst=True, fuzzy_with_tokens = True)
                enddate = parsedate(freetext_date, self.PARSERINFO, default=datetime.date(datetime.MINYEAR, 12, 31),  dayfirst=True)
            except (ValueError, TypeError):
                logging.debug("Could not parse as is, moving to complex parsing")
                startdate, enddate = self.parse_freetext_date2(freetext_date, original_date)
            else:
                logging.debug("parsed: %s  :  %s", startdate, enddate)
                if startdate != enddate:
                    logging.debug("start and end differ")
                    self.IS_APPROXIMATE == True
##                elif self.list_has_alphanumeric(tokens):
##                    logging.info("Could not parse tokens %s in original datestring %s", tokens, original_date)

        if startdate.year < self.DATERANGE[0]:
            logging.warning("start date %s out of range (<%i)", startdate, self.DATERANGE[0])
            raise self.YearOutOfRangeWarning(original_date, self.DATERANGE[0], self.DATERANGE[1])
        if enddate.year > self.DATERANGE[1]:
            logging.warning("end date %s out of range (>%i)", enddate, self.DATERANGE[1])
            raise self.YearOutOfRangeWarning(original_date, self.DATERANGE[0], self.DATERANGE[1])

        kwresults = {}
        kwresults['startdate'] = startdate
        kwresults['enddate'] = enddate
        kwresults['is_approximate'] = self.IS_APPROXIMATE
        kwresults['apprx'] = self.MYAPPRX
        kwresults['period_list'] = self.MYPERIOD
        kwresults['season_list'] = self.MYSEASON
        
        logging.debug("Result: %s", kwresults)
        
        return kwresults


               
            
            

