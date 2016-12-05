import os, sys, string
import itertools
import random

import utils
import tracery
from tracery.modifiers import base_english

from pulpmill import world, utils, character, combat

# TODO List for scene types
# Scene Type        Placeholder  Text


def placeholder( text ):
    """
    Adds punctuation. Also a useful place to check if I have placeholders in the future.
    """
    if text[-1] != '.':
        return text+"."
    else:
        return text

def punctuate( text ):
    """
    Adds punctuation.
    """
    if text[-1] != '.':
        return text+"."
    else:
        return text

def first_lower(s):
    if len(s) == 0:
      result = s
    else:
      result = s[0].lower() + s[1:]

    return result

def speakText( text, speaker, isReply ):

    speakStatments = ['"%(text)s", said %(speaker)s.//',
                     '%(speaker)s said, "%(text)s"//',
                     ]

    if isReply:
        speakStatments += ['"%(text)s", replied %(speaker)s.//',
                           '%(speaker)s replied, "%(text)s"//',
                            ]

    statement = random.choice( speakStatments )

    result = statement % {"speaker" : speaker, "text" : text }

    return result

def genWanderText( charName, wanderList, numSteps ):

    wanderText = "#" + charName +"Name#"
    for i in range(numSteps):
        step = random.choice( wanderList )
        if i>0:
            wanderText += random.choice( [". #"+charName+"They.capitalize#", ", and" ])

        wanderText += " " +step

    wanderText += "."
    return wanderText

class Scene(object):

    def __init__(self):

        self.desc = "Empty Scene"

        self.node = None
        self.chars = {}

        self.storyText = []
        self.origin = 'TODO'
        self.chapterTitle = "Chapter Title"

        self.wordCount = 0

        self.sceneRules = {}
        self.newChars = []

        # Some special flags
        self.quest = None
        self.lastDungeon = False
        self.incitingIncident = False


    def checkPPText(self, pptext ):

        if pptext.find('((') != -1 and pptext.find('))') != -1:
            print "StoryText: ", pptext
            print "Party:", self.party
            print "Node: ", self.node
            if self.node:
                print "Region: ", self.node.region
            else:
                print "No region..."

            raise Exception( "StoryError", "Found unexpanded rules in story text")

    def growParagraph(self, pptext ):

        self.checkPPText( pptext )

        if len(self.storyText[-1]) < 250:
            self.storyText[-1] = self.storyText[-1] + " " + pptext
        else:
            self.storyText.append( pptext )

        self.wordCount += len( string.split( pptext ))

    def addParagraph(self, pptext ):

        # hack fix punctuation
        # if pptext.endswith['..']:
        #     pptext[-2:] = '.'

        self.checkPPText( pptext )

        self.storyText.append( pptext )
        self.wordCount += len( string.split( pptext ))

    def buildSceneRules(self, sg):

        commonRules = sg.getCommonRules( self.node )

        # Build chars from party and newChars
        protag = self.party[0]

        otherchars = self.party[1:]
        random.shuffle(otherchars)

        # new chars go first, then repeat other chars until enough
        allchars = [protag ] + self.newChars
        charRoles = ['protag', 'alice', 'bob', 'chuck']
        otherchars = list(itertools.islice( itertools.cycle( otherchars ), None, 3 )) # Ensure enough otherchars
        for role, char in zip( charRoles, allchars + otherchars ):
            #print role, char.name
            self.chars[role] = char

        # HACK -- make sure there are enough chars. fix  make scenes
        # only emit with enough ppl
        for role in charRoles:
            if not self.chars.has_key( role):
                self.chars[role] = protag


        # Add character rules
        for role,char in self.chars.iteritems():
            charRules = char.getCharacterRules( role )
            #print "Add char rules", charRules
            #self.dbgPrintRules( charRules )
            self.sceneRules.update( charRules )

        self.sceneRules.update( commonRules )

    def dbgPrintRules(self, rules ):
        kk = rules.keys()
        kk.sort()
        for k in kk:
            print k, "-> ", rules[k]

    def generate(self, sg ):
        """
        Fills in storyText and possibly override chapterTitle
        """
        self.sceneRules['origin'] = self.origin
        #print self, "origin is ", self.origin
        #self.dbgPrintRules( self.sceneRules )

        # print "SCENE RULES:"
        # self.dbgPrintRules( self.sceneRules )

        grammar = tracery.Grammar( self.sceneRules )
        grammar.add_modifiers( base_english )

        try:
            print "---"
            print self.origin
            pp = grammar.flatten( "#origin#" )
            self.addParagraph( pp )

        except:
            print "Tracery error, failed to expand #origin#"
            print self.sceneRules

            sys.exit(1)


    def doGenerate(self, sg ):
        self.buildSceneRules( sg )
        self.generate( sg )

