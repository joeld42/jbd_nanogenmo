import os, sys, math, string
import random

from PIL import Image, ImageDraw, ImageFont

import storygen

DISPLAY_FONTS = [
    "instantzen",
    "DevinneSwash",
    "Dyer Arts and Crafts",
    "electrical",
    "nightsky",
    "Nougat-ExtraBlack",
    "QueensSquare",
    "ROGERS",
    "Excalibur Nouveau",
    "American Captain",
]

# Fonts legible enough to use as a subtitle
READABLE_FONTS = [
    "Bolton",
    "IDAHO_Conrad_Garner",
    "Storyboo",
    "The Goldsmith_Vintage",
    "Titania-Regular"
]

ALL_FONTS = DISPLAY_FONTS + READABLE_FONTS

COVER_TEMPLATES = [
        {
        "overlay" : "hobbit_overlay.png",
        "mask" : None,
        "border" : None,
        "titleBorder" : False,
        "authorBorder" : False,
        "subtitleColor" : (255, 255, 255),
        "author_rect" : ( 29, 73, 595, 192),
        "subtitle_rect" : ( 25, 277, 591, 33 ),
        "title_rect" : ( 30, 317, 584, 138 ),
        "image_rect" : ( 144, 475, 345, 518 ),
    },
    {
        "overlay" : None,
        "mask" : "covermask1_mask.png",
        "border" : "covermask1_border.png",
        "titleBorder" : True,
        "authorBorder" : False,
        "author_rect" : ( 58, 14, 556, 117),
        "title_rect" : ( 93, 234, 477, 200),
        "image_rect" : ( 34, 139, 589, 872 ),
        "subtitle_rect" : ( 63, 902, 528, 102 ),
    },
    {
        "overlay" : "cover_ace.png",
        "mask" : None,
        "border" : None,
        "titleBorder" : False,
        "authorBorder" : False,
        "author_rect" : ( 142, 234, 327, 62 ),
        "title_rect" : ( 141, 78, 323, 143),
        "image_rect" : ( 0, 0, 640, 1038 ),
        "subtitle_rect" : ( 56, 810, 235, 189 ),
    },
    {
        "overlay" : "dragonlance_overlay.png",
        "mask" : None,
        "border" : "dragonlance_border.png",
        "titleBorder" : True,
        "authorBorder" : True,
        "author_rect" : ( 108, 845, 421, 104 ),
        "title_rect" : ( 68, 228, 493, 176),
        "image_rect" : ( 55, 60, 519, 901 ),
        "subtitle_rect" : ( 70, 189, 492, 40 ),
    },
    {
        "overlay" : "signet_overlay.png",
        "mask" : None,
        "border" : None,
        "titleBorder" : False,
        "authorBorder" : False,
        "subtitleColor" : (190, 38, 27 ),
        "author_rect" : ( 85, 420, 529, 50 ),
        "title_rect" : ( 83, 204, 530, 195),
        "image_rect" : ( 0, 386, 640, 651 ),
        "subtitle_rect" : ( 214, 22, 403, 146 ),
        "titleCenter" : False,
        "authorCenter" : False
    },
    {
        "overlay" : "conan_overlay.png",
        "mask" : None,
        "border" : None,
        "titleBorder" : False,
        "authorBorder" : False,
        "authorColorMatch" : True,
        "subtitleColor" : ( 41, 38, 29 ),
        "author_rect" : ( 16, 261, 607, 62 ),
        "title_rect" : ( 17, 85, 603, 179),
        "image_rect" : ( 27, 372, 585, 610 ),
        "subtitle_rect" : ( 14, 321, 603, 50 )
    },
    {
        # Modern, "When Gravity Fails" style
        "overlay" : None,
        "mask" : None,
        "border" : "border_tor.png",
        "titleBorder" : False,
        "authorBorder" : False,
        "authorColorMatch" : True,
        "tintImage" : True,
        # "subtitleColor" : ( 41, 38, 29 ),
        "author_rect" : ( 21, 954, 595, 68 ),
        "title_rect" : ( 21, 395, 595, 120),
        "image_rect" : (0, 520, 640, 415 ),
        "subtitle_rect" : ( 206, 150, 238, 87 )
    }
]

