#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <assert.h>

#include <exception>

extern "C" { 
#include "picosat/picosat.h" 
};

namespace py = pybind11;



struct UnsatisfiableException : public std::exception
{
	const char * what () const throw (){
		return "SAT problem does not have a solution that satisfies the constraints";
	}
};
struct UnknownPicosatException : public std::exception
{
	const char * what () const throw (){
		return "Unknown exception";
	}
};


std::vector<int> solve(const std::vector<std::vector<int>> & cnf, unsigned seed, int verbose, unsigned long long prop_limit){
	auto picosat = picosat_init();
	int res;
	// Set the random number generator seed
	picosat_set_seed(picosat, seed);
	// Set the verbosity level
	picosat_set_verbosity(picosat, verbose);
	// Only set the propagation limit if it is non-zero
	if (prop_limit)
		picosat_set_propagation_limit(picosat, prop_limit);	

	// Copy over the clauses into the solver
	for (auto clause : cnf ){
		// Add the current clause
		for (auto v : clause){
			picosat_add(picosat, v);
		}
		// terminate with a zero
		picosat_add(picosat,0);
	}	
	// now solve
	Py_BEGIN_ALLOW_THREADS // Release GIL
	res = picosat_sat(picosat, -1);
	Py_END_ALLOW_THREADS // Return GIL
	auto max_idx = picosat_variables(picosat);
	int v=0;
	std::vector<int> result(max_idx,0);

	
	switch (res) {
		case PICOSAT_SATISFIABLE:
			for (int i=1; i<= max_idx; i++){
				// Now copy over the results, following Pycosat
				// https://github.com/ContinuumIO/pycosat/blob/b38fd85b6f4dcc18efd6027e96e5785104f53bb0/pycosat.c#L198
				v = picosat_deref(picosat, i);
				assert( v == -1 || v == 1);
				result[i-1] = v*i;
			}
			break;
		case PICOSAT_UNSATISFIABLE:
			throw UnsatisfiableException();
			break;
		case PICOSAT_UNKNOWN:
			throw UnknownPicosatException();
			break;
	}
	// Free memory
	picosat_reset(picosat);
	return result;
}


PYBIND11_MODULE(satyrn, m){
	m.def("solve", &solve, "solve a SAT problem",
		py::arg("cnf"), py::arg("seed") = 0, py::arg("verbose") = 0, py::arg("prop_limit") = 0);
	py::register_exception<UnsatisfiableException>(m, "UnsatisfiableException");
	py::register_exception<UnknownPicosatException>(m, "UnknownPicosatException");
}