# -------------------------------------------------------------
#   Add Character
# -------------------------------------------------------------
def sceneAddCharacter( node, world ):

    scenes = []

    if (utils.randomChance(0.5)):
        homeNode = node
    else:
        homeNode = world.randomTownNode()

    newChar = character.Character( homeNode)

    scn = SceneAddChar( newChar )
    scn.node = node
    scn.newChars = [ newChar ]
    scn.desc = "Add " + newChar.name + " from "+newChar.hometown.name+ " to party"
    scn.chapterTitle = random.choice( [ newChar.name, "Meeting "+newChar.name ] )

    scenes.append( scn )

    return scenes

class SceneAddChar( Scene ):

    def __init__(self, newChar):
        super(SceneAddChar, self).__init__()

        self.newChar = newChar

    def generate(self, sg ):
        """New char is Alice"""
        template = []

        # Setup
        template.append( random.choice([ '#protagName# visited a tavern.',
                      '#protagName# was #the_feels#. #protagThey.capitalize# wandered into a garden full of #kfruit.s#.',
                      '#protagName# heard an animated conversation coming from a #propBuilding# and peeked inside.',
                      '#protagName# was hungry and stopped into an inn for some food.',
                      '#cityname# was hardly a cosmopolitan town, but it had a coffee shop.',
                     ]))

        template.append( random.choice( ['A #aliceClass# was there, lurking in the shadows.',
                          "#protagName# couldn't help but notice a #aliceClass# nearby.",
                          "There was a #aliceClass# sipping #beverage#.",
                          ]))

        template.append( random.choice([
            'The #aliceClass# noticed #protagName#. "Hello there," the #aliceClass# said, '
            '"You look like you could use a #aliceClass# in your group, and I could use some'
            ' adventure. I\'m #aliceName#."',

            '#protagName# strode up to the stranger. "You have the look of an #aliceClass#,"'
            'said #protagName#, "we could use someone like you in our party."//"I\'m #aliceName#,"'
            '#aliceThey# replied, "maybe you\'re right. I\'ve been in this town too long."',

            'Suddenly, a brawl broke out among the patrons. A mug of #beverage# splashed #protagName# '
            'in the face. At the center, a flailing #aliceClass# was throwing loose punches. #protagName# '
            'decided to help #aliceThem# out.//#protagThey# extricated #aliceThem# from the fight and after '
            'a few minutes, the #aliceClass# said, "Thanks for your help back there. I\'m #aliceName#." //'
            'They chatted for the rest of the afternoon, and soon it was clear that #aliceName# would be '
            'joining them for the rest of their journey.'
        ]))


        self.origin = string.join( template, ' ')

        super(SceneAddChar,self).generate( sg )

# -------------------------------------------------------------
#   Inciting Incident (TODO part of quest?)
# -------------------------------------------------------------

def sceneIncitingIncident( node, protag ):

    scn = Scene()
    scn.node = node
    scn.chars = { "protag" : protag }
    scn.desc = "Inciting Incident"
    scn.incitingIncident = True

    #TEST -- Replace with inciting scene from quest
    #scn.origin = placeholder("#protagName#'s life was about to change in ways #protagThey# never expected")

    # Oh well, this was supposed to be the setup for the epic quest but didnt
    # get to that...
    scn.sceneRules = {
        "foreshadow" : [
            "#protagName#'s life was about to change in ways #protagThey# never expected.",
            "#moodLighting#. #weather_sentence# A storm was coming.",
            'This was the last #daytime# #protagName# would spend #protagJobTask#.',
            'Change was on the #weather_air#.'
        ]
    }
    scn.origin = '#foreshadow#'


    return [ scn ]

