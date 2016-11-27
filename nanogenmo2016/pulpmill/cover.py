import os, sys, math
import random

from PIL import Image, ImageDraw, ImageFont

import storygen

COVER_TEMPLATES = [
    {
        "mask" : "covermask1.png",
        "author_rect" : ( 58, 14, 556, 117),
        "title_rect" : ( 93, 234, 477, 200),
        "image_rect" : ( 34, 139, 589, 872 ),
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
    }
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
    print "new size ", new_size

    img = img.resize((new_size[0], new_size[1]), Image.LANCZOS)
    img = resize_crop(img, size)
    img.format = img_format
    return img

def drawCoverText( draw, text, fontname, color, borderColor, rect, border=0 ):

    fontsize = 10
    # Enlarge until text doesn't fit
    coverFont = None
    while 1:
        font = ImageFont.truetype( fontname, fontsize )

        textsize = font.getsize( text )

        if textsize[0] > rect[2] or textsize[1] > rect[3]:
            break

        coverFont = font
        fontsize += 1

    print "textsize is ", textsize, rect, "fontsize", fontsize


    if (border > 0):
        for i in range( -border, border ):
            for j in range( -border, border ):
                draw.text( (rect[0] + i, rect[1] + j ),
                           text, borderColor, coverFont )



    draw.text( rect[:2], text, color, coverFont )

def hex_to_rgb(value):
    """Return (red, green, blue) for the color given as #rrggbb."""
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def genCover( title, author, subtitle, colorScheme ):

    booksize = (640, 1038)

    titleColor = hex_to_rgb( colorScheme[0])
    subtitleColor = hex_to_rgb( colorScheme[1])

    bgcolor1 = hex_to_rgb( colorScheme[-2])
    bgcolor2 = hex_to_rgb( colorScheme[-1])


    coverImage = Image.new("RGBA", booksize, bgcolor2 )
    draw = ImageDraw.Draw(coverImage)
    font = "covers/fonts/Bolton.ttf"

    template = random.choice( COVER_TEMPLATES )
    # artinfo = random.choice( COVER_IMAGES )
    artinfo = COVER_IMAGES[1]

    artsize = template['image_rect'][2:]
    print artsize

    artImage = Image.open( os.path.join( "covers", "artwork", artinfo['src']))
    artScaled = resize_cover( artImage, artsize )

    coverImage.paste( artScaled, template['image_rect'][:2] )

    # Template mask
    coverTemplate = Image.open( os.path.join( "covers", "templates", template['mask']))
    coverImage.paste( coverTemplate, mask=coverTemplate  )

    # Author and title
    drawCoverText( draw, title, font, titleColor, bgcolor1,template['title_rect'], border=2)

    drawCoverText( draw, author, font, subtitleColor,bgcolor1, template['author_rect'])

    coverImage.save("testcover.png")

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