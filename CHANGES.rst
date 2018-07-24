Changelog
=========

0.9.6 (2018-07-24)
------------------
* Fix a bug

  - Fix #24 Python 3.7 compatibility

0.9.5 (2015-01-01)
------------------
* Support blockdiag 1.5.0 core interface

0.9.4 (2014-11-05)
------------------
* Fix bugs

  - Fix :desctable: ignores edge direction

0.9.3 (2014-07-03)
------------------
* Fix bugs

0.9.2 (2014-07-02)
------------------
* Change interface of docutils node (for sphinxcontrib module)

0.9.1 (2014-06-23)
------------------
* Add options to blockdiag directive (docutils extension)

  - :width:
  - :height:
  - :scale:
  - :align:
  - :name:
  - :class:
  - :figwidth:
  - :figclass:

0.9.0 (2013-10-05)
------------------
* Support python 3.2 and 3.3 (thanks to @masayuko)
* Drop supports for python 2.4 and 2.5
* Replace dependency: PIL -> Pillow

0.8.2 (2013-02-09)
------------------
* Fix bugs

0.8.1 (2012-11-12)
------------------
* Add altblock feature (experimental)
* Fix bugs

0.8.0 (2012-10-22)
------------------
* Optimize algorithm for rendering shadow
* Add options to docutils directive
* Fix bugs

0.7.5 (2012-09-29)
------------------
* Fix bugs

0.7.4 (2012-09-20)
------------------
* Support blockdiag-1.1.7 interface
* Fix bugs

0.7.3 (2012-03-16)
------------------
* Allow to insert separators in subedge-group
* Fix bugs

0.7.2 (2011-12-12)
------------------
* Fix bugs

0.7.1 (2011-11-30)
------------------
* Fix bugs

0.7.0 (2011-11-19)
------------------
* Add fontfamily attribute for switching fontface
* Fix bugs

0.6.3 (2011-11-06)
------------------
* Add docutils extention
* Fix bugs

0.6.2 (2011-11-01)
------------------
* Add class feature (experimental)

0.6.1 (2011-11-01)
------------------
* Follow blockdiag-0.9.7 interface

0.6.0 (2011-10-28)
------------------
* Add edge attributes: note, rightnote, leftnote, notecolor
* Add diagram atteribute: default_note_color

0.5.2 (2011-10-27)
------------------
* Implement auto edge height adjusting
* Fix bugs

0.5.1 (2011-10-24)
------------------
* Fix bugs

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
