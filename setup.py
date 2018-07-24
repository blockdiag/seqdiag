# -*- coding: utf-8 -*-
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

requires = ['blockdiag>=1.5.0']
test_requires = ['nose',
                 'pep8>=1.3',
                 'reportlab',
                 'docutils']

# only for Python2.6
if sys.version_info > (2, 6) and sys.version_info < (2, 7):
    test_requires.append('unittest2')

if (3, 2) < sys.version_info < (3, 3):
    requires.append('webcolors < 1.5')  # webcolors-1.5 does not support py32


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
    install_requires=requires,
    extras_require=dict(
        testing=test_requires,
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
