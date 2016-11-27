import os, sys

import tracery
from tracery.modifiers import base_english
import utils
import random

HUMANOID_MOVEMENTS = [
    "walked", "strode", "stepped", "jumped", "ran", "shuffled"
]

MONSTER_DICT = {
    "rat" : {
        "name" : [ "rat", "capybara", "rodent", "dire nutria" ],
        "tags" : [ "animal" ],
        "leader" : [ "Giant Rat", "RatKing", "Rattus"],
        "rules": {
            "m_moved" : ["scurry", "dart", "scamper" ],
            "m_attacked" : [ "bit", "scratched", "gnawed", "nibbled" ],
            "m_sound" : [ "hissed", "chittered", "squeaked", "scritched"],
            "m_part" : [ "head", "ear", "body", "leg", "nose", "tail"]
        },
    },

    "skeleton" : {
        "name" : [ "skeleton" ],
        "tags" : [ "humanoid" ],
        "leader" : [ "Lich", "Skeleton King"],
        "rules": {
            "m_moved" : HUMANOID_MOVEMENTS + [ "clattered", 'clacked' ],
            "m_attacked" : [ "struck", "stabbed", "swung" ],
            "m_sound" : [ "chittered", "moaned", "shrieked", "clattered" ],
            "m_part" : [ "head", "skull", "ribcage", "leg", "femur", "spine"]
        },
    }

}

class MonsterInfo(object):

    def __init__(self, info, leader ):

        self.info = info
        self.leader = leader
        if (self.leader):
            self.hp = 3
        else:
            self.hp = random.randint(1,2)

        # fill in some specifics
        if leader:
            self.name = random.choice( self.info['leader'])
        else:
            self.name = random.choice( self.info['name'])

