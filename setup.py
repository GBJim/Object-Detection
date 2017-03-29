from setuptools import setup

setup(
	name = "Object-Detection",
	version = "0.1",
	py_modules=['hello'],
	install_requires=['Click', 'celery'],
	entry_points= '''
	[console_scripts]
	obd=cli:main
'''


)
