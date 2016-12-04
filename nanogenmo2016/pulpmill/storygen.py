import os, sys, copy
import random

import tracery
from tracery.modifiers import base_english
import json

from pulpmill import world, scene, utils, character


# https://github.com/dariusk/corpora
CORPORA_ROOT = './extern/corpora'

class StoryGen(object):

    _fruits = None
    _weather = None
    _common = None
    _region = None
    _tarot = None
    _colorSchemes = None

    def __init__(self):
        pass

    def getFruitRules(self):

        if not StoryGen._fruits:
            with open( os.path.join( CORPORA_ROOT, 'data', 'foods', 'fruits.json') ) as datafile:
                data = json.load(datafile)
                StoryGen._fruits = data['fruits']

        return StoryGen._fruits

    def getTarotMeanings(self):

        if not StoryGen._tarot:
            with open( os.path.join( CORPORA_ROOT, 'data', 'divination', 'tarot_interpretations.json') ) as datafile:
                    data = json.load(datafile)
                    StoryGen._tarot = data['tarot_interpretations']

        return StoryGen._tarot

    def getColorSchemes(self):
        if not StoryGen._colorSchemes:
            with open( os.path.join( CORPORA_ROOT, 'data', 'colors', 'palettes.json') ) as datafile:
                data = json.load(datafile)
                StoryGen._colorSchemes = data['palettes']

        return StoryGen._colorSchemes

    def getKingdomRules(self, kingdom ):

        return {
            "kingdomname" : [ kingdom.name ],
            "kfruit1" : [ kingdom.fruits[0] ], # Main fruit grown in kingdom
            "kfruit2" : [ kingdom.fruits[1] ], # Other common fruits in kingdom
            "kfruit3" : [ kingdom.fruits[2] ],
            "kfruit"  : [ "#kfruit1#", "#kfruit2#", "#kfruit3#"],
        }

    def getRegionRules(self, node ):

        if not StoryGen._region:
            StoryGen._region = {
                "mountain": {
                    "region" : ["mountain", "rocky steppe", "steep shard", "crater"],
                    "critter" : [ "goat", "bird", "eagle" ],
                    "ground" : [ "rocks", "narrow path", "stones"],
                    "magic_nature" : [ 'tree', 'cloud', 'mist', 'wind'],
                    "natureThing" : ["thin branch", "skree", "bones of a #critter#", "#critter# scat"]
                },
                "swamp": {
                    "region" : [ "swamp", "bog", "marsh", "wetland", "salt marsh", "marshland", "estuary" ],
                    "critter" : [ "alligator", "rat", "lizard" ],
                    "magic_nature" : [ 'bog', 'swamp', 'water', 'murk'],
                    "ground" : [ "mud", "mire", "muck", "fetid soil", "bog"],
                    "natureThing" : [ "dirt mound", "dry patch", "#critter# corpse", "#critter# scat" ]
                },
                "forest": {
                    "region" : [ "forest", "wood", "woodland", "grove", "wilderness", "jungle", "pine forest"  ],
                    "critter" : [ "bear", "rat", "lizard" ],
                    "magic_nature" : [ 'wood', 'moss', 'stone', 'forest'],
                    "ground" : [ "fallen logs", "undergrowth", "moss", "leaves", "pine straw"],
                    "natureThing" : ["stump", "lichen", "fern", "#critter#'s den", "log" ]
                },
                "desert": {
                    "region" : [ "desert", "prarie", "arid sands", "high desert" ],
                    "critter" : [ "horse", "camel", "iguana", "rattlesnake", "armadillo",
                                  "rabbit", "hare", "shrew", "bat", "mouse", "coyote",
                                  "scorpian", "crow", "fox", "jackal", "oryx", "sand cat",
                                  "meercat", "xerus", "viper", "toad", "horned toad",
                                  "tortoise", "hyrax", "cobra", "chipmunk", "caracal",
                                  "aardwolf" ],
                    "magic_nature" : [ 'sand', 'sun', 'desert', 'salt'],
                    "ground" : [ "rocks", "sand", "cracked mud"],
                    "natureThing" : ["outcrop", "gulley", "bonepile", "creekbed", "#critter# skull"]
                },
            }

        return StoryGen._region[ node.region.ident ]

    def getWeatherRules(self, node ):

        if not StoryGen._weather:

            # Note this is kind of broken since StoryGen might not be a singleton but
            # im not fixing it for this project
            self.season = random.choice(['winter', 'summer', 'spring', 'fall'])
            # the rainy season? dry season?

            StoryGen._weather = {
                "season" : [ self.season ],
                'weather_airword' : [ 'air', 'wind', 'breeze' ],
                'weather_air' : [ '#weather_airword#', '#weather_adj# #weather_airword#'],
                'weather_sentence' : ['#weather_airborne_stuff1# #weather_air_verb# in the #weather_air#.',
                                      '#weather_ground_stuff# rested on the #ground#.'],
                'weather_airborne_stuff1' : [ '#weather_airborne_stuff#', '#weather_adj# #weather_airborne_stuff#'],
            }
            weather_air_verbs_C = [ 'danced', 'floated', 'hung', 'hovered', 'spun']

            if self.season == 'winter':
                StoryGen._weather.update( {
                    'weather_airborne_stuff' : [ 'snow', 'rain', 'sleet', 'mist' ],
                    'weather_ground_stuff' : [ 'snow', 'puddles', 'ice' ],
                    'weather_air_verb' : ['sliced', 'tinkled' ] + weather_air_verbs_C,
                    'weather_adj' : ['frigid', 'icy', 'frozen', 'bitter', 'cool', 'chilly', 'frosty' ],
                })
            elif self.season == 'summer':
                StoryGen._weather.update( {

                    'weather_airborne_stuff' : [ 'dust', 'haze', 'mist', 'motes', 'specks of dust', '#bug.s#' ],
                    'weather_ground_stuff' : [ 'dirt', 'dry grass', 'chaff' ],
                    'weather_air_verb' : ['tarried', 'rose' ] + weather_air_verbs_C,
                    'weather_adj' : ['warm', 'hot', 'stagnant', 'languid', 'humid', 'dry', 'dusty', 'sun-dappled' ],
                })
            elif self.season == 'spring':
                StoryGen._weather.update( {
                    'bird' : ['starling', 'sparrow', 'nuthatch' ],
                    'weather_airborne_stuff' : [ 'dew', 'mist', 'birds', 'pollen', 'rain' ],
                    'weather_ground_stuff' : [ 'toadstools', 'dew', 'feathers', '#critter# poop' ],
                    'weather_air_verb' : ['lifted', 'sparkled', 'rose', 'played' ] + weather_air_verbs_C,
                    'weather_adj' : ['warm', 'cool', 'fresh', 'verdant', 'dewy' ],
                })
            elif self.season == 'fall':
                StoryGen._weather.update( {
                    'bird' : ['crow', 'vulture', 'owl' ],
                    'weather_airborne_stuff' : [ 'leaves', '#bug.s#', 'rain', '#bird.s#' ],
                    'weather_ground_stuff' : [ 'leaves', 'dry branches', 'dust' ],
                    'weather_air_verb' : ['cooled', 'waited', 'fell', 'settled' ] + weather_air_verbs_C,
                    'weather_adj' : ['warm', 'cool', 'stale', 'smoky', 'fetid', 'languid', 'tired' ],
                })


        return StoryGen._weather


    def getCommonRules(self, node ):

        if not StoryGen._common:
            StoryGen._common = {
                'bug' : ['bee', 'gnat', 'cicada', 'butterfly', 'locust', 'insect'],
                'economic_state' : ['poor', 'wealthy', 'modest', 'rich' ],
                'civic_state' : [ 'proud', 'stable', 'hungry', 'growing'],
                'beautiful' : ['beautiful', 'charming', 'lovely', 'enchanting', 'alluring' ],
                'foodQuality' : ['delicious', 'good', 'sweet', 'rotten', 'bland', 'juicy', 'sour'],
                'ocean' : ['sea', 'ocean', 'water', 'docks', 'ships', 'boats', 'beach', 'pier'],
                'compassDir' : [ 'north', 'northeast', 'east', 'southeast', 'south', 'southwest', 'west', 'northwest' ],
                'rough' : ['rough', 'coarse', 'tough', 'grizzled'],
                'legends' : ['legends', 'old stories', 'old tales', 'some tales', 'whispered rumors', 'rumors' ],
                'industry' : ['mining', 'logging', 'blacksmithing', 'mercenary', 'farming' ],
                'kind' : ['kind', 'friendly', 'agreeable', 'generous', 'welcoming', 'hospitable' ],
                'mean' : [ '#rough#', 'mean', 'grumpy', 'drunk', 'bitter', 'sour', 'angry' ],
                'kind_or_mean' : ["#kind#", "#mean#"],

                # Magic and Stuff
                'type_of_elves' : ['#magic_nature# elves', 'druids' ],

                # Descriptive Nonsense
                'purple' : ['golden', 'shimmering', 'purple', '#purple# and #purple',
                            'fiery', 'auburn'],
                'fungus' : ['fungus', 'root system', "vole's burrow" ],
                'bad_vibe' : ['oppressive', 'claustrophobic', 'empty', 'gloomy', 'foreboding' ],
                'long_time' : ['a #thousand# #years#', "#ages#", "since before #the_past#"],
                'ages' : ['ages', 'aeons', 'epochs', 'millenia'],
                'years' : ['moons', 'years', 'seasons' ],
                'thousand' : ['thousand', 'hundred', 'uncounted' ],
                'the_past' : ['the great war', 'the age of man', 'recorded history', 'living memory'],
                'in_the_distance' : ['in the distance', 'on the horizon', 'across the sky', 'behind them',
                                     'above them', 'toward the heavens'],
                'moodLighting' : ['The sunset was #purple# #in_the_distance#.',
                                  '#purple.capitalize# clouds hung #in_the_distance#.',
                                  'The #weather_adj# air looked #purple#.'
                                  ],
                'humble' : [ 'humble', 'regular', 'skilled', 'apprentice', 'practiced'],

                # Misc
                'said' : ['said', 'cried', 'yelled', 'exclaimed', 'whispered', 'suggested', 'whimpered'],
                'silly_exclaim' : [ "Yeargh!", "Oh Hells", "Yipes", "Why not?", "For Glory!", "AaaAaaaaaAA",
                                    "Victory!", "Oh Fudge it!"],
                'daytime' : ['morning', 'evening', 'afternoon' ],
                'fish' : ['halibut', 'tuna', 'whitefish', 'scalefish', 'bonefish'],

                # Deep Thoughts
                'wondered' : ['wondered about', 'pondered', 'considered', 'thought about'],
                'the_future' : [ 'the future', '#protagTheir# future', 'what was coming', '#protagTheir# next steps',
                                 'all that had happened', '#protagTheir# journey', 'the #weather_air#',
                                 '#protagTheir# home back in #protagHome#', 'a #critter#',
                                 '#protagJobTask# back in #protagHome#. #that_was_gone#'
                                 '#protagTheir# simple life as a #protagJob#. #that_was_gone#'
                                 ],
                'that_was_gone' : [ "", "That was gone now...", "Those days were over.", "That life was just a memory now."],
                'the_feels' : [ "happy", "sad", "wistful", "forlorn", "confused", "good", "foul" ],
                'it_gave_feels' : [
                    "it reminded #protagThem# of #protagHome#.",
                    "and felt #the_feels#.",
                    ". #protagThey.capitalize# felt #the_feels#, but didn't dwell.",
                    "and it cheered #protagThem# up for a moment.",
                    ", this put #protagThem# in a #the_feels# mood."
                ],
                'thinkWonder' : [ '#protagName# #wondered# #the_future#.'],
            }

        rules = StoryGen._common.copy()

        if node:

            if node.city:
                citytype = {
                    'small' : [ 'village' ],
                    'medium' : [ 'city', 'town' ],
                    'large' : [ 'city', 'metropolis' ],
                }

                portDirs = []
                portPropBuildings = []
                portPropJobs = []
                if node.city.port:
                    portDirs = ['toward the #ocean#', 'away from the #ocean#', 'by the #ocean#' ]
                    portPropBuildings = [ "shipwright's office", "fishmonger's", "fisherman's hovel" ]
                    portPropJobs = [ 'sailer', 'fisherman', 'fisherwoman', 'fishmonger' ]

                rules.update( {
                    "cityname" : [ node.city.name ],
                    "citytype" : citytype[node.city.size],
                    "cityDir" : ["#compassDir#", "uphill", "downhill" ] + portDirs,
                    "dungeonDir" : ["#compassDir#", "downward" ],
                    'cityWalked' : [ 'walked', 'turned', 'strolled', 'wandered' ],

                    # city rules
                    "marketDesc" : ['tiny', 'overlooked', 'busy', 'tidy', 'messy', 'colorful', 'nearly empty'],
                    "marketStall" : [ 'stall', '#marketDesc# stall', 'vendor'],
                    "propBuilding" : [ 'smithy', 'tavern', 'clothseller', 'armourer', 'garrison',
                                       'grainery', 'church', 'plaza', 'bakery' ] + portPropBuildings,
                    "propJob" : ['cobbler', 'blacksmith', 'armourer', 'wizard', 'monk', 'mercenary', 'merchant',
                                 'miller', 'street vendor', 'beggar', 'priest',
                                 'tinker', 'tailer', 'soldier', 'scribe' ] + portPropJobs
                })

            if node.region:
                rules.update( self.getRegionRules( node ))
            else:
                print "WARNING: node lacks a region"


            if node.kingdom:
                rules.update( self.getKingdomRules( node.kingdom ))

        rules.update( self.getWeatherRules( node ) )

        return rules




