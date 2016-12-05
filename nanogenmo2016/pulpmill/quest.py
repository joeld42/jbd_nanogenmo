import os, sys
import random

# This is probably the least generative part of this whole thing

QuestType_DESTROY_ITEM  = "destroy"
QuestType_RETRIEVE_ITEM = "retrieve"

class Quest(object):

    def __init__(self, culture):

        self.culture = culture
        self.item, self.itemtags = culture.genMacGuffin()

        self.questType = random.choice([ QuestType_DESTROY_ITEM, QuestType_RETRIEVE_ITEM ])
        self.desc =  self.questType.title() + " the " + self.item

        self.startPhrase, self.finishPhrase = self.getPhrases()
        self.startPhrase = "#questGiverIntro# " + self.startPhrase

        self.startCity = None
        self.destCity = None

        # quest giver rules
        questGiverRulesCommon = {
              "placeDesc" : [ "ramshackle", "dilapidated", "cozy", "wood-paneled",
                              "fabric-walled", "quilted", "patchwork", "ornamented"],
        }

        questGiverRules = random.choice([

            # old gypsy -------------
            { "questGiver" : "old gypsy",
              "questGiverAction" : [ 'flipped a line of Tarot cards',
                                     'lit a stick of incense that smelled of #kfruit#',
                                     'lit a candle', 'put out a candle',
                                     'stared into a crystal ball'],
              "gypsyPlace" : ["#placeDesc# caravan", "#placeDesc# hut"],
              "questGiverIntro" :
'''
They passed a #gypsyPlace#. A voice from within said "#protagName#...". #protagThey# looked up
 and peeked inside. A smokey fire burned in the hearth. Within, an old gypsy woman was hunched
 over a small table.//
'''
            },

            # witch -------------
            { "questGiver" : "witch",
              "questGiverAction" : [ 'shooed a rat away',
                                     'gazed into the sockets of a yellowing skull',
                                     'stirred some entrails with her knotted finger',
                                     'stirred a potion', 'sipped a noxious tea'
                                     ],
              "witchPlace" : ["#placeDesc# cavern", "#placeDesc# hut", "#placeDesc# warren"],
              "questGiverIntro" :
'''
Outside the town, there was a small #witchPlace#. #protagName# felt drawn inside. Within, there
 was a gnarled witch. The air smelled #weather_adj#. "Ah, #protagName#, I have been expecting you for
 #long_time#," the old witch #said#. "I have a favor to ask..."//
'''
            },

            # courier -------------
            { "questGiver" : "slain courier",
              "questGiverAction" : [ 'coughed up a plume of blood',
                                     'groaned and clutched his wound',
                                     'slumped, then weakly clung to life'
                                     ],
              "questGiverIntro" :
'''
They walked through the market. Suddenly, a young man pushed past, running frantically,
knocking over a crate of #kfruit#. #protagName# turned and saw a hooded form clad in
black leather armour chasing him. The assassin snapped an arrow from a crossbow and
it struck the courier, who fell over his feet to the #ground# like a sack of potatoes.//
The assassin vanished into the crowd. #protagName# rushed to the side of the fallen
courier.//
'''
            },

            # wizard -------------
            { "questGiver" : "old wizard",
              "questGiverAction" : [ 'finished his tankard and called for another',
                                     'shook his head with sad rememberance',
                                     'tugged on his beard',
                                     'cried into his whiskey'
                                     ],
              "bondingStuff" : [
                  "As it turned out, the old wizard was also from #protagHome#.",
                  "They lamented about lost loves and better times.",
                  '"My lord said he wanted to make #kingdomname# great again," he #said#, "but it was all a big con".',
                  '"I am near the end of my journey," the mage lamented, "but you remind me of my younger self."',
              ],
              "questGiverIntro" :
'''
#protagName# stopped into a tavern for some refreshment. The only open seat
was beside an old wizard in auburn robes. #protagName# took a seat and after
a while they started talking. #bondingStuff# #protagName# seemed to gain the
old wizard's trust.//
'''
            },

            # bandits -------------
            { "questGiver" : "nobleman",
              "questGiverAction" : [ 'apologised profusely', 'pressed coins into #protagName#\'s hand',
                                     'muttered about bandits', 'promised them great rewards',
                                     'offered to hire the group as bodyguards, but they declined'
                                     ],
              "questGiverIntro" :
'''
On a rutted #ground# road outside of town, the party was discussing if
they should make camp. A heavy coach thundered past them, painted with
bright purples and gilded trim. "Well," said #aliceName#, "That's the way
to travel, eh?"//
But as it neared the corner, a band of highwaymen rushed out from the trees.
They stopped the coach and forced the occupant, a portly gentleman in velvet
finery, out onto the rough #ground#.//
The group spring into action. #protagName# disarmed the lead robber and the
rest scattered. #protagName# knelt by the nobleman, who was professing his
gratitude.
'''
            },

        ])

        questGiverRules.update( questGiverRulesCommon )

        self.questGiverRules = questGiverRules

    def getReminder(self):

        remindPhrases = [
            "#protagName# thought about the #questItem#, and all the trouble it had brought into "+
                "#protagTheir# life. Soon, this would be over.",

            "#protagName# thought about the #questItem#. #protagThey.capitalize# was sure they would reach #destCity#."
        ]

        if self.questType==QuestType_DESTROY_ITEM:
            remindPhrases += [
                "#protagName#'s fingers wandered to the #questItem#. It felt heavy to #protagThem#, "+
                "heavier than it should be.",

                "#protagName# would be glad when #questItem# was destroyed."
            ]
        elif self.questType==QuestType_RETRIEVE_ITEM:
            remindPhrases += [
                "The #questItem#. That would fix this. #protagName# felt sure of this.",
                "If only they had the #questItem#.",
                    ]

        return random.choice( remindPhrases )

    def getPhrases(self):

        if self.questType == QuestType_DESTROY_ITEM:
            questPairs = [(
"""
The #questGiver# handled #protagName# a bundle of cloth. #protagThey.capitalize#
slowly unwrapped it. "This is #questItem#", the #questGiver# #said#.
"It is most evil and most be destroyed."//
The #questGiver# leaned close and whispered, "There is a great forge and
golden anvil built into the walls at #destCity#. Use it. It can destroy
the #questItem#." The #questGiver# #questGiverAction#.
""",
"""
#protagName# reached the anvil. The forge glowed red-hot even though it was
abandoned for #long_time#. #protagThey.capitalize# set the #questItem# on the shining
anvil. #protagThey# picked up the hammer. It was massive, but seemed to
weigh no more than a #kfruit#. #protagName# yelled, screamed out an
intense cry, venting all #protagTheir# frustration and hopes and fears
at the world and let the hammer ring against the stone. The #questItem#
was unchanged. #protagThey.capitalize# struck again. It seemed to flex, to wobble.
And finally the #questItem# shattered, splitting into a #thousand# pieces.
"""
                ), (
"""
"Take this", said the #questGiver#, holding out something with shaking hands. #protagName#
took the offered item.//"This is the #questItem#", the #questGiver# #said#. "It is powerful
 but cursed. Only the magic fire at #destCity# can destroy it. Go there, and destroy it,
 for your own sake and for the sake of all of #kingdomname#."//
""",
"""
 They came to an inner room, covered with arcane ruins. From a circle etched into
 the center of the floor, a column of shimmering energy pulsed and swayed. "This
 must be the magic fire that the #questGiver# spoke of," whispered #aliceName#.//
 #protagName# nodded. #protagThey# raised the #questItem# and it seemed to jump from
 #protagTheir# hands, into the gout of #purple# fire. It flared up into a shower
 of magical sparks, and an instant later, was gone.
"""
                ), (
"""
 "Over there", gestured the #questGiver#, "in that basket." The #questGiver#
  #questGiverAction#. #moodLighting# "That is the #questItem#, and it is how
  I gained and lost my fortune. But it is an evil thing. Please, I beg of you,
  take it to #destCity# and there you will find a well so deep as to have no
  bottom. Drop it into the well and the world will be free of it. But be careful,
  as long as you carry it ill luck will befall you." #questGiverAction#
""",
"""
 In the deepest part of #destCity#, they reached the well and stared into
 the abyss. It truly seemed to have no bottom. #protagName# held out the
 #questItem# above the brink.//
 "We should keep it," suggested #aliceName#, "we can learn to use its power."//
 "We cannot," said #protagName#, and dropped the #questItem#. "No mortal could."
 #moodLighting#
"""
                )
                , (
"""
 "I am the last of a once-proud people," said the #questGiver#.//
 "What happened?" asked #protagName#.//
 "This. This happened," said the #questGiver# and from their robes produced
 a small object. "This is the #questItem#," the #questGiver# said, "it is responsibile
 for the fall of my people, and I have pledged to destroy it. But I fear I cannot
 complete my quest any longer. It need to be brought to where it was created, the
 dark alter at #destCity#, and there its magic will be rendered powerless. This
 burden, I'm afraid, falls to you now, #protagName#."//
 The #questGiver# #questGiverAction#. #protagName# took the #questItem#
 with shaking hands.
""",
"""
 The reached the innermost chamber of the #destCity#. There was an alter, it
 was not much more than a chisled block of stone, but the air around it crackled
 with magic and felt heavy and oppressive. #moodLighting#//
 #protagName# set #questItem# down on the crude alter and at once it began
 to glow with eldrich power. It crackled and fizzled until it was no more
 than a ordinary ornament.//
 "Let's go," said #protagName#, and turned towards the fading sunlight.//
 #aliceName# grabbed the #questItem#, now inert and lifeless. "What?" #aliceThey#
 shrugged, "it's for my knick-knack shelf.".
"""
                )
            ]
        elif self.questType == QuestType_RETRIEVE_ITEM:
            questPairs = [
                (
                    # Map ---------
"""
 "Here!" said the #questGiver#, and thrust a ragged, crumbling map into
 #protagName#'s hand. #protagThey# looked it over.//
 "#destCity#?", #protagName# wondered aloud. "I thought that was just a legend."//
 "Oh, no", whispered the #questGiver#, "it's no legend. And the #questItem# is there."//
 #protagName# nodded with understanding.
""",
"""
 #protagName# consulted the old map they had got from the #questGiver#.//
 "This must be the place," #protagThey# murmured.//
 "There's nothing here," said #aliceName#, exasperated.//
 "No, look, there," said #protagName# as #protagThey# moved a flagstone
 aside. Beneath it was a small chamber, barely large enough for a #critter#, and
 contained within was #questItem#.//
 "I don't believe it," #said# #aliceName#. They had found it. They found
 the #questItem#.
"""
                ), # Grave Robbers ---------
                (
"""
 "I will tell you a great secret," said the #questGiver#.//
 "Why?" asked #protagName#, "would you tell me this?"//
 "Isn't it obvious?" grinned the #questGiver#. #questGiverAction#. "In
  #destCity#, there is the grave of a lost king. Buried with him is
  the #questItem#."//
  "We are not grave robbers," said #protagName#.//
  "Aren't you?" the #questGiver# squinted, "and besides, how do you think
  this dead king got the #questItem# in the first place."//
  #protagName# pondered the story, and pondered the #questItem#.
""",
"""
 The grave was there, deep in #destCity#, just as the #questGiver# had
 foretold. #aliceName# pried off the lid of the sarcophagus. Inside,
 resting on a web of bones and tight-stretched skin wrapped in rusting
 armour, was the #questItem#. It looked untouched by time.//
 #aliceName# hesitated.//
 "This is no time to be squeamish", said #protagName#, and #protagThey
 reached into the grave and drew out the #questItem#. It glowed softly
 with a mystical energy.
"""
                ), # Spirit World ---------
                (
"""
 "I can see between the worlds of the living and the dead," intoned the #questGiver#.//
 "What?", #protagName# recoiled.//
 "It's the #questItem#. It haunts my dreams and has warped my sight. You can
 find it in #destCity#. But beware, because it is well guarded." The #questGiver#
 #questGiverAction#.//
 "We will go," said #protagName#, "We shall not fail."
""",
"""
 They reached #destCity#. The walls were smeared with blood. "The #questItem# is
  here somewhere, I'm sure of it," said #aliceName#.//
  "We've searched this whole ruin," sighed #protagName#. I think the #questGiver#
  was lying to us.//
  "Wait," said #aliceName#, "It wasn't a lie. I sense something." #aliceThey.capitalize#
  shut #aliceTheir# eyes and pushed aside a gargoyle to reveal a hidden chamber. Inside,
  on a starry plinth, was the #questItem#.//
  "We have it," mused #protagName#, hefting the #questItem# in his hand, "but I can't
   help but think it was not worth the price we paid."//
   They made their way in silence back out to the #natureThing#
   where the horses were tied. #moodLighting#
"""
                ), # Keyhole ---------
                (
"""
 "Have you heard of the #questItem#?" asked the #questGiver#.//
 "Of course," said #protagName#, "but that's just a story told to children."//
 "It's no story," said the #questGiver#. The #questGiver# paused, #questGiverAction# and
  whispered, "It's real, and it's in #destCity#. Take this key."//
  The #questGiver# pressed a tiny key into #protagName#'s hand.
""",
"""
 "Here!" called #aliceName#, and pointed at a blank space on the wall. The stonework
 was interrupted by a square of white marble. In the center was a tiny keyhole.//
 #protagName# raised the tiny brass key from the #questGiver# to the keyhole.
 #protagThey.capitalize# turned the tiny key and the marble square pivoted open. From a
 small space inside #protagThey# draw the #questItem#. It sparkled in the #weather_adj#
 air.//
 "Well," said #aliceName#, "we have what we came for. Let's get out of here and
 find a tavern."
"""
                )
            ]

        return random.choice( questPairs )






