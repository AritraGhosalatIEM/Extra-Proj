from itertools import repeat,chain,zip_longest
from functools import total_ordering
from queue import SimpleQueue#,PriorityQueue #Priority queue does not work in python
def straight(player,obstacles,start,to,width,height):
    stepsx,extrax=divmod(abs(start[0]-to[0]),player.velocity_x)
    stepsy,extray=divmod(abs(start[1]-to[1]),player.velocity_y)
    velx=player.velocity_x*((-1)**(start[0]>to[0]))
    vely=player.velocity_y*((-1)**(start[1]>to[1]))
    if start[0]==to[0]:
        xpoints=repeat(start[0])
        ypoints=chain(range(start[1],to[1],vely),(to[1],)) if extray else range(start[1],to[1]+vely,vely)
        return zip(xpoints,ypoints)
    elif start[1]==to[1]:
        ypoints=repeat(start[1])
        xpoints=chain(range(start[0],to[0],velx),(to[0],)) if extrax else range(start[0],to[0]+velx,velx)
        return zip(xpoints,ypoints)
    xpoints=chain(range(start[0],to[0],velx),(to[0],)) if extrax else range(start[0],to[0]+velx,velx)
    ypoints=chain(range(start[1],to[1],vely),(to[1],)) if extray else range(start[1],to[1]+vely,vely)
    return tuple(zip_longest(xpoints,ypoints,fillvalue=to[1] if stepsx>stepsy else to[0]))
