import os
import sys
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import copy
import sysconfig
from distutils.sysconfig import get_config_var
from distutils.ccompiler import new_compiler
from distutils import ccompiler
###############################################################################
# Generic Pybind11 setup config
###############################################################################
class get_pybind_include(object):
	"""Helper class to determine the pybind11 include path
	The purpose of this class is to postpone importing pybind11
	until it is actually installed, so that the ``get_include()``
	method can be invoked. """

	def __init__(self, user=False):
		self.user = user

	def __str__(self):
		import pybind11
		return pybind11.get_include(self.user)




# As of Python 3.6, CCompiler has a `has_flag` method.
# cf http://bugs.python.org/issue26689
def has_flag(compiler, flagname):
	"""Return a boolean indicating whether a flag name is supported on
	the specified compiler.
	"""
	import tempfile
	with tempfile.NamedTemporaryFile('w', suffix='.cpp') as f:
		f.write('int main (int argc, char **argv) { return 0; }')
		try:
			compiler.compile([f.name], extra_postargs=[flagname])
		except setuptools.distutils.errors.CompileError:
			return False
	return True


def cpp_flag(compiler):
	"""Return the -std=c++[11/14/17] compiler flag.
	The newer version is prefered over c++11 (when it is available).
	"""
	flags = ['-std=c++17', '-std=c++14', '-std=c++11']
	flags = flags[1:]
	for flag in flags:
		if has_flag(compiler, flag): return flag

	raise RuntimeError('Unsupported compiler -- at least C++11 support '
					   'is needed!')


class BuildExt(build_ext):
	"""A custom build extension for adding compiler-specific options."""
	c_opts = {
		'msvc': ['/EHsc'],
		'unix': [],
	}
	l_opts = {
		'msvc': [],
		'unix': [],
	}

	if sys.platform == 'darwin':
		darwin_opts = ['-stdlib=libc++', '-mmacosx-version-min=10.7']
		c_opts['unix'] += darwin_opts
		l_opts['unix'] += darwin_opts

	def build_extensions(self):
		ct = self.compiler.compiler_type
		opts = self.c_opts.get(ct, [])
		link_opts = self.l_opts.get(ct, [])
		if ct == 'unix':
			opts.append('-DVERSION_INFO="%s"' % self.distribution.get_version())
			#opts.append(cpp_flag(self.compiler))
			if has_flag(self.compiler, '-fvisibility=hidden'):
				opts.append('-fvisibility=hidden')
		elif ct == 'msvc':
			opts.append('/DVERSION_INFO=\\"%s\\"' % self.distribution.get_version())
	
		# Compile C extensions
		preargs = []
		comp = new_compiler()
		if has_flag(comp, '-fPIC'):
			preargs += ['-fPIC']

		comp.compile(['satyrn/picosat/picosat.c'], 
			include_dirs=['satyrn/picosat'], 
			output_dir = _get_distutils_temp_directory(),
			extra_preargs = preargs,
			)		

		for ext in self.extensions:
			ext.extra_compile_args = copy.deepcopy(opts)
			# We've moved the CPP flag setting here so that it doesn't trigger when
			# compiling picosat
			if ext.language == 'c++':
			 	ext.extra_compile_args += [cpp_flag(self.compiler)]
			ext.extra_link_args = link_opts

		print("Include dirs*********")
		print(self.include_dirs)
		build_ext.build_extensions(self)

###############################################################################
# End of pybind generic config
###############################################################################

# This allows us to link against things we've built separately 
# from: https://github.com/blue-yonder/turbodbc/blob/master/setup.py#L116
def _get_distutils_build_directory():
	"""
	Returns the directory distutils uses to build its files.
	We need this directory since we build extensions which have to link
	other ones.
	"""
	pattern = "lib.{platform}-{major}.{minor}"
	return os.path.join('build', pattern.format(platform=sysconfig.get_platform(),
												major=sys.version_info[0],
												minor=sys.version_info[1]))

def _get_distutils_temp_directory():
	"""
	Returns the directory distutils uses to build its files.
	We need this directory since we build extensions which have to link
	other ones.
	"""
	pattern = "temp.{platform}-{major}.{minor}"
	return os.path.join('build', pattern.format(platform=sysconfig.get_platform(),
												major=sys.version_info[0],
												minor=sys.version_info[1]))


# These are the additional object files 
extra_objects = [
	'satyrn/picosat/picosat.o',
	]

# This prefixes with the build location of these files 
extra_objects = [ os.path.join(str(_get_distutils_temp_directory()), obj) for obj in extra_objects]

ext_modules = [
	# This module generates the object files for the c dependencies
	Extension(
		'picosat',
		['satyrn/picosat/py_picosat.cpp'],
		include_dirs=[
			# Path to pybind11 headers
			get_pybind_include(),
			get_pybind_include(user=True)
		],
		language='c++', 
		extra_objects = extra_objects,
		extra_compile_args = ['-Wall'],
	),
]


with open('README.md', 'r') as f:
	long_description = f.read()

setup(name='satyrn',
	version = '0.3.6',
	description = 'SAT Solver Interface',
	long_description = long_description,
	long_description_content_type = 'text/markdown', 
	author = 'Jeffrey M. Hokanson',
	author_email = 'jeffrey@hokanson.us',
	packages = ['satyrn', 'satyrn.picosat'],
	ext_modules=ext_modules,
	install_requires = ['pybind11>=2.3'],
	setup_requires=['pybind11>=2.3'],
#	tests_requires = ['pycosat'],
	cmdclass={'build_ext': BuildExt},
	zip_safe=False,
	license = 'MIT',
	classifiers = [
		'Development Status :: 3 - Alpha',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: MIT License',
	],
	project_urls={ 
		'Source': 'https://github.com/jeffrey-hokanson/SATyrn',
		},
	)
