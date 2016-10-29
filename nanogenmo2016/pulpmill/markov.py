import os, sys, string
import random
import utils
import pickle

STARTMARKER = '*START*'
ENDMARKER = '*END*'

class MarkovGenerator(object):

    def __init__(self, depth=2, weights = {}):

        self.depth = depth
        self.weights = weights

    def trainOne(self, sequence):

        #print sequence

        seq = ([ STARTMARKER ] * self.depth) + sequence + [ ENDMARKER]
        currPrior = []

        while len(seq):

            while len(currPrior) < self.depth:
                item = seq.pop(0)
                currPrior.append( item )

            if len(seq):
                nextItem = seq[0]
                priorKey = tuple(currPrior)

                if not self.weights.has_key(priorKey):
                    self.weights[priorKey] = {}

                #print "Prior", priorKey, " -> ", nextItem
                wgt = self.weights[priorKey]
                oldWgt = wgt.get(nextItem, 0 )
                wgt[nextItem] = oldWgt + 1

            # Done with this step
            currPrior.pop( 0 )


    def trainFinish(self):

        # Normalize all the weights
        for prior, wgt in self.weights.iteritems():

            total = 0
            for itemKey, itemWeight in wgt.items():
                #print total, itemWeight
                total += itemWeight

            wgtNormalized = {}
            for itemKey, itemWeight in wgt.iteritems():
                wgtNormalized[itemKey] = float(itemWeight) / float(total)

            self.weights[prior] = wgtNormalized

    def generate(self):

        result = []

        prior = tuple([ STARTMARKER ] * self.depth )

        while 1:
            wgts = self.weights[prior]


            #item = random.choice( wgts.keys() )
            item = utils.randomChoiceWeighted( wgts )

            if item==ENDMARKER:
                break

            # Append result and update prior
            result.append( item )
            prior =  prior[1:] + tuple( item )

        return result

    def genString(self):
        return string.join( self.generate(), '' )



def testSimple():
    # Test code for markov stuff
    gen = MarkovGenerator()
    for w in ['hello', 'howdy', 'hella', 'help', 'hubba', 'wot', 'well', 'welcome' ]:
        wseq = list(w)
        gen.trainOne( wseq )

    print gen.weights
    print "---- Normalize ---"

    gen.trainFinish()

    print gen.weights

    for i in range(15):
        print gen.genString()

def testUSCities():

    count = 0
    gen = MarkovGenerator( depth=4 )
    cities = []
    for line in open("data/island_cities.txt"):
        w = string.strip(line)
        cities.append(w)

    random.shuffle(cities)

    trainCities = cities[:10000]

    for w in trainCities:
        wseq = list(w)
        gen.trainOne( wseq )

        count += 1
        #if count >= 1000:
        #    break


    #print gen.weights
    #print "---- Normalize ---"

    gen.trainFinish()

    #print gen.weights

    targetNum = 20
    uniqCount = 0
    for i in range(targetNum):
        city = gen.genString()
        if city in trainCities:
            orig = "(input)"
        else:
            orig = "UNIQUE *"
            uniqCount += 1

        print city.title(), orig

    print "%3.2f unique" % (float(uniqCount) / float(targetNum))


# =============================================================


def scanDataCities():

    # Some crap code to inspect the city data
    count = 0
    countryCodes = {}
    for line in open(CITIES_FILE):
        lsplit = string.split(string.strip(line),',')
        cc = lsplit[0]
        countryCodes[cc] = countryCodes.get(cc, 0) + 1

        if (cc in [ 'ba', 'aw', 'ai', 'bb', 'bm', 'vg', 'ky', 'ht', 'jm', 'kn', 'sc', 'tt', 'tm', 'vi' ]):
            print lsplit[1]

        count += 1
        #if (count %1000)==0:
        #    print "Processed ", count, "lines"

    return

    print countryCodes
    print countryCodes.keys(), len(countryCodes.keys())
    print "total count", count

    exclude_ccs = []
    for cc, count in countryCodes.iteritems():
        if count < 1000:
            exclude_ccs.append(cc)

    print "EXCLUDE:", exclude_ccs, len(exclude_ccs)

    return

def trainDataCities():

    # exclude countries with < 1000 entries listed,
    excludeCities = ['gs', 'gp', 'gy', 'gg', 'gf', 'gd', 'gl', 'gi', 'lc', 'tv', 'tt', 'li', 'to', 'lu',
                     'ls', 'tf', 'tc', 'dm', 'dj', 'vc', 'yt', 'qa', 'eh', 'wf', 'sj', 're', 'tk', 'vg',
                     'bb', 'bm', 'bn', 'bh', 'bt', 'bw', 'ws', 'bs', 'je', 'bz', 'ck', 'cc', 'cx', 'cv',
                     'pw', 'pf', 'pn', 'pm', 'mc', 'mo', 'mh', 'mu', 'mt', 'mv', 'mq', 'mp', 'ms', 'im',
                     'ae', 'ad', 'ag', 'ai', 'vi', 'is', 'an', 'aw', 'nc', 'nf', 'sh', 'nr', 'nu',
                     'fk', 'fm', 'fo', 'sz', 'sr', 'ki', 'kn', 'km', 'st', 'kw', 'sm', 'sc', 'ky', 'sg']

    # exclude cities that get garbagy results
    excludeCities += [ 'dk', 'bd', ]

    generators = {}

    #gen = MarkovGenerator( depth=3 )

    count = 0
    for line in open(CITIES_FILE):
        lsplit = string.split(string.strip(line),',')

        # Skip header
        if (count==0):
            count += 1
            continue

        cc = lsplit[0]
        if cc in excludeCities:
            continue

        try:
            city = lsplit[1].encode('ascii', 'ignore')
        except UnicodeDecodeError:
            continue

        # Check for nonsense chars
        isNonsense = False
        for ch in city:
            if ch in '0123456789()?':
                isNonsense = True
                break

        if isNonsense:
            #print "Nonsense:", city
            continue

        seq = list(city)
        if not generators.has_key( cc):
            generators[cc] = MarkovGenerator(depth=3)

        generators[cc].trainOne(seq)

        count += 1
        if (count %1000)==0:
            print "Processed ", count, "cities"

        #if (count>=100000):
        #    break

    print generators.keys()

    for cc, gen in generators.iteritems():
        gen.trainFinish()


    return generators


if __name__=='__main__':
    #testSimple()

    #scanDataCities()
    testUSCities()

    sys.exit(1)

    doTrain = False
    if doTrain:
        generators = trainDataCities()
        pickle.dump( generators, open("data/citygen.p", "wb") )
    else:
        generators = pickle.load( open("data/citygen.p", "rb"))

    cckeys = generators.keys()
    cckeys.sort()
    for cc in cckeys:
        gen = generators[cc]
        print "----------- COUNTRY", cc, "----------------"
        for i in range(5):

            done = False
            while not done:
                cityname =  gen.genString()
                done = True
                if len(cityname) > 20:
                    done = False

            print cityname.title()





