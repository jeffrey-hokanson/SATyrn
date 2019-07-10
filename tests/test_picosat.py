from __future__ import print_function

from satyrn import picosat

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
	sol = picosat.solve(cnf, seed = 2)
	assert check_solution(sol, cnf)
	print(sol)


	
def test_unsat():
	cnf = [[1],[-1]]
	try:
		sol = picosat.solve(cnf)
		assert False, "Incorrect exception raised"
	except picosat.UnsatisfiableException:
		print("raised right exception")

def test_short():
	# This fails because the 
	cnf = [[1,-5,4],[-1,5,3,4], [-3, -4]]
	try:
		sol = picosat.solve(cnf, prop_limit = 1)
		assert False, "Incorrect exception raised"
	except picosat.UnknownPicosatException:
		print("raised right exception")
		
def test_itersolve():
	cnf = [[1,-5,4],[-1,5,3,4], [-3, -4]]
	all_sols = []
	for sol in picosat.itersolve(cnf):
		print(sol)
		assert check_solution(sol, cnf)
		assert set(sol) not in all_sols, "Solution repeated"
		all_sols.append(set(sol))

def test_random():
	cnf = [[20,],]
	sols = []
	for i in range(10):
		sol = picosat.solve(cnf, seed = i, initialization = 'random')
		print(sol)
		sol = set(sol)
		if sol not in sols:
			sols.append(sol)
	
	assert len(sols) > 1, "Random solutions not generated"	


if __name__ == '__main__':
#	test_solve()
#	test_itersolve()
#	test_unsat()	
#	test_short()	
	test_random()
