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

def randx(x):
    random.seed(x)
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
    allsprites = pygame.sprite.Group(plot)		#order makes layers, first on top


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
    
    for y in range(400):
        plot.set(25,y,200)
        plot.set(25*4,y,200)
        plot.set(25*13,y,200)
        
    for x in range(400):
        x=float(x)
        p=50.0
        plot.set(x, 15 - sawwave(x/p)*10, 0) # gör x till alltid float så man kan / 20
        plot.set(x, 30 - sinwave(x/p)*10, 0)
        plot.set(x, 50 - sqrwave(x/p)*10,0)
        plot.set(x, 70 - triwave(x/p)*10, 0)
        plot.set(x, 100 - bllwave(x/p)*25, 0)
        plot.set(x, 125 - topwave(x/p)*25, 0)
        x2=x/400   #x/(x/40+50)
        plot.set(x, 300 - topwave(x2)*150, 0)
        #plot.set(x, 400 - int(log((x*0.02+1), 1.5))*10, 0)
        plot.set(x, 400 - logset(x, 3, 25)*10, 0)


    
    allsprites.update()
    allsprites.draw(screen)
    pygame.display.flip()

if __name__ == '__main__':
    main()