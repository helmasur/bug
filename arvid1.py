import os, pygame
import sys
import time
from pygame.locals import *
import random
import math
import colorsys

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')

def triscale(triplet=(1,1,1), factor=255):
    triplet = [triplet[0]*factor, triplet[1]*factor, triplet[2]*factor, ]
    return triplet


def main():
    """this function is called when the program starts.
       it initializes everything it needs, then runs in
       a loop until the function returns."""

#initialize and setup screen
    pygame.init()
    screen = pygame.display.set_mode((300, 480))
    screenrect=screen.get_rect()
    screen.fill ((220, 0, 0))
    clock = pygame.time.Clock()
    font = pygame.font.Font(os.path.join(data_dir, 'AndBasR.ttf'), 300)    
    keytext=""
    pygame.midi.init()
    mididev=pygame.midi.get_default_output_id()
    midiout=pygame.midi.Output(mididev)
    midiout.set_instrument(0)
    

#mainloop
    going = True
    while going:
        clock.tick(60) #framerate limiter

        #Handle Input Events
        for event in pygame.event.get():
            if event.type == QUIT:
                going = False
            if  event.type == KEYDOWN:
                print "Key", event.key, event.unicode, event.mod
                hue=(event.key % 100)/100.0
                note = event.key % 100 + 20
                print "Note", note
                midiout.note_on(note, 100)
                keytext=event.unicode
                screen.fill(triscale(colorsys.hsv_to_rgb(hue, 1, 1),255))
            if event.type == KEYUP:
                note = event.key % 100 + 20      
                midiout.note_off(note)
                

        #create texts
        keytextsurf = font.render(keytext, False, (0,0,0))
        ktsrect=keytextsurf.get_rect()

      
        #Draw Everything
        screen.blit(keytextsurf, (screenrect.width/2-ktsrect.width/2, screenrect.height/2-ktsrect.height/2))
        pygame.display.flip()

    pygame.quit()
        
#this calls the 'main' function when this script is executed
if __name__ == '__main__':
    main()