COVER_IMAGES = [
    {
        "src": "Dobrinya.jpg",
        "copyright" : "Bogatyrs (1898) by Viktor Vasnetsov. (Public Domain)"
    },
    {
        "src" : "Elf_markwoman_by_Kitty_square.png",
        "copyright" : "'Elf Markswoman' by Kathrin 'Kitty' Polikeit (GPL)"
    },
    {
        "src" : "800px-Environments-15-Ishtar-dragons.png",
        "copyright" : "by David Revoy, used under Creative Commons."
    },
    {
        "src" : "Dore_-_the_ice_was_all_around.jpg",
        "copyright" : "by Gustave Dore. (Public Domain)"
    },
    {
        "src" : "Mariner_deathfires.jpg",
        "copyright" : "by Gustave Dore. (Public Domain)"
    },
    {
        "src" : "plate28.jpg",
        "copyright" : "by Gustave Dore. (Public Domain)"
    },
    {
        "src" : "Paradiso_Canto_31.jpg",
        "copyright" : "by Gustave Dore. (Public Domain)"
    },
    {
        "src" : "Les_Oceanides_Les_Naiades_de_la_mer.jpg",
        "copyright" : "by Gustave Dore. (Public Domain)"
    },
    {
        "src" : "Loch_Lomond.jpg",
        "copyright" : "'Loch Lomond' by Gustave Dore. (Public Domain)"
    },
    {
        "src" : "Dore_woodcut_Divine_Comedy_01.jpg",
        "copyright" : "by Gustave Dore. (Public Domain)"
    },
    {
        "src" : "Don_Quijote_illustrated_by_Gustav_Dore_III.jpg",
        "copyright" : "by Gustave Dore. (Public Domain)"
    },
    {
        "src" : "800px-Mont_Sainte-Odile.jpg",
        "copyright" : "by Gustave Dore. (Public Domain)"
    },
    {
        "src" : "Castle_of_Reflection_by_Birgit_Anderson_Ridderstedt_1931.jpg",
        "copyright" : "'Castle of Reflection' by Birgit Anderson Ridderstedt, 1931. "+
                      "Courtesy of Southerly Clubs, Sweden (Public Domain)"
    },
    {
        "src" : "shaman_hut1.png",
        "copyright" : "'Shaman Hut' by David Revoy and Blender Foundation (Creative Commons)"
    },
    {
        "src" : "shaman_hut2.png",
        "copyright" : "'Shaman Hut' by David Revoy and Blender Foundation (Creative Commons)"
    },
    {
        "src" : "shaman_hut3.png",
        "copyright" : "'Shaman Hut' by David Revoy and Blender Foundation (Creative Commons)"
    },
    {
        "src" : "Face_in_the_Pool_frontispiece.jpg",
        "copyright" : "Frontispiece to 1905 edition of J. Allen St. John's The Face in the Pool (Public Domain)"
    },
    {
        "src" : "meeting-under-the-tree1.png",
        "copyright" : "'Meeting Under the Tree' by David Revoy (Creative Commons)"

    },
    {
        "src" : "meeting-under-the-tree2.png",
        "copyright" : "'Meeting Under the Tree' by David Revoy (Creative Commons)"

    },
    # {
    #     "src" : "meeting-under-the-tree3.png",
    #     "copyright" : "'Meeting Under the Tree' by David Revoy (Creative Commons)"
    #
    # }


]

# From
# https://github.com/charlesthk/python-resize-image
def resize_crop(image, size):
    """
    Crop the image with a centered rectangle of the specified size
    image:      a Pillow image instance
    size:       a list of two integers [width, height]
    """
    img_format = image.format
    image = image.copy()
    old_size = image.size
    left = (old_size[0] - size[0]) / 2
    top = (old_size[1] - size[1]) / 2
    right = old_size[0] - left
    bottom = old_size[1] - top
    rect = [int(math.ceil(x)) for x in (left, top, right, bottom)]
    left, top, right, bottom = rect
    crop = image.crop((left, top, right, bottom))
    crop.format = img_format
    return crop

