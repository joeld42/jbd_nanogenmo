import os, sys
import fpdf

import tracery
from tracery.modifiers import base_english

from pulpmill import *

if __name__=='__main__':

    culture.setupCultures()

    novel = novel.Novel( culture.CULTURES )
    novel.generate()

    # print novel.title
    # for i in range(20):
    #     print novel.genTitle()

    typesetter = typesetter.Typesetter( novel )
    typesetter.typesetNovel( "novel.pdf")