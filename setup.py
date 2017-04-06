from setuptools import setup

setup(
	name = "Object-Detection",
	version = "0.1",
	py_modules=['hello'],
	install_requires=['Click', 'flask'],
	entry_points= '''
	[console_scripts]
	obd=cli:main
'''


)