def resize_cover(image, size):
    """
    Resize image according to size.
    image:      a Pillow image instance
    size:       a list of two integers [width, height]
    """
    img_format = image.format
    img = image.copy()
    img_size = img.size
    print img_size
    ratio = max(float(size[0]) / img_size[0], float(size[1]) / img_size[1])
    new_size = [
        int(math.ceil(img_size[0] * ratio)),
        int(math.ceil(img_size[1] * ratio))
    ]
    #print "new size ", new_size

    img = img.resize((new_size[0], new_size[1]), Image.LANCZOS)
    img = resize_crop(img, size)
    img.format = img_format
    return img

# Returns the text split by lines so that it fits into rect, if possible,
# otherwise returns None
def wrapFitText( text, font, rect ):

    result = []
    currline = []
    currhite = 0

    for word in string.split(text):
        testline = " ".join(currline + [word] )
        textsize = font.getsize( testline )

        if textsize[0] > rect[2]:
            # Doesn't fit, wrap line
            result.append( " ".join(currline) )
            currline = [word]
            currhite += textsize[1]
        else:
            currline.append( word )

        if currhite > rect[3]:
            return None

    result.append( " ".join(currline) )
    currhite += textsize[1]
    if currhite > rect[3]:
        return None

    return result

def drawTextBlock( draw, textlines, font, color, rect, center ):

    yoffs = 0
    totalhite = 0
    for line in textlines:
        textsize = font.getsize( line )
        totalhite += textsize[1]

    offs = max( 0.0, (rect[3] - totalhite ) / 2 )
    for line in textlines:
        textsize = font.getsize( line )

        # center text
        xoffs = (rect[2] - textsize[0]) / 2.0

        if not center:
            xoffs = 0

        draw.text( (rect[0] + xoffs, rect[1] +offs ), line, color, font  )
        offs += textsize[1]

def drawCoverText( draw, text, fontname, color, borderColor, rect, border=0, center=True  ):

    fontsize = 10
    # Enlarge until text doesn't fit
    coverFont = None
    wrappedText = [ text ]
    while 1:
        font = ImageFont.truetype( fontname, fontsize )

        # wrappedTextTest = font.getsize( text )
        wrappedTextTest = wrapFitText( text, font, rect )

        if not wrappedTextTest:
            break



        coverFont = font
        wrappedText = wrappedTextTest
        fontsize += 1


    #draw.rectangle( (rect[0], rect[1], rect[0]+rect[2], rect[1]+rect[3]), outline=color )

    if (border > 0):
        for i in range( -border, border ):
            for j in range( -border, border ):
                drawTextBlock( draw, wrappedText, coverFont, borderColor,
                               (rect[0]+i, rect[1]+j, rect[2], rect[3] ), center=center )

    drawTextBlock( draw, wrappedText, coverFont, color, rect, center=center )

def hex_to_rgb(value):
    """Return (red, green, blue) for the color given as #rrggbb."""
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def lerp( a, b, t ):
    return (1.0-t)*a + t*b

def valueForColor( p ):
    return (0.2126*p[0] + 0.7152*p[1] + 0.0722*p[2]) / 255.0

def applyGradient( image, color1, color2 ):

    print color1, color2
    for j in xrange(image.size[1]):
        for i in xrange(image.size[0]):
            p = image.getpixel( (i,j))

            if len(p)<=3:
                alpha = 255
            else:
                alpha = p[3]

            if (alpha > 0):
                val = valueForColor(p)

                result = ( int(lerp(color1[0], color2[0], val)),
                            int(lerp(color1[1], color2[1], val)),
                            int(lerp(color1[2], color2[2], val)),
                            alpha )
                image.putpixel( (i,j), result )





