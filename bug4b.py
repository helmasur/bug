import os, pygame
import sys
import time
from pygame.locals import *
import random
import math

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')

globalseed=0

#functions to create our resources
def load_image(filename):
    fullpath = os.path.join(data_dir, filename)
    try:
        image = pygame.image.load(fullpath)
    except pygame.error:
        print ('Cannot load image:', fullpath)
        raise SystemExit(str(geterror()))
    image = image.convert()
    return image

def load_alphaimage(filename):
    fullpath = os.path.join(data_dir, filename)
    try:
        image = pygame.image.load(fullpath)
    except pygame.error:
        print ('Cannot load image:', fullpath)
        raise SystemExit(str(geterror()))
    image = image.convert_alpha()
    return image, image.get_rect()

def pos_add(a=(0,0), b=(0,0)):
    sum=(a[0]+b[0], a[1]+b[1])
    return sum

def pos_sub(a=(0,0), b=(0,0)):
    diff = (a[0]-b[0], a[1]-b[1])
    return diff

def pos_dist(a=(0,0), b=(0,0)):
    diff = pos_sub(b, a)
    dist = math.hypot(diff[0], diff[1])
    return dist

def pos_direction(a=(0,0), b=(0,0)):
    diff = pos_sub(b, a)
    direction = math.atan2(diff[1], diff[0])        
    return direction

#functions to convert between screen coordinates SC and world coordinates WC
def to_sc(wc=(0,0), wcview=(0,0)):
    sc = (wc[0]-wcview[0], 0-(wc[1]-wcview[1]))
    return sc

def to_wc(sc = (0,0), wcview=(0,0)):
    wc = (wcview[0]+sc[0], wcview[1]-sc[1])
    return wc

def pos_step(origin=(0,0), direction=0, distance=1):
    step = (origin[0]+(distance*math.cos(direction)), origin[1]+(distance*math.sin(direction)))
    return step


def randget(pos=(0,0), optA=0, optB=0, seed=globalseed):
    string=str(pos)+str(optA)+str(optB)+str(seed)
    random.seed(string)
    return random.random()

#classes for our game objects
class Player(pygame.sprite.Sprite):
    "stores information about the player"
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image, self.rect = load_alphaimage('tass.tga')    #, -1)
        self.nonrotatedimage = self.image
        self.rect.center=(0,0)
        self.viewrect = pygame.Rect(0,0,0,0)
        self.WC = (0,0)
        self.WCdestination = (0,0)
        self.WCview = (0,0)
        self.newmove = False
        self.moving = False
        self.speed = 10
        self.direction = 0
        self.dist = 0
        self.totaltravel = 0
        self.step=0

    def move(self):
        
        if self.moving:
            newdest = to_wc(pygame.mouse.get_pos(), self.WCview)
            if pos_dist(self.WCdestination, newdest) > self.speed*1:
                self.WCdestination = newdest
                self.newmove = True

        if self.newmove:
            self.moving = True
            self.newmove = False
            self.dist = pos_dist(self.WC, self.WCdestination)
            self.speed=math.pow(self.dist/50.0, 2)
            self.direction = pos_direction(self.WC, self.WCdestination)
            self.rot = math.degrees(self.direction)
            self.image = pygame.transform.rotate(self.nonrotatedimage, self.rot-90)
        if self.moving:
            if self.dist > self.speed :
                self.step = [self.WC[0]+(self.speed*math.cos(self.direction)), self.WC[1]+(self.speed*math.sin(self.direction))]
                self.totaltravel += pos_dist(self.WC, self.step)
                self.WC = self.step
                self.dist = pos_dist(self.WC, self.WCdestination)
            elif self.dist <= self.speed :
                self.step = self.WCdestination
                self.WC = self.step
                self.totaltravel += pos_dist(self.WC, self.WCdestination)
                self.speed=0.0 #varför måste detta göras annars bugg vid hög hastighet?
                self.moving = False
        self.WCview = (self.WC[0] - self.viewrect.center[0], self.WC[1] + self.viewrect.center[1])
        

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image, self.rect = load_alphaimage('car.tga')    #, -1)
        self.nonrotatedimage = self.image
        self.rect.center=(0,0)
        self.WC = (100,100)
        self.WCdestination = (0,0)
        self.newmove = True
        self.moving = False
        self.speed = 2
        self.direction = 0
        self.dist = 0

    def move(self, player):
        if player.totaltravel > 50:
            self.moving = True
            self.newmove = False
            self.dist = pos_dist(self.WC, player.WC)
            self.direction = pos_direction(self.WC, player.WC)
        if self.dist > 50 :
            step = [self.WC[0]+(self.speed*math.cos(self.direction)), self.WC[1]+(self.speed*math.sin(self.direction))]
            self.WC = step

    def update(self, WCview = (0,0)):
        self.rect.center = to_sc(self.WC, WCview)

