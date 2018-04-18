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

#def testrandstuff():
    #chance= random.random()
    #choice=random.random()
    #if chance < .5: # 0-0.5               1/2
        #elif chance < .75: # 0.5-0.75         1/4
        #elif chance < .85: # .75-.85          1/10
        #elif chance < .90: # .85-.90          1/20
        #elif chance < .91: # .90-.91          1/100
        #elif chance < .912: # .91-.912        1/500
        #elif chance < .913: # .912-.913       1/1000
    
    
    
    
    
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
        #self.qbordn = 4000
        self.qborde = 4000
        self.qbords = -4000
        #self.qbordw = -4000

    def move(self):
        if self.newmove:
            self.moving = True
            self.newmove = False
            self.dist = pos_dist(self.WC, self.WCdestination)
            self.speed=math.pow(self.dist/50.0, 2)+0.5
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

class Ground(pygame.sprite.Sprite):
    def __init__(self,images=None, WC = (0,0)):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        #self.image, self.rect = load_image('4k.jpg')    #, -1)
        self.image = images[0]
        self.rect = images[1].copy()
        self.WC = WC
        
    def update(self, WCview = (0,0)):
        self.rect.bottomleft = (self.WC[0]-WCview[0], 0-(self.WC[1]-WCview[1]))                 

#class Images():
#    def __init__(self):
#        self.image, self.rect = load_image('4k.jpg')
        
def main():
    """this function is called when the program starts.
       it initializes everything it needs, then runs in
       a loop until the function returns."""

#initialize and setup screen
    pygame.init()
    screen = pygame.display.set_mode((600, 400), 0, 32)
    screen.fill ((100, 100, 100))

#Create The Backgound
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 100, 100))

#Display The Background
    screen.blit(background, (0, 0))
    pygame.display.flip()

#Prepare Game Objects
    images = [load_image('4k.jpg'), None]
    images[1] = images[0].get_rect()
    
    clock = pygame.time.Clock()
    player = Player()
    enemy = Enemy()
    #view = Viewport()
    player.viewrect = screen.get_rect()
    player.rect.center = player.viewrect.center
    #ground = Ground()
    ground4 = [Ground(images, (-4000,0)), Ground(images, (0,0)), Ground(images, (0,-4000)), Ground(images, (-4000,-4000))]
    floorsprites = pygame.sprite.Group(ground4[0], ground4[1], ground4[2], ground4[3])
    allsprites = pygame.sprite.Group(player, enemy)		#order makes layers, first on top

    font = pygame.font.Font(os.path.join(data_dir, 'imagine_font.ttf'), 14)


