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
TerrainType_WATER = "water" # ocean water
TerrainType_LAKE = "lake"
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

    def __init__(self, kingdom, node, port=False, dungeon=False ):
        self.kingdom = kingdom

        if port:
            self.name = kingdom.culture.genPortCityName()
        elif dungeon:
            # Generate dungeon
            self.name = kingdom.culture.genDungeonName()
        else:
            self.name = kingdom.culture.genPlaceName()

        self.node = node

        self.port = port
        self.dungeon = dungeon

        self.size = random.choice(['small', 'medium', 'large'])



class TerrainArc(object):

    def __init__(self, a, b ):

        self.a = a
        self.b = b
        self.arcType = TerrainArc_ROAD
        self.onStoryPath = False

    def match(self, a, b ):
        if ( (a==self.a and b==self.b) or
             (b==self.a and a==self.b)):
            return True
        else:
            return False

    def other(self, n):
        assert (n==self.a or n==self.b)
        if n==self.a:
            return self.b
        else:
            return self.a

    def __str__(self):

        if self.arcType == TerrainArc_ROAD:
            desc="Road"
        elif self.arcType == TerrainArc_SEA:
            desc="Sea"
        else:
            desc=""
        return "<TerrainArc(%s)>" % desc


class TerrainRegion(object):

    def __init__(self, ident, color ):
        self.ident = ident
        self.color = color


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
        self.region = None
        self.mtnDebug = -1

        # Temps used for traversals
        self.visited = False

        # story gen stuff
        self.storyVisited = False

    def isDeadEnd(self):
        return not self.city and self.nodeType == TerrainType_LAND and (len(self.arcs)==1)

    def __str__(self):

        desc = self.nodeType

        if self.city:
            desc += " " + self.city.name
            attrs = []
            if self.city.port:
                attrs.append( "Port" )
            if self.city.dungeon:
                attrs.append("Dungeon")

            if attrs:
                desc += " (%s)" % ",".join(attrs)

        return '<TerrainNode: %s>' % desc

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

    def setup(self, sg ):

        fruits = sg.getFruitRules()[:]

        # each kingdom has 3 common fruits
        random.shuffle(fruits)
        self.fruits = fruits[:3]


