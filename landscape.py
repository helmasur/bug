import os, pygame
import sys
import time
from pygame.locals import *
import random
import math
import colorsys
from PIL import Image

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')

def load_image(filename):
    fullpath = os.path.join(data_dir, filename)
    try:
        image = pygame.image.load(fullpath)
    except pygame.error:
        print ('Cannot load image:', fullpath)
        raise SystemExit(str(geterror()))
    image = image.convert()
    return image


def main():

    pygame.init()
    screen = pygame.display.set_mode((200, 200), 0, 32)
    screen.fill ((100, 100, 100))
    screensize = screen.get_size()
    background = pygame.Surface(screensize)
    background = background.convert()
    background=load_image('2x2.png')
    screen.blit(background, (0, 0))
    pygame.display.flip()

    pic = Image.new('RGB', screensize)




    i=0
    picdata=[]
    pixnr=0
    pixtot=screensize[0]*screensize[1]
    while i < pixtot:
        luminosity=random.random()*255
        luminosity=int(luminosity)
        picdata.append(colorsys.hls_to_rgb(0,luminosity,0))
        i+=1
    pic.putdata(picdata, 1, 0)
    picstr=pic.tostring()
    background=pygame.image.frombuffer(picstr, screensize, 'RGB')
    screen.blit(background, (0,0))
    pygame.display.flip()

if __name__ == '__main__':
    main()