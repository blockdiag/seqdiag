# -*- coding: utf-8 -*-
import sys
from setuptools import setup, find_packages

sys.path.insert(0, 'src')
import seqdiag

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Topic :: Software Development",
    "Topic :: Software Development :: Documentation",
    "Topic :: Text Processing :: Markup",
]


setup(
    name='seqdiag',
    version=seqdiag.__version__,
    description='seqdiag generates sequence-diagram image from text',
    long_description=open("README.rst").read(),
    classifiers=classifiers,
    keywords=['diagram', 'generator'],
    author='Takeshi Komiya',
    author_email='i.tkomiya@gmail.com',
    url='http://blockdiag.com/',
    download_url='http://pypi.python.org/pypi/seqdiag',
    license='Apache License 2.0',
    py_modules=['seqdiag_sphinxhelper'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    package_data={'': ['buildout.cfg']},
    include_package_data=True,
    python_requires=">=3.5",
    install_requires=[
        'blockdiag >= 1.5.0',
    ],
    extras_require={
        'testing': [
            'nose',
            'flake8',
            'flake8-coding',
            'flake8-copyright',
            'reportlab',
            'docutils',
        ],
    },
    test_suite='nose.collector',
    entry_points="""
       [console_scripts]
       seqdiag = seqdiag.command:main
    """,
)
