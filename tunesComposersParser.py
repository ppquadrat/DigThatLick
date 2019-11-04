# -*- coding: utf-8 -*-
# Python3

"""
parse tune titles and composers from Jazz Encyclopedia csv file

use:
from tunesComposersParser import TunesComposersParser
parser = TunesComposersParser()
parser.parse_tunes_composers(tunesString, composersString)

returns:

    tunes_composers_list, track_qualifiers_dict

where:
 - tunes_composers_list is a list of tuples of the kind:

         primary_title_dict, secondary_title_dict, composer_list

    - primary_title_dict always has a keyword 'title' and can have keywords: part, w, vocal, take, intro, theme, changes
    - secondary_title_dict can be empty; if not, has a keyword 'title' and can have keyqords: part, aka, intro, take, theme, changes
    - composer_list is a list of dictionaries, each of them always has the keyword 'name' and can have a keyword 'arr'; can be empty

 - track_qualifiers_dict contains optional qualifiers related to the whole track such as:
         - part: is a string, can be '1', '2', '1&2', '1 & 2'
         - medley: 1 if the overall_title contains the word 'Medley'
         - variation: 1 if the overall_title contains the word 'Variation'
         - intro: 1 if the overall_title contains the word 'Intro'
         - take: same as part
         - overall_title - the rest of the overall description before the list of tunes with qualifiers removed, e.g. for "Perfume Suite, Part 1" it would be "Perfume Suite" 


NrTunesException is raised if the parser cannot separate the tunes string into the same number of titles as there are composers

examples:

Alice Blue Gown (w)                                 (Tierney-McCarthy)
Broadway Rose (intro: Dolly I Love You)             (West-Fried-Spencer-Arden-Wadworth) 
Mad (Cause You Treat Me This Way)                   (McHugh-Heath)
Really A Pain (A Stomp)                             (Kassel-Sturr-Spanier)
Choo Choo (Gotta Hurry Home)                        (Ellington-Ringle-Schafer)
(You‚Äôve Got Those) Wanna-Go-Back-Again Blues      (Turk-Handman)
Harlem River Quiver (Brown Berries)                 (Fields-Healy-McHugh)
Harlem River Quiver                                 (Fields-Healy-McHugh)
(I‚Äôm Goin‚Äô Back To) Bottomland                  (Williams-Trent) 
I‚Äôm Goin‚Äô Back To Bottomland                    (Williams-Trent)
Every Day Blues (Yo Yo Blues)                       (Moten-Durham)
Creole Rhapsody ‚Äì Part 1                          (Ellington)
Creole Rhapsody ‚Äì Part 2                          (Ellington)
Creole Rhapsody, Part 1                             (Ellington)
Creole Rhapsody, Part 2                             (Ellington)
Mood Indigo/Hot And Bothered/Creole Love Call       (Ellington-Bigard-Mills/ Ellington-Miley/Ellington-Miley-Jackson)
Pickin‚Äô My Way (Guitar Mania Pt.1)                (Lang-Kress)
Feeling My Way (Guitar Mania Pt.2)                  (Lang-Kress)
Stampede ‚ÄìA                                       (Henderson)
Stampede ‚ÄìB                                       (Henderson)
Stampede ‚ÄìC                                       (Henderson)
Stampede ‚ÄìA                                       (Mertz)
Mississippi Mud (Barris)                            (Barris-Cavanaugh)
Yes She Do - No She Don't                           (DeRose-Trent)
I'll Be A Friend "With Pleasure"                    (Rich-Hoffmann)
I Remember You - Chelsea Bridge - I‚Äôve Got The World On A String      (Schwertzinger-Mercer)(Strayhorn)(Arlen-Koehler)
Pick-A-Rib - Part 1                                 (Goodman)
Opus ?                                              (Goodman-Hampton)
My Last Affair (take -2)                            (Johnson)
I'se A Muggin' Pt. 1                                (Smith)
Liebestraum No. 3                                   (Liszt, arr. Reinhardt)
Interpretation Swing J.S. Bach, Part 1              (arr. South-Grappelli)
Improvisation J.S. Bach Part 2                      (arr. Reinhardt)
I'se A Muggin', Part 1                              (Smith)
I'm A Hundred Per Cent For You (vocal)              (Parish-Oakland-Mills)
I'm A Hundred Per Cent For You (non vocal)          (Poe-Greer-Tomlin-Hatch)
Ballad Medley: Over The Rainbow-You've Changed-Time After Time-This Is Always-My Heart Stood Still-I Hadn't Anyone Till You	    (Harburg-Arlen)(Carey-Fischer)(Styne-Cahn)(Gordon-Warren)(Rodgers-Hart)(Noble)
How High The Moon  Part 1 & 2                       (Lewis-Hamilton)
All The Things You Are - Dearly Beloved - The Nearness Of You - I‚Äôll Get By - Everything Happens To Me - The Man I Love - What‚Äôs New? - Someone To Watch Over Me - Isn‚Äôt It Romantic                      (Kern-Hammerstein II)(Kern-Mercer)(Carmichael-Washington)(Ahlert-Turk)(Adair-Dennis)(Gershwin-Gershwin)(Haggart-Burke)(Gershwin-Gershwin)(Rodgers-Hart)
Ballad Medley: Indian Summer - Willow Weep For Me - If I Had You - Ghost Of A Chance -              (Herbert)(Ronell)(Campbell-Connelly-Shapiro)(Young-Crosby-Washington)(Gershwin-Gershwin)(Ellington-Mills-Parish)(Silvers-VanHeusen)(Noble)
Jam Blues                                           (P.D.)
Jammin‚Äô For Clef                                  (Shrdlu)
Medley: When My Sugar Walks Down The Street / I Can't Believe That You're In Love With Me           (Austin-McHugh-Mills/Gaskill-McHugh)
Black Bird Medley Part 1                            (Fields-McHugh)
Reminiscin‚Äò In Tempo, Part 4                      (Ellington)
Perfume Suite, Part 1 - a) Under The Balcony - b) Strange Feeling               (Strayhorn-Ellington)
Perfume Suite, Part 2 - a) Dancers In Love - b) Coloratura                      (Strayhorn-Ellington)
Black, Brown And Beige, Part 1 - a) Blues                                       (Ellington)
Black, Brown And Beige, Part 2 - b) West Indiean Dance - c) Emancipation Celebration - d) Sugar Hill Penthouse          (Ellington)
Yes! Yes!                                           (unknown)
Sonata by L. Van Beethoven (Pathetique, Op. 13)                 (PD, arr. Willet)
Chopin‚Äôs Prelude No. 7                                        (PD, arr. Lunceford)
I Ain‚Äôt Gonna Study War No More                               (PD)
Honeysuckle Rose (quartet)                                      (Razaf-Waller)
Medley Of Armstrong Hits - Part 2 / When You're Smiling / St. James Infirmary / Dinah               (Fisher-Goodwin-Shay)(Primrose)(Lewis-Young-Akst)
Medley Of Armstrong Hits - Part 1 / You Rascal You / When It‚Äôs Sleepy Time Down South / Nobody‚Äôs Sweetheart                 (Theard)(Rene-Rene-Muse)(Kahn-Erdman-Meyers-Schoebel)
On The Sunny Side Of The Street, Pt. 1 & 2          (Fields-McHugh)
Sing, Sing, Sing (intro: Christopher Columbus) Part 1 & 2               (Prima/Berry-Razaf)
Blues Downstairs / Upstairs                         (Herman-Bishop)
Get Your Boots Laced, Papa ‚Äì Part 1 & 2           (Herman-Bishop)
Topsy Turvy (Hard Times)                            (Calloway-Battle-Noel) 
Hard Times (Topsy Turvy)                            (Calloway-Battle-Noel)
Swing To Bop (aka: Stompin‚Äô At The Savoy)         (Sampson-Goodman-Webb)
Lips Flips (aka Stompin‚Äô At The Savoy)            (Sampson-Goodman-Webb)
Rainbow Mist (Body And Soul)                        (Hawkins)
Variations on: Honeysuckle Rose & Body And Soul      (Razaf-Waller/Green-Heyman)
Blue 'n Boogie (theme)                              (Gillespie)
Koko (Theme) / On The Sunny Side Of The Street      (Parker)(Fields-McHugh)
Confirmation (Riff Warmer)                          (Parker)
One Bass Hit (Part 1)                               (Gillespie-Brown-Fuller)
Home Cookin' I (Opus)                               (McKusick)
Home Cookin' II (Cherokee)                          (Noble)
Cool Blues (aka Hot Blues)                          (Parker)
Cool Blues (aka Blowtop Blues)                      (Parker)
Dewey Square (aka Prezology/Bird Feathers)          (Parker)
Bongo Beep (aka Bird Feathers/Charlie‚Äôs Wig)      (Parker)
Crazeology (also issued as: Move/Bird Feathers)     (Harris)
Mango Mangue (band: v)                              (Sunshine)
Segment - Tune X                                    (Parker)
Diverse - Tune X                                    (Parker)
Passport - Tune Y                                   (Parker)
Passport - Tune Z                                   (Parker)
Little Willie Leaps & 52nd Street Theme             (Davis/Monk)
The Chase Pt. 1/ Pt. 2                              (Gordon)
The Duel Pt. 1& 2 (Hornin' In)                      (Gordon)
Settin' The Pace Pt. 2                              (Gordon)
Dat‚Äôs It 	(Gray)                              (Pettiford)
Ballad Medley: I Cover The Waterfront - Gone With The Wind - Easy To Love/ 52nd Street Theme            (Heyman-Green)(Wrubel-Magidson)(Porter/Monk)
Ballad Medley: Tenderly / Autumn In New York / East Of The Sun / I Can't Get Started                (Lawrence-Gross) / (Duke) / (Bowman) / (Duke-Gershwin)
Scintilla 2                                         (Giuffre)
Scintilla 1                                         (Giuffre)
Livery Stable Blues                                 (ODJB)
Intro                                               ()



Note:
parenthesis are used for a variety of semantic purposes: a continuation of the title, an altermative title (e.g. aka)
a part of the track (e.g. intro), form/function (e.g. theme), instrumentation (e.g. vocal), composer (e.g. Bach)
We cannot resolve all of them at this stage. The most difficult and important is to differentiate between a continuation
of the title and an alternative title. For that a dicitionary of all existing titles should be compiled. Those titles
that are always encountered in the same form should be treated as genuine titles; those where primary and/or secondary
titles are found separately should be treated as alternatives


Polina Proutskova
April 2019

"""

