from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT']='hide'
from pygame import init,quit
from pygame.display import list_modes,set_mode,set_caption,set_icon,flip
from pygame.event import get as get_events
from pygame.time import Clock
from pygame.sprite import Group,GroupSingle,Sprite,spritecollide
from pygame.image import load as load_image
from pygame.transform import scale_by
from pygame.mouse import get_pos
from pygame.locals import QUIT,MOUSEBUTTONDOWN
from pygame.draw import circle,lines
from random import randint,uniform,choice
from itertools import count,cycle
from sys import exit
from os.path import join
from config import *
from algorithms import a_star as algorithm
init()
WIDTH,HEIGHT=list_modes()[0]
surface=set_mode((WIDTH,HEIGHT))
set_caption("Path")
set_icon(load_image(join('assets','logo.png')))
clock=Clock()
obstacles=Group()
destination=start=None
class Obstacle(Sprite):
    obstacle_img=load_image(join('assets','obstacle.png')).convert_alpha()
    def __init__(self):
        Sprite.__init__(self)
        self.image=scale_by(Obstacle.obstacle_img,uniform(*OBSTACLE_SIZE))
        self.rect=self.image.get_rect()
        #start from any border
        if choice((True,False)):#vertical border
            if choice((True,False)):#left border
                self.start_x=-self.rect.width
                self.velocity_x=randint(0,MAX_OBSTACLE_VELOCITY_X)
            else:#right border
                self.start_x=WIDTH
                self.velocity_x=randint(-MAX_OBSTACLE_VELOCITY_X,0)
            self.start_y=randint(0,HEIGHT)
            self.velocity_y=randint(-MAX_OBSTACLE_VELOCITY_Y,MAX_OBSTACLE_VELOCITY_Y)
        else:#horizontal border
            if choice((True,False)):#top border
                self.start_y=-self.rect.height
                self.velocity_y=randint(0,MAX_OBSTACLE_VELOCITY_Y)
            else:#bottom border
                self.start_y=HEIGHT
                self.velocity_y=randint(-MAX_OBSTACLE_VELOCITY_Y,0)
            self.start_x=randint(0,WIDTH)
            self.velocity_x=randint(-MAX_OBSTACLE_VELOCITY_X,MAX_OBSTACLE_VELOCITY_X)
        if self.velocity_x==0:
            xrange=(self.start_x,)
        elif self.velocity_x<0:
            xrange=range(self.start_x,-self.rect.width,self.velocity_x)
        else:
            xrange=range(self.start_x,WIDTH,self.velocity_x)
        if self.velocity_y==0:
            yrange=(self.start_y,)
        elif self.velocity_y<0:
            yrange=range(self.start_y,-self.rect.width,self.velocity_y)
        else:
            yrange=range(self.start_y,WIDTH,self.velocity_y)
        self.position=cycle(zip(xrange,yrange))
        obstacles.add(self)
    def update(self):
        self.rect.x,self.rect.y=next(self.position)
class Me(Sprite):
    my_img=load_image(join('assets','player.png')).convert_alpha()
    def __init__(self):
        Sprite.__init__(self)
        self.image=scale_by(Me.my_img,1)
        self.rect=self.image.get_rect()
        self.velocity_x=MY_VELOCITY_X
        self.velocity_y=MY_VELOCITY_Y
        self.moving=False
        self.path=[]
        self.point=None
    def move(self):
        self.moving=True
        self.path=algorithm(self,obstacles,start,destination,WIDTH,HEIGHT)
        self.point=(p for p in self.path)
    def update(self):
        try:
            self.rect.center=next(self.point)
        except StopIteration:
            global start,destination
            start=destination=None
            self.moving=False
for _ in range(randint(*NUMBER_OF_OBSTACLES)):Obstacle()
me=Me()
my_group=GroupSingle(me)
#game loop
while True:
    #collision check
    assert not me.moving or len(spritecollide(me,obstacles,False))==0,'collision'
    #wait
    clock.tick(FPS)
    #events
    for event in get_events():
        if event.type==QUIT:
            quit()
            exit(0)
        elif event.type==MOUSEBUTTONDOWN and not me.moving:
            if start==None:
                start=get_pos()
            else:
                destination=get_pos()
                me.move()
    #update
    obstacles.update()
    #render
    surface.fill(BACKGROUND_COLOR)
    if start!=None:circle(surface,START_COLOR,start,POINT_DIAMETER,0)
    if destination!=None:
        circle(surface,DESTINATION_COLOR,destination,POINT_DIAMETER,0)
        lines(surface,PATH_COLOR,False,me.path,PATH_WIDTH)
        my_group.update()
        my_group.draw(surface)
    obstacles.draw(surface)
    #show
    flip()
