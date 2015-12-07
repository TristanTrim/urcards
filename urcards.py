import urwid
import json
import random
from os import walk

def ultimateKeys(key):
    pass

class flashcard(urwid.Pile):
    def randomizeQuestion(self):
        self.questionNumber=random.randint(0,len(self.deck)-1)
        self.question.set_text(self.deck[self.questionNumber][self.questionKey])
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
            if self.answer.edit_text == str(self.deck[self.questionNumber][self.answerKey]):
                self.randomizeQuestion()
            # incorrect answer
            else:
                self.question.set_text("{} is {}".format(
                    str(self.deck[self.questionNumber][self.questionKey]),
                    str(self.deck[self.questionNumber][self.answerKey]))
                    )
                self.answer.set_edit_text("")
        elif key == 'esc':
            #THIS IS HACKY AS FUCK. tbh I don't urwid so good yet.
            padd.original_widget=padd.original_widget[0]
        return self.answer.keypress(size,key)# pass the keypress onto the answerbox

def deckChosen(button,deck):
    fl = open('decords/{}'.format(deck),'r')
    deck = json.load(fl)
    fl.close()
    del fl
    cardwidget = flashcard(deck,'binary','decimal')
    box = urwid.LineBox(cardwidget)
    fill = urwid.Filler(box,'middle')
    padd.original_widget = urwid.Overlay(fill,
            padd.original_widget,
            align='center', width=('relative',80),
            valign='middle', height=('relative',80),
            left=12,right=12,top=12,bottom=12)


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
padd = urwid.Padding(menu,'center',('relative',80))

loop = urwid.MainLoop(padd, unhandled_input=ultimateKeys)

loop.run()

