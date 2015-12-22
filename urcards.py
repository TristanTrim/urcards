import urwid
import json
import random
import six
from six import u as unicode
def strOrU(foo):
    """I love Unicode. This fancy function takes an object that
    might be unicode or a str and returns a unicode."""
    try:
        bar = unicode(str(foo))
        return bar
    except TypeError as e:
        if "decoding Unicode is not supported" in str(e):
            return foo

from os import walk
from os import path
import time

class flashcard(urwid.Pile):
    "flashcard widget, needs a json list of dictionarys as a deck"
    def __init__(self, deck,deckName,questionKey,answerKey,*args,**kwargs):
        self.recordFile = open("decords/{}.record".format(path.splitext(deckName)[0]),'a')
        self.answerModes = [self.answerByLetter,self.answerByEnter]
        self.cardModes = [self.randomCard]

        self.answerMode = self.answerModes[0]
        self.cardMode = self.cardModes[0]

        self.deck = deck
        self.questionKey = questionKey
        self.answerKey = answerKey
        self.timedelta = urwid.Text("")
        self.question = urwid.Text("")
        self.answer = urwid.Edit()
        self.responses=[]

        self.getNextCard()
        super(flashcard,self).__init__([self.timedelta,self.question,self.answer],**kwargs)

    ### Stuff to do with the selection of cards from the deck!
    def getNextCard(self):
        self.cardMode()
    def randomCard(self):
        self.questionNumber=random.randint(0,len(self.deck)-1)
        self.question.set_text(strOrU(self.deck[self.questionNumber][self.questionKey]))
        self.answer.set_edit_text("")
        self.lastTime=time.time()

    def keypress(self,size,key):
        return(self.answerMode(size,key))

    def answerByEnter(self,size,key):
        """Type whatever answer, however long, and then press 'enter'.
         Only then do you know whether or not your answer is correct."""
        if key == 'enter':
            # correct answer
            if self.answer.edit_text == strOrU(self.deck[self.questionNumber][self.answerKey]):
                self.randomizeQuestion()
            # incorrect answer
            else:
                self.question.set_text(u"{} is {}".format(
                    strOrU(self.deck[self.questionNumber][self.questionKey]),
                    strOrU(self.deck[self.questionNumber][self.answerKey])
                    ))
                self.answer.set_edit_text("")
        elif key == 'esc':
            #THIS IS HACKY AS FUCK. tbh I don't urwid so good yet.
            padd.original_widget=padd.original_widget[0]
        return self.answer.keypress(size,key)# pass the keypress onto the answerbox

    def answerByLetter(self,size,key):
        """Accepts one letter at a time, lets you know if and when you screw up.
         And deletes your dumb wrongness."""
        answerData={
            "t":time.time(),#Time of answer
            "q":self.deck[self.questionNumber][self.questionKey],#question
            "a":self.deck[self.questionNumber][self.answerKey],#correct answer
            #"r":,#user response
            "d":time.time()-self.lastTime,#timedelta
            #"c":,#if users response is correct
            }
        # correct letter
        if strOrU(self.deck[self.questionNumber][self.answerKey]
                  ).startswith(self.answer.edit_text + strOrU(key)):
            # complete correct answer!
            if strOrU(self.deck[self.questionNumber][self.answerKey]) == self.answer.edit_text + key:
                self.responses+=[(key,time.time()-self.lastTime)]
                string=""
                for foo in self.responses:
                    string+="{0[0]}:{0[1]:.2f}, ".format(foo)
                self.timedelta.set_text(string)
                self.getNextCard()
                answerData['c']=True
                self.recordFile.write(json.dumps(answerData,
                                              sort_keys=True, indent=4)+",\n")
                self.recordFile.flush()
            # correct so far
            else:
                # pass on the correct key to the answerbox
                self.answer.keypress(size,key)
        # exit widget on esc keypress
        elif key == 'esc':
            #THIS IS HACKY AS FUCK. tbh I don't urwid so good yet.
            padd.original_widget=padd.original_widget[0]
        # incorrect letter
        else:
            self.question.set_text(u"{} is {}".format(
                strOrU(self.deck[self.questionNumber][self.questionKey]),
                strOrU(self.deck[self.questionNumber][self.answerKey])
                ))
            answerData['c']=False
            answerData['r']= self.answer.edit_text + strOrU(key)
            self.recordFile.write(json.dumps(answerData,
                                              sort_keys=True, indent=4)+",\n")
            self.recordFile.flush()

