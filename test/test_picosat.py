from __future__ import print_function

import satyrn
import pycosat

def check_solution(sol, cnf):
	# Check that each clause is true
	for clause in cnf:
		this_clause = False
		for c in clause:
			if sol[abs(c) - 1] * c > 0:
				this_clause = True
				break
		
		if not this_clause:	
			return False

	return True


def test_solve():
	cnf = [[1,-5,4],[-1,5,3,4], [-3, -4]]
	sol = satyrn.solve(cnf, seed = 2)
	assert check_solution(sol, cnf)
	print(sol)


	
def test_unsat():
	cnf = [[1],[-1]]
	try:
		sol = satyrn.solve(cnf)
		assert False, "Incorrect exception raised"
	except satyrn.UnsatisfiableException:
		print("raised right exception")

def test_short():
	# This fails because the 
	cnf = [[1,-5,4],[-1,5,3,4], [-3, -4]]
	try:
		sol = satyrn.solve(cnf, prop_limit = 1)
		assert False, "Incorrect exception raised"
	except satyrn.UnknownPicosatException:
		print("raised right exception")
		

if __name__ == '__main__':
	test_solve()
#	test_unsat()	
#	test_short()	
