import os
from setuptools import setup

import floatextras

def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()

setup(
    name = 'floatextras',
    version = floatextras.version,
    author = 'Andrew Barnert',
    author_email = 'abarnert@yahoo.com',
    description = ('Extra functions on the built-in `float` similar '
                   'to those on `Decimal`.'),
    license = 'MIT',
    keywords = 'float',
    url = 'https://github.com/abarnert/floatextras',
    py_modules = ['floatextras'],
    long_description = read('README.md'),
    classifiers = [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3'])
