from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(
    name='libsheep',
    version='0.1',
    description="ADC Protocol Library",
    url='http://code.google.com/p/cwru-hackers/',
    packages=find_packages(),
    extras_require={
        'TIGR': ['python-mhash>=1.4']
    }
)
