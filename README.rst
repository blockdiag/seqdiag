`seqdiag` generate sequence-diagram image file from spec-text file.

.. image:: https://drone.io/bitbucket.org/blockdiag/seqdiag/status.png
   :target: https://drone.io/bitbucket.org/blockdiag/seqdiag
   :alt: drone.io CI build status

.. image:: https://pypip.in/v/seqdiag/badge.png
   :target: https://pypi.python.org/pypi/seqdiag/
   :alt: Latest PyPI version

.. image:: https://pypip.in/d/seqdiag/badge.png
   :target: https://pypi.python.org/pypi/seqdiag/
   :alt: Number of PyPI downloads


Features
========

* Generate sequence-diagram from dot like text (basic feature).
* Multilingualization for node-label (utf-8 only).

You can get some examples and generated images on 
`blockdiag.com <http://blockdiag.com/en/seqdiag/index.html>`_ .

Setup
=====

Use easy_install or pip::

   $ sudo easy_install seqdiag

   Or

   $ sudo pip seqdiag


Copy and modify ini file. example::

   $ cp <seqdiag installed path>/blockdiag/examples/simple.diag .
   $ vi simple.diag

Please refer to `spec-text setting sample`_ section for the format of the
`simpla.diag` configuration file.

spec-text setting sample
========================

Few examples are available.
You can get more examples at
`blockdiag.com <http://blockdiag.com/en/seqdiag/index.html>`_ .

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
* Python 3.7 or later
* blockdiag 1.5.0 or later
* funcparserlib 0.3.6 or later
* reportlab (optional)
* wand and imagemagick (optional)
* setuptools


License
=======
Apache License 2.0