# general import
from os.path import join
import re
import logging




class TunesComposersParser():

    class NrTunesException(Exception):
        pass

    PART = [" Part", "Part ", " part ", " part", " Pt", "Pt.", "Pt " " pt"]
    PD = ["P.D."]
    TRAD = ["Traditional", "Trad."]

    def parse_composers(self, composersString):
        logging.debug("separating composers: %s ...", composersString)
        composers = re.split("\) ?\(", composersString)
        composers[0] = composers[0].lstrip(' (')
        composers[-1] = composers[-1].rstrip(') ')
        logging.debug("composers: %s", composers)
        if len(composers) == 0:
            raise Exception
        if len(composers) == 1:
            composers = composers[0].split("/")
        for composer in composers:
            composer = composer.strip()
        logging.debug("composers separated: %s", composers)
        return composers

    def extract_part_qualifier(self, title):
        logging.debug("extracting part qualifier: %s ...", title)
        partQualifier = None
        for part_word in self.PART:
            if part_word in title:
                logging.debug("part word found: %s", part_word)
                lst = re.split(part_word, title)
                title = lst[0].rstrip(",- ")
                partQualifier = lst[1].lstrip(". ")              
                lst1 = partQualifier.split()
                if len(lst1) > 1:
                    if lst1[1].isdigit() and "&" in lst1[0]:
                        partQualifier = lst1[0].strip() + lst1[1].strip()
                        partQualifier = partQualifier.strip(",. -")
                        if len(lst1) > 2:
                            title_rest = " ".join(lst1[2:])
                            title = title + "  " + title_rest
                    elif len(lst1) == 2:
                        partQualifier = lst1[0].strip(",. -")
                        title_rest = lst1[1]
                        title = title + "  " + title_rest
                    else:  # len(lst1) > 2
                        if lst1[1] == "&" and lst1[2].isdigit():
                            partQualifier = " ".join(lst1[0:3]).strip(",. -")  
                            if len(lst1) > 3:
                                title_rest = " ".join(lst1[3:])
                                title = title + "  " + title_rest
                        else:
                            partQualifier = lst1[0].strip(",. -")
                            title_rest = " ".join(lst1[2:])
                            title = title + "  " + title_rest
                logging.debug("title modified: %s, part qualifier: %s", title, partQualifier)
                break
        return title, partQualifier

    def extract_take_qualifier(self, title):
        logging.debug("extracting take qualifier: %s ...", title)
        takeQualifier = None
        if "take " in title:
            lst = re.split("take ", title)
            title = lst[0].rstrip(",- ")
            takeQualifier = lst[1].lstrip(". -")
            logging.debug("title modified: %s, take qualifier: %s", title, takeQualifier)
        return title, takeQualifier
                                                 
    def parse_tunes_composers(self, tunesString, composersString):
        logging.debug("""\nparsing tunes and composers ...
         tunes: %s
         composers: %s""", tunesString, composersString)
        tunes_composers_list = []
        track_qualifiers_dict = {}

        # ellington suites case
        if tunesString.count("(") == 0 and tunesString.count(")") > 0:
            if tunesString.count(")") == 1:
                composersString = composersString + "()"
                tunesString = tunesString + " x) "
            else:
                processed_composersString = ""
                for i in range(tunesString.count(")")):
                    processed_composersString = processed_composersString + composersString
                composersString = processed_composersString
            

        # if more than one tunes in a track, separate them and process track qualifiers
        tunes = [tunesString]
        composers = self.parse_composers(composersString)
        nrTunes = len(composers)
        logging.debug("number of tunes on track: %i", nrTunes)
        if nrTunes > 1:
            # separate tune titles
            tunes = re.split(" ?-? [a-z]\) ", tunesString)
            if len(tunes) != nrTunes and len(tunes) != nrTunes + 1:
                tunes = re.split(",? into: ", tunesString)
            if len(tunes) != nrTunes and len(tunes) != nrTunes + 1:
                tunes = re.split(" - ", tunesString)
            if len(tunes) != nrTunes and len(tunes) != nrTunes + 1:
                tunes = re.split("\/", tunesString)
            if len(tunes) != nrTunes and len(tunes) != nrTunes + 1:
                tunes = re.split("-", tunesString)
            if len(tunes) == 0:
                tunes = [tunesString]
            logging.debug("tunes separated in %i tunes: %s", len(tunes), tunes)
            # check number of tunes
            overall_title = ""
            if len(tunes) == nrTunes + 1:
                overall_title = tunes[0]
                tunes = tunes[1:]
                logging.debug("overall title: %s	tunes: %s", overall_title, tunes)
            elif len(tunes) == nrTunes:
                lst = re.split(":| - |\/", tunes[0], 1)
                if len(lst) == 2:
                    overall_title = lst[0]
                    tunes[0] = lst[1]
                    logging.debug("overall title: %s	tunes: %s", overall_title, tunes)
            else:
                logging.warning("""\nNr tunes != nr composers, track will not be processed
        tunes: %s
        composers: %s""", tunes, composers)
                raise self.NrTunesException 
            
            # parse track qualifiers at the beginning
            if len(overall_title) > 0:
                if "Medley" in overall_title: # medley
                    track_qualifiers_dict['medley'] = 1
                    logging.debug("medley: %i", track_qualifiers_dict['medley'])
                if "Variation" in overall_title: # variation
                    track_qualifiers_dict['variation'] = 1
                    logging.debug("variation: %i", track_qualifiers_dict['variation'])
                if "Intro" in overall_title: # medley
                    track_qualifiers_dict['intro'] = 1
                    logging.debug("intro: %i", track_qualifiers_dict['intro'])
                # part
                part_of, part = self.extract_part_qualifier(overall_title)
                if part != None:
                    track_qualifiers_dict['part'] = part
                    overall_title = part_of
                    logging.debug("overall title: %s,      part: %s", part_of, part)
                # take
                take_of, take = self.extract_take_qualifier(overall_title)
                if take != None:
                    track_qualifiers_dict['take'] = take
                    overall_title = take_of
                    logging.debug("overall title: %s,      part: %s", take_of, take)
                if len(overall_title) > 0:
                    track_qualifiers_dict['overall_title'] = overall_title
                logging.debug("track qualifiers: %s", track_qualifiers_dict)
                
            


        for tunestr, composerstr in zip(tunes, composers):
            # main loop: process each tune in a track
            
            logging.debug("processing tune: %s ...", tunestr)
            primary_title_dict = {}
            secondary_title_dict = {}
            composer_list = []
            
            # parse tune string
            primary_title = tunestr.strip()
            secondary_title = None          
            
            # split on ()
            lst2 = re.split("[\(\)]", tunestr)
            if tunestr.count("(") > 0 and tunestr.count(")") > 0:    # meaning there is a secoondary title or something in ()
                if tunestr.startswith("("):
                    primary_title = lst2[2].strip()
                    secondary_title = lst2[1].strip()
                else:
                    primary_title = lst2[0].strip()
                    secondary_title = lst2[1].strip()
                    if len(lst2[2].strip()) > 0:
                        primary_title = primary_title + " - " + lst2[2].strip()
                logging.debug("primary title: %s, secondary title: %s",primary_title, secondary_title)
                # where secondary title is in fact a qualifier of the primary
                if secondary_title == "w":
                    logging.debug("'w' qualifier")
                    primary_title_dict['w'] = 1
                    secondary_title = None
                elif "vocal" in secondary_title:
                    if "non vocal" in secondary_title:
                        primary_title_dict['vocal'] = 0                
                    else:
                        primary_title_dict['vocal'] = 1
                    secondary_title = None
                    logging.debug("vocal qualifier: %i", primary_title_dict['vocal'])
                elif "theme" in secondary_title or "Theme" in secondary_title:
                    lst_theme = re.split("[Tt]heme", secondary_title, 1)
                    rest = "".join(lst_theme)
                    if len(rest.strip()) == 0:
                        primary_title_dict['theme'] = 1
                        secondary_title = None
                        logging.debug("theme qualifier")
                elif "intro" in secondary_title or "Intro" in secondary_title:
                    lst_intro = re.split("[Ii]ntro", secondary_title, 1)
                    rest = "".join(lst_intro)
                    if len(rest.strip()) == 0:
                        primary_title_dict['intro'] = 1
                        secondary_title = None
                        logging.debug("intro qualifier") 
                elif "take" in secondary_title:
                    take_of, take = self.extract_take_qualifier(secondary_title)
                    if take != None and len(take_of.strip()) == 0:
                        logging.debug("take: %s", take)
                        primary_title_dict['take'] = take
                        secondary_title = None
                else:
                    part_of, part = self.extract_part_qualifier(secondary_title)
                    if part != None and len(part_of.strip()) == 0:
                        logging.debug("part: %s", part)
                        primary_title_dict['part'] = part
                        secondary_title = None

            # extract qualifiers from primary title
            for word in self.PART:
                if word in primary_title:
                    primary_title, partQualifier1 = self.extract_part_qualifier(primary_title)
                    logging.debug("primary title: %s, part: %s", primary_title, partQualifier1)
                    primary_title_dict['part'] = partQualifier1
            if "take" in primary_title:
                primary_title, take = self.extract_take_qualifier(primary_title)
                logging.debug("primary title: %s, take: %s", primary_title, take)
                primary_title_dict['take'] = take
            if primary_title.startswith("changes of:"):
                primary_title_dict['changes'] = 1
                primary_title = primary_title.replace("changes of:", "").strip()
                logging.debug("changes: 1, primary title modified: %s", primary_title)            

            # primary title processed, add to dictionary
            primary_title_dict['title'] = primary_title
            primary_title_dict['primary'] = 1
            logging.debug("primary: %s", primary_title_dict)

            
            if secondary_title != None:
                # extract qualifiers for secondary title
                if secondary_title.startswith("changes:"):
                    secondary_title_dict['changes'] = 1
                    secondary_title = secondary_title.replace("changes:", "").strip()
                    logging.debug("changes: 1, secondary title modified: %s", secondary_title)
                if " theme" in secondary_title or "Theme" in secondary_title:
                    secondary_title_dict['theme'] = 1
                    lst2_theme = re.split("[Tt]heme", secondary_title, 1)
                    secondary_title = "".join(lst2_theme)
                    logging.debug("theme: 1, secondary title modified: %s", secondary_title)
                if secondary_title.startswith("aka"):
                    secondary_title_dict['aka'] = 1
                    secondary_title = re.sub("aka:* *", "", secondary_title)
                    logging.debug("secondary title: %s, 'aka': %i", secondary_title, secondary_title_dict['aka'])
                if secondary_title.startswith("intro"):
                    secondary_title_dict['intro'] = 1
                    secondary_title = re.sub("intro:* *", "", secondary_title)
                    logging.debug("secondary title: %s, 'intro': %i", secondary_title, secondary_title_dict['intro'] )
                for word in self.PART:
                    if word in secondary_title:
                        secondary_title, partQualifier2 = self.extract_part_qualifier(secondary_title)
                        logging.debug("secondary title: %s, part: %s", secondary_title, partQualifier2)
                        secondary_title_dict['part'] = partQualifier2
                if "take" in secondary_title:
                    secondary_title, take = self.extract_take_qualifier(secondary_title)
                    logging.debug("secondary title: %s, take: %s", secondary_title, take)
                    secondary_title_dict['take'] = take
                # secondary title processed, add to dictionary
                secondary_title_dict['title'] = secondary_title
                secondary_title_dict['primary'] = 0
                logging.debug("secondary: %s", secondary_title_dict)
            

            # process composer
            logging.debug("process composer: %s ...", composerstr)
            composer_list = []
            for word in self.PD:
                composerstr = composerstr.replace(word, "PD")
            for word in self.TRAD:
                composerstr = composerstr.replace(word, "Trad")
            if re.search("[Tt]rad,? +arr", composerstr):
                re.sub("[Tt]rad,? +arr", "Trad, arr", composerstr)
            if "arr." in composerstr:
                lst3 = composerstr.rsplit(',', 1)
                if len(lst3) > 1:
                    composerstr = lst3[0]
                    arr1str = lst3[1]
                else:
                    arr1str = composerstr
                    composerstr = ""
                arr1str = re.sub("arr\.*:* *", "", arr1str)
                logging.debug("arr. by %s", arr1str)
                lst_comp = arr1str.split("-")
                for composer in lst_comp:
                    composer_list.append({"name": composer.strip(), "arr": 1})
            if len(composerstr) > 0:
                lst_comp = composerstr.split("-")
                for composer in lst_comp:
                    composer_list.append({"name": composer})
            logging.debug("composer list: %s", composer_list)

            # add to overall list
            tunes_composers_list.append( (primary_title_dict, secondary_title_dict, composer_list) )

        return tunes_composers_list, track_qualifiers_dict

                  
            
                    

