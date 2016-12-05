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
    "Cinder", # @rgrrl
    "Blackle Mori",  # @blacklemon67
    "Jovoc", # @joeld42
    "Zecmo", # @zecmo,
    "Nikon Pythed", # @Tariq_Ali38

]

# NAME_RULES = {
#     "origin" : ['#twitter#', '#markov#', '#markov#', '#markov#', '#markov#', '#markov#' ],
#     "twitter" : TWITTER_FOLKS,
#     "markov" : ['$AA']
# }

class CharacterClass( object ):

    def __init__(self, rpgClass, weapons, rules ):
        self.rpgClass = rpgClass
        self.rules = rules
        self.rules['weapon'] = random.choice( weapons )

    def getCharClassRules(self):

        charClassRules = {
            'ROLEClass' : self.rpgClass
        }

        charClassRules.update( self.rules )

        return charClassRules


def setupRpgClasses():

    rpgClasses = []

    # NOTE: blocks aren't yet used so they're not filled out

    cc = CharacterClass( 'Barbarian', ['battle-axe', 'great sword', 'halbard', 'pole-arm' ],
                         {
                             'attack' : [ '#ROLEName# swung #ROLETheir# #weapon# at #monsterName#'],
                             'block'  : ['#ROLEName# blocked it with #ROLETheir# bare hands.']
                         })
    rpgClasses.append(cc)

    cc = CharacterClass( 'Bard', ['lute', 'lyre', 'flute', 'harp', 'panpipe', 'bagpipe' ],
                         {
                             'attack' : [ '#ROLEName# played a jaunty tune on the #weapon# and it dazed #monsterName#',
                                          '#ROLEName# #said#, "#silly_exclaim#", and smacked #monsterName# with the #weapon#',
                                          '"Music," #said# #ROLEName#, "can tame the savage #monsterName#!" ',
                                          '#ROLEName# raised #ROLETheir# #weapon#. #ROLEThey# hit the '+
                                            'brown note, and the #monsterName# was gravely moved',
                                          '#ROLEName# played an old melody, an enchanted tune on '+
                                            'the #weapon# and the #monsterName# #m_moved# helplessly and was knocked back,'
                                          ],
                             'block'  : [ '"#silly_exclaim#", #said# #ROLEName#, and blocked the #monsterName# with #ROLETheir# #weapon#',
                                          "#ROLEName# played a bizarre arpeggio on the #weapon# and it confused the #monsterName#"
                                        ],
                                })
    rpgClasses.append(cc)

    # cc = CharacterClass( 'Cleric')
    # rpgClasses.append(cc)
    #
    cc = CharacterClass( 'Druid', ['tree branch', 'staff', 'Druid Staff', 'quarterstaff', "bird's nest" ],
                         {
                             'attack' : [ "#ROLEName# struck with #ROLETheir# #weapon#",
                                          "#ROLEName# draw upon the power of nature with #ROLETheir# #weapon#",
                                          "#ROLEName# drew power from the #magic_nature#"
                                          "The spirits of the forest inhabited #ROLEName#'s #weapon#",
                                          "#ROLEName# cast entangle, and brambles grew to cover #monsterName#"
                                          ],
                             'block'  : ['#ROLEName# blocked it with #ROLETheir# bare hands.']
                         })
    rpgClasses.append(cc)

    cc = CharacterClass( 'Fighter', [ "sword", "axe", "longsword", "broadsword", "short sword" ],
                         {
                             'attack' : [ "#ROLEName# slashed with #ROLETheir# #weapon#",
                                          "#ROLEName# executed a practiced move with #ROLETheir# #weapon#",
                                          "#ROLEName#'s #weapon# flashed in the #weather_air#",
                                          "#ROLEName# struck at the #monsterName#",
                                          "#ROLEName#'s #weapon# swung at #monsterName#"
                                          ],
                             'block'  : ['#ROLEName# blocked it with #ROLETheir# bare hands.']
                         })
    rpgClasses.append(cc)

    cc = CharacterClass( 'Mage', [ "staff", "amulet", "fingers" ],
                         {
                             'combatElement' : ['fire', 'steam', 'ice', 'lightning'],
                             'attackSpell' : ['Magic Missle', 'Fireball', 'Lighting', 'Force Lightning',
                                              'Fury of #combatElement.capitalize#', 'Burning Hands',
                                              'Flaming Sphere', 'Shatter'],
                             'attack' : [ "#combatElement.capitalize# flew from #ROLEName#'s #weapon#",
                                          "#ROLEName# waved #ROLETheir# #weapon# and #combatElement# materialized around #monsterName#",
                                          "#ROLEName# cast #attackSpell#",
                                          "#ROLEName# cast #attackSpell# and #combatElement# blazed from #ROLETheir# #weapon#"
                                          '#ROLEName#\'s mana was weak. #ROLEThey.capitalize# #said#, "#silly_exclaim#", and smacked #monsterName# with #ROLETheir# #weapon#',
                                          ],
                             'block'  : ['#ROLEName# blocked it with #ROLETheir# bare hands.']
                         })
    rpgClasses.append(cc)

    cc = CharacterClass( 'Ranger',  [ "crossbow", "shortbow", "longbow", "bow", "elven bow" ],
                         {
                             'attack' : [ '#ROLEName# took aim with #ROLETheir# #weapon# and loosed an arrow',
                                          '#ROLEName# ducked up from behind a #natureThing# and got off a shot from #ROLETheir# #weapon#',
                                          '#ROLEName# shot an arrow from #ROLETheir# #weapon#',
                                          '#ROLEName# aimed at #monsterName#\'s #m_part#',
                                          ],
                             'block'  : ['#ROLEName# blocked it with #ROLETheir# bare hands.']
                         })
    rpgClasses.append(cc)

    cc = CharacterClass( 'Thief',  [ "dagger", "shiv", "foil", "barb" ],
                         {
                             'attack' : [ '#ROLEName# snuck behind #monsterName# and stabbed at a vertebrae',
                                          '#ROLEName# deftly snapped #ROLETheir# at #monsterName#\'s ribs',
                                          '#ROLEName# attempted backstab',
                                          '#ROLEName# attempted to backstab #monsterName#'
                                          '#ROLEName# gutted #monsterName# with a #weapon#'
                                          ],
                             'block'  : ['#ROLEName# blocked it with #ROLETheir# bare hands.']
                         })
    rpgClasses.append(cc)



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

        if utils.randomChance(0.1):
            name = random.choice( TWITTER_FOLKS )
        else:
            name = '$AA'

        jobs = [ 'baker', 'farmer', 'soldier', 'carpenter' ]
        if self.hometown.port:
            jobs += [ 'fisherman', 'sailor', 'dockworker' ]

        jobTasks= {
            'baker' : ['kneading dough', 'heating up the oven for a loaf of bread',
                       'folding pastry', 'grinding wheat', 'mixing frosting'],
            'farmer' : [ 'digging a furrow', 'shucking corn', 'sorting seeds',
                         'shearing a sheep', 'feeding cattle', 'planting #kfruit#'],
            'soldier' : [ 'marching with comrades', 'practicing swordfighting',
                          'building an encampment', 'digging ditches'],
            'carpenter' : [ 'sanding planks', 'cutting joints into timber',
                            'planing rough lumber', 'driving nails into timber'],
            'fisherman' : [ 'gutting perch', 'filetting halibut', 'repairing nets',
                            'floating idly in the sunshine', 'building lures' ],
            'sailor' : [ 'tying knots', 'climbing the rigging', "pacing the fo'c'sle",
                         'reading a star chart', 'taking a sounding for depth'],
            'dockworker' : [ 'loading crates', 'adjusting rigging', 'unloading a cargo barge' ]
        }

        self.job = random.choice( jobs )
        self.jobTasks = jobTasks[ self.job ]

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
            'ROLEJobTask' : self.jobTasks
        }

        charRules.update (self.rpgClass.getCharClassRules() )

        charRules.update( self.pronouns )

        charRules2 = {}
        for key, item in charRules.iteritems():

            # fixme: make this handle lists as well as strings
            key2 = key.replace( 'ROLE', role )
            if isinstance( item, basestring):
                item2 = item.replace( 'ROLE', role )
            else:
                item2 = map( lambda x: x.replace('ROLE', role ), item )
            charRules2[key2] = item2



        return charRules2

