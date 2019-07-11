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


def test_assumptions():
	it = picosat.itersolve([[20]])
	it.assume([1,2,3,4,5])
	sol = it.next()
	assert(all([sol[i] == i+1 for i in range(5)]))
	


def test_add():
	cnf = [[1,-5,4],[-1,5,3,4], [-3, -4]]
	cnf2 = [[ 2]]
	it = picosat.itersolve(cnf)
	it.add_clauses(cnf2)
	sol = it.next()	
	assert check_solution(sol, cnf + cnf2)

	it = picosat.itersolve([[5]], initialization = 'random')
	for i, sol in enumerate(it):
		it.add_clauses([[4]])
		if i > 0:
			assert check_solution(sol, [[5],[4]])	

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

	sols = []
	sols2 = []
	for i in range(10):
		it = picosat.itersolve(cnf, initialization = 'random', seed = i)
		sol = it.next()
		print(sol)
		sol = set(sol)
		if sol not in sols:
			sols.append(sol)

		sol2 = it.next()
		sol2 = set(sol2)
		if sol2 not in sols2:
			sols2.append(sol2)
		
	
	assert len(sols) > 1, "Random solutions not generated"	
	assert len(sols2) > 1, "Random solutions not generated"	


if __name__ == '__main__':
#	test_solve()
#	test_itersolve()
#	test_unsat()	
#	test_short()	
	test_random()
