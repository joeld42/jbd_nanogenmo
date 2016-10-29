import os, sys
import fpdf

import tracery
from tracery.modifiers import base_english

from pulpmill import *

if __name__=='__main__':

    rules = {
        'origin' : '#hello.capitalize#, #location#!',
        'hello' : ['hello', 'greetings', 'howdy', 'hey there'],
        'location' : ['world', 'solar system', 'galaxy', 'universe']
    }

    grammar = tracery.Grammar( rules )
    grammar.add_modifiers( base_english )
    print grammar.flatten( "#origin#")

    novel = novel.Novel()
    novel.generate()

    typesetter = typesetter.Typesetter( novel )
    typesetter.typesetNovel( "novel.pdf")