# -------------------------------------------------------------
#   Everyday Life
# -------------------------------------------------------------

def sceneNormalLife( node, char ):

    scenes = []

    scn = Scene()
    scn.node = node
    scn.desc = char.name + " does normal stuff in " + node.city.name

    scn.sceneRules = {
        'scnDidStuff' : [ '#protagName# wandered by the #propBuilding#',
                          '#protagThey.capitalize# spent the #daytime# #protagJobTask#',
                          '#protagThey.capitalize# busied #protagThem#self #protagJobTask#',
                          '#protagName# thought to visit a #propBuilding#, but was busy #protagJobTask#' ],
    }

    scn.origin = punctuate("#protagName# was a #humble# #protagJob# in #protagHome#. #scnDidStuff#. "+
                             "#moodLighting.capitalize#. #scnDidStuff# #it_gave_feels#")

    scenes.append( scn )

    return scenes

# -------------------------------------------------------------
#   Dialogue Filler
# -------------------------------------------------------------
def sceneDialogueFiller( node ):

    scenes = []

    scn = SceneDialogueFiller()
    #scn.origin = placeholder( "#protagName# and #aliceName# had a profound conversation")
    scenes.append( scn )

    scn.desc = "Dialogue Filler"

    return scenes

class SceneDialogueFiller( Scene ):

    def __init__(self):
        super(SceneDialogueFiller,self).__init__()


    def generate( self, sg ):

        """
        Judge-y squabble. Would be nice to add more types of filler. :)
        """
        template = []

        # Set up the conversation
        sentences = [
            ( 0.3, '#weather_sentence.capitalize#' ),

            # Judgy statement
            ( 0.3, '#protagName# and #aliceName# stopped in to a tavern.' )

            ]

        template += utils.addSentencesWithChances( sentences )
        random.shuffle( template )

        sg.tarot = sg.getTarotMeanings()
        tarot = random.choice( sg.tarot)

        self.chapterTitle = random.choice( tarot['keywords'] ).title()
        lightStatements = tarot['meanings']['light'][:]
        shadowStatements = tarot['meanings']['shadow'][:]

        allResponses = [
                "I see it as more %s.",
                "Is that what you think? I think it's %s.",
                "Is that how you see it? It's just %s.",
                "Really? More like %s.",
                "I'm merely %s.",
                "Certainly not. I'm %s.",
            ]

        allStatments = [
                    "I mean, it just seems like you're %s.",
                    "Maybe %s, just a bit?",
                    "You're %s. It's not uncommon for #aliceClass.a#."
                ]

        for i in range(random.randint(1,2)):
            if i==0:
                stmt = random.choice([
                    '''"I'm wondering, #aliceName#," asked #protagName#," do you worry that you're %s?"//''',
                    'I wanted to talk to you about %s.',
                    "You're %s. It makes me #the_feels#.",
                    'Can we chat about %s',
                    "Hey! You're %s. Knock it off.",
                    "Are you aware that you're %s?",
                    '''"Hey, I just..." #protagName# trailed off. #protagThey.capitalize# shifted on the #ground#. "Are you %s?" #protagThey# asked.//'''
                ])
            else:
                stmt = random.choice( allStatments)
                allStatments.remove( stmt )

            response = random.choice(allResponses)
            allResponses.remove( response )

            shadowThing = random.choice(shadowStatements)
            shadowStatements.remove(shadowThing)
            shadowThing = first_lower( shadowThing )
            stmt = stmt % (shadowThing)

            lightThing = random.choice(lightStatements)
            lightStatements.remove(lightThing)

            lightThing = string.replace( first_lower( lightThing ), "your", "my" )
            response = response % (lightThing)

            isReply = (i!=0)

            if stmt.find('"') == -1:
                speakStatment = speakText( stmt, '#protagName#', isReply )
            else:
                speakStatment = stmt

            template.append( speakStatment )
            template.append( speakText( response, '#aliceName#', isReply ) )

        template.append( random.choice( ['#thinkWonder#', '#weather_sentence.capitalize#'] ))

        self.origin = string.join( template, ' ')
        # print self.origin

        super(SceneDialogueFiller,self).generate( sg )

# -------------------------------------------------------------
#   Sea Voyage
# -------------------------------------------------------------

