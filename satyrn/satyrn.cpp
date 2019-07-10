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

class itersolve {
	PicoSAT * picosat;
	public:
	itersolve(const std::vector<std::vector<int>> & cnf, unsigned seed, int verbose, unsigned long long prop_limit);
	std::vector<int> next();
	~itersolve(){picosat_reset(picosat); };
};


itersolve::itersolve(const std::vector<std::vector<int>> & cnf, unsigned seed, int verbose, unsigned long long prop_limit){
	picosat = picosat_init();		
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

}

std::vector<int> itersolve::next(){
	int res;
	// now solve
	Py_BEGIN_ALLOW_THREADS // Release GIL
	res = picosat_sat(picosat, -1);
	Py_END_ALLOW_THREADS // Return GIL

	// If we've failed in any way, raise the stop iteration command
	if ( res != PICOSAT_SATISFIABLE ){
		throw pybind11::stop_iteration();
	}
	auto max_idx = picosat_variables(picosat);
	int v=0;
	std::vector<int> result(max_idx,0);
			
	for (int i=1; i<= max_idx; i++){
		// Now copy over the results, following Pycosat
		// https://github.com/ContinuumIO/pycosat/blob/b38fd85b6f4dcc18efd6027e96e5785104f53bb0/pycosat.c#L198
		v = picosat_deref(picosat, i);
		assert( v == -1 || v == 1);
		result[i-1] = v*i;
		// Also negate these results to ensure we do not see this solution again
	}
	picosat_reset_phases(picosat);
	for (int i=1; i <= max_idx; i++)	
		picosat_add(picosat, -result[i-1]);
	picosat_add(picosat, 0);
	return result;
}


std::vector<std::vector<int>> empty;

PYBIND11_MODULE(satyrn, m){
	py::register_exception<UnsatisfiableException>(m, "UnsatisfiableException");
	py::register_exception<UnknownPicosatException>(m, "UnknownPicosatException");
	m.def("solve", &solve, "solve a SAT problem",
		py::arg("cnf"), 
		py::arg("seed") = 0, 
		py::arg("verbose") = 0, 
		py::arg("prop_limit") = 0);
	py::class_<itersolve>(m, "itersolve")
		.def(py::init< const std::vector<std::vector<int>>, unsigned, int, unsigned long long >(), 
			py::arg("cnf"),
			py::arg("seed") = 0,
			py::arg("verbose") = 0,
			py::arg("prop_limit") = 0
			)
		.def("next", &itersolve::next, "get next item")  // Python2 compatability 
		.def("__next__", &itersolve::next, "get next item")  // Python3
		.def("__iter__", [](const itersolve &s){ return &s;});
}
