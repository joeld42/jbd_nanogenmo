import os, sys
import random

QuestType_DESTROY_ITEM  = "destroy"
QuestType_RETRIEVE_ITEM = "retrieve"

class Quest(object):

    def __init__(self, culture):

        self.culture = culture
        self.item, self.itemtags = culture.genMacGuffin()

        self.questType = random.choice([ QuestType_DESTROY_ITEM, QuestType_RETRIEVE_ITEM ])
        self.desc =  self.questType.title() + " the " + self.item

        self.startPhrase, self.finishPhrase = self.getPhrases()

        self.startCity = None
        self.destCity = None

    def getPhrases(self):

        if self.questType == QuestType_DESTROY_ITEM:
            questPairs = [
                (
"""
The #questGiver# leaned close and whispered, "There is a great forge and
golden anvil built into the walls at #cityname#. Use it. It can destroy
the #questItem#."
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
                )
            ]
        elif self.questType == QuestType_RETRIEVE_ITEM:
            questPairs = [
                (
"""
Placeholder: Hey #protagName#, go find the #questItem#. It's in #destCity#.
""",
"""
Placeholder: There it was. The #questItem#. #protagName# picked it up.
"""
                )
            ]

        return random.choice( questPairs )






