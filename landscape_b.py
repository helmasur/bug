import os, pygame
import sys
import time
from pygame.locals import *
import random
from math import *
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

def pos_sub(a=(0,0), b=(0,0)):
    diff = (a[0]-b[0], a[1]-b[1])
    return diff

def pos_dist(a=(0,0), b=(0,0)):
    diff = pos_sub(b, a)
    dist = hypot(diff[0], diff[1])
    return dist

class Plot(pygame.sprite.Sprite):
    def __init__(self, width, height):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        #self.image, self.rect = load_image('4k.jpg')    #, -1)
        self.data = [[0 for i in range(width)] for i in range(height)]

    def set(self, x, y, value):
        self.data[y][x]=value

    def get(self, x, y):
        return self.data[y][x]
        
    def update(self):
        print ""


def main():

    pygame.init()
    screen = pygame.display.set_mode((400, 400), 0, 32)
    screen.fill ((100, 100, 100))
    screensize = screen.get_size()
    background = pygame.Surface(screensize)
    background = background.convert()
    background=load_image('2x2.png')
    screen.blit(background, (0, 0))
    pygame.display.flip()

    plot = Plot(3,4)
    print plot.data
    plot.set(0,1,3)
    print plot.data

    pic = Image.new('RGB', screensize)
    pixtot=screensize[0]*screensize[1]
    picdata=[]
    y=0
    i=0
    while y < screensize[1]:
        x=0
        while x < screensize[0]:
            dist=pos_dist((0,0),(x,y))
            dist+=1000
            luminosity=sin((dist * (1/(dist)) % (2*pi) ) - pi )
            luminosity += 1
            luminosity = int(luminosity)
            luminosity *= 255
            picdata.append(colorsys.hls_to_rgb(0,luminosity,0))
            x+=1
            i+=1
        y+=1
    
    pic.putdata(picdata, 1, 0)
    picstr=pic.tostring()
    background=pygame.image.frombuffer(picstr, screensize, 'RGB')
    screen.blit(background, (0,0))
    pygame.display.flip()

if __name__ == '__main__':
    main()