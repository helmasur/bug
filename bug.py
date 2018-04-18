import os, pygame
import sys
import time
from pygame.locals import *
import random
import math

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')

#functions to create our resources
def load_image(filename):
    fullpath = os.path.join(data_dir, filename)
    try:
        image = pygame.image.load(fullpath)
    except pygame.error:
        print ('Cannot load image:', fullpath)
        raise SystemExit(str(geterror()))
    image = image.convert()
    return image, image.get_rect()

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

def pos_futuretarget(origin=(0,0), ospeed=1, target=(1,1), tdirection=0, tspeed=1):
    disttotarget = pos_dist(origin, target)
    timetotarget = disttotarget / ospeed
    tnewpos = pos_step(target, tdirection, timetotarget*tspeed)
    i = 5
    while i > 0:
        i -= 1
        newdisttotarget = pos_dist(origin, tnewpos)
        newtimetotarget = newdisttotarget / ospeed
        tnewpos = pos_step(target, tdirection, newtimetotarget*tspeed)
    return tnewpos
    
#classes for our game objects
class Player(pygame.sprite.Sprite):
    "stores information about the player"
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image, self.rect = load_alphaimage('tass.tga')    #, -1)
        self.nonrotatedimage = self.image
        self.rect.center=(0,0)
        self.WC = (0,0)
        self.WCdestination = (0,0)
        self.newmove = False
        self.moving = False
        self.speed = 3
        self.direction = 0
        self.dist = 0
        self.totaltravel = 0

    def move(self):
        if self.newmove:
            self.moving = True
            self.newmove = False
            self.dist = pos_dist(self.WC, self.WCdestination)
            self.direction = pos_direction(self.WC, self.WCdestination)
            self.rot = math.degrees(self.direction)
            self.image = pygame.transform.rotate(self.nonrotatedimage, self.rot-90)
        if self.moving:
            if self.dist > self.speed :
                    step = [self.WC[0]+(self.speed*math.cos(self.direction)), self.WC[1]+(self.speed*math.sin(self.direction))]
                    self.totaltravel += pos_dist(self.WC, step)
                    self.WC = step
                    self.dist = pos_dist(self.WC, self.WCdestination)
            elif self.dist <= self.speed :
                    self.totaltravel += pos_dist(self.WC, self.WCdestination)
                    self.WC = self.WCdestination
                    self.moving = False

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

    def move(self, playerpos=(0,0), playertraveled=0, playerdirection=0, playerspeed=0):
        if playertraveled > 50:
            self.moving = True
            self.newmove = False
            self.dist = pos_dist(self.WC, playerpos)
            #target = pos_futuretarget(self.WC, self.speed, playerpos, playerdirection, playerspeed)
            #self.direction = pos_direction(self.WC, target)
            self.direction = pos_direction(self.WC, playerpos)
            #self.rot = math.degrees(self.direction)
            #self.image = pygame.transform.rotate(self.nonrotatedimage, self.rot-90)
        if True:
            if self.dist > 50 :
                    step = [self.WC[0]+(self.speed*math.cos(self.direction)), self.WC[1]+(self.speed*math.sin(self.direction))]
                    self.WC = step
                    #self.dist = pos_dist(self.WC, playerpos)
            elif False:#self.dist <= 10:
                    self.WC = self.WCdestination
                    self.moving = False

    def update(self, WCview = (0,0)):
        self.rect.center = to_sc(self.WC, WCview)

class Viewport():
    def __init__(self):
        self.rect = pygame.Rect(0,0,0,0)
        self.WC = (0 - self.rect.center[0], self.rect.center[1])

    def update(self, playerwc = (0,0)):
        self.WC = (playerwc[0] - self.rect.center[0], playerwc[1] + self.rect.center[1])

class Ground(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image, self.rect = load_image('2k.png')    #, -1)
        self.WC = (0,0)
        
    def update(self, WCview = (0,0)):
        self.rect.center = (self.WC[0]-WCview[0], 0-(self.WC[1]-WCview[1]))                 

def main():
    """this function is called when the program starts.
       it initializes everything it needs, then runs in
       a loop until the function returns."""

#initialize and setup screen
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    screen.fill ((100, 100, 100))

#Create The Backgound
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 250, 250))

#Display The Background
    screen.blit(background, (0, 0))
    pygame.display.flip()

#Prepare Game Objects
    clock = pygame.time.Clock()
    player = Player()
    enemy = Enemy()
    view = Viewport()
    view.rect = screen.get_rect()
    player.rect.center = view.rect.center
    ground = Ground()
    floorsprites = pygame.sprite.Group(ground)
    allsprites = pygame.sprite.Group(player, enemy)		#order makes layers, first on top

#Variables
    moving = False
    isfull=False
    
    def fullscreen(gofull=False):
        if gofull:
            screen = pygame.display.set_mode((1280, 800), FULLSCREEN|HWSURFACE|DOUBLEBUF)
            view.rect = screen.get_rect()
            player.rect.center = view.rect.center
        elif not gofull:
            screen = pygame.display.set_mode((640, 480))
            view.rect = screen.get_rect()
            player.rect.center = view.rect.center
        return screen

#mainloop
    going = True
    while going:
        clock.tick(60) #framerate limiter

        #Handle Input Events
        for event in pygame.event.get():
            if  event.type == KEYDOWN:
                print "Keypress", event.key            
            if event.type == QUIT:
                going = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                going = False
            elif event.type == KEYDOWN and event.key == K_UP:
                floory -= 10
            elif event.type == KEYDOWN and event.key == K_DOWN:
                floory += 10
            elif event.type == KEYDOWN and event.key == K_LEFT:
                going = False
            elif event.type == KEYDOWN and event.key == K_RIGHT:
                going = False
            elif event.type == KEYDOWN and event.key == 293:
                #print fullscreen
                if not isfull:
                    screen = fullscreen(True)
                    isfull = True
                elif isfull:
                    screen = fullscreen(False)
                    isfull = False
            elif event.type == KEYDOWN and event.key == 102:
                print "FPS", clock.get_fps()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                moving = True
            elif event.type == MOUSEBUTTONUP and event.button == 1:
                moving = False

                

        if moving:
            newdest = to_wc(pygame.mouse.get_pos(), view.WC)
            if pos_dist(player.WCdestination, newdest) > player.speed*4:
                player.WCdestination = newdest
            #player.WCdestination = to_wc(pygame.mouse.get_pos(), view.WC)
                player.newmove = True
                
                
        #Move and update all coordinates
        player.move()
        view.update(player.WC)
        enemy.move(player.WC, player.totaltravel, player.direction, player.speed)
        enemy.update(view.WC)
        ground.update(view.WC)
        #allsprites.update()
        

        #Draw Everything
        screen.blit(background, (0, 0))
        #screen.blit(ground.image, ground.rect.center)
        floorsprites.draw(screen)
        allsprites.draw(screen)
        pygame.display.flip()

    pygame.quit()
        
#this calls the 'main' function when this script is executed
if __name__ == '__main__':
    main()