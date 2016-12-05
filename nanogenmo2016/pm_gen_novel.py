import os, sys
import fpdf
import random

import tracery
from tracery.modifiers import base_english

from pulpmill import *

def testCover():
    nn = novel.Novel( [] )
    title = nn.genTitle()
    author = nn.genAuthor()
    subtitle = nn.genSubtitle()

    colorScheme = random.choice( nn.sg.getColorSchemes() )
    novel.coverImage,copyright = cover.genCover( title, author, subtitle, colorScheme )

    sys.exit(1)


if __name__=='__main__':

    #testCover()

    culture.setupCultures()

    # Test generator
    # for x in range(50):
    #     c = random.choice( culture.CULTURES.values() )
    #     q = quest.Quest( c )
    #
    #     # itemName, itemTags = c.genMacGuffin()
    #
    #     print q.item, '(',','.join(q.itemtags), ')'
    #
    # sys.exit(1)

    novel = novel.Novel( culture.CULTURES )
    novel.generate()

    novel.dbgPrint()

    # print novel.title
    # for i in range(20):
    #     print novel.genTitle()

    colorScheme = random.choice( novel.sg.getColorSchemes() )

    novel.coverImage, novel.artCopyright = cover.genCover( novel.title, novel.author, novel.subtitle, colorScheme )

    typesetter = typesetter.Typesetter( novel )
    typesetter.typesetNovel( "novel.pdf")