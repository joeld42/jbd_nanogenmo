import os, sys, string
import random

import utils
import tracery
from tracery.modifiers import base_english


class Scene(object):

    def __init__(self):

        self.desc = "Empty Scene"

        self.node = None
        self.chars = []

        # todo: events

        self.storyText = []
        self.origin = 'TODO'
        self.chapterTitle = "Chapter Title"

        self.wordCount = 0

    def addParagraph(self, pptext ):
        self.storyText.append( pptext )
        self.wordCount += len( string.split( pptext ))

    def generate(self, sg ):
        """
        Fills in storyText and possibly override chapterTitle
        """

        commonRules = sg.getCommonRules( self.node )

        # Base scene just uses origin rule, but complex scenes might
        # mix up more than one rule set or sequence
        sceneRules = {
             'origin' : self.origin
         }
        sceneRules.update( commonRules )

        grammar = tracery.Grammar( sceneRules )
        grammar.add_modifiers( base_english )
        self.addParagraph( grammar.flatten( "#origin#") )

class ScenePlaceDesc( Scene ):

    def __init__(self):
        super(ScenePlaceDesc,self).__init__()

    def generate( self, sg ):

        template = []

        if utils.randomChance(0.3):
            template.append( '#weather_sentence.capitalize#' )

        template.append( self.node.city.name + ' was a ' + self.node.city.size + ' city')

        random.shuffle( template )

        self.origin = string.join( template, ' ')
        super(ScenePlaceDesc,self).generate( sg )