#Variables
    moving = False
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

    #def extendfloor(playero):
        ##for sprite in ground:
            
        #"""currentsprite=pygame.sprite.spritecollide(player, floorsprites, False, None)
        #cstop=currentsprite[0].WC[1]+2000
        #csright=currentsprite[0].WC[0]+2000
        #csbottom=currentsprite[0].WC[1]-2000
        #csleft=currentsprite[0].WC[0]-2000"""
        
        ##if -2000 <= player.WC[0] <= 2000 and -2000 <= player.WC[1] <= 2000:
        ##    print "origin"
        ##    ext = (0,0)
        ##    floorwc=player.WC
        ##else:
        ##    print "outside"
        ##    ext = player.WC
        ##    ext = (ext[0]+math.copysign(2000,ext[0]), ext[1]+math.copysign(2000,ext[1]))
        ##    ext = (int(ext[0]/4000.0)*4000, int(ext[1]/4000.0)*4000)

        #floorwc = [player.WC[0], player.WC[1]]
        #if floorwc[0] < 0:
            #floorwc[0] = floorwc[0] - 4000
        #if floorwc[1] < 0:
            #floorwc[1] = floorwc[1] - 4000        
        #floorwc = (int(floorwc[0]/4000.0)*4000, int(floorwc[1]/4000.0)*4000)
        #"""bordn=floorwc[1]+4000
        #borde=floorwc[0]+4000
        #bords=floorwc[1]
        #bordw=floorwc[0]"""
        ##distn = player.qbordn - player.WC[1]
        #diste = player.qborde - player.WC[0] #distance from player to current quad of grounds north border
        #dists = player.WC[1] - player.qbords
        ##distw = player.WC[0] - player.qbordw

        #if dists > 5300:            # top 3rd
            #if diste > 5300:                   # right 3rd
                #if diste > 7900 or dists > 7900:
                    #ground4[0].WC = (floorwc[0], floorwc[1]+4000)
                    #ground4[1].WC = (floorwc[0]+4000, floorwc[1]+4000)
                    #ground4[2].WC = (floorwc[0]+4000, floorwc[1])
                    #ground4[3].WC = (floorwc[0], floorwc[1])
                    #player.qborde += 4000
                    #player.qbords += 4000
            #elif diste > 2700:                   # mid 3rd
                #if diste < 100 or dists > 7900:
                    #ground4[0].WC = (floorwc[0]-4000, floorwc[1]+4000)
                    #ground4[1].WC = (floorwc[0], floorwc[1]+4000)
                    #ground4[2].WC = (floorwc[0], floorwc[1])
                    #ground4[3].WC = (floorwc[0]-4000, floorwc[1])
            #else:                               # left 3rd
                #if diste > 7900 or dists > 7900:
                    #ground4[0].WC = (floorwc[0], floorwc[1]+4000)
                    #ground4[1].WC = (floorwc[0]+4000, floorwc[1]+4000)
                    #ground4[2].WC = (floorwc[0]+4000, floorwc[1])
                    #ground4[3].WC = (floorwc[0], floorwc[1])
        #elif dists > 2700:          # mid 3rd
            #if diste > 4000:                    # 3rd quadrant
                #if diste > 7900 or dists < 100:
                    #ground4[0].WC = (floorwc[0], floorwc[1])
                    #ground4[1].WC = (floorwc[0]+4000, floorwc[1])
                    #ground4[2].WC = (floorwc[0]+4000, floorwc[1]-4000)
                    #ground4[3].WC = (floorwc[0], floorwc[1]-4000)
            #else:                               # 4th quadrant
                #if diste < 100 or dists < 100:
                    #ground4[0].WC = (floorwc[0]-4000, floorwc[1])
                    #ground4[1].WC = (floorwc[0], floorwc[1])
                    #ground4[2].WC = (floorwc[0], floorwc[1]-4000)
                    #ground4[3].WC = (floorwc[0]-4000, floorwc[1]-4000)
        #else:                       # bottom 3rd
        
        
        ##print "floorwc",floorwc
        
        ##print "left border",csleft
        ##print player.viewrect
        
        ##print "current floor wc",currentsprite[0].WC
        #return        

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
            elif event.type == KEYDOWN and event.key == 103:    #G
                #print "player", player.WC
                #print "view", player.WCview
                #print "g1", ground.WC
                #ground[1] = Ground((4000, 0))
                #print "g2", ground2.WC
                #floorsprites.add(ground[1])
                extendfloor(player)
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
                if -2000 <= player.WC[0] <= 2000 and -2000 <= player.WC[1] <= 2000:
                    print "origin"
                    ext = (0,0)
                    bordn=2000
                    borde=2000
                    bords=-2000
                    bordw=-2000
                    print ext
                else:
                    print "outside"
                    ext = player.WC
                    ext = (ext[0]+math.copysign(2000,ext[0]), ext[1]+math.copysign(2000,ext[1]))
                    
                    ext = (int(ext[0]/4000.0)*4000, int(ext[1]/4000.0)*4000)
                    
                    print ext
                    
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                moving = True
            elif event.type == MOUSEBUTTONUP and event.button == 1:
                moving = False

                

        if moving:
            newdest = to_wc(pygame.mouse.get_pos(), player.WCview)
            if pos_dist(player.WCdestination, newdest) > player.speed*1:
                player.WCdestination = newdest
                player.newmove = True
        
        
                
        #Move and update all coordinates
        player.move()
        enemy.move(player)
        enemy.update(player.WCview)
        #ground.update(player.WCview)
        floorsprites.update(player.WCview)
        #ground2.update_screenpos(player.WCview)
        #allsprites.update()

        #create texts
        coord=player.WC
        coord=(int(coord[0]/100.0), int(coord[1]/100.0))
        coord=(str(coord[0]), str(coord[1]))
        coord="POS: "+coord[0]+"m"+" "+coord[1]+"m"
        coordsurf = font.render(coord, False, (200,200,100))        

        #Draw Everything
        screen.blit(background, (0,0))
        floorsprites.draw(screen)
        allsprites.draw(screen)
        screen.blit(coordsurf, (10, 10))
        pygame.display.flip()

    pygame.quit()
        
#this calls the 'main' function when this script is executed
if __name__ == '__main__':
    main()