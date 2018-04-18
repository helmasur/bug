import os, pygame
import sys
import time
from pygame.locals import *
import random
import math
print "1"
main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')

antalgodisar=10

#functions to create our resources
print "def global functions"
def load_image	(filename):
    print "loading image"
    fullpath = os.path.join(data_dir, filename)
    try:
        image = pygame.image.load(fullpath)
    except pygame.error:
        print ('Cannot load image:', fullpath)
        raise SystemExit(str(geterror()))
    image = image.convert()
    print "image loaded"
    return image, image.get_rect()

def load_alphaimage(filename):
    print "loading alpha image"
    fullpath = os.path.join(data_dir, filename)
    try:
        image = pygame.image.load(fullpath)
    except pygame.error:
        print ('Cannot load image:', fullpath)
        raise SystemExit(str(geterror()))
    image = image.convert_alpha()
    print "alpha image loaded"
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

def pos_aim(angle, dist):
    newpos=(dist*math.cos(angle), dist*math.sin(angle))
    return newpos

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

def seekangle(a, b, step):
    if a < math.pi * -1:
        a += math.pi*2
    elif a > math.pi:
        a -= math.pi*2
    if math.fabs(b-a) <= step:
        a=b
        return a
    if math.fabs(b-a) >= math.pi:
        if b > a:
            a -= step
            return a
        elif a > b:
            a += step
            return a
    else:
        if b > a:
            a += step
            return a
        elif a > b:
            a -= step
            return a

def chance(chance=1000):
    rand = random.random()
    if rand*chance >= chance-1:
        return True
    else: return False
print "global functions ready"
        
print "making classes"    
#classes for our game objects
class Player(pygame.sprite.Sprite):
    "stores information about the player"
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image, self.rect = load_alphaimage('tass.tga')    #, -1)
        self.nonrotatedimage = self.image
        self.rect.center=(0,0)
        self.viewrect = pygame.Rect(0,0,0,0)
        self.viewrad = math.hypot(self.viewrect[0], self.viewrect[1])
        self.WC = (0,0)
        self.WCdestination = (0,0)
        self.WCview = (0,0)
        self.newmove = False
        self.moving = False
        self.speed = 10
        self.direction = 0
        self.dist = 0
        self.totaltravel = 0
        self.timealive = 0.0
        self.start = False
        self.endgame = False
        self.radius = self.rect.width/2
        self.kills=0
        self.goodies=antalgodisar

    def move(self):
        if self.newmove:
            if self.start == False: self.start = True
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
        

print "player class ok"
class Enemy(pygame.sprite.Sprite):
    def __init__(self, WC=(0,-150)):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image, self.rect = load_alphaimage('car.tga')    #, -1)
        self.nonrotatedimage = self.image
        self.rect.center=(0,0)
        self.startpos=WC
        self.WC = self.startpos
        self.WCdestination = (0,0)
        self.newmove = True
        self.moving = False
        self.speed = 2
        self.direction = 0
        self.dist = 0
        self.rotspeed = 0.02
        self.radius = self.rect.width/2

    def update(self, player):
        self.speed = pow(player.timealive/20000, 1.00)+2
        self.rotspeed = self.speed/100
        if player.start:
            self.moving = True
            self.newmove = False
            self.dist = pos_dist(self.WC, player.WC)
            self.direction = pos_direction(self.WC, player.WC)
            step = pos_step(self.WC, self.direction, self.speed)
            self.WC = step
            self.rect.center = to_sc(self.WC, player.WCview)

    def respawn(self, player):
        self.WC=pos_step(player.WC, random.random()*math.pi*2-math.pi, 300)
        

print "enemy class ok"
class Ground(pygame.sprite.Sprite):
    def __init__(self, WC = (0,0)):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image, self.rect = load_image('4k.jpg')    #, -1)
        self.WC = WC
        
    def update(self, WCview = (0,0)):
        self.rect.center = (self.WC[0]-WCview[0], 0-(self.WC[1]-WCview[1]))

print "ground class ok"

class Hole(pygame.sprite.Sprite):
    def __init__(self, player, safedist):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        maxsize=300
        self.cancrash=True
        self.size=random.random()*40+math.pow(random.random(), 13)*240+20
        self.radius = self.size/2
        self.imagetrans = pygame.Surface((self.size, self.size), SRCALPHA)
        self.imagecircle = pygame.Surface((self.size, self.size), SRCALPHA)
        self.rect = self.imagetrans.get_rect()
        self.imagecircle.fill((255,255,255,0))
        pygame.draw.ellipse(self.imagecircle, (0,0,0), self.rect)
        self.imagetrans.fill((0,0,0,0))
        self.image = self.imagecircle
        self.playerdist=2000
        self.enemydist=2000
        
        self.crash=True
        while self.crash:
            posx=random.random()*(5000-maxsize)-(2500-(maxsize/2))
            posy=random.random()*(5000-maxsize)-(2500-(maxsize/2))
            self.WC = (posx,posy)
            if pos_dist(self.WC, player.WC)+player.radius+self.radius > safedist:
                self.crash = False
                
    def update(self, player, enemylist):
        self.rect.center = (self.WC[0]-player.WCview[0], 0-(self.WC[1]-player.WCview[1]))
        if pygame.sprite.collide_circle(self, player):# and self.cancrash:
            player.endgame=True
        for enemy in enemylist:
            edist=pos_dist(self.WC, enemy.WC)
            edir=pos_direction(self.WC, enemy.WC)
            if edist < self.size/2+enemy.radius:
                enemy.WC=pos_step(self.WC, edir, self.size/2+enemy.radius)
