#include <pybind11/pybind11.h>
#include <pybind11/stl.h>


extern "C" { 
#include "picosat/picosat.h" 
};


//#include "picosat.c"

namespace py = pybind11;


void print_vector(const std::vector<std::vector<int>> & v){
	for (auto item : v){
		for (auto item2 : item)
			std::cout << item2 << "\t";
		std::cout << "\n";
	}
}


std::vector<int> solve(const std::vector<std::vector<int>> & cnf){
	auto picosat = picosat_init();
	for (auto clause : cnf ){
		// Add the current clause
		for (auto v : clause){
			picosat_add(picosat, v);
		}
		// terminate with a zero
		picosat_add(picosat,0);
	}	
	// now solve
	auto res = picosat_sat(picosat, -1);
	auto max_idx = picosat_variables(picosat);
	std::vector<int> result(max_idx,0);
	
	switch (res) {
	case PICOSAT_SATISFIABLE:
		for (int i=1; i<= max_idx; i++){
			result[i-1] = picosat_deref(picosat, i);
		}
	}
	return result;
}


PYBIND11_MODULE(satyrn, m){
	m.def("print_vector", &print_vector, "print a vector");
	m.def("solve", &solve, "solve a SAT problem");
}
