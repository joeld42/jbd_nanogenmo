import os, sys, string
import itertools
import random

import utils
import tracery
from tracery.modifiers import base_english

from pulpmill import world, utils, character, combat

# TODO List for scene types
# Scene Type        Placeholder  Text
# ------------------------------------
#  Place Desc           [X]       [X]
#  Normal Life          [X]       [ ]
#  Epic: Incit. Inc.    [X]       [ ]
#  Sea Voyage           [X]       [ ]
#  Add Character        [X]       [ ]
#  Encounter Outdoor    [ ]       [ ]
#  Dungeon Desc         [X]       [ ]
#  Dungeon Filler       [ ]       [ ]
#  Dialogue Filler      [X]       [ ]
#  Quest: Setup         [X]       [ ]
#  Quest: Resolve       [X]       [ ]
#  Epic: Return         [ ]       [ ]


def placeholder( text ):
    """
    Adds punctuation. Also a useful place to check if I have placeholders in the future.
    """
    return text+"."

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

        self.sceneRules = []
        self.newChars = []

        # Some special flags
        self.quest = None
        self.lastDungeon = False
        self.incitingIncident = False

    def addParagraph(self, pptext ):

        if pptext.find('((') != -1 and pptext.find('))') != -1:
            print "StoryText: ", pptext
            print "Party:", self.party
            print "Node: ", self.node
            if self.node:
                print "Region: ", self.node.region
            else:
                print "No region..."

            raise Exception( "StoryError", "Found unexpanded rules in story text")

        self.storyText.append( pptext )
        self.wordCount += len( string.split( pptext ))

    def buildSceneRules(self, sg):

        commonRules = sg.getCommonRules( self.node )

        # Base scene just uses origin rule, but complex scenes might
        # mix up more than one rule set or sequence
        self.sceneRules = {
             'origin' : self.origin
         }

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

        pp = grammar.flatten( "#origin#" )
        self.addParagraph( pp )


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
        sentences = [
            ( 0.5, [ '#protagName# visited a tavern.',
                     '#protagName# was #the_feels#. #protagThey.capitalize# wandered into a garden full of #kfruit.s#.'
                     ])
        ]
        template += utils.addSentencesWithChances( sentences )

        template.append( 'A #aliceClass# joined the party. #aliceTheir.capitalize# name was #aliceName#.')

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
    scn.origin = placeholder("#protagName#'s life was about to change in ways #protagThey# never expected")
    return [ scn ]

# -------------------------------------------------------------
#   Everyday Life
# -------------------------------------------------------------

def sceneNormalLife( node, char ):

    scenes = []

    scn = Scene()
    scn.node = node
    scn.desc = char.name + " does normal stuff in " + node.city.name

    scn.origin = placeholder("#protagName# was a humble #protagJob# in #protagHome#")

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

    if utils.randomChance(0.3):
        scn = Scene()
        scn.desc = "Finding passage in " + node.city.name
        scn.node = node
        scn.chapterTitle = "Find a boat" # name of the boat?
        scn.origin = placeholder("#protagName# had some trouble finding a boat to "+destNode.city.name )
        scenes.append( scn )

    scn = Scene()
    scn.node = node
    scn.desc = "Voyage to " + destNode.city.name
    scn.origin = placeholder( "Stuff happened on the boat ride to "+destNode.city.name )

    scenes.append( scn )

    if utils.randomChance(0.3):
        scn = Scene()
        scn.desc = "Arriving in " + node.city.name
        scn.node = node
        scn.orign = placeholder( "#protagName# arrived in "+destNode.city.name+" and #it_gave_feels#")
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
            "questGiver" : "TODO:questGiver"
        }

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
    scn.origin = "Placeholder: #protagName# thought about #questItem#."

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

            # TODO: Add some random stuff here





    def generate( self, sg ):

        monsters = self.csim.monsters
        mname = []
        for m in monsters:
            mname.append( m.name )

        mdesc = "Fight against " + ", ".join( mname )

        mdesc = mdesc + ". Party is: "
        for h in self.party:
            mdesc += h.name
            mdesc += ", "


        self.addParagraph( mdesc )
        print mdesc

        # Here -- emit self.csim actions
        for act in self.csim.combatActions:
            scn, hero, monster, startrule = act
            self.csim.genCombatAction( self, hero, monster, startrule )


