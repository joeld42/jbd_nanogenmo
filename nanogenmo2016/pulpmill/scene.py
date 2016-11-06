import os, sys, string
import random

import utils
import tracery
from tracery.modifiers import base_english


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
        self.setters = []

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
                     'The stories of #cityname# were legendary.',
                     '#cityname# was a #citytype# of kind people.',
                     '#cityname# was a #economic_state# #citytype#, and that kept it #civic_state#.',
                     ] ),
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

        while not len(template):
            for prob, sentence in sentences:
                if (utils.randomChance(prob)):
                    if not (isinstance( sentence, basestring )):
                        sentence = random.choice( sentence )

                    template.append( sentence )

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
            wanderText = "#protagName#"
            steps = random.randint(3, 5 )
            stepList = ['#cityWalked# #cityDir#',
                        'saw a #critter# and kept moving',
                        'tarried for a bit',
                        'passed a #propBuilding#' ]

            for i in range(steps):
                step = random.choice( stepList )
                if i>0:
                    wanderText += random.choice( [". #protagThey.capitalize#", ", and" ])

                wanderText += " " +step

            wanderText += "."
            template.append( wanderText )




        # Take another idle action
        idleAction = random.choice( protagIdleActions )
        template.append( random.choice( protagIdleActions ))
        protagIdleActions.remove( idleAction )


        self.origin = string.join( template, ' ')
        # print self.origin

        super(ScenePlaceDesc,self).generate( sg )




