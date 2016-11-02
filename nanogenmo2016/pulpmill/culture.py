import os, sys
import string
import random
import tracery
from tracery.modifiers import base_english

import markov

# A Culture Generates names for people and places, and has character
# attributes.

# Funny names from markov cities:
# Funkstown 'N' Country Estate
# Snoverdale-By-The-Lake
# Musselwhitemarshville Manors
# Umbers Locational Highgate Of Bachmann
# Smileyview
# Bjorkdale Hill
# Poignant Acre

# From https://www.maxmind.com/en/free-world-cities-database
CITIES_FILE = "srcdata/worldcitiespop.txt"

CULTURES = { }

PORT_RULES = {
    "origin" : ['$PP', '#portname#', '#featurename#' ],
    "portname" : ['Port $PP', '$PP Harbour', '#minorport#' ],
    "minorport" : ['$PP Landing', '$PP Docks'],
    "featurename" : ['$PP Cove', '$PP Bay', '$PP Beach']
}

DUNGEON_RULES = {
    "origin" : ['#building#', '#evocative#' ],
    "somebody" : ['$PP', '#creature#'],
    "creature" : ["dragon", "witch", "knight", "orc", "king", "wizard" ],
    "building" : [ "#bad##place#", "the #bad##place#", "#creature# #place#"  ],
    "bad" : [ "foul", "dread", "dire", "krak", "$PP", "dragon", "witch", "frost", "blood" ],
    "place" : [ "fort", "keep", "hold", "fast", "spire", "spike", "tomb", "cave", "gloss", "hollow", "tower" ],
    "evocative" : ["#somebody#'s #bodypart#", "#somebody#'s #downfall#", "ruins of $PP"],
    "bodypart" : ["eye", "knee", "crown", "ear" ],
    "downfall" : ["end", "bane", "tomb", "lament", "ruin" ],
}


class Culture(object):

    def __init__(self):

        self.placeNameGenerator = None
        self.personNameGenerator = None
        self.ranks = [ ('Emperor', 'Emperess'), # Ruler of continent
                       ('King', 'Queen'),       # Ruler of country
                       ('Duke', 'Duchess'),     # Ruler of province

                       [('Marquess','Marchioness'), # Other misc nobility
                        ('Earl', 'Countess'),
                        ('Viscount', 'Viscountess'),
                        ('Baron', 'Baroness') ] ]

    def title2(self, s):
        # like title() but better
        s2 = []
        for p in string.split(s,' '):

            if not p in ["on", "of", "a", "the", "to"]:
                p = p.capitalize()

            s2.append(p)

        # Always cap the first word
        s2[0] = s2[0].capitalize()

        return ' '.join(s2)


    def genPlaceName(self):

        city = self.placeNameGenerator.genString()

        # some sanity checks
        parts = city.split( ' ' )

        didFilter = False
        filteredParts = []
        for part in parts:
            if len(part) > 1:
                filteredParts.append( part )
                didFilter = True
        if (didFilter):
            parts = filteredParts
            city = ' '.join(filteredParts)

        if (len(parts) > 2):
            city = ' '.join(parts[:2])

        return self.title2(city)

    def genContinentName(self):
        """
         Generates a place name, but makes sure it's short and a single word so you
         don't get stuff like 'Clebe Farm'
        """
        while 1:
            candidate = self.genPlaceName()

            parts = string.split( candidate )
            if (len(parts)==1) and len(candidate) < 10:
                return candidate

    def genNameWithMinMaxLength(self, minLen, maxLen ):
        baseName = None
        while not baseName:
            baseName = self.genPlaceName()
            if len(baseName) > maxLen or len(baseName) < minLen:
                baseName = None

        return baseName

    def genPortCityName(self):

        # TODO: make better and more culturaly difference
        baseName = self.genNameWithMinMaxLength( 2, 10 )

        grammar = tracery.Grammar( PORT_RULES )
        grammar.add_modifiers( base_english )
        title = grammar.flatten( "#origin#")
        portName = string.replace( title, "$PP", baseName )

        return self.title2(portName)

    def genDungeonName(self):
        # TODO: generate more than just name here
        baseName = self.genNameWithMinMaxLength( 2, 10 )
        grammar = tracery.Grammar( DUNGEON_RULES )
        grammar.add_modifiers( base_english )
        title = grammar.flatten( "#origin#")
        dungeonName = string.replace( title, "$PP", baseName )

        return self.title2(dungeonName)

