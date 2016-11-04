import os, sys

class Scene(object):

    def __init__(self):

        self.desc = "Empty Scene"
        self.characters = {}

        self.chapterTitle = "Chapter Title"

        self.regionRules = []
        self.sceneRules = []

        # todo: events

        self.storyText = []

    def addLocationRules(self, node ):

        pass

    def generate(self):
        """
        Fills in storyText and chapterTitle
        """
        pass