def sceneSeaVoyage( node, arc ):

    # TODO: more types of sea voyages
    print "destNode", node, node.city, "arc:", arc.arcType
    print "arc", arc.a.city.name, arc.b.city.name
    destNode = arc.other(node)

    scenes = []

    # Should do this better but this will do for now
    BOAT_RULES = {
        "boatname" : [ "the #boatname1#", "the #seaboatname#" ],
        "seaboatname" : ["#boatname1# of the sea", "#boatname1# on the waves",
                         "#boatname1# of the water"],
        "boatname1" : [ '#conceptual#','#creature#', '#girlfriend#' ],
        "adj" : [ 'lost', 'new', 'newfound', "sailor's", 'enchanted', 'bonnie' ],
        "conceptual" : [ '#concept#', '#adj# #concept#'],
        "concept" : ['freedom', 'hope', 'commerce', 'tradewinds',
                    'delight', 'remorse', 'spice', 'wind',
                    'happiness', 'compass rose', 'compass', 'mutineer',
                     'windlass', ],
        'creature' : ['dolphin', 'whale', 'sunfish', 'bonefish', 'jellyfish',
                      'narwhal'],
        'girlfriend' : [ '#adj# #girlfriend1#', '#girlfriend1#'],
        'girlfriend1' : ['mermaid', 'siren', 'enchantress', 'lady', 'queen', 'princess', 'lass',
                        'manatee', 'narwhal']

    }
    grammar = tracery.Grammar( BOAT_RULES )
    grammar.add_modifiers( base_english )

    boatName = grammar.flatten( "#boatname#")
    boatName = boatName.title()

    captainName  = node.kingdom.culture.genContinentName()
    captainThey = random.choice( ['he', 'she'] )

    commonSeaRules = {
        "startCity" : arc.a.city.name,
        "destCity" : arc.b.city.name,
        "boatName" : boatName,
        "captainName" : captainName,
        "captainThey" : captainThey,
        "wavey" : [ "calm", "choppy", "rough", "stormy", "churning" ],
    }

    if utils.randomChance(0.3):
        scn = Scene()
        scn.desc = "Finding passage in " + node.city.name
        scn.node = node
        scn.chapterTitle = boatName

        scn.sceneRules.update( commonSeaRules )

        findboat_rules = {
            "hear_about_boat" : [
                "There was notice board at the #place# that listed shipping schedules.",
                "#aliceName# bought a round for the sailors at the local tavern and asked about ships.",
                "#protagName# made friends with a local #portJob# who knew the comings and goings of the port.",
                "#protagName# met a #portJob# and got a lead on a ship sailing to #destCity#.",
            ],

            "boat_schedule" : [
                "#boatName# was set to sail to #destCity# #soon#.",
                "A #boatType# named #boatName# was sailing to #destCity#.",
                "#soon.capitalize#, #boatName# was set to sail to #destCity#.",
                "#boatName# was the only #boatType# from #startCity# to #destCity# this moon."
            ],

            "captain_desc" : [
                "The captain was a #capt_desc# #sea_dog# named #captainName#.",
                'The #boatName# was piloted by a #capt_desc# #sea_dog# named #captainName#.'
            ],

            "capt_problem" : [
                "#captainName# had no interest in letting them on #boatName#.",
                "But #boatName# was at capacity, and had no room for adventureres.",
                '"Sorry," said #captainName#, "but #boatName# isn\'t a passenger vessel."',
                'There should have been plenty of space on #boatName#, but #captainName# said it was full. #aliceName# guessed that it was a smuggler.',
                '"I\'m looking for sailors, not a #protagClass#," said #captainName#, "find some other boat".',
                '"Sod off," said #captainName#, "#boatName#\'s not for landlubbers like ya."'
            ],

            "kill_time" : [
                "#protagName# wandered the streets of #startCity#. #moodLighting#.",
                '#protagName# walked the docks and pondered. #protagThey# scanned the #wavey# horizon.',
                '#protagName# visited a tavern and considered #protagTheir# options.',
                '#protagName# mused, visited a street market and ate some fried #critter#. #moodLighting#.'
            ],

            "resolve" : [
                "Then, #aliceName# saw #captainName# in a tavern. #aliceThey# bought the #capt_desc# captain enough "+
                "whiskey to change their mind, even if they had a little trouble recalling it the next day.",

                "#aliceName# followed a couple of sailors from #boatName# into an alley. The next day, #captainName# "+
                "found themselves short on crew, and had little choice but to take on the party if they agreed to help sail.",
            ],

            "portJob" : [ "fisherman", "sailor", "dockworker"],
            "place" : [ "tavern", "docks", "fish market", "quay", "pier"],
            "boatType" : ['barque', 'schooner', 'scow', 'galley', 'longboat', 'caravel'],
            "capt_desc" : [ 'salty', 'grumpy', 'prancing', 'gruff', 'bitter', 'grizzled' ],
            "sea_dog" : ['sea dog', 'mariner', 'freebooter', 'pirate', 'mercenary'],
            "soon" : ['that evening', 'at dawn', 'tomorrow', 'in a few days',
                      'at midnight', 'at noon', 'on wednesday'],

        }
        scn.sceneRules.update( findboat_rules )

        scn.origin = "#hear_about_boat# #boat_schedule# #captain_desc#//#capt_problem# #kill_time# #resolve#"
        scenes.append( scn )


    scn = Scene()
    scn.node = node
    scn.desc = "Voyage to " + destNode.city.name
    scn.chapterTitle = random.choice(['Voyage to $PP', 'Sailing to $PP', 'The Open Ocean',
                                      'Across the Vast Sea', 'A Trip to $PP', 'An Ocean Voyage',
                                      'A Sea Voyage'])
    scn.chapterTitle = scn.chapterTitle.replace( '$PP', destNode.city.name )

    scn.sceneRules.update( commonSeaRules )


    voyageRules = {

        "voyage_origin" : [
            "#sea_desc# #sea_detail# #voyage_overview#"
        ],

        "sea_desc" : [
            "The #weather_adj# sea was #wavey#.",
            "The waves were #wavey# and the air was #weather_adj#."
        ],

        "sea_detail" : [
            "Seagulls circled #boatName# and #aliceName# fretted that they might poop on #protagThem#.",
            "#boatName# was followed for a while by a pod of dolphins.",
            "The air was pleasent but there were #bug.s# in #protagName#'s cabin.",
            "They saw a humpback whale breach the #weather_adj# waves."
        ],

        "voyage_overview" : [
            "#v_uneventful#", "#v_good#", "#v_bad#"
        ],

        "v_uneventful" : [
            "The voyage to #destCity# was uneventful.",
            "The sail to #destCity# was a much needed rest for the party.",
            "Much happened on the voyage to #destCity#, but that is a tale for another time.",
            "Not much happened on the voyage to #destCity#."
        ],

        "v_good" : [
            "#aliceName# spent the trip to #destCity# pilfering grog from the #boatName#'s crew.",
            "#protagName# learned the fisherman's trick of baiting with spoiled #kfruit# to catch #fish#.",
            "On the way to #destCity#, #protagName# climbed the #boatName#'s mast and surveyed the vast ocean. #moodLighting#."
        ],

        "v_bad" : [
            "#aliceName# never found #aliceTheir# sea legs on the whole trip to #destCity#.",
            "#aliceName# spend most of #aliceTheir# time on the voyage to #destCity# puking over the gunwales.",
            "On the voyage to #destCity#, #protagName# lost most of #protagTheir# gold playing dice with the crew."
        ]
    }
    scn.sceneRules.update( voyageRules )
    scn.origin = "#voyage_origin#"

    scenes.append( scn )

    if utils.randomChance(0.3):
        scn = Scene()
        scn.desc = "Arriving in " + node.city.name
        scn.node = node
        scn.sceneRules.update( commonSeaRules )

        arrive_rules = {
            "arrive_origin" : [ "#protagName# arrived in #destCity# and #it_gave_feels#.",
                                "It was #daytime# when they reached the docks in #destCity#.",
                                "#moodLighting# as they sailed into the harbor at #destCity#.",
                                "It seemed as if weeks had passed since they left #startCity#. The harbor in #destCity# was #wavey#."
                                ]

        }
        scn.sceneRules.update( arrive_rules )

        scn.origin = "#arrive_origin#"
        scenes.append( scn )

    return scenes

