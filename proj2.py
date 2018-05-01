"""
File: proj2.py -- Dana, April 24, 2018
A simple-minded proj2 program. It uses racetrack.py to find a path to the goal
ignoring the possibility of steering erros, and returns the first move in this path.
"""

import time
import heuristics
import racetrack   # program that runs fsearch
import math


# Your proj2 function
def main(state,finish,walls):
    ((x,y), (u,v)) = state
    f = open('choices.txt', 'w')
    path = racetrack.main(state,finish,walls,'gbf', heuristics.h_walldist, verbose=0, draw=0)
    print('  Proj2: path =', path)
    for i in range(len(path)):
        print('  Proj2: path[',i,'] =', path[i])
        if path[i] == state:
            print('  Proj2: found state', state)
            velocity = path[i+1][1]
            print('  Proj2: new velocity', velocity)
            break
    print(velocity,file=f,flush=True)

def initialize(state,fline,walls):
    print('Unfortunately, this work will be lost when the process exits.')
    heuristics.edist_grid(fline,walls)

def edist_to_line(point, edge):
    """
    Euclidean distance from (x,y) to the line ((x1,y1),(x2,y2)).
    """
    (x,y) = point
    ((x1,y1),(x2,y2)) = edge
    if x1 == x2:
        ds = [math.sqrt((x1-x)**2 + (y3-y)**2) \
            for y3 in range(min(y1,y2),max(y1,y2)+1)]
    else:
        ds = [math.sqrt((x3-x)**2 + (y1-y)**2) \
            for x3 in range(min(x1,x2),max(x1,x2)+1)]
    return min(ds)
                

