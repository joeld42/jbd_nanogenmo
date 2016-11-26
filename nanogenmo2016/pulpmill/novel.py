import os, sys
import random

import tracery
from tracery.modifiers import base_english

from pulpmill import world, scene, storygen, character, utils, quest


title_rules = {
    'origin' : ['#a_conflict# #preposition# #desc_context#', '#a_and_b#',
                'the #desc_context#'],

    'a_and_b' : [ 'the #context# and the #desc_context#', 'of #context# and #context#',
                  '#context# and #context#'],

    'conflict' : ['war', 'battle', '#weather#', 'shadow', 'king', 'lord', 'god',
                  'trials', 'time', 'age', 'host' ],
    'a_conflict' : ['#conflict#','the #conflict#', 'a #conflict#'],
    'preposition' : ['of the', 'above the', 'through', 'amidst', 'among', 'amongst',
                     'beyond', 'against', 'from the', 'between'],
    'desc_context' : ['#context#', '#awesome# #context#'],
    'context' : ['rings', 'dragons', 'swords', 'roses', 'kingdoms',
                 'wizards', 'sorcerers', 'curses', 'spells', '#season#',
                 '#barren# lands', 'dungeons', 'fortresses', 'enchantresses',
                 'queens', 'kings'],

    'awesome' : ['lost', 'mighty', 'forgotten', 'purple', 'heavenly', '#number#',
                 'undead', 'unholy', 'cursed', 'hidden', 'false',
                 'royal', 'promised', 'forgotten', '#season#', 'golden' ],
    'number' : ['two', 'three', 'seven', 'nine', 'hundred'],
    'weather' : ['storm', 'thunder', 'lightning'],
    'season' : ['spring', 'summer', 'winter', 'autumn', 'night', 'dawn' ],
    'barren' : ['broken', 'barren', 'burning', 'auburn']
}