def genCover( title, author, subtitle, colorScheme ):

    # copyrights = set()
    # for img in COVER_IMAGES:
    #     copyrights.add( img['copyright'])
    # for cp in copyrights:
    #     print "Cover Art " + cp

    booksize = (640, 1038)

    titleColor = hex_to_rgb( colorScheme[0])
    subtitleColor = hex_to_rgb( colorScheme[1])

    bgcolor1 = hex_to_rgb( colorScheme[-2])
    bgcolor2 = hex_to_rgb( colorScheme[-1])


    coverImage = Image.new("RGBA", booksize, bgcolor2 )
    draw = ImageDraw.Draw(coverImage)
    #font = "covers/fonts/Bolton.ttf"
    #font = "covers/fonts/instantzen.ttf"
    titleFont = os.path.join( "covers", "fonts", random.choice( ALL_FONTS ) + ".ttf" )
    subtitleFont = os.path.join("covers", "fonts", random.choice( READABLE_FONTS ) + ".ttf" )

    print "Title Font", titleFont
    print "Subtitle", subtitleFont

    template = random.choice( COVER_TEMPLATES )
    #template = COVER_TEMPLATES[-1]

    artinfo = random.choice( COVER_IMAGES )
    #artinfo = COVER_IMAGES[-1]

    artsize = template['image_rect'][2:]
    print artsize

    artImage = Image.open( os.path.join( "covers", "artwork", artinfo['src']))
    artScaled = resize_cover( artImage, artsize )

    gradientColor1 = hex_to_rgb(colorScheme[1])
    gradientColor2 = hex_to_rgb(colorScheme[3])

    # swap so it's always lighter to darker
    if valueForColor(gradientColor1) > valueForColor(gradientColor2):
        gradientColor2, gradientColor1 = gradientColor1, gradientColor2

    if template.get('tintImage', False ):
        applyGradient( artScaled, gradientColor1, gradientColor2 )

        #use different colors for border
        #gradientColor1 = hex_to_rgb(colorScheme[4])
        #gradientColor2 = hex_to_rgb(colorScheme[0])

    if template.get('mask',None):
        coverImage1 = coverImage.copy()
        coverImage1.paste( artScaled, template['image_rect'][:2] )

        coverMask = Image.open( os.path.join( "covers", "templates", template['mask']))

        coverImage.paste( coverImage1, mask=coverMask )

    else:
        coverImage.paste( artScaled, template['image_rect'][:2] )


    # Border
    if template['border']:
        coverBorder = Image.open( os.path.join( "covers", "templates", template['border']))

        applyGradient( coverBorder, gradientColor1, gradientColor2 )

        coverImage.paste( coverBorder, mask=coverBorder  )


    # Overlay
    if template['overlay']:
        coverOverlay = Image.open( os.path.join( "covers", "templates", template['overlay']))
        print "coverImage size", coverImage.size
        print "Overlay size", coverOverlay.size
        coverImage.paste( coverOverlay, mask=coverOverlay  )

    # Author and title
    borderCol= None
    borderWidth = 0
    if template.get('titleBorder', False):
        borderCol = bgcolor1
        borderWidth = 2

    titleCenter = template.get('titleCenter', True)
    drawCoverText( draw, title, titleFont, titleColor, borderCol,
                   template['title_rect'], border=borderWidth, center=titleCenter )

    # Author
    borderCol= None
    borderWidth = 0
    if template.get('authorBorder', False):
        borderCol = bgcolor1
        borderWidth = 2

    authorCenter = template.get('authorCenter', True)
    authorColor = subtitleColor
    if template.get('authorColorMatch', False):
        authorColor = titleColor

    drawCoverText( draw, author, titleFont, authorColor,borderCol,
                   template['author_rect'], border=borderWidth, center=authorCenter)

    subtitleColor = template.get('subtitleColor', subtitleColor )
    drawCoverText( draw, subtitle, subtitleFont, subtitleColor,borderCol, template['subtitle_rect'] )

    coverImageName = "cover_pic.png"
    coverImage.save(coverImageName )

    return coverImageName, 'Cover Art ' + artinfo['copyright']

# import cairocffi as cairo
#
# def genCover( title ):
#
#     PocketBookformat = (108, 175)
#     dpi = 150.0
#     dpmm = dpi * 0.0393701 # Inch per mm
#
#     surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
#                                  int(PocketBookformat[0] * dpmm),
#                                  int(PocketBookformat[1] * dpmm) )
#     context = cairo.Context(surface)
#     with context:
#         context.set_source_rgb(1, 1, 1)  # White
#         context.paint()
#
#     # Restore the default source which is black.
#     context.move_to(90, 140)
#     context.rotate(-0.5)
#     context.set_font_size(20)
#     context.show_text(u'Hi from cairo!')
#     surface.write_to_png('example.png')