class World(object):

    def __init__(self, cultures, storygen ):

        self.worldname = 'Test World'
        self.daylength = datetime.timedelta( hours = random.randint( 20, 35 ) )
        self.size = MAP_SIZE
        self.cultures = cultures
        self.sg = storygen

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

        # Find Lakes
        self.findLakes()


        # Regionize terrain
        self.makeRegions()

        # Assign some kingdoms
        cultureIds = self.cultures.keys()

        landNodes = self.getLandNodes()

        numKingdoms = random.randint( 2, 5 )
        for i in range(numKingdoms):

            cid = random.choice( cultureIds )
            cultureIds.remove( cid )

            culture = self.cultures[cid]
            kingdom = Kingdom( culture )
            kingdom.setup( self.sg )

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

        # There may be some straggling unreachable nodes
        for n in self.nodes:
            if n.nodeType==TerrainType_LAND and not n.kingdom:
                n.kingdom = random.choice( self.kingdoms )

        # Make some more cities
        numMoreCities = 10
        landNodes = self.getLandNodes()
        random.shuffle(landNodes)
        for n in landNodes[:numMoreCities]:
            cc = City( kingdom, n )
            n.city = cc

        # Make some port cities
        self.addPortCities()

        # Add sea lanes
        self.addSeaLanes()

        # Build arc lists
        self.buildNodeArcs()

        # Add dungeons and clean up dead ends
        #self.addDungeons()

        self.makeStoryPath()
        #self.storyPath = []

        # Prune roads and dead ends
        self.pruneRoads()
        self.removeDeadEnds()

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

    def clearVisited(self):
        for n in self.nodes:
            n.visited = False

    def getConnectedWater(self, n, nlist ):

        n.visited = True
        nlist.append( n )
        for n2 in n.adj:
            if (not n2.visited) and n2.nodeType == TerrainType_WATER:
                self.getConnectedWater( n2, nlist )

        return nlist

    def buildNodeArcs(self):

        for n in self.nodes:
            n.arcs = []
            for arc in self.arcs:
                if arc.a == n or arc.b==n:
                    n.arcs.append( arc )

    def makeStoryPath(self):

        numDungeons = random.randint( len(self.kingdoms), len(self.kingdoms)*2  )

        #DBG
        numDungeons = 0

        for ndx in xrange(numDungeons):
            k = self.kingdoms[ ndx % len(self.kingdoms)]

            dungeonPlaces = filter( lambda n: n.city and n.nodeType == TerrainType_LAND and (len(n.arcs)>1) and n.kingdom == k,
                                    self.nodes )

            print "Make story path adding dungeon"
            d = random.choice( dungeonPlaces )
            cc = City( d.kingdom, d, dungeon=True )
            d.city = cc

        # Max dungeons in our novel
        maxDungeons = 3
        storyDungeons = min( numDungeons, maxDungeons )

        cities = filter( lambda n: n.city and n.nodeType==TerrainType_LAND and not n.city.dungeon and len(n.arcs)>1, self.nodes )

        retryCount = 0
        while 1:
            startCity = random.choice( cities )
            print "MakestoryPath: start/end in ", startCity.city.name, "storyDungeons", storyDungeons

            self.clearVisited()
            self.dbg_bestSoFar = 999
            self.dbg_count = 0
            storyPath = self.findStoryPath( startCity, startCity, storyDungeons, [] )

            if storyPath and storyPath[0]:
                retryCount += 1
                if retryCount > 3 and storyDungeons > 2:
                    # Try fewer dungeons if this is too hard
                    storyDungeons -= 1

                break

        # Close path
        storyPath.append( storyPath[0])

        print "findStoryPath, result:"

        first = True
        steps = 0
        lastStep = TerrainArc_ROAD
        for step in storyPath:
            if isinstance( step, TerrainArc):
                step.onStoryPath = True
                steps += 1
                lastStep = step.arcType

            if isinstance( step, TerrainNode):
                if step.city:
                    if steps > 0:
                        if lastStep == TerrainArc_ROAD:
                            if (steps > 2):
                                print "Travel overland a great distance"
                        else:
                            print "Take an ocean voyage."
                    steps = 0
                    if step.city.dungeon:
                        print "Adventure at", step.city.name
                    else:
                        if first:
                            print "Start at", step.city.name
                        else:
                            print "Visit",step.city.name

            first = False

        # Save the storypath for the novel
        self.storyPath = storyPath



    def findStoryPath(self, curr, targ, dleft, storypath ):

        curr.visited = True
        storypath.append( curr )

        dbgPrint = False
        self.dbg_count += 1
        if len(storypath) > self.dbg_bestSoFar:
            dbgPrint = True
            self.dbg_bestSoFar = len(storypath)
        elif self.dbg_count % 1000 == 0:
            dbgPrint = True

        #if dbgPrint:
        #    print self.dbg_count, "findStoryPath, pathlen", len(storypath), dleft

        # give up if it's taking too long
        if self.dbg_count > 1000000:
            print "Restarting story path..."
            return [ None ]

        # If we're visiting a dungeon, count it
        dsub = 0
        if curr.city and curr.city.dungeon:
            dsub = 1

        travelArcs = curr.arcs[:]
        random.shuffle(travelArcs)
        for arc in travelArcs:

            n2 = arc.other( curr )
            if n2 == targ and dleft==0:
                #print "Found targ"
                return storypath

            if not n2.visited:
                storypath.append( arc )
                sp = self.findStoryPath( n2, targ, dleft-dsub, storypath )
                if (sp):
                    return sp

                storypath.pop()

        storypath.pop()
        curr.visited = False
        return None




    def removeDeadEnds(self):

        # Find all the dead-end arcs
        deadEnds = self.findDeadEnds()

        # Make the first few of them villiages
        numDeadEnds = min( len(deadEnds), random.randint( 1, 3) )
        for d in deadEnds[:numDeadEnds]:
        #for d in deadEnds:
            cc = City( d.kingdom, d )
            d.city = cc
            print "Added deadend city..."

        # Remove all other dead-ends until there are none
        while 1:
            deadEnds = self.findDeadEnds()
            if len(deadEnds) == 0:
                break
            else:
                print "Trimming ", len(deadEnds), "dead ends"

            for d in deadEnds:
                self.removeArc( d.arcs[0] )

    def findDeadEnds(self):
        return filter( lambda x: x.isDeadEnd(), self.nodes )

    def findLakes(self):

        self.clearVisited()

        for n in self.nodes:

            if (not n.visited) and n.nodeType == TerrainType_WATER:

                # Check if n is a lake
                waterNodes = self.getConnectedWater( n, [] )
                if len(waterNodes) <= 4:
                    for wn in waterNodes:
                        n.nodeType = TerrainType_LAKE

        # clean up all the lake nodes
        for n in self.nodes:
            if n.nodeType==TerrainType_LAKE:
                n.adj=[]
            else:
                n.adj = filter( lambda x: not x.nodeType == TerrainType_LAKE, n.adj )
                n.adj = filter( lambda x: not x.nodeType == TerrainType_LAKE, n.adj )

    def randomTownNode(self):

        townNodes = filter( lambda x: x.nodeType==TerrainType_LAND and x.city and not x.city.dungeon, self.nodes )
        return random.choice(townNodes)

    def makeRegions(self):

        landNodes = filter( lambda x: x.nodeType==TerrainType_LAND, self.nodes )

        # Add random regions
        regions = []
        regions.append( TerrainRegion( "swamp", (95, 112, 0) ))
        regions.append( TerrainRegion( "forest", (35, 178, 0) ))
        regions.append( TerrainRegion( "desert", (214, 183, 113) ))

        unassignedLands = filter( lambda x: x.region == None, landNodes )
        numSeeds = len(unassignedLands) / 5
        random.shuffle(unassignedLands)

        for n in unassignedLands[:numSeeds]:
            n.region = random.choice( regions )

        # propogate regions
        while 1:
            didChange = False
            for n in landNodes:
                if n.region and not (n.region.ident == "mountain"):
                    nadj = n.adj[:]
                    random.shuffle(nadj)
                    for n2 in nadj:
                        if n.nodeType==TerrainType_LAND and not n2.region:
                            n2.region = n.region
                            didChange = True

            if not didChange:
                break

        # Finally, add mountain ranges
        #numMtns = min(len(landNodes) / 10, 2)
        numMtns = random.randint( 2, 10)
        for i in xrange(numMtns):

            curr = random.choice( landNodes )
            stepDir = random.uniform( 0.0, 360.0 )
            mtnSize = random.randint( 3, 7 )
            # mtnSize = 10
            # stepDir = 45.0

            regionMountian = TerrainRegion( "mountain",(163, 194, 204) )
            for step in xrange(mtnSize):
                curr.region = regionMountian
                curr.mtnDebug = step

                bestNode = None
                bestAng = 0.0
                for n2 in curr.adj:
                    dir = math.atan2( n2.pos[1] - curr.pos[1], n2.pos[0] - curr.pos[0]) * (180.0/math.pi)
                    ang = math.fabs( dir - stepDir ) # fixme: wrap angles
                    if not bestNode or ang < bestAng:
                        bestAng = ang
                        bestNode = n2

                    #print "step", step, "target dir", stepDir, "n2 dir", ang
                if not bestNode:
                    break

                curr = bestNode





    def getLandNodes(self):

        landNodes = []
        for n in self.nodes:
            if n.nodeType == TerrainType_LAND and not n.city:
                landNodes.append( n )

        return landNodes

    def removeArc(self, arc ):
        arc.a.arcs.remove( arc )
        arc.b.arcs.remove( arc )
        self.arcs.remove( arc )

    def pruneRoads(self):

        print "PruneRoads..."
        iterCount = 500
        origVisitable = self.countVisitableIfArcRemoved( None )

        print "origVisitable ", origVisitable

        roads = filter( lambda x: x.arcType==TerrainArc_ROAD, self.arcs )
        for i in xrange(iterCount):


            while 1:
                checkArc = random.choice( roads )
                if not checkArc.onStoryPath:
                    break

            count2 = self.countVisitableIfArcRemoved( checkArc )

            if count2 == origVisitable:
                #print "Removing arc, count unchanged", origVisitable
                self.removeArc( checkArc )
                roads.remove( checkArc)
            #else:
            #    print "Check arc failed, count is", count2, "continuing"

    def countVisitableIfArcRemoved(self, arc ):

        # Pick a random city to start
        for startNode in self.nodes:
            if startNode.city:
                break

        self.clearVisited()
        self._doCountVisited( startNode, arc )

        count = 0
        for n in self.nodes:
            if n.visited:
                count += 1

        return count

    def _doCountVisited(self, curr, removeArc ):

        curr.visited = True

        for arc in curr.arcs:
            n2 = arc.other(curr)
            if not n2.visited:
                if not removeArc or (not removeArc==arc):
                    self._doCountVisited( n2, removeArc )



    def getEmptyCoastalNodes(self):

        landNodes = []
        for n in self.nodes:
            if n.nodeType == TerrainType_LAND and not n.city:

                # See if there's water adjacent
                # FIXME: move this to TerrainNode
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

                for arc in self.arcs:
                    if arc.match( n, n2 ):
                        foundArc = arc
                        break

                if not foundArc:
                    if (n.nodeType == TerrainType_LAND and
                            n2.nodeType == TerrainType_LAND):
                        self.arcs.append( TerrainArc( n, n2) )


    def isReachable(self, targ, curr, travelType ):
        """Note must clearVisited first"""
        curr.visited = True
        for n2 in curr.adj:

            if n2==targ:
                return True

            # Only travel on travelType
            if not n2.visited and n2.nodeType==travelType:
                if self.isReachable( targ, n2, travelType ):
                    return True

        return False


    def addSeaLanes(self):

        # Put arcs between all port cities
        portCities = []
        for n in self.nodes:
            if n.city and n.city.port:
                portCities.append( n )

        for p in portCities:
            for p2 in portCities:
                if p==p2:
                    continue

                self.clearVisited()
                if self.isReachable( p2, p, TerrainType_WATER ):
                    #print "Adding sea lane from ", p.city.name, " --> ",p2.city.name
                    arc = self.addArc( p, p2 )
                    arc.arcType = TerrainArc_SEA

    def addArc(self, a, b ):
        for arc in self.arcs:
            if arc.match( a, b ):
                return arc

        arc = TerrainArc( a, b )
        self.arcs.append( arc )

        return arc

    def addPortCities(self):

        # First mark any cities near water as port
        for n in self.nodes:
            if n.city:
                for n2 in n.adj:
                    if n2.nodeType == TerrainType_WATER:
                        #print "Marking", n.city.name, "as Port"
                        n.city.port = True
                        break

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

            #print "Kingdom", k.name, "has", len(kingdomCoastals), "coastal lands, adding", numMoreCities, "port cities"

            for n in kingdomCoastals[:numMoreCities]:
                cc = City( k, n, port=True )
                n.city = cc
                #print "  Added", cc.name

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

