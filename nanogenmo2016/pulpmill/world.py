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
class TerrainNode(object):

    def __init__(self):

        self.nodeType = TerrainType_LAND
        self.pos = ( random.uniform( 10, (MAP_SIZE[0] - 10)),
                     random.uniform( 10, (MAP_SIZE[1] - 10)))

        self.elevation = 40.0
        self.cell = []

class Kingdom(object):

    def __init__(self, culture ):

        self.culture = culture

class World(object):

    def __init__(self):

        self.worldname = 'Test World'
        self.daylength = datetime.timedelta( hours = random.randint( 20, 35 ) )
        self.size = MAP_SIZE

        self.nodes = []

        self.mapTris = []

        self.kingdoms = []

    def buildMap(self):

        numExclusionZones = random.randint(1,5)
        exclusionArea = 50.0 / numExclusionZones
        exclusionZones = []
        for zi in range(numExclusionZones):
            zone = (random.uniform( 0.0, 100.0 ),
                    random.uniform( 0.0,100.0 ),
                    random.uniform( 0.1,exclusionArea ) )
            exclusionZones.append( zone )

        targNodes = 150
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
        for tpos in [ (0.0, 0.0), (self.size[0], 0.0),
                      (0.0, self.size[1]), (self.size[0], self.size[1])]:
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
        # TODO random now
        for n in self.nodes:
            n.elevation = random.uniform( 0.0, 40.0 )
            if (n.elevation > 20.0):
                n.nodeType = TerrainType_WATER

        # Assign some kingdoms
        # numKingdoms = random.randint( 2, 5 )
        # for i in range(numKingdoms):
        #     kingdom = Kingdom( culture )

        self.calcTriangleCenters()

        self.calcTerrainCells()

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
            n.cell = map( lambda x: (x[1], x[2]), cellPoints )


    def dbgPrint(self):

        print "This world is called", self.worldname
        print "A day in this world takes ", self.daylength

