import os, sys
import math
import datetime
import random

MAP_SIZE = (100.0, 120.0)

class TerrainTri(object):
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    def calcCenter(self):

        # centeroid
        self.center = ( (self.a.pos[0] + self.b.pos[0] + self.c.pos[0]) / 3.0,
                        (self.a.pos[1] + self.b.pos[1] + self.c.pos[1]) / 3.0 )

    def circumcenter(self):

        # returns (x, y, radius)
        ax, ay = self.a.pos
        bx, by = self.b.pos
        cx, cy = self.c.pos
        ax2 = ax*ax
        ay2 = ay*ay
        bx2 = bx*bx
        by2 = by*by
        cx2 = cx*cx
        cy2 = cy*cy

        d = 2.0 * ( ay*cx + by*ax - by*cx - ay*bx - cy*ax + cy*bx )

        if abs(d) < 0.000001:
            return (ax, ay, 0.0 )
        else:
            ccx = ( by*ax2 - cy*ax2 - by2*ay + cy2*ay +
                    bx2*cy + ay2*by + cx2*ay - cy2*by -
                    cx2*by - bx2*ay + by2*cy - ay2*cy ) / d

            ccy = ( ax2*cx + ay2*cx + bx2*ax - bx2*cx +
                    by2*ax - by2*cx - ax2*bx - ay2*bx -
                    cx2*ax + cx2*bx - cy2*ax + cy2*bx) / d

            rad = math.sqrt( (ccx-ax)*(ccx-ax) + (ccy-ay)*(ccy-ay) )

        return ( ccx, ccy, rad )


TerrainType_LAND = "land"
TerrainType_WATER = "water"
TerrainType_TEMP = "TEMP"

TerrainArc_ROAD = "road"  # A road or path
TerrainArc_SEA = "sea"  # A sea voyage
TerrainArc_QUEST = "quest" # e.g. mirkwood or moria

kingdom_colors = [ (105,112,55), (184,138,83), (213,183,32),
                   (27,63,100), (80,134,149) ]


def dist( pA, pB ):

    return math.sqrt( ((pA[0] - pB[0])**2) + ((pA[1] - pB[1])**2) )

class CountEdge(object):

    def __init__(self, a, b):
        self.a = a
        self.b = b
        self.count = 1

    def match(self, aa, bb):
        if self.a==aa and self.b==bb:
            return True
        elif self.b==aa and self.a==bb:
            return True
        return False

# World-building stuff
class City( object ):

    def __init__(self, kingdom, node, port=False ):
        self.kingdom = kingdom

        if port:
            self.name = kingdom.culture.genPortCityName()
        else:
            self.name = kingdom.culture.genPlaceName()
        self.node = node
        self.port = port

class TerrainArc(object):

    def __init__(self, a, b ):

        self.a = a
        self.b = b
        self.arcType = TerrainArc_ROAD

    def match(self, a, b ):
        if ( (a==self.a and b==self.b) or
             (b==self.a and a==self.b)):
            return True
        else:
            return False


class TerrainNode(object):

    def __init__(self):

        self.nodeType = TerrainType_LAND
        # self.pos = ( random.uniform( 10, (MAP_SIZE[0] - 10)),
        #               random.uniform( 10, (MAP_SIZE[1] - 10)))

        self.pos = (random.uniform( 0, MAP_SIZE[0]),
                    random.uniform( 1, MAP_SIZE[1]) )

        self.elevation = 40.0
        self.cell = []
        self.adj = []
        self.kingdom = None

        self.city = None

class Kingdom(object):

    def __init__(self, culture ):
        self.culture = culture

        self.capital = None
        self.center = ( 0, 0 )
        self.nodeCount = 0

        self.name = culture.genContinentName()

        if len(kingdom_colors):
            self.color = random.choice( kingdom_colors )
            kingdom_colors.remove( self.color )
        else:
            self.color = ( random.randint( 50, 255 ),
                           random.randint( 50, 255 ),
                           random.randint( 50, 255 ) )

