from itertools import repeat,chain,zip_longest
def straight(player,obstacles,start,to):
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
