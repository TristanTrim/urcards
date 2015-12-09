import urwid
import json
import random
import six
from six import u as unicode


from os import walk

def ultimateKeys(key):
    pass

class flashcard(urwid.Pile):
    def randomizeQuestion(self):
        self.questionNumber=random.randint(0,len(self.deck)-1)
        self.question.set_text(unicode(self.deck[self.questionNumber][self.questionKey]))
        self.answer.set_edit_text("")
    def __init__(self, deck,questionKey,answerKey,*args,**kwargs):
        self.deck = deck
        self.questionKey = questionKey
        self.answerKey = answerKey
        self.question = urwid.Text("")
        self.answer = urwid.Edit()
        self.randomizeQuestion()
        super(flashcard,self).__init__([self.question,self.answer],**kwargs)
    def keypress(self,size,key):
        if key == 'enter':
            # correct answer
            if self.answer.edit_text == unicode(self.deck[self.questionNumber][self.answerKey]):
                self.randomizeQuestion()
            # incorrect answer
            else:
                self.question.set_text(u"{} is {}".format(
                    unicode(self.deck[self.questionNumber][self.questionKey]),
                    unicode(self.deck[self.questionNumber][self.answerKey])
                    ))
                self.answer.set_edit_text("")
        elif key == 'esc':
            #THIS IS HACKY AS FUCK. tbh I don't urwid so good yet.
            padd.original_widget=padd.original_widget[0]
        return self.answer.keypress(size,key)# pass the keypress onto the answerbox

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

def deckChosen(button,deck):
    if deck.lower().endswith(".json"):
        deck = jsonDeck(deck)
    elif deck.lower().endswith(".md"):
        deck = markdownDeck(deck)
    keys = set()
    for card in deck:
        for key in card:
            keys.add(key)
    keys=list(keys)
    prompt=random.choice(keys)
    keys.remove(prompt)
    answer=random.choice(keys)
    cardwidget = flashcard(deck,prompt,answer)
    box = urwid.LineBox(cardwidget)
    fill = urwid.Filler(box,'middle')
    openSimpleOverlay(fill)

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
            for fyle in fyles:
                newButton = urwid.Button(fyle)
                buttons.append(newButton)
                urwid.connect_signal(newButton, 'click', deckChosen, fyle)
        super(Menu,self).__init__(buttons,**kwargs)
    def keypress(self,size,key):
        if key == 'esc':
            raise urwid.ExitMainLoop()
        return super(Menu,self).keypress(size,key)

menu = Menu()
padd = urwid.Padding(menu,'center',left=2,right=2)

loop = urwid.MainLoop(padd, unhandled_input=ultimateKeys)

loop.run()

