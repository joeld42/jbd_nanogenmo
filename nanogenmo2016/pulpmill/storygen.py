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

    def __init__(self):
        pass

    def getFruitRules(self):

        if not StoryGen._fruits:
            with open( os.path.join( CORPORA_ROOT, 'data', 'foods', 'fruits.json') ) as datafile:
                data = json.load(datafile)
                StoryGen._fruits = data['fruits']

        return StoryGen._fruits

    def getWeatherRules(self, node ):

        if not StoryGen._weather:

            # Note this is kind of broken since StoryGen might not be a singleton but
            # im not fixing it for this project
            self.season = random.choice(['winter', 'summer', 'spring', 'fall'])
            # the rainy season? dry season?

            #DBG
            self.season = 'fall'

            StoryGen._weather = {
                "season" : [ self.season ],
                'weather_airword' : [ 'air', 'wind', 'breeze' ],
                'weather_air' : [ '#weather_airword#', '#weather_adj# #weather_airword#'],
                'weather_sentence' : ['#weather_airborne_stuff1# #weather_air_verb# in the #weather_air#.' ],
                'weather_airborne_stuff1' : [ '#weather_airborne_stuff#', '#weather_adj# #weather_airborne_stuff#'],
            }
            weather_air_verbs_C = [ 'danced', 'floated', 'hung', 'hovered', 'spun']

            if self.season == 'winter':
                StoryGen._weather.update( {
                    'weather_airborne_stuff' : [ 'snow', 'rain', 'sleet', 'mist' ],
                    'weather_air_verb' : ['sliced', 'tinkled' ] + weather_air_verbs_C,
                    'weather_adj' : ['frigid', 'icy', 'frozen', 'bitter', 'cool', 'chilly', 'frosty' ],
                })
            elif self.season == 'summer':
                StoryGen._weather.update( {

                    'weather_airborne_stuff' : [ 'dust', 'haze', 'mist', 'motes', 'specks of dust', '#bug.s#' ],
                    'weather_air_verb' : ['tarried', 'rose' ] + weather_air_verbs_C,
                    'weather_adj' : ['warm', 'hot', 'stagnant', 'languid', 'humid', 'dry', 'dusty', 'sun-dappled' ],
                })
            elif self.season == 'spring':
                StoryGen._weather.update( {
                    'bird' : ['starling', 'sparrow', 'nuthatch' ],
                    'weather_airborne_stuff' : [ 'dew', 'mist', 'birds', 'pollen', 'rain' ],
                    'weather_air_verb' : ['lifted', 'sparkled', 'rose', 'played' ] + weather_air_verbs_C,
                    'weather_adj' : ['warm', 'cool', 'fresh', 'verdant', 'dewy' ],
                })
            elif self.season == 'fall':
                StoryGen._weather.update( {
                    'bird' : ['crow', 'vulture', 'owl' ],
                    'weather_airborne_stuff' : [ 'leaves', '#bug.s#', 'rain', '#bird.s#' ],
                    'weather_air_verb' : ['cooled', 'waited', 'fell', 'settled' ] + weather_air_verbs_C,
                    'weather_adj' : ['warm', 'cool', 'stale', 'smoky', 'fetid', 'languid', 'tired' ],
                })


        return StoryGen._weather


    def getCommonRules(self, node ):

        if not StoryGen._common:
            StoryGen._common = {
                'bug' : ['bee', 'gnat', 'cicada', 'butterfly', 'locust', 'insect']
            }
        rules = StoryGen._common.copy()

        rules.update( self.getWeatherRules( node ) )
        return rules

# --------------------------------------------

def sceneIncitingIncident( node, protag ):

    scn = scene.Scene()
    scn.node = node
    scn.chars = [ protag ]
    scn.desc = "Inciting Incident "
    return [ scn ]


def scenePlaceDesc( node ):

    scn = scene.ScenePlaceDesc()
    city = node.city
    scn.desc = "Description of " + city.name
    scn.chapterTitle = city.name
    scn.origin= '#weather_sentence.capitalize#'
    scn.node = node
    
    node.storyVisited = True

    return [ scn ]

def sceneCity( node ):

    scenes = []

    if not node.storyVisited:
        scenes += scenePlaceDesc( node )

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


