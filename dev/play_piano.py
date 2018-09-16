import cv2
import numpy as np
import pygame

channels = 10
pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(channels)

class Key:

    def __init__(self, note, sound):
        self.note = note #str
        self.sound = sound #Pygame Sound object
        self.isPlaying = False

    def stop(self):
        if self.isPlaying:
            self.isPlaying = False
            self.sound.stop()

    def play(self):
        if not self.isPlaying:
            self.isPlaying = True
            self.sound.play()

    def keyIsPlaying(self):
        return self.isPlaying

class Piano:

    def __init__(self):
        self.notes = self.initNotes() #List[str]
        self.keys = self.initKeys(self.notes) #Dict{str note: Key key}
        self.previousPressedNotes = []

    def initNotes(self):
        whites = "ABCDEFG"
        blacks = "ABDEG"
        octaves = range(3, 8)
        allNotes = []
        for i in octaves:
            for letter in whites:
                allNotes.append(letter + str(i))
            for letter in blacks:
                allNotes.append(letter + "b" + str(i))
        allNotes.append("C8") #the last note
        return allNotes

    def initKeys(self, notes):
        keys = {}
        for note in notes:
            soundPath = "piano_sounds/Piano.ff." + note + ".wav"
            rawSound = bytes(
                list(bytearray(
                    pygame.mixer.Sound(soundPath).get_raw()
                ))[ int((2**16)) : int((2**19)) ]
            )
            sound = pygame.mixer.Sound(rawSound)
            keys[note] = Key(note, sound)
        return keys

    def getNotes(self):
        return self.notes[:]

    def getKeys(self):
        return dict(self.keys)

    """
    string[] pressedNotes = List containing pressed notes
    
    Plays keys that are pressed. Stops keys that are not pressed.
    Call on every frame!
    """
    def playKeys(self, pressedNotes):
        if self.previousPressedNotes == pressedNotes:
            return
        for note in self.notes:
            if note in pressedNotes and not self.keys[note].keyIsPlaying():
                self.keys[note].play()
            elif note not in pressedNotes:
                self.keys[note].stop()
        self.previousPressedNotes = pressedNotes

    # def playKey(self, note):
    #     if not self.keys[note].keyIsPlaying():
    #         self.keys[note].play()
    #     return
    #
    # def stopKey(self, note):
    #     if self.keys[note].keyIsPlaying():
    #         self.keys[note].stop()

piano = Piano()

#Example mapping of k presses to notes
keyToNote = {121: "C3", 117:"E3", 105:"G3", 111:"C4"}
image = np.full((30,30), np.inf)
while(1):
    #Example CV window open
    cv2.imshow('image', image)
    k = cv2.waitKey(0)
    if k == 27:
        break

    pressedNotes = []
    #Populate pressed Notes here
    piano.playKeys(pressedNotes)