# -------------------------------------------------------------
#   Place Desc
# -------------------------------------------------------------


def sceneCity( node, protag ):

    scenes = []

    if not node.storyVisited:
        scenes += scenePlaceDesc( node, protag )

    if node.city.port:
        scn = Scene()
        scn.node = node
        scn.desc = "Visit Port town of " + node.city.name
        scn.origin = placeholder("#protagName# visited the port town of " + node.city.name )
    elif not node.city.dungeon:
        scn = Scene()
        scn.node = node
        scn.desc = "Visit City " + node.city.name
        scn.origin = placeholder( "#protagName# had some stuff happen in "+ node.city.name )

    return scenes

def scenePlaceDesc( node, protag ):

    scn = ScenePlaceDesc()
    city = node.city
    scn.chars = { "protag" : protag }
    scn.desc = "Description of " + city.name
    scn.chapterTitle = city.name
    scn.node = node

    node.storyVisited = True

    return [ scn ]


class ScenePlaceDesc( Scene ):

    def __init__(self):
        super(ScenePlaceDesc,self).__init__()

    def generate( self, sg ):

        if self.node.city.dungeon:
            self.generateDungeon( sg )
        else:
            self.generateCity(sg)

        super(ScenePlaceDesc,self).generate( sg )

    def generateDungeon( self, sg ):

        template = []

        sentences = [
            ( 0.3, '#weather_sentence.capitalize#' ),

            # Description/entrance
            ( 0.99, ['#cityname# was barely more than a speck on the #region#, but spread beneath the #ground# like #fungus#.',
                     'Behind a #natureThing#, #aliceName# spotted the entrance to #cityname#.',
                     '#cityname# had been left to the #critter.s# for #long_time#.',
                     '#cityname# was a forlorn ruin, abandonded for #long_time#, but it was far from empty.',
                     '"I have a bad feeling about this," muttered #aliceName#, as they approach the entrance to #cityname#.',
                     ] ),

            # Foreboding event
            ( 0.5, [ 'A #critter# hissed and scurried past them.',
                     'A hollow booming sound echoed from underground.',
                     'They passed scratch marks tinged with dried blood on the #weather_adj# walls.',
                     'Their footsteps echoed in the chamber.',
                     'The wind howled through gaps in the rough stone.',
                     "A chill ran down #protagName#'s spine. #protagThey# felt #the_feels#."
                ] ),

            # Ambience
            ( 0.3, [ 'Lightning flashed in the #weather_adj# air outside, throwing shadows on the walls.',
                     'A distant thunder rumbled.',
                     'Rats scurried away around their feet.',
                     'The #weather_adj# air felt #bad_vibe#.' ] )
            ]

        template += utils.addSentencesWithChances( sentences )

        random.shuffle( template )

        # Walk for a bit deeper into the dungeon
        steps = random.randint(3, 5 )
        wanderDungeon = ['walked carefully on the crumbling stones',
                         'walked #dungeonDir#', 'ducked to pass the low ceiling',
                         'breathed cautiously', 'shivered', 'lit a torch',
                         'squinted']

        wanderText = genWanderText( random.choice(["protag", "alice", "bob"]), wanderDungeon, steps )
        template.append( wanderText )


        # Now they are in the belly of the dungeon
        template.append( random.choice( [
            "The air was #weather_adj#. They were well into #cityname# now.",
            "A door boomed closed behind them. They were trapped in #cityname#, but they weren't alone.",
            "Inhuman sounds echoed from the walls. A #critter# fled in terror from whatever lay ahead.",
            "This was the belly of #cityname#."
        ] ))


        self.origin = string.join( template, ' ')

    def generateCity( self, sg ):

        template = []

        sentences = [
            ( 0.3, '#weather_sentence.capitalize#' ),

            # Judgy statement
            ( 0.3, [ '#cityname# was the jewel of #kingdomname#.',
                     '#cityname# was kind of a dump.',
                     '#cityname# was a #beautiful# #citytype#.',
                     'The #legends# of #cityname# were legendary.',
                     '#cityname# was a #citytype# of #kind_or_mean# people.',
                     '#cityname# was a #economic_state# #citytype#, and that kept it #civic_state#.',
                     ] ),

            # Historical Info
            ( 0.3, ['#cityname# had been founded by the #type_of_elves#, but it was all #rough# men and women now.',
                    '#legends.capitalize# stated that #cityname# was built where a fallen star had landed.',
                    '#cityname# was once the seat of the empire, but no longer.',
                    'Started as a #industry# town, #cityname# was now a thriving #citytype#.',
                    '#cityname# was once a trading center at a great crossroads, but those roads faded into #critter# trails.'
                    ])
        ]

        if self.node.city.size == 'small':
            sentences += [
                ( 0.5, [ '#cityname# was hardly more than a handful of buildings.',
                         '#cityname# was not much to look at.',
                         'More of a commune than a #citytype#, #cityname# was home to a few stubborn families and their livestock.',
                         '#cityname# counted its population in #kfruit.s#.'
                         ]) ]
        elif self.node.city.size == 'medium':
            sentences += [
                ( 0.5, [ '#cityname# covered a square mile of countryside.',
                         '#cityname# had cobblestone steets, and a few taverns on each.',
                         '#cityname# was a growing town.',
                         '#cityname# boasted a thriving market.'
                         ]) ]
        elif self.node.city.size == 'large':
            sentences += [
                ( 0.5, [ '#cityname# stretched to the horizon.',
                         '#cityname# was the largest city in #kingdomname#.',
                         '#cityname# bustled with activity.',
                         '#cityname# was huge.'
                         ]) ]

        template += utils.addSentencesWithChances( sentences )

        random.shuffle( template )

        # Add some idle actions and thoughts
        protagIdleActions = [
            "#protagName# scanned the horizon. #protagThey.capitalize# breathed in the #weather_adj# #weather_air#.",
            "A hint of motion caught #protagName#'s eye, #protagThey# turned. It might have been a #critter#, but it was gone.",
            "#protagName# watched a #critter# by a #natureThing# on the #ground#.",
            "#protagName# saw a #natureThing#, and it reminded #protagThem# of #protagHome#.",
            "#critter.a.capitalize# passed through the #weather_air#.",
            "#protagName# wandered through the market. #protagThey.capitalize# bought a #kfruit# from a #marketStall# and took a bite. It was #foodQuality#. #thinkWonder#",
            "#protagName# walked for a bit. #protagThey.capitalize# passed a #propBuilding#.",
            "Some peasants were dyeing cloth nearby, it made the #weather_air# smell of #kfruit2#. #thinkWonder#",
            "#protagName# wondered about the folks living here. Most that #protagThey# passed seemed happy, but, #protagThey# would be glad to move on.",
            "#protagName# sat down on the #ground# for a bit. #thinkWonder#",
        ]

        # Do something
        idleAction = random.choice( protagIdleActions )
        template.append( random.choice( protagIdleActions ))
        protagIdleActions.remove( idleAction )

        # Do something
        busyAction = random.choice( ["wander" ] )

        if busyAction == 'wander':

            steps = random.randint(3, 5 )
            wanderCity = ['walked #cityDir#',
                        'saw a #critter# and kept moving',
                        'saw a #critter#', 'chatted with a #kind_or_mean# #propJob#',
                        'tarried for a bit', 'kicked the #ground#',
                        'took a few steps', 'sat for a while', 'stopped for a drink',
                        'passed a #propBuilding#' ]

            wanderText = genWanderText( "protag", wanderCity, steps )

            template.append( wanderText )

        # Take another idle action
        idleAction = random.choice( protagIdleActions )
        template.append( random.choice( protagIdleActions ))
        protagIdleActions.remove( idleAction )


        self.origin = string.join( template, ' ')
        # print self.origin

