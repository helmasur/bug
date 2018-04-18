import os, pygame
import sys
import time
from pygame.locals import *
import random
import math

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')

#functions to create our resources
def load_image	(filename):
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

    def move(self):
        #self.speed = pow(self.timealive/10000, 1.24)+2.2
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
        

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image, self.rect = load_alphaimage('car.tga')    #, -1)
        self.nonrotatedimage = self.image
        self.rect.center=(0,0)
        self.WC = (0,-150)
        self.WCdestination = (0,0)
        self.newmove = True
        self.moving = False
        self.speed = 2
        self.direction = 0
        self.dist = 0
        self.rotspeed = 0.02
        self.radius = self.rect.width/2

    def move(self, player):
        self.speed = pow(player.timealive/10000, 1.2)+2
        self.rotspeed = self.speed/100
        if player.start:
            self.moving = True
            self.newmove = False
            self.dist = pos_dist(self.WC, player.WC)
            #olddir=self.direction
            self.direction = pos_direction(self.WC, player.WC)
            #newdir = pos_direction(self.WC, player.WC)
            #self.direction = seekangle(olddir, newdir, self.rotspeed)
            step = pos_step(self.WC, self.direction, self.speed)
            #step = [self.WC[0]+(self.speed*math.cos(self.direction)), self.WC[1]+(self.speed*math.sin(self.direction))]
            self.WC = step

    def respawn(self, player):
        self.WC=pos_step(player.WC, random.random()*math.pi*2-math.pi, 300)

    def update(self, WCview = (0,0)):
        self.rect.center = to_sc(self.WC, WCview)

class Ground(pygame.sprite.Sprite):
    def __init__(self, WC = (0,0)):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image, self.rect = load_image('4k.jpg')    #, -1)
        self.WC = WC
        
    def update(self, WCview = (0,0)):
        self.rect.center = (self.WC[0]-WCview[0], 0-(self.WC[1]-WCview[1]))

class Hole(pygame.sprite.Sprite):
    def __init__(self, player):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        maxsize=300
        #posx=random.random()*(4000-maxsize)-(2000-(maxsize/2))
        #posy=random.random()*(4000-maxsize)-(2000-(maxsize/2))
        self.size=math.pow(random.random(), 10)*300+20
        #print "Size",self.size
        self.radius = self.size/2
        self.image = pygame.Surface((self.size, self.size), SRCALPHA)
        self.image.fill((255,255,255,0))
        self.rect = self.image.get_rect()
        self.WC=pos_step(player.WC, random.random()*math.pi*2-math.pi, 800)
        #self.WC = (posx,posy)
        pygame.draw.ellipse(self.image, (0,0,0), self.rect)
        
    def update(self, player, enemy):
        self.rect.center = (self.WC[0]-player.WCview[0], 0-(self.WC[1]-player.WCview[1]))
        if player.speed > self.size:
            self.image.set_alpha(0)
        else: self.image.set_alpha(255)
        if pygame.sprite.collide_circle(self, player):
            player.endgame=True
        elif pygame.sprite.collide_circle(self, enemy):
            player.kills+=1
            enemy.respawn(player)


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
    clock = pygame.time.Clock()
    player = Player()
    enemy = Enemy()
    
    #view = Viewport()
    player.viewrect = screen.get_rect()
    player.rect.center = player.viewrect.center
    ground = [Ground((0,0)), None, None, None]
    floorsprites = pygame.sprite.Group(ground[0])
    actors = pygame.sprite.Group(player, enemy)		#order makes layers, first on top
    hole = []
    holes = pygame.sprite.Group()
    font = pygame.font.Font(os.path.join(data_dir, 'imagine_font.ttf'), 14)
    endfont = pygame.font.Font(os.path.join(data_dir, 'imagine_font.ttf'), 30)



#Variables
    moving = False
    isfull=False
    
    def fullscreen(gofull=False):
        if gofull:
            screen = pygame.display.set_mode((1024, 768), FULLSCREEN|HWSURFACE|DOUBLEBUF)
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
    def spawncar():
        return
        

#mainloop
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
                    enemy.WC = (0,-150)
                    player.timealive=0
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
        
        if chance(10) and not player.endgame and player.start:
            hole.append(Hole(player))
            #print len(hole)
            holes.add(hole[len(hole)-1])
                
        #Move and update all coordinates
        player.move()
        enemy.move(player)
        enemy.update(player.WCview)
        holes.update(player, enemy)
        
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

        timedisp=player.timealive/1000
        timedisp=int(timedisp)
        timestr="Tid: "+str(timedisp)
        timesurf = font.render(timestr, False, (200,200,100))
        

        #Draw Everything
        screen.blit(background, (0,0))
        floorsprites.draw(screen)
        actors.draw(screen)
        holes.draw(screen)
        screen.blit(coordsurf, (10, 10))
        screen.blit(timesurf, (200, 10))
        if not player.endgame:
            pygame.display.flip()

        #Endgame checks
        if not pygame.sprite.collide_rect(player, ground[0]):
            player.endgame=True
        elif pygame.sprite.collide_circle(player, enemy):
            player.endgame=True

        if player.endgame and player.start:# and (enemy.dist < 20 or -2000 > player.WC[0] or 2000 < player.WC[0] or -2000 > player.WC[1] or 2000 < player.WC[1]):
            endstr = "Krash! Tid: "+str(timedisp)+" sekunder"
            endsurf = endfont.render(endstr, False, (200,0,0))
            screen.blit(endsurf, (50, 100))
            pygame.display.flip()
            hole=[]
            holes=pygame.sprite.Group()
            #player.endgame=True
            player.start=False

    #pygame.quit()
        
#this calls the 'main' function when this script is executed
if __name__ == '__main__':
    main()