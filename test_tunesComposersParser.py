# -*- coding: utf-8 -*-
# Python3

TESTFILE = "JEtunesComposers.csv"

# general import
import csv

##############################################################
import dtlutil

# logging
import logging
MIN_LEVEL = logging.DEBUG
dtlutil.setup_log(MIN_LEVEL)


#####################################################

"""
    weirdlist in "/Users/polina/WORK/DigThatLick/JE/test_tunesComposers_weirdlist.csv"


    Alice Blue Gown (w)                                 (Tierney-McCarthy)
    Broadway Rose (intro: Dolly I Love You)             (West-Fried-Spencer-Arden-Wadworth) 
    Mad (Cause You Treat Me This Way)                   (McHugh-Heath)
    Really A Pain (A Stomp)                             (Kassel-Sturr-Spanier)
    Choo Choo (Gotta Hurry Home)                        (Ellington-Ringle-Schafer)
!!  (You‚Äôve Got Those) Wanna-Go-Back-Again Blues      (Turk-Handman)
    Harlem River Quiver (Brown Berries)                 (Fields-Healy-McHugh)
    Harlem River Quiver                                 (Fields-Healy-McHugh)
!!  (I‚Äôm Goin‚Äô Back To) Bottomland                  (Williams-Trent) 
!!  I‚Äôm Goin‚Äô Back To Bottomland                    (Williams-Trent)
    Every Day Blues (Yo Yo Blues)                       (Moten-Durham)
!!  Creole Rhapsody ‚Äì Part 1                          (Ellington)
!!  Creole Rhapsody ‚Äì Part 2                          (Ellington)
    Creole Rhapsody, Part 1                             (Ellington)
    Creole Rhapsody, Part 2                             (Ellington)
    Mood Indigo/Hot And Bothered/Creole Love Call       (Ellington-Bigard-Mills/ Ellington-Miley/Ellington-Miley-Jackson)
!!  Pickin‚Äô My Way (Guitar Mania Pt.1)                (Lang-Kress)
    Feeling My Way (Guitar Mania Pt.2)                  (Lang-Kress)
!!  Stampede ‚ÄìA                                       (Henderson)
!!  Stampede ‚ÄìB                                       (Henderson)
!!  Stampede ‚ÄìC                                       (Henderson)
!!  Stampede ‚ÄìA                                       (Mertz)
    Mississippi Mud (Barris)                            (Barris-Cavanaugh)
    Yes She Do - No She Don't                           (DeRose-Trent)
!!  I'll Be A Friend "With Pleasure"                    (Rich-Hoffmann)
!!  I Remember You - Chelsea Bridge - I‚Äôve Got The World On A String      (Schwertzinger-Mercer)(Strayhorn)(Arlen-Koehler)
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
!!  All The Things You Are - Dearly Beloved - The Nearness Of You - I‚Äôll Get By - Everything Happens To Me - The Man I Love - What‚Äôs New? - Someone To Watch Over Me - Isn‚Äôt It Romantic                      (Kern-Hammerstein II)(Kern-Mercer)(Carmichael-Washington)(Ahlert-Turk)(Adair-Dennis)(Gershwin-Gershwin)(Haggart-Burke)(Gershwin-Gershwin)(Rodgers-Hart)
    Jam Blues                                           (P.D.)
    Jammin‚Äô For Clef                                  (Shrdlu)
    Medley: When My Sugar Walks Down The Street / I Can't Believe That You're In Love With Me           (Austin-McHugh-Mills/Gaskill-McHugh)
    Black Bird Medley Part 1                            (Fields-McHugh)
!!  Reminiscin‚Äò In Tempo, Part 4                      (Ellington)
    Perfume Suite, Part 1 - a) Under The Balcony - b) Strange Feeling               (Strayhorn-Ellington)
    Perfume Suite, Part 2 - a) Dancers In Love - b) Coloratura                      (Strayhorn-Ellington)
    Black, Brown And Beige, Part 1 - a) Blues                                       (Ellington)
    Black, Brown And Beige, Part 2 - b) West Indiean Dance - c) Emancipation Celebration - d) Sugar Hill Penthouse          (Ellington)
    Yes! Yes!                                           (unknown)
    Sonata by L. Van Beethoven (Pathetique, Op. 13)                 (PD, arr. Willet)
!!  Chopin‚Äôs Prelude No. 7                                        (PD, arr. Lunceford)
!!  I Ain‚Äôt Gonna Study War No More                               (PD)
    Honeysuckle Rose (quartet)                                      (Razaf-Waller)
    Medley Of Armstrong Hits - Part 2 / When You're Smiling / St. James Infirmary / Dinah               (Fisher-Goodwin-Shay)(Primrose)(Lewis-Young-Akst)
!!  Medley Of Armstrong Hits - Part 1 / You Rascal You / When It‚Äôs Sleepy Time Down South / Nobody‚Äôs Sweetheart                 (Theard)(Rene-Rene-Muse)(Kahn-Erdman-Meyers-Schoebel)
    On The Sunny Side Of The Street, Pt. 1 & 2          (Fields-McHugh)
!!!!Sing, Sing, Sing (intro: Christopher Columbus) Part 1 & 2               (Prima/Berry-Razaf)
    Blues Downstairs / Upstairs                         (Herman-Bishop)
!!  Get Your Boots Laced, Papa ‚Äì Part 1 & 2           (Herman-Bishop)
    Topsy Turvy (Hard Times)                            (Calloway-Battle-Noel) 
    Hard Times (Topsy Turvy)                            (Calloway-Battle-Noel)
    Swing To Bop (aka: Stompin‚Äô At The Savoy)         (Sampson-Goodman-Webb)
!!  Lips Flips (aka Stompin‚Äô At The Savoy)            (Sampson-Goodman-Webb)
    Rainbow Mist (Body And Soul)                        (Hawkins)
    Variations on: Honeysuckle Rose / Body And Soul     (Razaf-Waller/Green-Heyman)
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
    Little Willie Leaps / 52nd Street Theme             (Davis/Monk)
    The Chase Pt. 1&2                                   (Gordon)
    The Duel Pt. 1& 2 (Hornin' In)                      (Gordon)
    Settin' The Pace Pt. 2                              (Gordon)
!!  Dat‚Äôs It 	(Gray)                                  (Pettiford)
!!! Ballad Medley: I Cover The Waterfront - Gone With The Wind - Easy To Love/ 52nd Street Theme            (Heyman-Green)(Wrubel-Magidson)(Porter/Monk)
    Ballad Medley: Tenderly / Autumn In New York / East Of The Sun / I Can't Get Started                (Lawrence-Gross)(Duke)(Bowman)(Duke-Gershwin)
    Scintilla 2                                         (Giuffre)
    Scintilla 1                                         (Giuffre)
    Livery Stable Blues                                 (ODJB)
    Intro                                               ()
    Strut, Miss Lizzie (intro) / Sweet Mamma            (Parker)(Fields-McHugh)
    """