# -------------------------------------------------------------
#  Quest Scenes
# -------------------------------------------------------------

class SceneQuest( Scene ):

    def __init__(self, qq ):

        super(SceneQuest,self).__init__()
        self.quest = qq

    def generate( self, sg ):

        # Add quest rules
        questRules = {
            "questItem" : self.quest.item,
            "startCity" : self.quest.startCity.city.name,
            "destCity" : self.quest.destCity.city.name,
        }

        questRules.update( self.quest.questGiverRules )

        self.sceneRules.update( questRules )

        super(SceneQuest,self).generate( sg )

def sceneFinishQuest( qq, node, party ):

    scn = SceneQuest(qq)

    scn.chars = { "protag" : party[0] }
    scn.desc = "Finish Quest " + qq.desc + " at " + node.city.name
    scn.chapterTitle = qq.item
    scn.node = node
    scn.origin = qq.finishPhrase

    node.storyVisited = True

    return [ scn ]


def sceneStartQuest( qq, node, destNode, party ):

    scn = SceneQuest(qq)

    scn.chars = { "protag" : party[0] }
    placeName = "Wilderness (%s)" % destNode.region.ident
    if destNode.city:
        placeName = destNode.city.name
    scn.desc = "Start Quest " + qq.desc + " in " + placeName
    scn.chapterTitle = qq.item
    scn.node = node
    scn.origin = qq.startPhrase

    node.storyVisited = True

    return [ scn ]