@total_ordering
class Node:
    network=None
    disturbed=SimpleQueue()
    @staticmethod
    def safe(point,obstacles,player,width,height):
        for obstacle in obstacles:
            # breakpoint()
            try:
                startx,starty=obstacle.start_prediction
            except AttributeError:#not calculated yet
                startx=-obstacle.rect.width if obstacle.velocity_x>0 else width
                starty=-obstacle.rect.height if obstacle.velocity_y>0 else height
                timex=float('inf') if obstacle.velocity_x==0 else (obstacle.rect.x-startx)//obstacle.velocity_x
                timey=float('inf') if obstacle.velocity_y==0 else (obstacle.rect.y-starty)//obstacle.velocity_y
                if timex>timey:
                    startx=obstacle.rect.x-obstacle.velocity_x*timey
                elif timey>timex:
                    starty=obstacle.rect.y-obstacle.velocity_y*timex
                endx=-obstacle.rect.width if obstacle.velocity_x<0 else width
                endy=-obstacle.rect.width if obstacle.velocity_y<0 else height
                timex=float('inf') if obstacle.velocity_x==0 else (endx-obstacle.rect.x)//obstacle.velocity_x
                timey=float('inf') if obstacle.velocity_x==0 else (endy-obstacle.rect.y)//obstacle.velocity_y
                if timex>timey:
                    endx=obstacle.rect.x+obstacle.velocity_x*timey
                elif timey>timex:
                    endy=obstacle.rect.y+obstacle.velocity_y*timex
                assert startx==obstacle.start_x and starty==obstacle.start_y
                obstacle.start_prediction=(startx,starty)
                obstacle.step_prediction=(endy-starty)//obstacle.velocity_y if obstacle.velocity_x==0 else (endx-startx)//obstacle.velocity_x
            finally:
                current_step=(obstacle.rect.y-starty)//obstacle.velocity_y if obstacle.velocity_x==0 else (obstacle.rect.x-startx)//obstacle.velocity_x
                future_step=(current_step+point.distance)%obstacle.step_prediction
                futurex=future_step*obstacle.velocity_x+startx
                futurey=future_step*obstacle.velocity_y+starty
                futurexend=futurex+obstacle.rect.width
                futureyend=futurey+obstacle.rect.height
                playerx=point.coordinates[0]-player.rect.width//2
                playery=point.coordinates[1]-player.rect.height//2
                playerxend=point.coordinates[0]+player.rect.width//2
                playeryend=point.coordinates[1]+player.rect.height//2
                if not (playerxend<futurex or playerx>futurexend or playeryend<futurey or playery>futureyend):
                    return False
            return True
    @classmethod
    def create_network(cls,width,height,horizontal_separation,vertical_separation):
        cls.network=tuple(tuple((Node((j,i)) for j in range(0,width,horizontal_separation))) for i in range(0,height,vertical_separation))
        #corners
        cls.network[0][0].neighbours=(cls.network[0][1],cls.network[1][1],cls.network[1][0])
        cls.network[0][-1].neighbours=(cls.network[0][-2],cls.network[1][-2],cls.network[1][-1])
        cls.network[-1][0].neighbours=(cls.network[-1][1],cls.network[-2][-2],cls.network[-2][-1])
        cls.network[-1][-1].neighbours=(cls.network[-1][-2],cls.network[-2][-2],cls.network[-2][-1])
        #borders
        for index,node in enumerate(cls.network[0][1:-1],start=1):node.neighbours=(cls.network[0][index-1],cls.network[1][index-1],cls.network[1][index],cls.network[1][index+1],cls.network[0][index+1])
        for index,node in enumerate(cls.network[-1][1:-1],start=1):node.neighbours=(cls.network[-1][index-1],cls.network[-2][index-1],cls.network[-2][index],cls.network[-2][index+1],cls.network[-1][index+1])
        for index in range(1,len(cls.network)-1):cls.network[index][0].neighbours=(cls.network[index-1][0],cls.network[index-1][1],cls.network[index][1],cls.network[index+1][1],cls.network[index+1][0])
        for index in range(1,len(cls.network)-1):cls.network[index][0].neighbours=(cls.network[index-1][0],cls.network[index-1][1],cls.network[index][1],cls.network[index+1][1],cls.network[index+1][0])
        for index in range(1,len(cls.network)-1):cls.network[index][-1].neighbours=(cls.network[index-1][-1],cls.network[index-1][-2],cls.network[index][-2],cls.network[index+1][-2],cls.network[index+1][-1])
        #middle
        for row,i in enumerate(cls.network[1:-1],start=1):
            for column,node in enumerate(i[1:-1],start=1):
                node.neighbours=(cls.network[row-1][column-1],cls.network[row-1][column],cls.network[row-1][column+1],cls.network[row][column-1],cls.network[row][column+1],cls.network[row+1][column-1],cls.network[row+1][column],cls.network[row+1][column+1])
    @classmethod
    def reset_all(cls):
        while not cls.disturbed.empty():
            node=cls.disturbed.get_nowait()
            node.distance=float('inf')
            node.cost=float('inf')
            node.parent=None
    def __init__(self,coordinates):
        self.coordinates=coordinates
        self._distance=float('inf')
        self.cost=float('inf')
        self.parent=None
        self.neighbours=None
    @property
    def distance(self):return self._distance
    @distance.setter
    def distance(self,value):
        if value!=float('inf') and self._distance==float('inf'):Node.disturbed.put(self)
        self._distance=value
    def __lt__(self,other):return self.cost<other.cost
    def __eq__(self,other):return self.cost==other.cost
def a_star(player,obstacles,start,to,width,height):
    if Node.network==None:
        Node.create_network(width,height,player.velocity_x,player.velocity_y)
    start_node=Node.network[start[1]//player.velocity_y][start[0]//player.velocity_x]
    end_node=Node.network[to[1]//player.velocity_y][to[0]//player.velocity_x]
    nodes=list(chain(*Node.network))#should be priority queue
    start_node.distance=0
    start_node.cost=0#doesn't matter
    current=None
    while not(current is end_node):
        current=min(nodes)#priority queue behavior
        nodes.remove(current)#priority queue behavior
        for neighbour in current.neighbours:
            if neighbour.distance>(current.distance+1):
                neighbour.parent=current
                neighbour.distance=current.distance+1
                if Node.safe(neighbour,obstacles,player,width,height):
                    neighbour.cost=neighbour.distance+int(((end_node.coordinates[0]-current.coordinates[0])**2+(end_node.coordinates[1]-current.coordinates[1])**2)**0.5)
                else:
                    neighbour.cost=float('inf')
    path=[]
    while not(current is None):
        path.insert(0,current.coordinates)
        current=current.parent
    Node.reset_all()
    return path