from tunesComposersParser import TunesComposersParser
parser = TunesComposersParser()


# test on one string
##tunesString = """Jam Blues"""
##composersString = """Trad."""
##tunes_composers_list, track_qualifiers_dict = parser.parse_tunes_composers(tunesString, composersString)

### this should print a warning and throw an exception
### Ballad Medley: Indian Summer - Willow Weep For Me - If I Had You - Ghost Of A Chance -              (Herbert)(Ronell)(Campbell-Connelly-Shapiro)(Young-Crosby-Washington)(Gershwin-Gershwin)(Ellington-Mills-Parish)(Silvers-VanHeusen)(Noble)
##tunesString = """Ballad Medley: Indian Summer - Willow Weep For Me - If I Had You - Ghost Of A Chance - """
##composersString = """(Herbert)(Ronell)(Campbell-Connelly-Shapiro)(Young-Crosby-Washington)(Gershwin-Gershwin)(Ellington-Mills-Parish)(Silvers-VanHeusen)(Noble)"""
##tunes_composers_list, track_qualifiers_dict = parser.parse_tunes_composers(tunesString, composersString)



# test on weird list                             
##for count, string in enumerate(weirdlist):
##     logging.info("\nline %i",count)
##     parser = MusiciansInstrumentsParser()
##     parser.parse_session_participants(string)

##with open('test_tunesComposers_weirdlist.csv', 'r') as f:
##    csvreader = csv.reader(f)
##    for row in csvreader:
##        tunesString = row[0].strip("\n ")
##        composersString = row[1].strip("\n ")
##        try:
##            tunes_composers_list, track_qualifiers_dict = parser.parse_tunes_composers(tunesString, composersString)
##        except parser.NrTunesException:
##            continue

# test on all entries                    
with open(TESTFILE, 'r') as f:
    csvreader = csv.reader(f)
    for count, row in enumerate(csvreader):
        logging.info("\nline %i",count)
        tunesString = row[0].strip("\n ")
        composersString = row[1].strip("\n ")
        if len(tunesString) > 0 and len(composersString) > 0:
            try:
                tunes_composers_list, track_qualifiers_dict = parser.parse_tunes_composers(tunesString, composersString)
            except parser.NrTunesException:
                continue


    