print "hole class ok"

class Goodie(pygame.sprite.Sprite):
    def __init__(self, player, listnumber, holelist):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.size=20
        self.radius = self.size*0.75
        self.image = pygame.Surface((self.size, self.size), SRCALPHA)
        self.rect = self.image.get_rect()
        self.image.fill((255,255,255,0))
        pygame.draw.ellipse(self.image, (255,255,50), self.rect)
        self.playerdist=2000
        self.enemydist=2000
        self.listnumber = listnumber
        
        crash=True
        while crash:
            posx=random.random()*(4000-self.size)-(2000-(self.radius))
            posy=random.random()*(4000-self.size)-(2000-(self.radius))
            self.WC = (posx,posy)
            crash = False
            for hole in holelist:
                if pos_dist(self.WC, hole.WC)+hole.radius+self.radius <= 150:
                crash = True
            if pos_dist(self.WC, player.WC)+player.radius+self.radius <= 150:
                crash = True
                
    def update(self, player, goodielist, goodiegroup):
        #print "upd1"
        self.rect.center = (self.WC[0]-player.WCview[0], 0-(self.WC[1]-player.WCview[1]))
        if pygame.sprite.collide_circle(self, player):
            #print "upd 2"
            player.goodies-=1
            #print "listnum",self.listnumber
            goodiegroup.remove(goodielist[self.listnumber])
            #print "upd3"
            goodielist[self.listnumber]=None
print "goodie class ok"

print "going into main"
def main():
    """this function is called when the program starts.
       it initializes everything it needs, then runs in
       a loop until the function returns."""

#initialize and setup screen
    print "init"
    pygame.init()
    screen = pygame.display.set_mode((800, 600), 0, 32)
    screen.fill ((100, 100, 100))
    print "init ok"

#Create The Backgound
    print "background"
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 100, 100))
    print "background ok"
#Display The Background
    print "1st display"
    screen.blit(background, (0, 0))
    pygame.display.flip()
    print "1st display ok"

#Prepare Game Objects
    print "prep game obj"
    clock = pygame.time.Clock()
    player = Player()
    enemylist = [Enemy((-2500,2500)), Enemy((2500, 2500)), Enemy((2500,-2500)), Enemy((-2500,-2500))]
    player.viewrect = screen.get_rect()
    player.rect.center = player.viewrect.center
    ground = [Ground((0,0)), None, None, None]
    floorsprites = pygame.sprite.Group(ground[0])
    enemies = pygame.sprite.Group(enemylist[0], enemylist[1], enemylist[2], enemylist[3])
    playergroup = pygame.sprite.Group(player)
    holelist = []
    holegroup = pygame.sprite.Group()
    goodielist = []
    goodiegroup = pygame.sprite.Group()
    font = pygame.font.Font(os.path.join(data_dir, 'imagine_font.ttf'), 14)
    endfont = pygame.font.Font(os.path.join(data_dir, 'imagine_font.ttf'), 25)
    print "prep game obj ok"

#Variables
    print "variables"
    moving = False
    isfull=False
    print "variables ok"

    print "making main functions"
    def fullscreen(gofull=False):
        if gofull:
            screen = pygame.display.set_mode((1024, 768), FULLSCREEN)
            player.viewrect = screen.get_rect()
            player.rect.center = player.viewrect.center
        elif not gofull:
            screen = pygame.display.set_mode((640, 480))
            player.viewrect = screen.get_rect()
            player.rect.center = player.viewrect.center
        return screen

    def extendfloor(playero):
        #for sprite in ground:
            
        currentsprite=pygame.sprite.spritecollide(player, floorsprites, False, None)
        cstop=currentsprite[0].WC[1]+2000
        csright=currentsprite[0].WC[0]+2000
        csbottom=currentsprite[0].WC[1]-2000
        csleft=currentsprite[0].WC[0]-2000
        print csleft        
        print currentsprite[0].WC
        return

    def spawnholes(amount, safedist):
        i=0
        while i < amount:
            holelist.append(Hole(player, safedist))
            holegroup.add(holelist[len(holelist)-1])
            i += 1

    def spawngoodies(amount, holegroup):
        #print "spawn1"
        i=0
        while i < amount:
            #print "spwan2"
            goodielist.append(Goodie(player, i, holegroup))
            #print "sp3"
            goodiegroup.add(goodielist[len(goodielist)-1])
            #print "sp4"
            i += 1

    print "main functions ok"
    
    #create some game objects
    print "making holes"
    spawnholes(500, 100)
    print "holes ok, making goodies"
    spawngoodies(antalgodisar, holelist)
    print "goodies ok"

