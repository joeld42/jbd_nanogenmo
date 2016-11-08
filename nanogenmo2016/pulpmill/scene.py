import os, sys, string
import random

import utils
import tracery
from tracery.modifiers import base_english

def genWanderText( charName, wanderList, numSteps ):

    wanderText = "#" + charName +"Name#"
    for i in range(numSteps):
        step = random.choice( wanderList )
        if i>0:
            wanderText += random.choice( [". #"+charName+"They.capitalize#", ", and" ])

        wanderText += " " +step

    wanderText += "."
    return wanderText

class Scene(object):

    def __init__(self):

        self.desc = "Empty Scene"

        self.node = None
        self.chars = {}

        # todo: events

        self.storyText = []
        self.origin = 'TODO'
        self.chapterTitle = "Chapter Title"

        self.wordCount = 0

        self.sceneRules = []
        self.newChars = []

    def addParagraph(self, pptext ):
        self.storyText.append( pptext )
        self.wordCount += len( string.split( pptext ))

    def buildSceneRules(self, sg):
        commonRules = sg.getCommonRules( self.node )

        # Base scene just uses origin rule, but complex scenes might
        # mix up more than one rule set or sequence
        self.sceneRules = {
             'origin' : self.origin
         }

        # Add character rules
        for role,char in self.chars.iteritems():
            charRules = char.getCharacterRules( role )
            #print "Add char rules", charRules
            #self.dbgPrintRules( charRules )
            self.sceneRules.update( charRules )

        self.sceneRules.update( commonRules )

    def dbgPrintRules(self, rules ):
        kk = rules.keys()
        kk.sort()
        for k in kk:
            print k, "-> ", rules[k]

    def generate(self, sg ):
        """
        Fills in storyText and possibly override chapterTitle
        """
        self.sceneRules['origin'] = self.origin
        #print self, "origin is ", self.origin

        #print "SCENE RULES:"
        #self.dbgPrintRules( self.sceneRules )

        grammar = tracery.Grammar( self.sceneRules )
        grammar.add_modifiers( base_english )

        pp = grammar.flatten( "#origin#" )
        self.addParagraph( pp )


    def doGenerate(self, sg ):
        self.buildSceneRules( sg )
        self.generate( sg )

class SceneAddChar( Scene ):

    def __init__(self, newChar):
        super(SceneAddChar, self).__init__()

        self.newChar = newChar

    def generate(self, sg ):
        """New char is Alice"""
        template = []

        # Setup
        sentences = [
            ( 0.5, [ '#protagName# visited a tavern.',
                     '#protagName# was #the_feels#. #protagThey# wandered into a garden full of #kfruit.s#.'
                     ])
        ]
        template += utils.addSentencesWithChances( sentences )

        # FIXME: make better
        template.append( 'Placeholder: A #aliceClass# joined the party. #aliceTheir.capitalize# name was #aliceName#.')

        self.origin = string.join( template, ' ')
        super(SceneAddChar,self).generate( sg )


class ScenePlaceDesc( Scene ):

    def __init__(self):
        super(ScenePlaceDesc,self).__init__()

    def generate( self, sg ):

        template = []

        sentences = [
            ( 0.3, '#weather_sentence.capitalize#' ),

            # Judgy statement
            ( 0.3, [ '#cityname# was the jewel of #kingdomname#.',
                     '#cityname# was kind of a dump.',
                     '#cityname# was a #beautiful# #citytype#.',
                     'The #legends# of #cityname# were legendary.',
                     '#cityname# was a #citytype# of #kind_or_mean# people.',
                     '#cityname# was a #economic_state# #citytype#, and that kept it #civic_state#.',
                     ] ),

            # Historical Info
            ( 0.3, ['#cityname# had been founded by the #type_of_elves#, but it was all #rough# men and women now.',
                    '#legends.capitalize# stated that #cityname# was built where a fallen star had landed.',
                    '#cityname# was once the seat of the empire, but no longer.',
                    'Started as a #industry# town, #cityname# was now a thriving #citytype#.',
                    '#cityname# '
                    ])
        ]

        if self.node.city.size == 'small':
            sentences += [
                ( 0.5, [ '#cityname# was hardly more than a handful of buildings.',
                         '#cityname# was not much to look at.',
                         'More of a commune than a #citytype#, #cityname# was home to a few stubborn families and their livestock.',
                         '#cityname# counted its population in #kfruit.s#.'
                         ]) ]
        elif self.node.city.size == 'medium':
            sentences += [
                ( 0.5, [ '#cityname# covered a square mile of countryside.',
                         '#cityname# had cobblestone steets, and a few taverns on each.',
                         '#cityname# was a growing town.',
                         '#cityname# boasted a thriving market.'
                         ]) ]
        elif self.node.city.size == 'large':
            sentences += [
                ( 0.5, [ '#cityname# stretched to the horizon.',
                         '#cityname# was the largest city in #kingdomname#.',
                         '#cityname# bustled with activity.',
                         '#cityname# was huge.'
                         ]) ]

        template += utils.addSentencesWithChances( sentences )


        random.shuffle( template )

        # Add some idle actions and thoughts
        protagIdleActions = [
            "#protagName# scanned the horizon. #protagThey.capitalize# breathed in the #weather_adj# #weather_air#.",
            "A hint of motion caught #protagName#'s eye, #protagThey# turned. It might have been a #critter#, but it was gone.",
            "#protagName# watched a #critter# by a #natureThing# on the #ground#.",
            "#protagName# saw a #natureThing#, and it reminded #protagThem# of #protagHome#.",
            "#critter.a.capitalize# passed through the #weather_air#.",
            "#protagName# wandered through the market. #protagThey.capitalize# bought a #kfruit# from a #marketStall# and took a bite. It was #foodQuality#. #thinkWonder#",
            "#protagName# walked for a bit. #protagThey.capitalize# passed a #propBuilding#.",
            "Some peasants were dying cloth nearby, it made the #weather_air# smell of #kfruit2#. #thinkWonder#",
            "#protagName# wondered about the folks living here. Most that #protagThey# passed seemed happy, but, #protagThey# would be glad to move on.",
            "#protagName# sat down on the #ground# for a bit. #thinkWonder#",
        ]

        # Do something
        idleAction = random.choice( protagIdleActions )
        template.append( random.choice( protagIdleActions ))
        protagIdleActions.remove( idleAction )

        # Do something
        busyAction = random.choice( ["wander" ] )

        if busyAction == 'wander':

            steps = random.randint(3, 5 )
            wanderCity = ['#cityWalked# #cityDir#',
                        'saw a #critter# and kept moving',
                        'saw a #critter#', 'chatted with a #kind_or_mean# #propJob#',
                        'tarried for a bit', 'kicked the #ground#',
                        'took a few steps', 'sat for a while', 'stopped for a drink',
                        'passed a #propBuilding#' ]

            wanderText = genWanderText( "protag", wanderCity, steps )

            template.append( wanderText )

        # Take another idle action
        idleAction = random.choice( protagIdleActions )
        template.append( random.choice( protagIdleActions ))
        protagIdleActions.remove( idleAction )


        self.origin = string.join( template, ' ')
        # print self.origin

        super(ScenePlaceDesc,self).generate( sg )




