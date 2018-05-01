"""
File: supervisor.py -- Dana Nau, April 17, 2018
A simple supervisor for Project 2.
"""

import math, sys
import multiprocessing as mp
from sample_probs import *
import random                   # get random.choice
import ast						# get ast.literal_eval
import tdraw, turtle			# Code to use Python's "turtle drawing" package
import proj2					# File containing your programs for Project 2


def main(problem=rhook16b, time_limit=5):
	"""
	Call proj2.main and wait for time_limit (default 5) number of seconds, then
	kill it and read the last velocity it put into choices.txt. If the velocity
	is (0,0) and the position is on the finish line, the run ends successfully. 
	Otherwise, add an error to the velocity, and draw the move in the graphics window.
	If the move crashes into a wall, the run ends unsuccessfully.
	"""	
	print('Problem:', problem)
	(p0, f_line, walls) = problem
	
	turtle.Screen()				# open the graphics window
	tdraw.draw_problem((p0, f_line, walls))
	
	(x,y) = p0
	(u,v) = (0,0)

	# If proj2 includes an initialization procedure, call it to cache some data
	if 'initialize' in dir(proj2):
		print('Calling proj2.initialize.')
		p = mp.Process(target=proj2.initialize, \
			args = (((x,y),(u,v)), f_line, walls, ))
		p.start()
		# Wait for 10 seconds (the time limit I specified on Piazza)
		p.join(10)
		if p.is_alive():
			print('\nWarning: terminating proj2.initialize at 10 seconds.')
			print('This means its output may be incomplete.')
		p.terminate()
	else:
		print("Note: proj2.py doesn't contain an initialize program.")

	while True:

		if goal_test((x,y), (u,v), f_line):
			print('\nYour program completed a successful run.')
			break

		(u, v, ok) = get_proj2_choice((x,y), (u,v), f_line, walls, time_limit)
		if ok == False:
			print("\nYour program didn't produce a correct move.")
			break 

		draw_edge(((x,y), (x+u, y+v)), 'green') 
		error = steering_error(u,v)
		(xnew,ynew) = (x+u+error[0], y+v+error[1])
		print('proj2 chose velocity {}, steering error is {}, result is {}'.format( \
			(u,v), error, (xnew,ynew)))
		edge = ((x,y), (xnew, ynew))
		draw_edge(edge, 'red') 
		if crash(edge, walls):
			print('\nYou have crashed.')
			break		
		(x,y) = (xnew, ynew)

def steering_error(u,v):
    """
    return steering error e = (q,r), given the velocity (u,v) chosen by the user.
    If u is small enough, q=0. Otherwise q = -1,0,1 with probabilities 0.2, 0.6, 0.2.
    If v is small enough, r=0. Otherwise r = -1,0,1 with probabilities 0.2, 0.6, 0.2.
    """
    if abs(u) <= 1:
        q = 0
    else:
        q = random.choice([-1,0,0,0,1])
    if abs(v) <= 1:
        r = 0
    else:
        r = random.choice([-1,0,0,0,1])
    return (q,r)

def get_proj2_choice(position, velocity, f_line, walls, time_limit):
	"""
	Start proj2.main as a process, wait until time_limit and terminate it,
	then read the last choice it produced.
	"""
	
	# Start proj2.main as a process
	p = mp.Process(target=proj2.main, \
		args = ((position,velocity), f_line, walls, ))
	p.start()
	# Wait for proj2.main until time_limit
	p.join(time_limit)
	if p.is_alive():
		print('Terminating proj.main at time_limit = {} seconds.'.format(time_limit))
	p.terminate()

	with open('choices.txt') as fp:
		line = None
		got_value = False
		# read and evaluate lines until we've gotten the last one
		for line in iter(fp.readline, ''):
			try:
				(u,v) = ast.literal_eval(line)	# safer than doing a full eval
				got_value = True
			except TypeError:
				print("\nIn choices.txt, this line isn't a velocity (u,v):")
				print(line)
			except ValueError:
				print("\nIn choices.txt, this line isn't a velocity (u,v):")
				print(line)
			except SyntaxError:
				print("\nIn choices.txt, this line is syntactically wrong:")
				print(line)
				print("Maybe your program ran out of time while printing it?")
			
	if got_value == False:
		print("\nError: Couldn't read (u,v). Either your program produced bad")
		print("output, or it ran out of time before getting an answer. If it")
		print("ran out of time, try increasing time_limit to more than {}.".format(time_limit))
		return (-1, -1, False)

	return (u, v, True)


