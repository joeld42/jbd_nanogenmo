import os, sys

import tracery
from tracery.modifiers import base_english

from pulpmill import world

title_rules = {
    'origin' : ['#a_conflict# #preposition# #desc_context#'],
    'conflict' : ['war', 'battle', '#weather#', 'shadow', 'king', 'lord', 'god'],
    'a_conflict' : ['#conflict#','the #conflict#', 'a #conflict#'],
    'preposition' : ['of the', 'above the', 'through', 'amidst', 'among' ],
    'desc_context' : ['#context#', '#awesome# #context#'],
    'context' : ['rings', 'dragons', 'swords', 'roses', 'ages' ],

    'awesome' : ['lost', 'mighty', 'forgotten', 'purple', 'heavenly'],
    'weather' : ['storm', 'thunder', 'lightning']
}


class Novel(object):

    def __init__(self):
        pass

    def generate(self):

        self.map = world.World()
        self.map.buildMap()

        self.title = self.genTitle()


    def dbgPrint(self):

        print "Novel: ", self.title
        print "Setting Info: "
        self.map.dbgPrint()

    def genTitle(self):
        grammar = tracery.Grammar( title_rules )
        grammar.add_modifiers( base_english )
        title = grammar.flatten( "#origin#").title()

        return title