import os, sys, copy
import random

import tracery
from tracery.modifiers import base_english
import json

from pulpmill import world, scene, utils

# https://github.com/dariusk/corpora
CORPORA_ROOT = './extern/corpora'

class StoryGen(object):

    _fruits = None
    _weather = None
    _common = None
    _region = None

    def __init__(self):
        pass

    def getFruitRules(self):

        if not StoryGen._fruits:
            with open( os.path.join( CORPORA_ROOT, 'data', 'foods', 'fruits.json') ) as datafile:
                data = json.load(datafile)
                StoryGen._fruits = data['fruits']

        return StoryGen._fruits

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
                    "critter" : [ "goat", "bird", "eagle" ],
                    "ground" : [ "rocks", "narrow path", "stones"],
                    "natureThing" : ["thin branch", "skree", "bones of a #critter#", "#critter# scat"]
                },
                "swamp": {
                    "critter" : [ "alligator", "rat", "lizard" ],
                    "ground" : [ "mud", "mire", "muck", "fetid soil", "bog"],
                    "natureThing" : [ "dirt mound", "dry patch", "#critter# corpse", "#critter# scat" ]

                },
                "forest": {
                    "critter" : [ "bear", "rat", "lizard" ],
                    "ground" : [ "fallen logs", "undergrowth", "moss", "leaves", "pine straw"],
                    "natureThing" : ["stump", "lichen", "fern", "#critter#'s den", "log" ]
                },
                "desert": {
                    "critter" : [ "horse", "camel", "iguana", "rattlesnake" ],
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


                # Deep Thoughts
                'wondered' : ['wondered about', 'pondered', 'considered', 'thought about'],
                'the_future' : [ 'the future', '#protagTheir# future', 'what was coming', '#protagTheir# next steps',
                                 'all that had happened', '#protagTheir# journey', 'the #weather_air#',
                                 '#protagTheir# home back in #protagHome#', 'a #critter#',
                                 '#protagTheir# simple life as a #protagJob#. That was gone now.'
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
                if node.city.port:
                    portDirs = ['toward the #ocean#', 'away from the #ocean#', 'by the #ocean#' ]

                rules.update( {
                    "cityname" : [ node.city.name ],
                    "citytype" : citytype[node.city.size],
                    "cityDir" : ["#compassDir#", "uphill", "downhill" ] + portDirs,
                    'cityWalked' : [ 'walked', 'turned', 'strolled', 'wandered' ],

                    # city rules
                    "marketDesc" : ['tiny', 'overlooked', 'busy', 'tidy', 'messy', 'colorful', 'nearly empty'],
                    "marketStall" : [ 'stall', '#marketDesc# stall', 'vendor'],
                    "propBuilding" : [ 'smithy', 'tavern', 'clothseller', 'armourer', "shipwright's office", 'garrison',
                                       'grainery', 'church', 'plaza', 'bakery' ],
                })

            if node.region:
                rules.update( self.getRegionRules( node ))

            if node.kingdom:
                rules.update( self.getKingdomRules( node.kingdom ))

        rules.update( self.getWeatherRules( node ) )

        return rules

# --------------------------------------------

def sceneIncitingIncident( node, protag ):

    scn = scene.Scene()
    scn.node = node
    scn.chars = { "protag" : protag }
    scn.desc = "Inciting Incident"

    #TEST -- Replace with inciting scene from quest
    scn.origin = "#protagName#'s life was about to change in ways #protagThey# never expected."
    return [ scn ]


def scenePlaceDesc( node, protag ):

    scn = scene.ScenePlaceDesc()
    city = node.city
    scn.chars = { "protag" : protag }
    scn.desc = "Description of " + city.name
    scn.chapterTitle = city.name
    scn.origin= '#weather_sentence.capitalize#'
    scn.node = node

    node.storyVisited = True

    return [ scn ]

def sceneCity( node, protag ):

    scenes = []

    if not node.storyVisited:
        scenes += scenePlaceDesc( node, protag )

    scn = scene.Scene()
    if node.city.dungeon:
        scn.desc = "Adventure in " + node.city.name
    elif node.city.port:
        scn.desc = "Visit Port town of " + node.city.name
    else:
        scn.desc = "Visit City " + node.city.name

    scenes.append( scn )

    return scenes

def sceneNormalLife( node, char ):

    scenes = []

    scn = scene.Scene()
    scn.desc = char.name + " does normal stuff in " + node.city.name
    scenes.append( scn )

    return scenes

def sceneSeaVoyage( node, arc ):

    # TODO: more types of sea voyages
    print "destNode", node, node.city, "arc:", arc.arcType
    print "arc", arc.a.city.name, arc.b.city.name
    destNode = arc.other(node)

    scenes = []

    if utils.randomChance(0.3):
        scn = scene.Scene()
        scn.desc = "Finding passage in " + node.city.name
        scn.chapterTitle = "Find a boat" # name of the boat?
        scenes.append( scn )

    scn = scene.Scene()
    scn.desc = "Voyage to " + destNode.city.name
    scenes.append( scn )

    if utils.randomChance(0.3):
        scn = scene.Scene()
        scn.desc = "Arriving in " + node.city.name
        scenes.append( scn )

    return scenes


