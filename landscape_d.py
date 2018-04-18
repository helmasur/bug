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
        return max(1-abs(x*0.8%2-1), 0)
    def sqrwave(x):
        return int(x*0.4%1+0.5)
    def sinwave(x):
        return sin(x*0.4*pi*2)*0.5+0.5
    def sawwave(x):
        return (x*0.4 % 1)

    for x in range(400):
        plot.set(x, 15 - sawwave(x/20.0)*10, 0) # gör x till alltid float så man kan / 20
        plot.set(x, 30 - sinwave(x/20.0)*10, 0)
        plot.set(x, 50 - sqrwave(x/20.0)*10,0)
        plot.set(x, 70 - triwave(x/20.0)*10, 0)
    plot.set(50,0,0)



    
    allsprites.update()
    allsprites.draw(screen)
    pygame.display.flip()

if __name__ == '__main__':
    main()