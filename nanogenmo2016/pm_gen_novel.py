import os, sys
import fpdf
import random

import tracery
from tracery.modifiers import base_english

from pulpmill import *

if __name__=='__main__':

    culture.setupCultures()


    # Test dungeon names
    for x in range(50):
        c = random.choice( culture.CULTURES.values() )
        print c.genDungeonName()
    # sys.exit(1)

    novel = novel.Novel( culture.CULTURES )
    novel.generate()

    # print novel.title
    # for i in range(20):
    #     print novel.genTitle()

    typesetter = typesetter.Typesetter( novel )
    typesetter.typesetNovel( "novel.pdf")