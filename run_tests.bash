#!/bin/bash

###############################################################################
# run_tests.bash -- Dana Nau <nau@cs.umd.edu>, Feb 14, 2018
#
# This bash script takes three lists -- racetrack problems, heuristic functions,
# and search strategies -- and iterates over all the possible combinations.
#
# Modify this file to use the sample problems, heuristics, and
# search strategies that you want to use in your tests.
#
# Here are a few examples you can try:
#   ./run_one_test.bash rect20d h_edist gbf
#   ./run_one_test.bash rect50 h_edist gbf
#   ./run_one_test.bash rect50 h_esdist gbf
#   ./run_one_test.bash lhook16 h_esdist gbf


set -f    # disable globbing, because we don't want the name a* to be expanded

###############################################################################
### START OF CUSTOMIZATION OPTIONS


### IMPORTANT!!! Change this to use the pathname for your python program
#
python=/usr/local/anaconda3/bin/python    # python pathname


#### TEST PROBLEMS ###

# Specify the rootname of the file that contains the test problems
#
prob_file=sample_probs

# Here is a list of all the problems in sample_probs.py, in roughly increasing
# order of difficulty.
problems=(rect20a rect20b rect20c rect20d rect50a rect50b wall8a wall8b lhook16 rhook16a rhook16b spiral16 spiral24 pdes30 pdes30b rectwall8 rectwall16 rectwall32 rectwall32a walls32)

# You probably don't want to run all of the test problems at once -- so
# here you should put a list of the ones you currently want to use.
problems=(rect20e lhook16)

#### HEURISTIC FUNCTIONS ###

# Here's the rootname of the file that contains the heuristic functions.
# You should replace it with the rootname of YOUR hueuristic function file
#
heur_file=heuristics

# Here's a list of the heuristic functions in racetrack.py: 
heuristics=(h_edist h_esdist h_walldist)

# Put a list here of the heuristic functions you actually want to use
heuristics=(h_esdist h_walldist)


#### SEARCH STRATEGIES AND OTHER FLAGS ###

# Below, the first line is a list of all the available search strategies. Change the
# second line to include just the one(s) you want to use.

strategies=(bf df uc gbf a*)
strategies=(gbf)

# Specify the amount of verbosity you want fsearch.main to use:
verb=2       

# Use draw=1 to draw the search tree; use draw=0 to draw nothing
draw=1	


### End of customization options
#####################################################################


# The following code will iterate over every combination of sample problem, 
# heuristic function, and search strategy in your above lists. For each, it
# will first display the results graphically, and then do a time test.
#
for prob in ${problems[*]}
do
  for heur in ${heuristics[*]}
  do
    for strat in ${strategies[*]}
    do
		echo ''
		echo "Running '$strat, $heur, $prob"
		# string for setting everything up
		setup="import racetrack, $prob_file, $heur_file"

		# run the program and print the result
		print_test="result=racetrack.main($prob_file.$prob, '$strat', $heur_file.$heur, verbose=$verb, draw=$draw, title='$strat, $heur, $prob'); print('\nResult ({} states):\n{}'.format(len(result), result))"
		$python -c "$setup; $print_test"

		# code for doing a time test
		echo ''
		echo "Time test of '$strat, $heur, $prob'"
		# To do a proper time test, you need verbose=0 and draw=0 below.
		time_test="racetrack.main($prob_file.$prob, '$strat', $heur_file.$heur, verbose=0, draw=0)"
		$python -m timeit -s "$setup" "$time_test"
    done
  done
done