class CombatSimulator(object):

    def __init__(self, party, level, node ):

        self.level = level
        self.party = party
        self.monsters = []

        self.deadHeros = []

    def setupFight(self, node, party ):


        monsterTypes = MONSTER_DICT.keys()
        monsterInfo = random.choice( monsterTypes )

        numMonsters = random.randint( 2, 3 )
        self.monsters = []
        first = True
        totalhp = 0
        while (len(self.monsters) < numMonsters):
            m = MonsterInfo( MONSTER_DICT[monsterInfo], first )
            totalhp += m.hp
            first = False

            self.monsters.append( m )

        # Reset party HP
        totalhp += 2
        partyHP = min( totalhp / numMonsters, 3 )
        print "partyHP is ", partyHP
        for h in party:
            h.hp = partyHP

        self.combatActions = []

    def pushCombatAction(self, scn, hero, monster, startrule ):

        if (isinstance(hero, list)):
            heroName = str(map(lambda x: x.name, hero ))
        else:
            heroName = hero.name
        #print "DBG", heroName, startrule, str(monster)

        #print "pushCombatAction", heroName, monster.info['name'], startrule

        self.combatActions.append( ( scn, hero, monster, startrule) )

    def genCombatAction(self, scn, hero, monster, startrule ):

        rules = scn.sceneRules.copy()
        if (isinstance(hero, list)):
            # special case for multiple dead heros
            heroNames = map( lambda x: x.name, hero )
            a = ", ".join( heroNames[:-1])
            b = heroNames[-1]
            heroRules = { "heroNames" : a + " and " + b }
        else:
            heroRules = hero.getCharacterRules( "hero")

        rules.update( heroRules )

        # hero combat rules
        rules.update({
            "hero_dead" : ["#heroName# crumpled to the floor. #heroThey.capitalize# looked dead.",
                           "#heroName# staggered, and tumbled to the #ground#.",
                           "#heroName# collapsed.", "#heroName# was slain.",
                           "#heroName# met #heroTheir# demise.",
                           "#heroName# fell to the #ground#, #heroTheir# breath came in ragged bursts."
                           ],
            "hero_revive" : ["#heroName#'s body twitched. #heroThey.capitalize# was still alive!.",
                             "There was a groan from #heroName#. #heroThey# staggered to #heroTheir# feet.",
                             "#monsterName.capitalize# #m_moved# across the #ground#, #m_moved# over #heroName#'s prone body. " +
                             "#heroName# groaned, and turned, and reached out for #monsterName#.",
                             "#heroName# coughed, and rose to #heroTheir# feet",
                             "But #heroName# was still alive! #monsterName.capitalize# #m_sound# and turned to face #heroName#."
                             ],

            "was_dead" : [ "was dead", "had fallen", "was gone", "was cold"],
            "the_party" : [ "everyone", "the party", "the group", "all of them"],
            "everyone_sad" : [
                "The party hung their heads in the #weather_air#.",
                "A mournful silence hung in the #weather_air#",
                "#the_party.capitalize# was consumed with sadness"
            ],
            "mourn_hero" : ["#heroName# #was_dead#. #everyone_sad#"],

            "burial" : [ "#protagName# built a crude cairn from scattered #natureThing.s#.",
                         "#protagName# built a pyre and they all watched the flames in silence. #moodLighting#."],
            "mourn_multiple" : ["#heroNames# were all dead. #everyone_sad#.",
                                "#monsterName.capitalize# and it's ilk were slain, but at a steep cost. "+
                                "#heroNames# had all fallen. #burial#"
                                ]
        })

        # add monster rules
        monsterRules = {
            "m_name" : monster.name,
        }
        monsterRules.update( monster.info['rules'])

        rules.update( monsterRules )

        # Add combat rules
        if not monster.leader:
            # underling monster
            monsterBaseRules = {
                "monsterName" : "#m_name.a#"
            }
        else:
            monsterBaseRules = {
                "monsterName" : "the #m_name#"
            }
        rules.update( monsterBaseRules )

        combatRules = {
            "killed" : [ "had killed", "killed", "had slain", "slew", "dispatched", "vanquished",
                         "finished"],
            "monster_hit" : [ "#monsterName.capitalize# hit #heroName#." ],
            "monster_miss" : [ "#monsterName.capitalize# attacked #heroName#, but missed." ],
            "monster_dead" : [ "#monsterName.capitalize# fell to the #ground#, dead.",
                               "#monsterName.capitalize# was slain.",
                               "#heroName# had killed #monsterName#.",
                               "#heroName# #killed# #monsterName#.",
                               "#heroName# loosed a cry of rage and #killed# #monsterName#.",
                               "#heroName# was calm as #heroThey# #killed# #monsterName#."
                               ],

            "hero_hit" : [ "#heroName# hit #monsterName#.", "#attack#, and hit the #m_part#.",
                           "#attack#.", "#attack#, #monsterName# was gravely injured.",
                           "#attack#. It was super effective.", "#heroName# had the upper hand. #attack#.",
                           "#attack#. #attack#.", "#attack# and it met bone.",
                           "#attack#, it was devestating.", "#heroName# showed no mercy, #attack#",
                           "With fierce ferocity, #attack#.", "The bloody tide of battle rose and #attack#",
                           "#heroName# struck #monsterName#.",
                           "It took mere instants, but #legends# would tell of the next moment for #long_time#: #attack#."
                           ],
            "hero_miss" : [ "#heroName# attacked #monsterName#, but missed." ],

            "combat_filler" : ["#heroName# and #monsterName# circled each other, almost as a dance.",
                                "#heroName# ducked near a #natureThing#, and readied #heroTheir# #weapon#",
                            "#moodLighting#",
                            "#heroName# paced on the #weather_ground_stuff#.",
                            "#heroName#'s #weapon# #weather_air_verb# through the #weather_air#.",
                            '"#silly_exclaim.capitalize#," groaned #heroName#, "to be back in #heroHome#."//',
                            '"I should have stuck to being a #heroJob#," #said# #heroName#.//'
                               ]}
        rules.update( combatRules )

        grammar = tracery.Grammar( rules  )
        grammar.add_modifiers( base_english )

        pp = grammar.flatten( startrule )
        print "combatAction: ", pp
        scn.growParagraph( pp )

    def combatFiller(self, scn):

        activeHeros = filter( lambda x: x.hp > 0, self.party)
        activeMonsters = filter( lambda x: x.hp > 0, self.monsters)

        if activeHeros and activeMonsters:
            hero = random.choice( activeHeros)
            monster = random.choice( activeMonsters )
            self.pushCombatAction( scn, hero, monster, "#combat_filler#")


    def stepCombat(self, scn ):

        print "Combat step ----"


        # party inititive
        activeHeros = filter( lambda x: x.hp > 0, self.party)
        activeMonsters = filter( lambda x: x.hp > 0, self.monsters)

        actors = activeHeros + activeMonsters

        random.shuffle( actors )
        for actor in actors:
            if isinstance(actor, MonsterInfo):

                #print "Monster ", actor.info['name'], 'turn'
                # pick a party member to attack
                hero = random.choice( activeHeros )

                if utils.randomChance( 0.5 ):
                    # Monster hits hero
                    self.pushCombatAction( scn, hero, actor, "#monster_hit#")
                    hero.hp -= 1

                    if hero.hp == 0:
                        self.pushCombatAction( scn, hero, actor, "#hero_dead#")
                        activeHeros.remove( hero )

                        if not len(activeHeros):
                            # All heros dead, that's not good. Make all of them
                            # wake up dramatically...
                            first = True
                            for h in self.party:
                                if first or utils.randomChance(0.5):
                                    self.pushCombatAction( scn, h, actor, "#hero_revive#")
                                    h.hp = 3
                                first = False

                            return False

                else:
                    # Miss hero
                    self.pushCombatAction( scn, hero, actor, "#monster_miss#")
                    return False

            else:
                # It's a character
                #print "Actor", actor.name, "turn"
                monster = random.choice( activeMonsters )

                if utils.randomChance( 0.75 ):
                    # Hero hits monster
                    self.pushCombatAction( scn, actor, monster, "#hero_hit#")
                    monster.hp -= 1

                    if monster.hp==0:
                        self.pushCombatAction( scn, actor, monster, "#monster_dead#")
                        activeMonsters.remove( monster )

                        if not len(activeMonsters):
                            #print "All Monsters killed"

                            # If the protag is incapacitated, revive here
                            if not self.party[0].hp:
                                self.pushCombatAction( scn, self.party[0], monster, "#hero_revive#")
                                self.party[0].hp = 3

                            # Count up who died
                            deadHeros = filter( lambda x: x.hp == 0, self.party)

                            if (len(deadHeros) == 1):
                                self.pushCombatAction( scn, deadHeros[0], monster, "#mourn_hero#")
                            elif len(deadHeros) > 1:
                                self.pushCombatAction( scn, deadHeros, monster, "#mourn_multiple#")

                            self.deadHeros = deadHeros

                            return True
                else:
                    # Hero misses monstar
                    self.pushCombatAction( scn, actor, monster, "#hero_miss#" )
                    return False