#mainloop
    print "going into main loop"
    going = True
    while going:
        clock.tick(60) #framerate limiter
        if player.totaltravel < 10: player.timealive = 0.0
        else: player.timealive += clock.get_time()

        #Handle Input Events
        for event in pygame.event.get():
            if  event.type == KEYDOWN:
                print "Keypress", event.key            
            if event.type == QUIT:
                going = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                going = False
            elif event.type == KEYDOWN and event.key == 32:    #space
                if player.endgame:
                    player.totaltravel=0
                    player.start=False
                    player.WC = (0,0)
                    player.goodies=antalgodisar
                    for enemy in enemylist:
                        enemy.WC = enemy.startpos
                    player.timealive=0
                    goodielist = []
                    goodiegroup.empty()
                    holelist = []
                    holegroup.empty()
                    spawnholes(500, 100)
                    spawngoodies(antalgodisar, holegroup)
                    player.endgame=False
            elif event.type == KEYDOWN and event.key == 103:    #G
                #print "player", player.WC
                #print "view", player.WCview
                #print "g1", ground.WC
                ground[1] = Ground((4000, 0))
                #print "g2", ground2.WC
                floorsprites.add(ground[1])
                extendfloor(player)
            elif event.type == KEYDOWN and event.key == 120:    #X  random teleport
                randangle=random.random()*math.pi*2-1
                player.jump
                #(random()*4000-2000,random()*4000-2000)
                
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
                else:
                    print "outside"
                    ext = player.WC
                    ext = (ext[0]+math.copysign(2000,ext[0]), ext[1]+math.copysign(2000,ext[1]))
                    #ext = (int(ext[0]), int(ext[1]))
                    print ext[0]
                    print "x", int((ext[0]/4000.0))*4000#)4000#-ext[0]%4000
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                moving = True
            elif event.type == MOUSEBUTTONUP and event.button == 1:
                moving = False

        

        if moving and not player.endgame:
            newdest = to_wc(pygame.mouse.get_pos(), player.WCview)
            if pos_dist(player.WCdestination, newdest) > player.speed*1:
                player.WCdestination = newdest
                player.newmove = True
        
        if chance(500) and not player.endgame and player.start:
            holelist.append(Hole(player, 1000))
            #print len(hole)
            holegroup.add(holelist[len(holelist)-1])
                
        #Move and update all coordinates
        player.move()
        enemies.update(player)
        holegroup.update(player, enemylist)
        goodiegroup.update(player, goodielist, goodiegroup)
        floorsprites.update(player.WCview)
        
        #create texts
        coord=player.WC
        coord=(int(coord[0]/100.0), int(coord[1]/100.0))
        coord=(str(coord[0]), str(coord[1]))
        coord="POS: "+coord[0]+"m"+" "+coord[1]+"m"
        coordsurf = font.render(coord, False, (200,200,100))

        timedisp=player.timealive/1000
        timedisp=int(timedisp)
        timestr="Tid: "+str(timedisp)
        timesurf = font.render(timestr, False, (200,200,100))

        goodiedisp=player.goodies
        goodiestr="Godis kvar: "+str(goodiedisp)
        goodiesurf = font.render(goodiestr, False, (200,200,100))        

        #Draw Everything
        screen.blit(background, (0,0))
        floorsprites.draw(screen)
        playergroup.draw(screen)
        enemies.draw(screen)
        holegroup.draw(screen)
        goodiegroup.draw(screen)
        screen.blit(coordsurf, (10, 10))
        screen.blit(timesurf, (200, 10))
        screen.blit(goodiesurf, (300, 10))
        if not player.endgame:
            pygame.display.flip()

        #Endgame checks
        if not pygame.sprite.collide_rect(player, ground[0]):
            player.endgame=True
        elif len(pygame.sprite.spritecollide(player, enemies, False))>0:
            player.endgame=True

        if player.endgame and player.start:# and (enemy.dist < 20 or -2000 > player.WC[0] or 2000 < player.WC[0] or -2000 > player.WC[1] or 2000 < player.WC[1]):
            endstr = "Krash! Tid: "+str(timedisp)+" sekunder och "+str(goodiedisp)+" godisar kvar!"
            endsurf = endfont.render(endstr, False, (200,0,0))
            screen.blit(endsurf, (10, 100))
            pygame.display.flip()
            hole=[]
            holes=pygame.sprite.Group()
            #player.endgame=True
            player.start=False

    #pygame.quit()
        
#this calls the 'main' function when this script is executed
if __name__ == '__main__':
    main()