class World(object):

    def __init__(self, cultures):

        self.worldname = 'Test World'
        self.daylength = datetime.timedelta( hours = random.randint( 20, 35 ) )
        self.size = MAP_SIZE
        self.cultures = cultures

        self.nodes = []

        self.mapTris = []

        self.kingdoms = []
        self.arcs = [] # Like roads or sea routes


    def buildMap(self):


        exclusionZones = []
        if 0:
            numExclusionZones = random.randint(1,5)
            exclusionArea = 50.0 / numExclusionZones

            for zi in range(numExclusionZones):
                zone = (random.uniform( 0.0, 100.0 ),
                        random.uniform( 0.0,100.0 ),
                        random.uniform( 0.1,exclusionArea ) )
                exclusionZones.append( zone )

        targNodes = 200
        while (len(self.nodes) < targNodes):

            n = TerrainNode()

            tooClose = False
            closeDist2 = 4**2
            for n2 in self.nodes:
                d2 = ((n2.pos[0] - n.pos[0])**2) + ((n2.pos[1] - n.pos[1])**2)
                if d2 < closeDist2:
                    tooClose = True
                    break

            for z in exclusionZones:
                d2 = dist( n.pos, z )
                if d2 < z[2]:
                    tooClose = True
                    break

            if not tooClose:
                self.nodes.append( n )

        # Add build nodes on the corners
        doneNodes = []
        padSz = 20.0
        for tpos in [ (-padSz, -padSz), (self.size[0] + padSz, -padSz),
                      (-padSz, self.size[1] + padSz ), (self.size[0] + padSz, self.size[1] + padSz)]:
            n = TerrainNode()
            n.pos = tpos
            n.nodeType = TerrainType_TEMP
            doneNodes.append( n )

        a, b, c, d = doneNodes
        self.mapTris.append( TerrainTri( a, b, c ) )
        self.mapTris.append( TerrainTri( c, b, d ) )

        # Add all the map nodes to the triangulation
        for n in self.nodes:

            updatedTris = []
            self.edgeCounts = []
            for tri in self.mapTris:

                ccx, ccy, rad = tri.circumcenter()
                d = dist( (ccx, ccy), n.pos )
                if (d > rad):
                    # Triangle outside of circumcenter, just keep it
                    updatedTris.append( tri )
                else:

                    # Count edges
                    self.countEdge( tri.a, tri.b )
                    self.countEdge( tri.b, tri.c )
                    self.countEdge( tri.c, tri.a )

            # Add new triangles for any edge appearing exactly once
            for e in self.edgeCounts:
                if e.count == 1:
                    tri = TerrainTri( e.a, e.b, n )
                    updatedTris.append( tri )

            self.mapTris = updatedTris


        # assign elevations and water
        self.genTerrain()

        # Calculate Adjacency
        self.buildAdjacent()

        # Assign some kingdoms
        cultureIds = self.cultures.keys()

        landNodes = self.getLandNodes()

        numKingdoms = random.randint( 2, 5 )
        for i in range(numKingdoms):

            cid = random.choice( cultureIds )
            cultureIds.remove( cid )

            culture = self.cultures[cid]
            kingdom = Kingdom( culture )

            capitalNode = random.choice( landNodes )
            landNodes.remove( capitalNode )

            capital = City( kingdom, capitalNode )
            kingdom.capital = capital
            capitalNode.kingdom = kingdom
            capitalNode.city = capital

            print "Capital city: ", capital.name

            self.kingdoms.append( kingdom )

        # propagate kingdoms:
        while 1:
            didChange = False
            for n in self.nodes:

                if n.kingdom:
                    for n2 in n.adj:
                        if n.nodeType==TerrainType_LAND and not n2.kingdom:
                            n2.kingdom = n.kingdom
                            didChange = True

            if not didChange:
                break

        # Make some more cities
        numMoreCities = 10
        landNodes = self.getLandNodes()
        random.shuffle(landNodes)
        for n in landNodes[:numMoreCities]:
            cc = City( kingdom, n )
            n.city = cc

        # Make some port cities
        self.addPortCities()

        # get kingdom averages
        for n in self.getLandNodes():
            if n.kingdom:
                k = n.kingdom
                k.center = (k.center[0] + n.pos[0], k.center[1] + n.pos[1] )
                k.nodeCount += 1

        for k in self.kingdoms:
            if k.nodeCount > 0:
                k.center = (k.center[0] / k.nodeCount, k.center[1] / k.nodeCount )

        self.calcTriangleCenters()

        self.calcTerrainCells()

    def getLandNodes(self):

        landNodes = []
        for n in self.nodes:
            if n.nodeType == TerrainType_LAND and not n.city:
                landNodes.append( n )

        return landNodes

    def getEmptyCoastalNodes(self):

        landNodes = []
        for n in self.nodes:
            if n.nodeType == TerrainType_LAND and not n.city:

                # See if there's water adjacent
                # FIXME: move this to TerainNode
                hasWater = False
                for n2 in n.adj:
                    if (n2.nodeType == TerrainType_WATER):
                        hasWater = True
                        break

                if hasWater:
                    landNodes.append( n )

        return landNodes

    def countEdge(self, a, b):

        for e in self.edgeCounts:
            if e.match(a, b):
                e.count += 1
                return

        self.edgeCounts.append( CountEdge(a,b) )

    def calcTriangleCenters(self):

        for tri in self.mapTris:
            tri.calcCenter()

    def calcTerrainCells(self):

        for n in self.nodes:

            # find all map tris that use this node
            cellPoints = []
            for tri in self.mapTris:
                if (tri.a == n) or (tri.b==n) or (tri.c==n):
                    pc = tri.center
                    pp = (pc[0] - n.pos[0], pc[1]-n.pos[1])
                    pa = math.atan2( pp[1], pp[0])
                    cellPoints.append( (pa, pc[0], pc[1] ) )

            # sort by angle
            cellPoints.sort()
            n.cell = map( lambda x: self.clamp( (x[1], x[2]) ), cellPoints )

    def clamp(self, p ):
        return ( min( MAP_SIZE[0], max( p[0], 0.0 ) ),
                 min( MAP_SIZE[1], max( p[1], 0.0 ) ) )

    def buildAdjacent(self):

        for n in self.nodes:

            adj = set()
            for t in self.mapTris:
                if t.a==n or t.b==n or t.c==n:

                    for n2 in [t.a, t.b, t.c]:
                        if n2 != n:
                            adj.add( n2 )

            n.adj = adj

            # also add arcs
            foundArc = None
            for n2 in n.adj:

                for a in self.arcs:
                    if a.match( n, n2 ):
                        foundArc = a
                        break

                if not foundArc:
                    if (n.nodeType == TerrainType_LAND and
                            n2.nodeType == TerrainType_LAND):
                        self.arcs.append( TerrainArc( n, n2) )

    def addPortCities(self):

        # Make some more cities

        coastalNodes = self.getEmptyCoastalNodes()
        random.shuffle(coastalNodes)

        for k in self.kingdoms:

            kingdomCoastals = filter( lambda x: x.kingdom==k, coastalNodes )

            numCoastals = len(kingdomCoastals)
            if (numCoastals <=4):
                numMoreCities = 1
            elif (numCoastals <= 20):
                numMoreCities = 2
            else:
                numMoreCities = int(numCoastals * 0.1)

            print "Kingdom", k.name, "has", len(kingdomCoastals), "coastal lands, adding", numMoreCities, "port cities"

            for n in kingdomCoastals[:numMoreCities]:
                cc = City( k, n, port=True )
                n.city = cc
                print "  Added", cc.name

    def genTerrain(self):

        for n in self.nodes:
            n.elevation = 20.0

        # use the "fault line offset" method to generate terrain
        # because it's super simple and we just need coarse elevation
        numIters = 100
        for i in range(numIters):

            # Choose a line at random across the map
            pA = ( random.uniform( 0.0, self.size[0]), random.uniform( 0.0, self.size[1]) )
            pB = ( random.uniform( 0.0, self.size[0]), random.uniform( 0.0, self.size[1]) )

            for n in self.nodes:
                d = ((pB[0] - pA[0]) * (n.pos[1] - pA[1])) - ((pB[1] - pA[1]) * (n.pos[0] - pA[0]))
                if ( d < 0.0):
                    n.elevation += 1.0
                else:
                    n.elevation -= 1.0

        minElev = 99999.0
        maxElev = 0.0
        for n in self.nodes:
            minElev = min( n.elevation, minElev )
            maxElev = max( n.elevation, maxElev )

        for n in self.nodes:
            n.elevation = (n.elevation - minElev) / (maxElev - minElev)
            n.elevation *= 40.0

            if (n.elevation < 20.0):
                 n.nodeType = TerrainType_WATER


    def dbgPrint(self):

        print "This world is called", self.worldname
        print "A day in this world takes ", self.daylength

