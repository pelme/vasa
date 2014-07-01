#!/usr/bin/env python

import os
import codecs
from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(name='vasa',
      version=__import__('vasa').__version__,
      description='A Continuous Integration server',
      author='Andreas Pelme',
      author_email='andreas@pelme.se',
      maintainer="Andreas Pelme",
      maintainer_email="andreas@pelme.se",
      url='http://github.com/pelme/vasa',
      packages=['vasa'],
      long_description=read('README.rst'),
      install_requires=[],
      classifiers=['Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Testing',
                   'Topic :: Software Development :: Quality Assurance',
                   'Programming Language :: Python :: 3.4'],
      entry_points={'console_scripts': ['vasa-server = vasa.main:main']})
