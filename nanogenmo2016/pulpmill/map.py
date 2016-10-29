import os, sys
import datetime
import random

MAP_SIZE = (100.0, 120.0)

# World-building stuff
class TerrainNode(object):

    def __init__(self):

        self.pos = ( random.uniform( 10, (MAP_SIZE[0] - 10)),
                     random.uniform( 10, (MAP_SIZE[1] - 10)))

class World(object):

    def __init__(self):

        self.worldname = 'Test World'
        self.daylength = datetime.timedelta( hours = random.randint( 20, 35 ) )
        self.size = MAP_SIZE

        self.nodes = []

    def buildMap(self):

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

            if not tooClose:
                self.nodes.append( n )

    def dbgPrint(self):

        print "This world is called", self.worldname
        print "A day in this world takes ", self.daylength

