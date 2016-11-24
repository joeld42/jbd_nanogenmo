import os, sys
import random
import utils

import tracery
from tracery.modifiers import base_english

from pulpmill import world

# Characters are referred to in the substitution text as 'protag', 'alice',
# 'bob', and 'chuck'. (e.g. "#chuckName# handed #protagThem# a fruit").
# Protag is the main character, and alice, bob and chuck are three randomly
# selected characters from the party.


TWITTER_FOLKS = [
    "Booyah",  # @booyaa
    "Cindee", # @rgrrl
    "Blackle Mori",  # @blacklemon67
    "Jovoc", # @joeld42
    "Zecmo", # @zecmo,
    "Nikon Pythed", # @Tariq_Ali38

]

NAME_RULES = {
    "origin" : ['#twitter#', '#markov#', '#markov#', '#markov#', '#markov#', '#markov#' ],
    "twitter" : TWITTER_FOLKS,
    "markov" : ['$AA']
}

class CharacterClass( object ):

    def __init__(self, rpgClass, rules ):
        self.rpgClass = rpgClass
        self.rules = rules

    def getCharClassRules(self):

        charClassRules = {
            'ROLEClass' : self.rpgClass
        }

        charClassRules.update( self.rules )

        return charClassRules


def setupRpgClasses():

    rpgClasses = []

    cc = CharacterClass( 'Barbarian',
                         {
                             'weapon' : ['battle-axe', 'great sword'],
                             'attack' : [ '#ROLEName# swung #ROLETheir# #weapon# and struck the #enemy#.'],
                             'block'  : ['#ROLEName# blocked it with #ROLETheir# bare hands.']
                         })
    rpgClasses.append(cc)

    # cc = CharacterClass( 'Bard',
    #                      )
    # rpgClasses.append(cc)
    #
    # cc = CharacterClass( 'Cleric')
    # rpgClasses.append(cc)
    #
    # cc = CharacterClass( 'Druid')
    # rpgClasses.append(cc)
    #
    # cc = CharacterClass( 'Fighter')
    # rpgClasses.append(cc)
    #
    # cc = CharacterClass( 'Mage')
    # rpgClasses.append(cc)
    #
    # cc = CharacterClass( 'Monk')
    # rpgClasses.append(cc)
    #
    # cc = CharacterClass( 'Paladin')
    # rpgClasses.append(cc)
    #
    # cc = CharacterClass( 'Ranger')
    # rpgClasses.append(cc)
    #
    # cc = CharacterClass( 'Thief')
    # rpgClasses.append(cc)
    #
    # cc = CharacterClass( 'Witch')
    # rpgClasses.append(cc)
    #
    # cc = CharacterClass( 'Elementalist')
    # rpgClasses.append(cc)


    return rpgClasses

class Character( object ):

    _rpgClasses = None

    def __init__(self, homenode ):

        self.homenode = homenode
        self.hometown = homenode.city
        self.culture = self.hometown.kingdom.culture
        self.hp = 3

        if not Character._rpgClasses:
            Character._rpgClasses = setupRpgClasses()

        self.rpgClass = random.choice( Character._rpgClasses )

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
            'ROLEJob' : self.job,
        }

        charRules.update (self.rpgClass.getCharClassRules() )

        charRules.update( self.pronouns )

        charRules2 = {}
        for key, item in charRules.iteritems():

            # fixme: make this handle lists as well as strings
            key2 = key.replace( 'ROLE', role )
            charRules2[key2] = item

        return charRules2

