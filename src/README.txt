`seqdiag` generate sequence-diagram image file from spec-text file.

Features
========

* Generate sequence-diagram from dot like text (basic feature).
* Multilingualization for node-label (utf-8 only).

You can get some examples and generated images on 
`tk0miya.bitbucket.org <http://tk0miya.bitbucket.org/seqdiag/build/html/index.html>`_ .

Setup
=====

by easy_install
----------------
Make environment::

   $ easy_install seqdiag

by buildout
------------
Make environment::

   $ hg clone http://bitbucket.org/tk0miya/seqdiag
   $ cd seqdiag
   $ python bootstrap.py
   $ bin/buildout

Copy and modify ini file. example::

   $ cp <seqdiag installed path>/blockdiag/examples/simple.diag .
   $ vi simple.diag

Please refer to `spec-text setting sample`_ section for the format of the
`simpla.diag` configuration file.

spec-text setting sample
========================

Few examples are available.
You can get more examples at
`tk0miya.bitbucket.org <http://tk0miya.bitbucket.org/seqdiag/build/html/index.html>`_ .

simple.diag
------------

simple.diag is simply define nodes and transitions by dot-like text format::

    diagram {
      browser  -> webserver [label = "GET /index.html"];
      browser <-- webserver;
      browser  -> webserver [label = "POST /blog/comment"];
                  webserver  -> database [label = "INSERT comment"];
                  webserver <-- database;
      browser <-- webserver;
    }


Usage
=====

Execute seqdiag command::

   $ seqdiag simple.diag
   $ ls simple.png
   simple.png


Requirements
============

* Python 2.4 or later (not support 3.x)
* Python Imaging Library 1.1.6 or later.
* funcparserlib 0.3.4 or later.
* setuptools or distriubte.


License
=======
Python Software Foundation License.


History
=======

0.2.2 (2011-03-07)
------------------
* Fix could not run under python 2.4
* Support edge colors

0.2.1 (2011-02-28)
------------------
* Add default_shape attribute to diagram

0.2.0 (2011-02-27)
------------------
* Add metrix parameters for edge label: edge_height, edge_length
* Fix bugs

0.1.7 (2011-01-21)
------------------
* Fix TeX exporting in Sphinx extension

0.1.6 (2011-01-15)
------------------
* Support blockdiag-0.6.3
* Fix bugs

0.1.5 (2011-01-15)
------------------
* Draw activity on lifelines
* Support both direction edge with '=>' operator

0.1.4 (2011-01-13)
------------------
* Change synxtax around edges

0.1.3 (2011-01-12)
------------------
* Support diagonal edge
* Fix bugs

0.1.2 (2011-01-11)
------------------
* Support nested edges
* Add edge attributes; return, dir
* Add sphinx extention module(sphinxcontrib_seqdiag)
* Fix bugs

0.1.1 (2011-01-11)
------------------
* Fix bugs about layouting

0.1.0 (2011-01-08)
------------------
* first release

