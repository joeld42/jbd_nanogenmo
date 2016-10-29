import os, sys
import random
import utils

from fpdf import FPDF
import map

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

    # Stupid fpdf can't draw a polygon
    def polygon(self, pnts, style=''):
        "Draw a polygon"
        if(style=='F'):
            op='f'
        elif(style=='FD' or style=='DF'):
            op='B'
        else:
            op='S'
        #self._out(sprintf('%.2f %.2f %.2f %.2f re %s',x*self.k,(self.h-y)*self.k,w*self.k,-h*self.k,op))
        first = True
        for p in pnts:
            if first:
                cmd = 'm'
            else:
                cmd = 'l'
            self._out( '%.2f %.2f %s' % (p[0]*self.k, (self.h-p[1])*self.k, cmd) )
            first = False
        self._out( op )



    def mapToPage(self, p ):
        return ( self.map_rect[0] + (p[0] * (self.map_rect[2]/self.map_size[0])),
                 self.map_rect[1] + (p[1] * (self.map_rect[3]/self.map_size[1])) )

    def doMapPage(self):

        self.page_border = ( self.l_margin, self.t_margin,
                       self.w - (self.l_margin + self.r_margin),
                       self.h - (self.l_margin + self.r_margin) )

        worldMap = self.novel.map


        self.add_page()
        self.rect( *self.page_border )


        map_scale = (self.page_border[2]-2.0) / float(worldMap.size[0])
        print "map_scale", map_scale

        map_page_height = worldMap.size[1] * map_scale
        offs = (self.page_border[3] - map_page_height) / 2.0

        self.map_size = worldMap.size
        self.map_rect = ( self.page_border[0]+1.0, self.page_border[1]+1.0+offs,
                     worldMap.size[0] * map_scale,
                     worldMap.size[1] * map_scale )

        self.set_fill_color( 171, 198, 242 )
        self.rect( *self.map_rect, style='F' )

        # Draw map triangles
        # self.set_draw_color( 10, 100, 100)
        # for tri in worldMap.mapTris:
        #
        #
        #     pa = self.mapToPage( tri.a.pos )
        #     pb = self.mapToPage( tri.b.pos )
        #     pc = self.mapToPage( tri.c.pos )
        #
        #     self.set_fill_color( random.randint(0,255),
        #                          random.randint(100,255),
        #                          random.randint(0,255) )
        #
        #     self.polygon( [ pa, pb, pc], style='F' )
        #     # FPDF can't draw shapes??
        #     #self.line( pa[0], pa[1], pb[0], pb[1] )
        #     #self.line( pb[0], pb[1], pc[0], pc[1] )
        #     #self.line( pc[0], pc[1], pa[0], pa[1] )


        # Draw map nodes
        sz = 3.0
        sz2 = sz / 2.0
        for n in worldMap.nodes:

            if n.nodeType == map.TerrainType_LAND:
                col = utils.lerp( (28, 130, 31), (201, 252, 241), n.elevation / 40.0 )
                self.set_fill_color( *col )
            elif n.nodeType == map.TerrainType_WATER:
                self.set_fill_color(72, 120, 196)
            elif n.nodeType == map.TerrainType_TEMP:
                self.set_fill_color( 255, 0, 255)

            pp = self.mapToPage( n.pos )

            points = map( lambda x: self.mapToPage(x), n.cell )
            self.polygon( points, 'F' )

            # self.ellipse( pp[0]-sz2, pp[1]-sz2,
            #               sz, sz, style='DF' )



    def typesetNovel(self, filename ):

        self.doTitlePage()
        self.doMapPage()

        self.output( filename )