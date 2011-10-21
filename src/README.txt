`seqdiag` generate sequence-diagram image file from spec-text file.

Features
========

* Generate sequence-diagram from dot like text (basic feature).
* Multilingualization for node-label (utf-8 only).

You can get some examples and generated images on 
`blockdiag.com <http://blockdiag.com/seqdiag/build/html/index.html>`_ .

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
`blockdiag.com <http://blockdiag.com/seqdiag/build/html/index.html>`_ .

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
* Python Imaging Library 1.1.5 or later.
* funcparserlib 0.3.4 or later.
* setuptools or distribute.


License
=======
Apache License 2.0


History
=======

0.5.0 (2011-10-21)
------------------
* Add diagram attributes: activation, autonumber
* Add edge attribute: failed
* Add separator syntax

0.4.3 (2011-10-19)
------------------
* Follow blockdiag-0.9.5 interface

0.4.2 (2011-10-11)
------------------
* Fix bugs

0.4.1 (2011-09-30)
------------------
* Add diagram attribute: default_text_color
* Add node attribte: textcolor
* Fix bugs

0.4.0 (2011-09-26)
------------------
* Add diagram attributes: default_node_color, default_group_color and default_line_color

0.3.8 (2011-08-02)
------------------
* Allow dot characters in node_id
* Fix bugs

0.3.7 (2011-07-05)
------------------
* Fix bugs

0.3.6 (2011-07-03)
------------------
* Support input from stdin

0.3.5 (2011-06-02)
------------------
* Fix bugs

0.3.4 (2011-05-18)
------------------
* Fix bugs

0.3.3 (2011-05-16)
------------------
* Add --version option
* Add sphinxhelper module

0.3.2 (2011-05-14)
------------------
* Render group label
* Support blockdiag 0.8.1 core interface 

0.3.1 (2011-04-22)
------------------
* Render group label
* Fix sphinxcontrib_seqdiag does not work with seqdiag 0.3.0

0.3.0 (2011-04-22)
------------------
* Add group syntax

0.2.7 (2011-04-15)
------------------
* Adjust start coordinates of edges

0.2.6 (2011-04-14)
------------------
* Fix bugs
* Allow unquoted utf8 characters

0.2.5 (2011-03-26)
------------------
* Fix seqdiag could not run under blockdiag 0.7.6

0.2.4 (2011-03-20)
------------------
* Fix bugs

0.2.3 (2011-03-09)
------------------
* Fix bugs

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