class Novel(object):

    def __init__(self, cultures):
        self.cultures = cultures
        self.scenes = []

    def generate(self):

        self.sg = storygen.StoryGen()

        self.map = world.World( self.cultures, self.sg )
        self.map.buildMap()

        # Main character
        firstNode = self.map.storyPath[0]
        self.protag = character.Character( firstNode )
        self.protag.tag = 'protag'

        self.party = []

        commonRules = self.sg.getCommonRules( firstNode )
        # print "Common Rules:"
        # kk = commonRules.keys()
        # kk.sort()
        # for k in kk:
        #     print k, "-> ", commonRules[k]
        #
        # print "Season is ", self.sg.season

        # sceneRules = {
        #     'origin' : '#weather_sentence.capitalize#'
        # }
        # sceneRules.update( commonRules )

        # grammar = tracery.Grammar( sceneRules )
        # grammar.add_modifiers( base_english )
        # for i in range(10):
        #     print str(i+1)+".", grammar.flatten( "#origin#")
        #
        # sys.exit(1)


        self.scenes += scene.sceneNormalLife( firstNode, self.protag )

        if (utils.randomChance(0.5)):
            self.scenes += scene.scenePlaceDesc( firstNode, self.protag )

        # Scramble the prologue scenes
        random.shuffle( self.scenes )

        incitingIncident = scene.sceneIncitingIncident( firstNode, self.protag )
        self.scenes += incitingIncident

        # After this is the first point we can add new characters
        addCharIndex = len(self.scenes)

        # Walk the story path to generate scenes
        lastNode = None
        for item in self.map.storyPath:
            if isinstance(item,world.TerrainNode):

                if item.city:
                    self.scenes += scene.sceneCity( item, self.protag )
                    lastNode = item

                else:
                    # TODO encounter nodes
                    pass

            elif isinstance(item,world.TerrainArc):

                if item.arcType == world.TerrainArc_SEA:
                    self.scenes += scene.sceneSeaVoyage(  lastNode, item )


        self.currParty = [ self.protag ]


        # Add/Remove characters from the party
        addCooldown = 0
        maxChars = 5
        while addCharIndex < len(self.scenes):
            currScene = self.scenes[addCharIndex]

            if (addCooldown==0 and utils.randomChance(0.5) and
                    currScene.node and currScene.node.city and
                        len(self.currParty)<maxChars):
                addCooldown = 3

                print "currScene is ", currScene.desc, currScene.chapterTitle
                addCharScenes = scene.sceneAddCharacter( currScene.node, self.map )

                self.scenes[addCharIndex+1:addCharIndex+1] = addCharScenes

                for c in addCharScenes:
                    self.currParty += c.newChars

            # if chatCooldown==0 and len(self.currParty)>=2 and utils.randomChance(0.9):
            #
            #     convoScenes = scene.sceneDialogueFiller( currScene.node )
            #     self.scenes[addCharIndex+1:addCharIndex+1] = convoScenes
            #
            #     chatCooldown = 4


            addCharIndex += 1
            if addCooldown > 0:
                addCooldown -= 1


        # TODO: Here add fight scenes and run battle simulations

        # Update party track
        party = [ self.protag ]
        for scn in self.scenes:
            print "SCENE: %s -- %d in party, %d new" % ( scn.desc, len(party), len(scn.newChars) )
            scn.party = party[:]
            party += scn.newChars


        # Add a bunch of filler scenes
        chatCooldown = 0
        fillerSceneIndex = 0
        while fillerSceneIndex < len(self.scenes):
            currScene = self.scenes[fillerSceneIndex]

            if chatCooldown==0 and len(currScene.party)>=2 and utils.randomChance(0.9):
                convoScenes = scene.sceneDialogueFiller( currScene.node )

                for scn in convoScenes:
                    scn.node = currScene.node
                    scn.party = currScene.party

                self.scenes[fillerSceneIndex+1:fillerSceneIndex+1] = convoScenes

                chatCooldown = 4

            fillerSceneIndex += 1
            if chatCooldown > 0:
                chatCooldown -= 1


        # Add quest scenes to each dungeon
        for scn in reversed(self.scenes):
            if scn.node.city and scn.node.city.dungeon:
                scn.lastDungeon = True
                break

        dungeonIndex = 0
        while dungeonIndex < len(self.scenes):

            currScene = self.scenes[dungeonIndex]
            if currScene.node.city and currScene.node.city.dungeon and not currScene.node.city.quest:

                # It's a dungeon, add a quest and backfill the quest scenes
                qq = quest.Quest( currScene.node.kingdom.culture )
                print "GEN QUEST FOR DUNGEON", dungeonIndex, currScene.node.city.name
                currScene.node.city.quest = qq
                qq.destCity = currScene.node

                finishQuestScenes = scene.sceneFinishQuest( qq, currScene.node, party )

                for s in finishQuestScenes:
                    s.party = currScene.party[:]

                self.scenes[dungeonIndex+1:dungeonIndex+1] = finishQuestScenes

                # Precede with combat scenes
                fightScenes, deadHeros = scene.generateCombatScenes( currScene.party, 1, currScene.node )
                for s in fightScenes:
                    s.party = currScene.party[:]
                self.scenes[dungeonIndex+1:dungeonIndex+1] = fightScenes

                # Walk forward and remove dead heros
                for index in range(dungeonIndex+1, len(self.scenes)):
                    s = self.scenes[index]
                    for dh in deadHeros:
                        if dh in s.party:
                            s.party.remove( dh )

                # Start this quest sometime earlier
                if (currScene.lastDungeon):
                    # give the quest to the inciting incident
                    incitingIncident[0].quest = qq
                    print "Will be main quest"
                    qq.startCity = incitingIncident[0].node
                else:

                    if dungeonIndex > 1:
                        startIndex = random.randint( 1, dungeonIndex-1 )
                    else:
                        startIndex = 1

                    startScene = self.scenes[startIndex]
                    startQuestScenes = scene.sceneStartQuest( qq, startScene.node, currScene.node, startScene.party )
                    qq.startCity = startScene.node

                    for s in startQuestScenes:
                        s.party = startScene.party

                    self.scenes[startIndex+1:startIndex+1] = startQuestScenes

                # Now add some "quest reminder scenes" between start and end
                remindIndex = startIndex+1
                remindCooldown = random.randint(3,6)
                while remindIndex < len(self.scenes):
                    scn = self.scenes[remindIndex]
                    if scn is finishQuestScenes[0]:
                        break

                    if remindCooldown==0 and utils.randomChance(0.3):
                        # add reminder scene
                        remindQuestScenes = scene.sceneRemindQuest( qq, scn.node, currScene.node, scn.party )
                        for s in remindQuestScenes:
                            s.party = scn.party
                        self.scenes[remindIndex+1:remindIndex+1] = remindQuestScenes
                        remindCooldown = random.randint(3,5)
                    elif remindCooldown > 0:
                        remindCooldown -= 1

                    remindIndex += 1

            dungeonIndex += 1


        # Last, generate the title. Right now this is random but it would
        # be cool to use some info from the story
        self.title = self.genTitle()

        # Do some sanity checks
        for scn in self.scenes:
            if scn.node is None:
                print "SCENE MISSING NODE: ", scn, scn.desc, scn.chapterTitle, scn.party
                sys.exit(1)

    def dbgPrint(self):

        print "Novel: ", self.title
        print "Setting Info: "
        self.map.dbgPrint()

        print "---- PARTY ", len(self.currParty), "-----"
        for p in self.currParty:
            print "  ",p.name, "a", p.rpgClass.rpgClass, "from", p.hometown.name


        print "---- SCENES: -------"

        wordCountTot = 0
        for scn in self.scenes:
            scn.doGenerate( self.sg )
            wordCountTot += scn.wordCount

            print "-", scn.desc, "("+scn.chapterTitle, scn.wordCount, "words)"
            partyNames = map( lambda x: x.name, scn.party )
            print "  ", ', '.join( partyNames )
            for pp in scn.storyText:
                print pp
                print



        wordCountAvg = 50000 / len(self.scenes)
        print "Total word count", wordCountTot
        print "For a 50K novel, each scene would need to be approx ", wordCountAvg, "words."

        print "--- Kingdoms ---"
        for k in self.map.kingdoms:
            print k.name, "   Popular Fruits:", k.fruits


    def genTitle(self):
        grammar = tracery.Grammar( title_rules )
        grammar.add_modifiers( base_english )
        title = grammar.flatten( "#origin#").title()

        return title