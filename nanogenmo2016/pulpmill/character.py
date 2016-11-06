import os, sys
import random
import utils

import tracery
from tracery.modifiers import base_english

from pulpmill import world, scene, storygen

TWITTER_FOLKS = [
    "Booyah",  # @booyaa
    "Cindee", # @rgrrl
    "Blackle Mori",  # @blacklemon67
    "Jovoc", # @joeld42
    "Zecmo", # @zecmo,
    "Nikon Pythed", # @Tariq_Ali38

]

NAME_RULES = {
    "origin" : ['#twitter#', '#markov#' ],
    "twitter" : TWITTER_FOLKS,
    "markov" : ['$AA']
}

class Character( object ):

    def __init__(self, homenode ):

        self.homenode = homenode
        self.hometown = homenode.city
        self.culture = self.hometown.kingdom.culture

        grammar = tracery.Grammar( NAME_RULES )
        grammar.add_modifiers( base_english )
        name = grammar.flatten( "#origin#")

        jobs = [ 'baker', 'farmer', 'soldier', 'carpenter' ]
        if self.hometown.port:
            jobs += [ 'fisherman', 'sailor', 'dockworker' ]

        self.job = random.choice( jobs )

        self.rules = []

        if (utils.randomChance(0.5)):
            self.gender = "male"
            self.pronouns = { "ROLEThey":"he", "ROLEThem":"him", "ROLETheir":"his","ROLETheirs":"his" }
        else:
            self.gender = "female"
            self.pronouns = { "ROLEThey":"she", "ROLEThem":"her", "ROLETheir":"her","ROLETheirs":"hers" }

        if name.find('$AA') != -1:
            markovName = self.culture.genContinentName() # FIXME: need a person name generator
            name = name.replace( '$AA', markovName )

        self.name = name

    def getPronouns(self, tag ):

        return self.pronouns.replace('char', tag)

    def getCharacterRules(self, role ):
        """role is the character's name in this scene"""

        charRules = {
            'ROLEName' : self.name,
            'ROLEHome' : self.hometown.name,
            'ROLEKingdom' : self.homenode.kingdom.name,
            'ROLEJob' : self.job
        }

        charRules.update( self.pronouns )

        charRules2 = {}
        for key, item in charRules.iteritems():

            # fixme: make this handle lists as well as strings
            key2 = key.replace( 'ROLE', role )
            charRules2[key2] = item

        return charRules2

