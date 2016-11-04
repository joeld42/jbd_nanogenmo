import os, sys
import random

import tracery
from tracery.modifiers import base_english

from pulpmill import world, scene, utils

def scenePlaceDesc( node ):

    scn = scene.Scene()
    city = node.city
    scn.desc = "Description of " + city.name
    scn.chapterTitle = city.name

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


