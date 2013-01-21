#!/usr/bin/env python
from setuptools import setup

scripts = ['crawler.py']

setup(
    name='pywebcrawler',
    version='0.1',
    description='A simple webcrawler in Python.',
    long_description=open('README.md').read(),
    author='Ratnadeep Debnath',
    author_email='rtnpro@gmail.com',
    scripts=scripts,
    packages=[
        'pywebcrawler',
    ],
    install_requires=['BeautifulSoup']
)