def sceneRemindQuest( qq, node, destNode, party ):

    scn = SceneQuest(qq)

    scn.chars = { "protag" : party[0] }
    placeName = "Wilderness (%s)" % destNode.region.ident
    if destNode.city:
        placeName = destNode.city.name
    scn.desc = "Remind Quest " + qq.desc + " in " + placeName
    scn.chapterTitle = qq.item
    scn.node = node
    scn.origin = qq.getReminder()

    node.storyVisited = True

    return [ scn ]


# -------------------------------------------------------------
#  Combat scene
# -------------------------------------------------------------

def generateCombatScenes( party, level, node ):

    scn = SceneCombat( level )
    scn.node = node
    scn.party = party

    scn.desc = "Adventure in " + node.city.name
    scn.chapterTitle = node.city.name
    scn.origin = placeholder("#protagName# and #aliceName# fought their way through "+node.city.name )

    # Simulate the scenes
    scn.simulate()

    return [ scn ], scn.csim.deadHeros

class SceneCombat( Scene ):

    def __init__(self, level ):

        super(SceneCombat,self).__init__()
        self.level = level
        self.csim = None

    def simulate(self ):
        # test combat
        self.csim = combat.CombatSimulator( self.party, self.level, self.node )

        self.csim.setupFight( self.node, self.party )

        # Step combat until all creatures are dead
        while 1:
            if self.csim.stepCombat( self ):
                break

            self.csim.combatFiller( self )





    def generate( self, sg ):

        monsters = self.csim.monsters
        mname = []
        for m in monsters:
            mname.append( m )

        random.shuffle( mname )

        intro = random.choice([
            "Around a corner, they ran into trouble.",
            "Soon their fears were manifest.", "There were monsters ahead.",
            "Their passage was blocked.", "They were not alone.", "Things went from bad to worse.",
            "They braced for a fight.", "Ahead, there was a problem."
        ])
        self.addParagraph( intro )

        seenMonsters = set()
        for m in mname:

            if m.name in seenMonsters:
                monsterName = random.choice( ["another", "one more", "an additional", "a second", "an extra" ] ) + m.name
            else:
                monsterName = "a " + m.name
                seenMonsters.add( m.name )

            if m.leader:
                statement = random.choice([
                    "Their leader was a %s.", "They were lead by a %s.", "A %s called the shots.",
                    "A %s was in charge of them all.", "They served the %s.",
                    "A %s was their leader.", "The biggest was a %s", "The fiercest of all, a %s."
                ]) % m.name
            else:
                statement = random.choice([
                    "%s crouched by a wall", "%s faced the group.", "%s scuttled behind the rest.",
                    "There was %s.", "%s was ready to fight.", "There was %s.",
                    "%s glared at them.", "%s was pure evil.", "%s rounded out the cadre.",
                    "%s was maybe the worst of them.", "%s, and it looked hungry.",
                    "%s, ready for battle.", "Don't forget about %s.", "%s was across the cobbles.",
                    "%s jeered at them.", "%s licked it's jowls.", "%s glared fiercely.",
                    "%s posed a serious threat."
                ]) % monsterName

            statement = statement.capitalize() + " "

            self.growParagraph( statement )

        # Here -- emit self.csim actions
        for act in self.csim.combatActions:
            scn, hero, monster, startrule = act
            self.csim.genCombatAction( self, hero, monster, startrule )


