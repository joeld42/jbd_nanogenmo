import os, sys
import random, string

import tracery
from tracery.modifiers import base_english

from pulpmill import world, scene, storygen, character, utils, quest


title_rules = {
    'origin' : ['#title#'],

    'title' : ['#a_conflict# #preposition# #desc_context#', '#a_and_b#',
                'the #desc_context#'],

    'subtitle' : [ 'book #num# of #series#', '#sequel_stmt#',
                   'the #epic# #journey# of #protagName# the #protagClass#'],
    'sequel_stmt' : [ 'The #super# #sequel# to "#title#"',
                   'The #sequel# to the #super# #novel# "#title#"' ],
    'super' : ['long-awaited', 'bestselling', 'enchanting', 'award-winning'],
    'novel' : ['novel', 'masterpiece', 'saga'],
    'epic' : ['epic', 'amazing', 'enthralling', 'exciting'],
    'sequel' : ['sequel', 'follow-up', 'conclusion', 'prequel', 'predecessor'],
    'series' : [ 'the #desc_context# #saga#'],
    'saga' : ['saga', 'series', 'cycle', 'chronicles'],
    'journey' : ['journey', 'voyage', 'adventure'],
    'num' : [ '2', '3', '5', '7', 'one', 'two', 'three', 'four', 'five',
              'six', 'seven', 'nine', 'fifteen', 'twelve',
             'II', 'III', 'IV' ],
    'protagName' : 'a hero',
    'protagClass' : 'adventurer',

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

LAST_NAMES  = [ "Smith","Johnson","Williams","Jones","Brown","Davis","Miller","Wilson","Moore","Taylor",
"Anderson","Thomas","Jackson","White","Harris","Martin","Butcher","Thompson","Garcia","Martinez","Robinson",
"Clark","Rodriguez","Lewis","Lee","Walker","Hall","Allen","Young","Hernandez","King","Wright",
"Lopez","Hill","Scott","Green","Adams","Baker","Gonzalez","Nelson","Carter","Mitchell","Perez",
"Roberts","Turner","Phillips","Campbell","Parker","Evans","Edwards","Collins","Stewart","Sanchez",
"Morris","Rogers","Reed","Cook","Morgan","Bell","Murphy","Bailey","Rivera","Cooper","Richardson",
"Cox","Howard","Ward","Torres","Peterson","Gray","Ramirez","James","Watson","Brooks","Kelly","Sanders",
"Price","Bennett","Wood","Barnes","Ross","Henderson","Coleman","Jenkins","Perry","Powell","Long",
"Patterson","Hughes","Flores","Washington","Butler","Simmons","Foster","Gonzales","Bryant","Alexander",
"Russell","Griffin","Diaz","Hayes","Myers","Ford","Hamilton","Graham","Sullivan","Wallace","Woods","Cole",
"West","Jordan","Owens","Reynolds","Fisher","Ellis","Harrison","Gibson","Mcdonald","Cruz","Marshall",
"Ortiz","Gomez","Murray","Freeman","Wells","Webb","Simpson","Stevens","Tucker","Porter","Hunter",
"Hicks","Crawford","Henry","Boyd","Mason","Morales","Kennedy","Warren","Dixon","Ramos","Reyes",
"Burns","Gordon","Shaw","Holmes","Rice","Robertson","Hunt","Black","Daniels","Palmer","Mills",
"Nichols","Grant","Knight","Ferguson","Rose","Stone","Hawkins","Dunn","Perkins","Hudson","Spencer",
"Gardner","Stephens","Payne","Pierce","Berry","Matthews","Arnold","Wagner","Willis","Ray","Watkins",
"Olson","Carroll","Duncan","Snyder","Hart","Cunningham","Bradley","Lane","Andrews","Ruiz","Harper",
"Fox","Riley","Armstrong","Carpenter","Weaver","Greene","Lawrence","Elliott","Chavez","Sims","Austin",
"Peters","Kelley","Franklin","Lawson","Fields","Gutierrez","Ryan","Schmidt","Carr","Vasquez",
"Castillo","Wheeler","Chapman","Oliver","Montgomery","Richards","Williamson","Johnston","Banks",
"Meyer","Bishop","Mccoy","Howell","Alvarez","Morrison","Hansen","Fernandez","Garza","Harvey",
"Little","Burton","Stanley","Nguyen","George","Jacobs","Reid","Kim","Fuller","Lynch","Dean","Gilbert",
"Garrett","Romero","Welch","Larson","Frazier","Burke","Hanson","Day","Mendoza","Moreno","Bowman",
"Medina","Fowler","Brewer","Hoffman","Carlson","Silva","Pearson","Holland","Douglas","Fleming",
"Jensen","Vargas","Byrd","Davidson","Hopkins","May","Terry","Herrera","Wade","Soto","Walters","Curtis",
"Neal","Caldwell","Lowe","Jennings","Barnett","Graves","Jimenez","Horton","Shelton","Barrett","O'brien",
"Castro","Sutton","Gregory","Mckinney","Lucas","Miles","Craig","Rodriquez","Chambers","Holt","Lambert",
"Fletcher","Watts","Bates","Hale","Rhodes","Pena","Beck","Newman","Haynes","Mcdaniel","Mendez","Bush",
"Vaughn","Parks","Dawson","Santiago","Norris","Hardy","Love","Steele","Curry","Powers","Schultz","Barker",
"Guzman","Page","Munoz","Ball","Keller","Chandler","Weber","Leonard","Walsh","Lyons","Ramsey","Wolfe",
"Schneider","Mullins","Benson","Sharp","Bowen","Daniel","Barber","Cummings","Hines","Baldwin","Griffith",
"Valdez","Hubbard","Salazar","Reeves","Warner","Stevenson","Burgess","Santos","Tate","Cross","Garner",
"Mann","Mack","Moss","Thornton","Dennis","Mcgee","Farmer","Delgado","Aguilar","Vega","Glover","Manning",
"Cohen","Harmon","Rodgers","Robbins","Newton","Todd","Blair","Higgins","Ingram","Reese","Cannon",
"Strickland","Townsend","Potter","Goodwin","Walton","Rowe","Hampton","Ortega","Patton","Swanson",
"Joseph","Francis","Goodman","Maldonado","Yates","Becker","Erickson","Hodges","Rios","Conner",
"Adkins","Webster","Norman","Malone","Hammond","Flowers","Cobb","Moody","Quinn","Blake","Maxwell",
"Pope","Floyd","Osborne","Paul","Mccarthy","Guerrero","Lindsey","Estrada","Sandoval","Gibbs",
"Tyler","Gross","Fitzgerald","Stokes","Doyle","Sherman","Saunders","Wise","Colon","Gill",
"Alvarado","Greer","Padilla","Simon","Waters","Nunez","Ballard","Schwartz","Mcbride","Houston",
"Christensen","Klein","Pratt","Briggs","Parsons","Mclaughlin","Zimmerman","French","Buchanan",
"Moran","Copeland","Roy","Pittman","Brady","Mccormick","Holloway","Brock","Poole","Frank",
"Logan","Owen","Bass","Marsh","Drake","Wong","Jefferson","Park","Morton","Abbott","Sparks",
"Patrick","Norton","Huff","Clayton","Massey","Lloyd","Figueroa","Carson","Bowers","Roberson","Barton",
"Tran","Lamb","Harrington","Casey","Boone","Cortez","Clarke","Mathis","Singleton","Wilkins","Cain",
"Bryan","Underwood","Hogan","Mckenzie","Collier","Luna","Phelps","Mcguire","Allison","Bridges",
"Wilkerson","Nash","Summers","Atkins","Wilcox","Pitts","Conley","Marquez","Burnett","Richard",
"Cochran","Chase","Davenport","Hood","Gates","Clay","Ayala","Sawyer","Roman","Vazquez","Dickerson",
"Hodge","Acosta","Flynn","Espinoza","Nicholson","Monroe","Wolf","Morrow","Kirk","Randall","Anthony",
"Whitaker","O'connor","Skinner","Ware","Molina","Kirby","Huffman","Bradford","Charles","Gilmore",
"Dominguez","O'neal","Bruce","Lang","Combs","Kramer","Heath","Hancock","Gallagher","Gaines","Shaffer",
"Short","Wiggins","Mathews","Mcclain","Fischer","Wall","Small","Melton","Hensley","Bond","Dyer","Cameron",
"Grimes","Contreras","Christian","Wyatt","Baxter","Snow","Mosley","Shepherd","Larsen","Hoover","Beasley",
"Glenn","Petersen","Whitehead","Meyers","Keith","Garrison","Vincent","Shields","Horn","Savage","Olsen",
"Schroeder","Hartman","Woodard","Mueller","Kemp","Deleon","Booth","Patel","Calhoun","Wiley","Eaton",
"Cline","Navarro","Harrell","Lester","Humphrey","Parrish","Duran","Hutchinson","Hess","Dorsey","Bullock",
"Robles","Beard","Dalton","Avila","Vance","Rich","Blackwell","York","Johns","Blankenship","Trevino",
"Salinas","Campos","Pruitt","Moses","Callahan","Golden","Montoya","Hardin","Guerra","Mcdowell",
"Carey","Stafford","Gallegos","Henson","Wilkinson","Booker","Merritt","Miranda","Atkinson","Orr",
"Decker","Hobbs","Preston","Tanner","Knox","Pacheco","Stephenson","Glass","Rojas","Serrano","Marks",
"Hickman","English","Sweeney","Strong","Prince","Mcclure","Conway","Walter","Roth","Maynard","Farrell",
"Lowery","Hurst","Nixon","Weiss","Trujillo","Ellison","Sloan","Juarez","Winters","Mclean","Randolph",
"Leon","Boyer","Villarreal","Mccall","Gentry","Carrillo","Kent","Ayers","Lara","Shannon","Sexton",
"Pace","Hull","Leblanc","Browning","Velasquez","Leach","Chang","House","Sellers","Herring","Noble",
"Foley","Bartlett","Mercado","Landry","Durham","Walls","Barr","Mckee","Bauer","Rivers","Everett",
"Bradshaw","Pugh","Velez","Rush","Estes","Dodson","Morse","Sheppard","Weeks","Camacho","Bean","Barron",
"Livingston","Middleton","Spears","Branch","Blevins","Chen","Kerr","Mcconnell","Hatfield","Harding",
"Ashley","Solis","Herman","Frost","Giles","Blackburn","William","Pennington","Woodward","Finley",
"Mcintosh","Koch","Best","Solomon","Mccullough","Dudley","Nolan","Blanchard","Rivas","Brennan",
"Mejia","Kane","Benton","Joyce","Buckley","Haley","Valentine","Maddox","Russo","Mcknight","Buck","Moon",
"Mcmillan","Crosby","Berg","Dotson","Mays","Roach","Church","Chan","Richmond","Meadows","Faulkner",
"O'neill","Knapp","Kline","Barry","Ochoa","Jacobson","Gay","Avery","Hendricks","Horne","Shepard",
"Hebert","Cherry","Cardenas","Mcintyre","Whitney","Waller","Holman","Donaldson","Cantu","Terrell",
"Morin","Gillespie","Fuentes","Tillman","Sanford","Bentley","Peck","Key","Salas","Rollins","Gamble",
"Dickson","Battle","Santana","Cabrera","Cervantes","Howe","Hinton","Hurley","Spence","Zamora",
"Yang","Mcneil","Suarez","Case","Petty","Gould","Mcfarland","Sampson","Carver","Bray","Rosario",
"Macdonald","Stout","Hester","Melendez","Dillon","Farley","Hopper","Galloway","Potts","Bernard",
"Joyner","Stein","Aguirre","Osborn","Mercer","Bender","Franco","Rowland","Sykes","Benjamin","Travis",
"Pickett","Crane","Sears","Mayo","Dunlap","Hayden","Wilder","Mckay","Coffey","Mccarty","Ewing",
"Cooley","Vaughan","Bonner","Cotton","Holder","Stark","Ferrell","Cantrell","Fulton","Lynn","Lott",
"Calderon","Rosa","Pollard","Hooper","Burch","Mullen","Fry","Riddle","Levy","David","Duke","O'donnell",
"Guy","Michael","Britt","Frederick","Daugherty","Berger","Dillard","Alston","Jarvis","Frye",
"Riggs","Chaney","Odom","Duffy","Fitzpatrick","Valenzuela","Merrill","Mayer","Alford","Mcpherson",
"Acevedo","Donovan","Barrera","Albert","Cote","Reilly","Compton","Raymond","Mooney","Mcgowan",
"Craft","Cleveland","Clemons","Wynn","Nielsen","Baird","Stanton","Snider","Rosales","Bright",
"Witt","Stuart","Hays","Holden","Rutledge","Kinney","Clements","Castaneda","Slater","Hahn","Emerson",
"Conrad","Burks","Delaney","Pate","Lancaster","Sweet","Justice","Tyson","Sharpe","Whitfield","Talley",
"Macias","Irwin","Burris","Ratliff","Mccray","Madden","Kaufman","Beach","Goff","Cash","Bolton",
"Mcfadden","Levine","Good","Byers","Kirkland","Kidd","Workman","Carney","Dale","Mcleod","Holcomb",
"England","Finch","Head","Burt","Hendrix","Sosa","Haney","Franks","Sargent","Nieves","Downs",
"Rasmussen","Bird","Hewitt","Lindsay","Le","Foreman","Valencia","O'neil","Delacruz","Vinson",
"Dejesus","Hyde","Forbes","Gilliam","Guthrie","Wooten","Huber","Barlow","Boyle","Mcmahon",
"Buckner","Rocha","Puckett","Langley","Knowles","Cooke","Velazquez","Whitley","Noel","Vang"
]

author_rules = {
    'origin' : [ '#firstname# #lastname#', '#firstname# #initial# #lastname#', '#weird_name#'],
    'weird_name' : ['#initial# #initial# #lastname#',
                    '#initial# #lastname#',
                     '#firstname# #initial# #initial# #lastname#',
                     '#firstname# #firstname#',
                     ],
    'firstname' : ["Michael", "Christopher","Jason","David","James","Matthew","Joshua","John","Robert","Joseph",
                        "Daniel","Brian","Justin","William","Ryan","Eric","Nicholas","Jeremy","Andrew","Timothy","Jonathan",
                        "Adam","Kevin","Anthony","Thomas","Richard","Jeffrey","Steven","Charles","Brandon","Mark","Benjamin",
                        "Scott","Aaron","Paul","Nathan","Travis","Patrick","Chad","Stephen","Kenneth","Gregory","Jacob",
                        "Dustin","Jesse","Jose","Shawn","Sean","Bryan","Derek","Bradley","Edward","Donald","Samuel","Peter",
                        "Keith","Kyle","Ronald","Juan","George","Jared","Douglas","Gary","Erik","Phillip","Raymond","Joel",
                        "Corey","Shane","Larry","Marcus","Zachary","Craig","Derrick","Todd","Jeremiah","Antonio","Carlos",
                        "Shaun","Dennis","Frank","Philip","Cory","Brent","Gabriel","Nathaniel","Randy","Luis","Curtis",
                        "Jeffery","Alexander","Russell","Casey","Jerry","Wesley","Brett","Luke","Lucas","Seth","Billy",

                        "Jennifer","Amanda","Jessica","Melissa","Sarah","Heather","Nicole","Amy","Elizabeth","Michelle",
                        "Kimberly","Angela","Stephanie","Tiffany","Christina","Lisa","Rebecca","Crystal","Kelly","Erin",
                        "Laura","Amber","Rachel","Jamie","April","Mary","Sara","Andrea","Shannon","Megan","Emily","Julie",
                        "Danielle","Erica","Katherine","Maria","Kristin","Lauren","Kristen","Ashley","Christine","Brandy",
                        "Tara","Katie","Monica","Carrie","Alicia","Courtney","Misty","Kathryn","Patricia","Holly","Stacy",
                        "Karen","Anna","Tracy","Brooke","Samantha","Allison","Melanie","Leslie","Brandi","Susan","Cynthia",
                        "Natalie","Jill","Dawn","Dana","Vanessa","Veronica","Lindsay","Tina","Kristina","Stacey","Wendy",
                        "Lori","Catherine","Kristy","Heidi","Sandra","Jacqueline","Kathleen","Christy","Leah","Valerie",
                        "Pamela","Erika","Tanya","Natasha","Katrina","Lindsey","Melinda","Monique","Teresa","Denise",
                        "Tammy","Tonya","Julia","Candice","Gina" ],
    'initial' : map( lambda x: x+".", string.ascii_uppercase ),
    'lastname' : LAST_NAMES,
}


class Novel(object):

    def __init__(self, cultures):
        self.cultures = cultures
        self.scenes = []
        self.coverImage = None

        self.sg = storygen.StoryGen()

    def generate(self):

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
        title_rules['protagName'] = self.protag.name
        title_rules['protagClass'] = self.protag.rpgClass.rpgClass

        self.title = self.genTitle()
        self.subtitle = self.genSubtitle()
        self.author = self.genAuthor()

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
        title = utils.title2( grammar.flatten( "#origin#") )

        return title

    def genSubtitle(self):
        grammar = tracery.Grammar( title_rules )
        grammar.add_modifiers( base_english )
        subtitle = utils.title2( grammar.flatten( "#subtitle#") )

        return subtitle


    def genAuthor(self):
        grammar = tracery.Grammar( author_rules )
        grammar.add_modifiers( base_english )
        author = grammar.flatten( "#origin#").title()

        return author