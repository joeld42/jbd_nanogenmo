import os, sys

from fpdf import FPDF

class Typesetter(FPDF):

    def __init__(self, novel):

        Bformat = (130, 198) # 'B' format for trade paperbacks
        PocketBookformat = (108, 175) # PocketBook "pulp" paperback

        FPDF.__init__(self, 'P', 'mm', PocketBookformat )
        self.novel = novel

    def doTitlePage(self):

        self.add_page()
        self.set_font('Arial', 'B', 14)
        self.cell(self.w - (self.l_margin + self.r_margin), 24, self.novel.title, 1, 1, 'C' )

    def mapToPage(self, p ):
        return ( self.map_rect[0] + (p[0] * (self.map_rect[2]/self.map_size[0])),
                 self.map_rect[1] + (p[1] * (self.map_rect[3]/self.map_size[1])) )

    def doMapPage(self):

        self.page_border = ( self.l_margin, self.t_margin,
                       self.w - (self.l_margin + self.r_margin),
                       self.h - (self.l_margin + self.r_margin) )

        map = self.novel.map


        self.add_page()
        self.rect( *self.page_border )


        map_scale = (self.page_border[2]-2.0) / float(map.size[0])
        print "map_scale", map_scale

        map_page_height = map.size[1] * map_scale
        offs = (self.page_border[3] - map_page_height) / 2.0

        self.map_size = map.size
        self.map_rect = ( self.page_border[0]+1.0, self.page_border[1]+1.0+offs,
                     map.size[0] * map_scale,
                     map.size[1] * map_scale )

        self.set_fill_color( 171, 198, 242 )
        self.rect( *self.map_rect, style='F' )

        # Draw map nodes
        self.set_fill_color( 150, 131, 78)

        sz = 3.0
        sz2 = sz / 2.0
        for n in map.nodes:
            pp = self.mapToPage( n.pos )
            self.ellipse( pp[0]-sz2, pp[1]-sz2,
                          sz, sz, style='DF' )



    def typesetNovel(self, filename ):

        self.doTitlePage()
        self.doMapPage()

        self.output( filename )