# Block some frequent, modern words, or weird data in the src data
BANNED_WORDS = ['mobile home', 'trailer', 'condominium', 'subdivision', 'addition', '9zenic',
                '((', '))', '?' ]

def filterCities( countrycodes ):

    result = set()
    count = 0
    countryCodes = {}
    for line in open(CITIES_FILE):
        lsplit = string.split(string.strip(line),',')
        cc = lsplit[0]
        countryCodes[cc] = countryCodes.get(cc, 0) + 1

        if (cc in countrycodes):

            try:
                city = lsplit[1].encode('ascii', 'ignore')
            except UnicodeDecodeError:
                #print "BAD", lsplit[1]
                continue

            if not city in result:

                banned = False
                for bannedword in BANNED_WORDS:
                    if city.find( bannedword ) != -1:
                        banned = True

                if not banned:
                    result.add( city )

        count += 1

    result = list(result)
    result.sort()
    return result

def setupCulture( ident, countrycodes, srccount, depth, ranks=None ):


    print "Setup Culture : ", ident, "-"*10
    cachedPlacenames = os.path.join( 'data', ident+'_placenames.json')

    if os.path.exists( cachedPlacenames ):
        print "Reading cached placenames ", cachedPlacenames
        #result = pickle.load( open(cachedCulture, 'rb'))
        result = Culture()
        gen = markov.MarkovGenerator( )
        gen.loadCached(cachedPlacenames)
        result.placeNameGenerator = gen

    else:
        placeNameSrcList = os.path.join( 'data', ident+'_cities.txt' )

        if not os.path.exists( placeNameSrcList ):
            cities = filterCities( countrycodes )

            fp = open ( placeNameSrcList, "wt" )
            for city in cities:
                fp.write( city+'\n' )
            fp.close()
        else:
            # Read cached filtered names
            cities = []
            for line in open( placeNameSrcList ):
                cities.append( string.strip(line))

        print "Setup Culture", ident, len(cities), "cities "

        # Make a city generator
        gen = markov.MarkovGenerator( depth=depth )

        random.shuffle(cities)

        trainCities = cities[:srccount]
        for w in trainCities:
            wseq = list(w)
            gen.trainOne( wseq )

        gen.trainFinish()

        result = Culture()
        result.placeNameGenerator = gen

        #pickle.dump( result, open(cachedCulture, 'wb' ))
        gen.cache( cachedPlacenames )

    # Rank
    if ranks:
        result.ranks = ranks

    # Test cities
    # targetNum = 20
    # uniqCount = 0
    # for i in range(targetNum):
    #     #city = result.genPlaceName()
    #     city = result.genContinentName()
    #     print city.title()

    CULTURES[ident] = result

    return result

def setupCultures():

    newWorldRanks =[ ('Secretary-General', 'Secretary-General'),
                       ('President', 'President'),
                       ('Governer', 'Governer'),

                       [('Mayor','Mayor'), # Other misc nobility
                        ('Representitive', 'Representitive'),
                        ('Congressman', 'Congresswoman') ] ]

    setupCulture( "newworld", [ 'us', 'ca'], 50000, 5, ranks=newWorldRanks )

    setupCulture( "oldworld", [ 'gb', 'ie'], 50000, 5 ) # Old world uses default ranks

    # Magical, quasi-religious ranks
    islandRanks = [ ('God Priest', 'Goddess'),
                       ('Archdruid', 'Archdruidess'),
                       ('High Priest', 'High Priestess'),

                       [('Bishop','Mayor'), # Other misc nobility
                        ('Seer', 'Devoted'),
                        ('Watcher', 'Watcher') ] ]
    setupCulture( "island", [ 'ba', 'aw', 'ai', 'bb', 'bm', 'vg', 'ky', 'ht', 'jm', 'kn', 'sc', 'tt', 'tm', 'vi' ],
                   10000, 5 )

    # Needs more cleanup on input data
    # setupCulture( "spanish", [ 'es', 'mx', 'cr', 'br'], 50000, 5 )
    setupCulture( "india", [ 'in' ], 50000, 5 )

    setupCulture( "nordic", [ 'fi', 'se', 'no' ], 50000, 4 )



if __name__=='__main__':

    setupCultures()