def keypressBaselineChosen(button):
    keys=[{"letter":x} for x in " e t a o i n s h r d l c u m w f g y p b v k j x q z ".split()]
    cardwidget = flashcard(keys,'keypressBaseline.json','letter','letter')
    box = urwid.LineBox(cardwidget)
    fill = urwid.Filler(box,'middle')
    openSimpleOverlay(fill)

def jsonDeck(deck):
    fl = open('decords/{}'.format(deck),'r')
    deck = json.load(fl)
    fl.close()
    del(fl)
    return deck

import mistune
from lxml import etree
def markdownDeck(deck):
    fl = open('decords/{}'.format(deck),'r')
    xml = mistune.markdown(fl.read())
    fl.close()
    del(fl)
    xml = etree.fromstring(xml)
    pass

def deckChosen(button,deckName):
    if deckName.lower().endswith(".json"):
        deck = jsonDeck(deckName)
    elif deckName.lower().endswith(".md"):
        deck = markdownDeck(deckName)
    settingsFile = "decords/{}.settings".format(path.splitext(deckName)[0])
    if path.exists(settingsFile):
        settings = loadSettings(settingsFile)
    else:
        settings = initSettings(settingsFile,deck)
    prompt=random.choice(settings['keys'])
    answer=random.choice(settings['keys'])
    cardwidget = flashcard(deck,deckName,prompt,answer)
    box = urwid.LineBox(cardwidget)
    fill = urwid.Filler(box,'middle')
    openSimpleOverlay(fill)

def loadSettings(settingsFile):
    fl = open(settingsFile,'r')
    settings = json.load(fl)
    fl.close()
    del(fl)
    return settings

def initSettings(settingsFile,deck):
    keys = set()
    for card in deck:
        for key in card:
            keys.add(key)
    keys=list(keys)
   #prompt=random.choice(keys)
   ##keys.remove(prompt)
   #answer=random.choice(keys)
    settings = {"keys":keys}
    fl = open(settingsFile,'w')
    fl.write(json.dumps(settings,
                     sort_keys=True, indent=4))
    fl.close()
    del(fl)
    return(settings)

def openSimpleOverlay(wid):
    padd.original_widget = urwid.Overlay(wid,
            padd.original_widget,
            align='center', width=('relative',80),
            valign='middle', height=('relative',80),
            left=2,right=2,top=2,bottom=2)

class Menu(urwid.ListBox):
    def __init__(self,*args,**kwargs):
        buttons = []
        for directory,otherThing,fyles in walk('decords'):
            for fyle in [x for x in fyles if '.settings' not in x and '.record' not in x]:
                newButton = urwid.Button(fyle)
                buttons.append(newButton)
                urwid.connect_signal(newButton, 'click', deckChosen, fyle)
        # and then there's this keypress baseline...
        keypressBaseline=urwid.Button("keypress baseline")
        buttons.append(keypressBaseline)
        urwid.connect_signal(keypressBaseline, 'click',keypressBaselineChosen)
        super(Menu,self).__init__(buttons,**kwargs)
    def keypress(self,size,key):
        if key == 'esc':
            raise urwid.ExitMainLoop()
        return super(Menu,self).keypress(size,key)

if __name__=="__main__":
    menu = Menu()
    padd = urwid.Padding(menu,'center',left=2,right=2)
    loop = urwid.MainLoop(padd)
    loop.run()