class Groundsprite(pygame.sprite.Sprite):
    #skalor 1/10 av verkligheten?
    #storlandskap 200km
    #landskap 200/5km, 40km
    #stad 40/5km, 8km
    
    def __init__(self, pos, imagebank, WCview, spritesize):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.spritesize=spritesize
        self.image = imagebank['sand']
        self.rect = self.image.get_rect()
        self.rect = self.rect.copy()
        self.SC = (pos[0]*spritesize, pos[1]*spritesize)
        self.origin=self.SC
        self.WC = to_wc(self.SC, WCview)
        self.data = dict()
        self.gscale=16*4
        
        
    def update(self, player, imagebank):
        self.rect.bottomleft = (self.origin[0] - player.WC[0] % self.spritesize, self.origin[1] + player.WC[1] % self.spritesize)
        self.WC = to_wc(self.rect.bottomleft, player.WCview)
        pos = (int(self.WC[0]), int(self.WC[1]))
        if pos in self.data: return self.data[pos]
        else:
            grandpos = (pos[0]/self.gscale, pos[1]/self.gscale)
            gprand = randget(grandpos)
            if gprand > .9: self.image = imagebank['city']
            elif gprand > .45: self.image = imagebank['sand']
            else: self.image = imagebank['green']

class World_infineon(): #this world is coded here
    def __init__(self):
        self.name="Infineon"
        self.size=(0,0)
        self.imagebank = dict()
        self.imagebank['city'] = load_image('64city.tga')
        self.imagebank['sand'] = load_image('64sand.tga')
        self.imagebank['green'] = load_image('64green.tga')

        
        

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
            if gprand > .9: return 'city'
            elif gprand > .45: return 'sand'
            else: return 'green'
        
def main():
    """this function is called when the program starts.
       it initializes everything it needs, then runs in
       a loop until the function returns."""

#initialize and setup screen
    pygame.init()
    screen = pygame.display.set_mode((640, 480), 0, 32)
    screen.fill ((100, 100, 100))

#Create The Backgound
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 100, 100))

#Display The Background
    screen.blit(background, (0, 0))
    pygame.display.flip()

#Prepare Game Objects
    imagebank = dict()
    imagebank['city'] = load_image('64city.tga')
    imagebank['sand'] = load_image('64sand.tga')
    imagebank['green'] = load_image('64green.tga')
    
    clock = pygame.time.Clock()
    timer = pygame.time.Clock()
    player = Player()
    enemy = Enemy()
    player.viewrect = screen.get_rect()
    player.rect.center = player.viewrect.center
    actorspritegroup = pygame.sprite.Group(player, enemy)
    
#create ground sprites
    spritesize=64.0 #måste vara float
    screensize=screen.get_size()
    amountgroundspritesx = int(math.ceil(screensize[0]/spritesize)+1)
    amountgroundspritesy = int(math.ceil(screensize[1]/spritesize)+1)
    groundspritelist=[]
    groundspritegroup = pygame.sprite.Group()
    for y in range(amountgroundspritesy):
        for x in range(amountgroundspritesx):
            groundspritelist.append(Groundsprite((x, y), imagebank, player.WCview, int(spritesize)))
            groundspritegroup.add(groundspritelist[len(groundspritelist)-1])

#Fonts and text preparation
    font = pygame.font.Font(os.path.join(data_dir, 'imagine_font.ttf'), 14)

#Variables
    # moving = False
    isfull=False
    
    def fullscreen(gofull=False):
        if gofull:
            screen = pygame.display.set_mode((1280, 800), FULLSCREEN|HWSURFACE|DOUBLEBUF)
            player.viewrect = screen.get_rect()
            player.rect.center = player.viewrect.center
        elif not gofull:
            screen = pygame.display.set_mode((640, 480))
            player.viewrect = screen.get_rect()
            player.rect.center = player.viewrect.center
        return screen

#mainloop
    going = True
    while going:
        lastframetime = clock.tick(60) #framerate limiter

        #Handle Input Events
        for event in pygame.event.get():
            if  event.type == KEYDOWN:
                print "Keypress", event.key            
            if event.type == QUIT:
                going = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                going = False
            elif event.type == KEYDOWN and event.key == 293:    #F12
                #print fullscreen
                if not isfull:
                    screen = fullscreen(True)
                    isfull = True
                elif isfull:
                    screen = fullscreen(False)
                    isfull = False
            elif event.type == KEYDOWN and event.key == 111:    #O
                player.WC = pos_sub(player.WC,(2100, -2100))
            elif event.type == KEYDOWN and event.key == 102:    #F
                print "FPS", clock.get_fps()
                print "clock", timer.tick()
                #print "speed", (player.step/16.0/1000.0)/(lastframetime/1000.0/60/60)
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                player.moving = True
            elif event.type == MOUSEBUTTONUP and event.button == 1:
                player.moving = False

                

        
        
                
        #Move and update all coordinates
        player.move()
        enemy.move(player)
        enemy.update(player.WCview)
        groundspritegroup.update(player, imagebank)

        #create texts
        coord=player.WC
        coord=(int(coord[0]/16.0), int(coord[1]/16.0))
        coord=(str(coord[0]), str(coord[1]))
        coord="POS: "+coord[0]+" "+coord[1]+" m"
        coordsurf = font.render(coord, False, (0,0,0))        

        #Draw Everything
        screen.blit(background, (0,0))
        groundspritegroup.draw(screen)
        actorspritegroup.draw(screen)
        screen.blit(coordsurf, (10, 10))
        pygame.display.flip()

    print randget()
    print randget((1,1), 0,0)
    
    pygame.quit()
        
#this calls the 'main' function when this script is executed
if __name__ == '__main__':
    main()