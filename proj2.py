"""
File: proj2.py -- Dana, April 24, 2018
A simple-minded proj2 program. It uses racetrack.py to find a path to the goal
ignoring the possibility of steering erros, and returns the first move in this path.
"""

import time
import heuristics
import racetrack   # program that runs fsearch
import math

# min the prob of crash 
# min number of moves

# think: how to deal with the state currently not a crash, but the probability of crashing
# in next move is 1 ?????????????????????????????????????


# V(s) inf for crash no matter what

# Your proj2 function
def main(state,finish,walls):
    ((x,y), (u,v)) = state
    f = open('choices.txt', 'w')

    lao_star(state, finish, walls)
    velocity = policy[state]

    print(velocity,file=f,flush=True)

# helper functions
policy = {} # empty dictionary for policy pi; choices for z (not mv action list)
V = {} # empty dictionary for value function V
Envelope = set() # generated states

def lao_star(state, finish, walls):
    # V0 from initialize (first let them to be 0)
    Envelope.add(state)

    # debug, correct: {}, {}, {(2,2),(0,0)}
    # print(policy)
    # print(V)
    # print(Envelope)
    # print("debug")
    # V <- V0:
    if not next_possible_states(state, walls):
            # dead end
            V[state] = 1000 
            print("What  !!!!")
    else:
        V[state] = heuristics.h_esdist(state, finish, walls)
    while leaves_not_goal(state, policy, finish):
    # debug
    # count = 0
        # Python never implicitly copies objects
        # dict2 = dict(dict1)
        old_policy = dict(policy)
        s = leaves_not_goal(state, policy, finish).pop()
        if not next_possible_states(s, walls):
            # dead end
            V[s] = 1000 
        for s1 in next_possible_states(s, walls) - Envelope:
            Envelope.add(s1)
            # print("I am here !!!")
            # racetrack.crash((loc,newloc),walls)
            if racetrack.crash((s[0],s1[0]), walls):
                print("I am crash! YAYA  !!!!!!")
                V[s1] = 10000
            else:
                V[s1] = heuristics.h_esdist(s1, finish, walls)
        ######### debug #####################
        # print("Before lao update")
        lao_update(state, s, finish, walls)
        # print("After lao update")
        # count += 1
        # if count % 15 == 0:
        #     print(policy) # problem: policy not changed
        if(old_policy != policy):
            print(policy)
        else:
            break

    return policy

def lao_update(s0, s, finish, walls):
    """ LAO Update"""
    # here !!!!!! s in transitive closure, not s1 !!!!!!!!!!!!
    Z = {s} | {s1 for s1 in Envelope if s in transitive_closure(s1, policy)}
    old_leaves = (transitive_closure(s0, policy) - set(policy)).copy()
    while  True:
        r = - math.inf
        for state in Z:
            # print(" I am here!!!!") a lot of times after the last updated policy
            r_s = bellman_update(state, finish, walls)
            if r_s > r:
                r = r_s
        new_leaves = transitive_closure(s0, policy) - set(policy)
        if old_leaves != new_leaves or r <= 0.2:
            return

def bellman_update(state, finish, walls):
    """ bellman update"""
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
    if dead_end:
        print("Dead End!!!")
        V[state] = 10000
        # del policy[state]     wrong ......
    # debug
    # print("at the end of bellman_update")
    # print(abs(v_old - V[state]))
    return abs(v_old - V[state])



##################################### helper functions ###################################

def leaves_not_goal(s0, policy, finish):
    """ return a set of leaves that are not in goal set"""
    result = set()
    for s_leaf in transitive_closure(s0, policy) - set(policy):
        if not racetrack.goal_test(s_leaf,finish):
            result.add(s_leaf)
    return result

def cost_to_go(s, z, finish, walls):
    """ calculate cost to go Q(s,z) 
    s: state, z:velocity (u, v) """
    # key: think how to deal with crash
    # racetrack.crash((loc,newloc),walls)
    (u, v) = z
    (x_correct, y_correct) = (s[0][0]+u, s[0][1]+v) # next correct state without error
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
        if s_next not in V:
            # initialize
            V[s_next] = heuristics.h_esdist(s_next, finish, walls)
            if racetrack.crash((s[0],s_next[0]), walls):
                V[s_next] += 10000
                # debug
                print((s[0],s_next[0]))
                print("I am in crash !!!")
            # debug:
            # print(s_next)
            # print("probability " + str(weight))
            # print(V[s_next])
        cost += weight * V[s_next]
    return (1 + cost)




def transitive_closure(s, policy):
    """ transitive closure 
    {s and all descendants of s reachable by policy pi} """
    ## To think: how to handle the crash case?????
    result = set()
    Z = {s}
    while len(Z) > 0:
        state = Z.pop()
        result.add(state)
        if state in policy:
            (u, v) = policy[state]
            next_states = next_possible_states_with_z(state, (u, v))
            Z.update(next_states)
    return result

def next_possible_states(state, walls):
    # this is wrong !!!!!
    # next_states(state,walls):
    """Return a list of states we can go to from state"""
    result = set()
    for s in racetrack.next_states(state, walls):
        # choose a in Applicable(s)
        result.update(next_possible_states_with_z(state, s[1]))
    return result

def next_possible_states_with_z(state, z):
    """ next possible states
    state: current state (p_cur, z_cur)
    z: chosen velocity to move """

    (x, y) = state[0]
    (u, v) = z
    result = set()
    # possible velocities
    u_possible = {u} if abs(u) <= 1 else {u-1, u, u+1}
    v_possible = {v} if abs(v) <= 1 else {v-1, v, v+1}
    for u_next in u_possible:
        for v_next in v_possible:
            s_next = ((x+u_next, y+v_next),z)
            result.add(s_next)
    return result


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
                
######## test ##############
# s = ((10, 8), (1, 1))
# # z = (1, 1)
# # z = (1, 2)
# z = (2, 2)
# print(next_possible_states(s, z))   # done


# transitive_closure(s, policy):
""" transitive closure {s and all descendants of s reachable by policy pi} """

# policy = {}
# s = ((5,5), (2,3))
# policy[s] = (3, 4)

# print(transitive_closure(s, policy))


# test cost to go:
# rect20a = [(5,12), [(15,5),(15,15)],
#     [[(0,0),(20,0)], [(20,0),(20,20)], [(20,20),(0,20)], [(0,20),(0,0)]]]

# s = ((5,12),(3,2))
# z = (4,8)
# finish = rect20a[1]
# walls = rect20a[2]
# print(cost_to_go(s, z, finish, walls))















