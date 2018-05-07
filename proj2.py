"""
File: proj2.py -- Dana, April 24, 2018
A simple-minded proj2 program. It uses racetrack.py to find a path to the goal
ignoring the possibility of steering erros, and returns the first move in this path.
"""

import time
import heuristics
import racetrack   # program that runs fsearch
import math
import random                   # get random.choice

# Your proj2 function
def main(state,finish,walls):
    
    lao_star(state, finish, walls)
    velocity = policy[state]
    f = open('choices.txt', 'w')
    print(velocity,file=f,flush=True)


#################################### LAO * #######################################
# global variables for LAO*
policy = {} # empty dictionary for policy pi; choices for z (not mv action list)
V = {} # empty dictionary for value function V
Envelope = set() # generated states, this is also for UCT

def lao_star(s0, finish, walls):
    """ LAO * algorithm """
    Envelope.add(s0)

    if not next_possible_states(s0, walls):
            # starting at dead end
            V[s0] = 100
            print("What  !!!! The starting point is a dead end!!!")
    else:
        V[s0] = heuristics.h_walldist(s0, finish, walls)

    count = 0
    init = False
    while leaves_not_goal(s0, policy, finish):

        old_policy = dict(policy)
        s = leaves_not_goal(s0, policy, finish).pop()
        if not next_possible_states(s, walls):
            # dead end
            V[s] = 100
        for s1 in next_possible_states(s, walls) - Envelope:
            Envelope.add(s1)
            if racetrack.crash((s[0],s1[0]), walls):
                V[s1] = 100
            else:
                V[s1] = heuristics.h_walldist(s1, finish, walls)
        # lao star
        lao_update(s0, s, finish, walls)
        # ao_update(s, finish, walls)


        if(init and old_policy[s0] == policy[s0]):
            # the new policy doesn't change the action taken at state s0
            count += 1
        if count > 15:
            print("Exit !!! ")
            break
        init = True
    return policy

def lao_update(s0, s, finish, walls):
    """ LAO Update """
    Z = {s} | {s1 for s1 in Envelope if s in transitive_closure(s1, policy)}
    old_leaves = (transitive_closure(s0, policy) - set(policy)).copy()
    while  True:
        r = - math.inf
        for state in Z:
            r_s = bellman_update(state, finish, walls)
            if r_s > r:
                r = r_s
        new_leaves = transitive_closure(s0, policy) - set(policy)
        if old_leaves != new_leaves or r <= 0.2:
            return

def ao_update(s, finish, walls):

    Z = {s}

    while Z:
        for state in Z:
            if transitive_closure(s, policy) & Z =={s}:
                bellman_update(state, finish, walls)
                Z.remove(state)
                break
        Z = Z | {s1 for s1 in Envelope if s in transitive_closure(s1,policy)}



def bellman_update(state, finish, walls):
    """ bellman update """
    v_old = V[state]
    min_cost = math.inf;
    # applicable actions in state
    dead_end = True
    for next_state in racetrack.next_states(state,walls):
        dead_end = False
        (p_next, (u_next, v_next)) = next_state
        cost = cost_to_go(state, (u_next, v_next), finish, walls)
        if cost < min_cost:
            V[state] = cost
            policy[state] = (u_next, v_next)
            min_cost = cost
    if dead_end:
        V[state] = 100
    return abs(v_old - V[state])

############################### helper functions ##############################

def leaves_not_goal(s0, policy, finish):
    """ return a set of leaves that are not in goal set """
    result = set()
    for s_leaf in transitive_closure(s0, policy) - set(policy):
        if not racetrack.goal_test(s_leaf,finish):
            result.add(s_leaf)
    return result

def cost_to_go(s, z, finish, walls):
    """ calculate cost to go Q(s,z) 
        s:current state, z:velocity (u,v) """
    (u, v) = z
    # next correct state without error:
    (x_correct, y_correct) = (s[0][0]+u, s[0][1]+v)
    # probability mass function:
    u_same = 0.6 if abs(u) > 1 else 1
    u_diff = 0.2
    v_same = 0.6 if abs(v) > 1 else 1
    v_diff = 0.2
    cost = 0
    for ((x_next, y_next), z_next) in next_possible_states_with_z(s, z):
        weight = (u_same * (x_next == x_correct) +  \
                  u_diff * (x_next != x_correct)) * \
                 (v_same * (y_next == y_correct) +  \
                  v_diff * (y_next != y_correct))
        s_next = ((x_next,y_next),z_next)

        # penalize not moving if not at the goal state
        if not racetrack.goal_test(s_next,finish):
            if z_next == (0,0):
                V[s_next] = 100

        if racetrack.crash((s[0],s_next[0]), walls):
            V[s_next] = 100

        cost += weight * V[s_next]
    return (1 + cost)


def transitive_closure(s, policy):
    """ transitive closure:
    {s and all descendants of s reachable by policy pi} """
    result = set()
    Z = {s}
    while len(Z) > 0:
        state = Z.pop()
        result.add(state)
        if state in policy:
            (u, v) = policy[state]
            next_states = next_possible_states_with_z(state, (u, v))
            # avoid the loop:
            Z.update(next_states - result)
    return result

def next_possible_states(state, walls):
    """ next possible states we can go to from current state """
    result = set()
    for s in racetrack.next_states(state, walls):
        # choose a in Applicable(s)
        result.update(next_possible_states_with_z(state, s[1]))
    return result

def next_possible_states_with_z(state, z):
    """ next possible states from current state
        with the chosen velocity z """
    (x, y) = state[0]  # current location
    (u, v) = z         # chosen velocity
    result = set()
    # possible velocities
    u_possible = {u} if abs(u) <= 1 else {u-1, u, u+1}
    v_possible = {v} if abs(v) <= 1 else {v-1, v, v+1}
    for u_next in u_possible:
        for v_next in v_possible:
            s_next = ((x+u_next, y+v_next),z)
            result.add(s_next)
    return result

# def initialize(state,fline,walls):
#     print('Unfortunately, this work will be lost when the process exits.')
#     heuristics.edist_grid(fline,walls)

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