def draw_edge(edge,color):
	tdraw.draw_lines([edge], width=2, color=color,dots=6)


def goal_test(point,velocity,f_line):
	"""Test whether state is with distance 1 of the finish line and has velocity (0,0)"""
	return velocity == (0,0) and edist_to_line(point, f_line) == 0


def edist_to_line(point, edge):
	"""
	Euclidean distance from point to edge, if edge is either vertical or horizontal.
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
				

def crash(move,walls):
	"""Test whether move intersects a wall in walls"""
	for wall in walls:
		if intersect(move,wall): return True
	return False


def intersect(e1,e2):
	"""Test whether edges e1 and e2 intersect"""	   
	
	# First, grab all the coordinates
	((x1a,y1a), (x1b,y1b)) = e1
	((x2a,y2a), (x2b,y2b)) = e2
	dx1 = x1a-x1b
	dy1 = y1a-y1b
	dx2 = x2a-x2b
	dy2 = y2a-y2b
	
	if (dx1 == 0) and (dx2 == 0):		# both lines vertical
		if x1a != x2a: return False
		else: 	# the lines are collinear
			return collinear_point_in_edge((x1a,y1a),e2) \
				or collinear_point_in_edge((x1b,y1b),e2) \
				or collinear_point_in_edge((x2a,y2a),e1) \
				or collinear_point_in_edge((x2b,y2b),e1)
	if (dx2 == 0):		# e2 is vertical (so m2 = infty), but e1 isn't vertical
		x = x2a
		# compute y = m1 * x + b1, but minimize roundoff error
		y = (x2a-x1a)*dy1/float(dx1) + y1a
		return collinear_point_in_edge((x,y),e1) and collinear_point_in_edge((x,y),e2) 
	elif (dx1 == 0):		# e1 is vertical (so m1 = infty), but e2 isn't vertical
		x = x1a
		# compute y = m2 * x + b2, but minimize roundoff error
		y = (x1a-x2a)*dy2/float(dx2) + y2a
		return collinear_point_in_edge((x,y),e1) and collinear_point_in_edge((x,y),e2) 
	else:		# neither line is vertical
		# check m1 = m2, without roundoff error:
		if dy1*dx2 == dx1*dy2:		# same slope, so either parallel or collinear
			# check b1 != b2, without roundoff error:
			if dx2*dx1*(y2a-y1a) != dy2*dx1*x2a - dy1*dx2*x1a:	# not collinear
				return False
			# collinear
			return collinear_point_in_edge((x1a,y1a),e2) \
				or collinear_point_in_edge((x1b,y1b),e2) \
				or collinear_point_in_edge((x2a,y2a),e1) \
				or collinear_point_in_edge((x2b,y2b),e1)
		# compute x = (b2-b1)/(m1-m2) but minimize roundoff error:
		x = (dx2*dx1*(y2a-y1a) - dy2*dx1*x2a + dy1*dx2*x1a)/float(dx2*dy1 - dy2*dx1)
		# compute y = m1*x + b1 but minimize roundoff error
		y = (dy2*dy1*(x2a-x1a) - dx2*dy1*y2a + dx1*dy2*y1a)/float(dy2*dx1 - dx2*dy1)
	return collinear_point_in_edge((x,y),e1) and collinear_point_in_edge((x,y),e2) 


def collinear_point_in_edge(point, edge):
	"""
	Helper function for intersect, to test whether a point is in an edge,
	assuming the point and edge are already known to be collinear.
	"""
	(x,y) = point
	((xa,ya),(xb,yb)) = edge
	# point is in edge if (i) x is between xa and xb, inclusive, and (ii) y is between
	# ya and yb, inclusive. The test of y is redundant unless the edge is vertical.
	if ((xa <= x <= xb) or (xb <= x <= xa)) and ((ya <= y <= yb) or (yb <= y <= ya)):
	   return True
	return False
		

