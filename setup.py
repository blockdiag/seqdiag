# -*- coding: utf-8 -*-
import os
import sys
from setuptools import setup, find_packages

sys.path.insert(0, 'src')
import seqdiag

classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python",
    "Topic :: Software Development",
    "Topic :: Software Development :: Documentation",
    "Topic :: Text Processing :: Markup",
]

test_requires = ['Nose', 'pep8>=1.3']


# only for Python2.6
if sys.version_info > (2, 6) and sys.version_info < (2, 7):
    test_requires.append('unittest2')


setup(
    name='seqdiag',
    version=seqdiag.__version__,
    description='seqdiag generates sequence-diagram image from text',
    long_description=open("README.txt").read(),
    classifiers=classifiers,
    keywords=['diagram', 'generator'],
    author='Takeshi Komiya',
    author_email='i.tkomiya at gmail.com',
    url='http://blockdiag.com/',
    download_url='http://pypi.python.org/pypi/seqdiag',
    license='Apache License 2.0',
    py_modules=['seqdiag_sphinxhelper'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    package_data={'': ['buildout.cfg']},
    include_package_data=True,
    install_requires=[
        'setuptools',
        'blockdiag>=1.3.0',
         # -*- Extra requirements: -*-
    ],
    extras_require=dict(
        test=test_requires,
        rst=[
            'docutils',
        ],
    ),
    test_suite='nose.collector',
    tests_require=test_requires,
    entry_points="""
       [console_scripts]
       seqdiag = seqdiag.command:main
    """,
)
