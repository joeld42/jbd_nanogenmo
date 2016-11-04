import os, sys

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

        self.hometown = homenode.city
        self.culture = self.hometown.kingdom.culture

        grammar = tracery.Grammar( NAME_RULES )
        grammar.add_modifiers( base_english )
        name = grammar.flatten( "#origin#")

        if name.find('$AA') != -1:
            markovName = self.culture.genContinentName() # FIXME: need a person name generator
            name = name.replace( '$AA', markovName )

        self.name = name


