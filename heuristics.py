"""
File: heuristics.py -- Dana Nau, Feb 14, 2018

This file contains three heuristic functions:
- h_edist returns the Euclidean distance from (s) to the goal, ignoring walls;
- h_esdist modifies h_edist to include an estimate of how long it will take to stop;
- h_walldist computes the approximate distance to the goal without ignoring walls. 

 Each heuristic function takes three arguments: state, edge, walls.
   state is the current state. It should have the form ((x,y), (u,v))
   edge is the finish line. It should have the form ((x1,y1), (x2,y2))
   walls is a list of walls, each wall having the form ((x1,y1), (x2,y2))
"""

import racetrack,math
import sys              # to get readline


def h_edist(state, edge, walls):
    """Euclidean distance from state to edge, ignoring walls."""
    (x,y) = state[0]
    ((x1,y1),(x2,y2)) = edge
    
    # find the smallest and largest coordinates
    xmin = min(x1,x2); xmax = max(x1,x2)
    ymin = min(y1,y2); ymax = max(y1,y2)

    return min([math.sqrt((xx-x)**2 + (yy-y)**2)
        for xx in range(xmin,xmax+1) for yy in range(ymin,ymax+1)])


def h_esdist(state, fline, walls):
    """
    h_edist modified to include an estimate of how long it will take to stop.
    """
    ((x,y),(u,v)) = state
    m = math.sqrt(u**2+v**2)
    stop_dist = m*(m-1)/2.0
    return max(h_edist(state, fline, walls)+stop_dist/10.0,stop_dist)


# Global variables for h_walldist

# in Python 3 we can just use math.inf, but that doesn't work in Python 2
infinity = float('inf')

g_fline = False
g_walls = False
grid = []


def h_walldist(state, fline, walls):
    """
    The first time this function is called, for each gridpoint that's not inside a wall
    it will cache a rough estimate of the length of the shortest path to the finish line.
    The computation is done by a breadth-first search going backwards from the finish 
    line, one gridpoint at a time.
    
    On all subsequent calls, this function will retrieve the cached value and add an
    estimate of how long it will take to stop. 
    """
    global g_fline, g_walls
    if fline != g_fline or walls != g_walls or grid == []:
        edist_grid(fline, walls)
    ((x,y),(u,v)) = state
    hval = float(grid[x][y])
    
    # add a small penalty to favor short stopping distances
    au = abs(u); av = abs(v); 
    sdu = au*(au-1)/2.0
    sdv = av*(av-1)/2.0
    sd = max(sdu,sdv)
    penalty = sd/10.0

    # compute location after fastest stop, and add a penalty if it goes through a wall
    if u < 0: sdu = -sdu
    if v < 0: sdv = -sdv
    sx = x + sdu
    sy = y + sdv
    if racetrack.crash([(x,y),(sx,sy)],walls):
        penalty += math.sqrt(au**2 + av**2)
    hval = max(hval+penalty,sd)
    return hval

def edist_grid(fline,walls):
    global grid, g_fline, g_walls, xmax, ymax
    xmax = max([max(x,x1) for ((x,y),(x1,y1)) in walls])
    ymax = max([max(y,y1) for ((x,y),(x1,y1)) in walls])
    grid = [[edistw_to_line((x,y), fline, walls) for y in range(ymax+1)] for x in range(xmax+1)]
    flag = True
    print('computing edist grid', end=' '); sys.stdout.flush()
    while flag:
        print('.', end=''); sys.stdout.flush()
        flag = False
        for x in range(xmax+1):
            for y in range(ymax+1):
                for y1 in range(max(0,y-1),min(ymax+1,y+2)):
                    for x1 in range(max(0,x-1),min(xmax+1,x+2)):
                        if grid[x1][y1] != infinity and not racetrack.crash(((x,y),(x1,y1)),walls):
                            if x == x1 or y == y1:
                                d = grid[x1][y1] + 1
                            else:
                                d = grid[x1][y1] + 1.4142135623730951
                            if d < grid[x][y]:
                                grid[x][y] = d
                                flag = True
    print(' done')
    g_fline = fline
    g_walls = walls
    return grid


def edistw_to_line(point, edge, walls):
    """
    straight-line distance from (x,y) to the line ((x1,y1),(x2,y2)).
    Return infinity if there's no way to do it without intersecting a wall
    """
#   if min(x1,x2) <= x <= max(x1,x2) and  min(y1,y2) <= y <= max(y1,y2):
#       return 0
    (x,y) = point
    ((x1,y1),(x2,y2)) = edge
    if x1 == x2:
        ds = [math.sqrt((x1-x)**2 + (y3-y)**2) \
            for y3 in range(min(y1,y2),max(y1,y2)+1) \
            if not racetrack.crash(((x,y),(x1,y3)), walls)]
    else:
        ds = [math.sqrt((x3-x)**2 + (y1-y)**2) \
            for x3 in range(min(x1,x2),max(x1,x2)+1) \
            if not racetrack.crash(((x,y),(x3,y1)), walls)]
    ds.append(infinity)
    return min(ds)

def distance(p1, p2):
    (x1,y1) = p1
    (x2,y2) = p2
    return math.sqrt((x1-x2)**2 + (y1-y2)**2)

