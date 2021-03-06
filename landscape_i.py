﻿import os, pygame
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

def randx(x):
    random.seed(x)
    return random.random()

def randxy(pos):
    random.seed(pos[0]+(1.0/(pos[1]+1.1)))
    return random.random()

class Plot(pygame.sprite.Sprite):
    def __init__(self, width, height):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.width = width
        self.height = height
        self.size = (width, height)
        self.image = pygame.Surface(self.size)
        self.rect = self.image.get_rect()
        self.data = [255 for i in range(width*height)]
        self.PILimage = Image.new('L', self.size)

    def set(self, x, y, value):
        if x < 0: x=0
        if x > self.width-1: x=self.width-1
        if y < 0: y=0
        if y > self.height-1: y=self.height-1
        x = int(round(x))
        y = int(round(y))
        pos = (y*self.width)+x
        self.data[pos]=value

    def get(self, x, y):
        return self.data[y][x]
        
    def update(self):
        self.PILimage.putdata(self.data, 1, 0)
        self.PILimage = self.PILimage.convert('RGB')
        imgstr=self.PILimage.tostring()
        self.image=pygame.image.frombuffer(imgstr, self.size, 'RGB')

class Lengths():
    def __init__(self, meanlength):
        self.data = dict()
        self.shift = 1 - 1.0/meanlength

    def get(self, pos):
        pos = int(pos)
        if pos in self.data: return self.data[pos]
        else:
            origin=pos
            while randx(pos-1) < self.shift:
                pos -= 1
            first = pos
            pos = origin
            while randx(pos) < self.shift:
                pos += 1
            last = pos
            setval = randx(pos+1)
            for a in range(first, last+1):
                self.data[a]=setval
            return setval
        
class Fields():
    #gång 14km/h
    #marathon 20km/h
    #100m 37km/h
    #tokyo 70km diameter
    
    #skala 32px/m
    #storskaligt landskap 2000km
    #stor stad 100km diameter
    #minsta enhet 5m = 160px
    
    
    
    def __init__(self):
        self.data = dict()
        self.gscale=2000*1000*32
        
    def get(self, pos):
        pos = (int(pos[0]), int(pos[1]))
        if pos in self.data: return self.data[pos]
        else:
            grandpos = (pos[0]/self.gscale, pos[1]/self.gscale)
            gprand = randxy(grandpos)
            if gprand > .9 return 'city'
            elif gprand > .45 return 'sand'
            else return 'green'
            

def main():

    pygame.init()
    screen = pygame.display.set_mode((400, 400), 0, 32)
    screen.fill ((100, 100, 100))
    screensize = screen.get_size()
    #background = pygame.Surface(screensize)
    #background = background.convert()
    #background=load_image('2x2.png')
    #screen.blit(background, (0, 0))
    pygame.display.flip()
    
    plot = Plot(400, 400)
    allsprites = pygame.sprite.Group(plot)

    lengths = Lengths(20)


  
    def triwave(x):
        return max(1-abs(x*2%2-1), 0)
    def sqrwave(x):
        return int(x%1+0.5)
    def sinwave(x):
        return sin(x*pi*2)*0.5+0.5
    def sawwave(x):
        return (x % 1)
    def bllwave(x):
        return sin(acos(x*2%2-1))
    def topwave(x):
        return 1-sin(acos((x*2+1)%2-1))
    def logset(x, base, firstrange):
        return int(log((x*((base-1.0)/firstrange)+1), base))

    
    #for y in range(400):
        #plot.set(25,y,200)
        #plot.set(25*4,y,200)
        #plot.set(25*13,y,200)
        
    #for x in range(400):
        #x=float(x)
        #p=50.0
        #plot.set(x, 15 - sawwave(x/p)*10, 0)
        #plot.set(x, 30 - sinwave(x/p)*10, 0)
        #plot.set(x, 50 - sqrwave(x/p)*10,0)
        #plot.set(x, 70 - triwave(x/p)*10, 0)
        #plot.set(x, 100 - bllwave(x/p)*25, 0)
        #plot.set(x, 125 - topwave(x/p)*25, 0)
        #plot.set(x, 400 - logset(x, 3, 25)*10, 0)
        #plot.set(x, 225 - lengths.get(x)*90, 0)
        
    #for y in range(400):
        #for x in range(400):
            #val=randxy(x,y)
            #if val < .99: val=0
            #else: val=1
            #plot.set(x, y, int(val)*255)

    
    #mainloop
    going=True
    while going:

        ##Handle Input Events
        for event in pygame.event.get():        
            if event.type == QUIT:
                going = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                going = False
                
        
        
    
        allsprites.update()
        allsprites.draw(screen)
        pygame.display.flip()
        

if __name__ == '__main__':
    main()