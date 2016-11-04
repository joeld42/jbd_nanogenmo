import os, sys
import random

import tracery
from tracery.modifiers import base_english

from pulpmill import world, scene, storygen, character, utils


title_rules = {
    'origin' : ['#a_conflict# #preposition# #desc_context#', '#a_and_b#',
                'the #desc_context#'],

    'a_and_b' : [ 'the #context# and the #desc_context#', 'of #context# and #context#',
                  '#context# and #context#'],

    'conflict' : ['war', 'battle', '#weather#', 'shadow', 'king', 'lord', 'god',
                  'trials', 'time', 'age', 'host' ],
    'a_conflict' : ['#conflict#','the #conflict#', 'a #conflict#'],
    'preposition' : ['of the', 'above the', 'through', 'amidst', 'among', 'amongst',
                     'beyond', 'against', 'from the', 'between'],
    'desc_context' : ['#context#', '#awesome# #context#'],
    'context' : ['rings', 'dragons', 'swords', 'roses', 'kingdoms',
                 'wizards', 'sorcerers', 'curses', 'spells', '#season#',
                 '#barren# lands', 'dungeons', 'fortresses', 'enchantresses',
                 'queens', 'kings'],

    'awesome' : ['lost', 'mighty', 'forgotten', 'purple', 'heavenly', '#number#',
                 'undead', 'unholy', 'cursed', 'hidden', 'false',
                 'royal', 'promised', 'forgotten', '#season#', 'golden' ],
    'number' : ['two', 'three', 'seven', 'nine', 'hundred'],
    'weather' : ['storm', 'thunder', 'lightning'],
    'season' : ['spring', 'summer', 'winter', 'autumn', 'night', 'dawn' ],
    'barren' : ['broken', 'barren', 'burning', 'auburn']
}


class Novel(object):

    def __init__(self, cultures):
        self.cultures = cultures
        self.scenes = []

    def generate(self):


        self.map = world.World( self.cultures )
        self.map.buildMap()

        # Main character
        firstNode = self.map.storyPath[0]
        self.protag = character.Character( firstNode )

        self.party = []

        self.scenes += storygen.sceneNormalLife( firstNode, self.protag )

        if (utils.randomChance(0.5)):
            self.scenes += storygen.scenePlaceDesc( firstNode )

        # Scramble the prologue scenes
        random.shuffle( self.scenes )

        self.scenes += storygen.sceneIncitingIncident( firstNode, self.protag )

        # Walk the story path to generate scenes
        lastNode = None
        for item in self.map.storyPath:
            if isinstance(item,world.TerrainNode):

                if item.city:
                    self.scenes += storygen.sceneCity( item )
                    lastNode = item

                else:
                    # TODO encounter nodes
                    pass

            elif isinstance(item,world.TerrainArc):

                if item.arcType == world.TerrainArc_SEA:
                    self.scenes += storygen.sceneSeaVoyage(  lastNode, item )


        self.title = self.genTitle()




    def dbgPrint(self):

        print "Novel: ", self.title
        print "Setting Info: "
        self.map.dbgPrint()

        print "---- SCENES: -------"
        for scn in self.scenes:
            print "-", scn.desc, "("+scn.chapterTitle+")"

        wordCount = 50000 / len(self.scenes)
        print "For a 50K novel, each scene would need to be approx ", wordCount, "words."

    def genTitle(self):
        grammar = tracery.Grammar( title_rules )
        grammar.add_modifiers( base_english )
        title = grammar.flatten( "#origin#").title()

        return title