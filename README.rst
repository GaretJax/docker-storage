==============
Docker storage
==============

Project information:

.. image:: https://img.shields.io/pypi/v/docker-storage.svg
   :target: https://pypi.python.org/pypi/docker-storage

.. image:: https://img.shields.io/pypi/dm/docker-storage.svg
   :target: https://pypi.python.org/pypi/docker-storage

.. image:: https://img.shields.io/badge/docs-TODO-lightgrey.svg
   :target: http://docker-storage.readthedocs.org/en/latest/

.. image:: https://img.shields.io/pypi/l/docker-storage.svg
   :target: https://github.com/GaretJax/docker-storage/blob/master/LICENSE

Automated code metrics:

.. image:: https://img.shields.io/travis/GaretJax/docker-storage.svg
   :target: https://travis-ci.org/GaretJax/docker-storage

.. image:: https://img.shields.io/coveralls/GaretJax/docker-storage/master.svg
   :target: https://coveralls.io/r/GaretJax/docker-storage?branch=master

.. image:: https://img.shields.io/codeclimate/github/GaretJax/docker-storage.svg
   :target: https://codeclimate.com/github/GaretJax/docker-storage

.. image:: https://img.shields.io/requires/github/GaretJax/docker-storage.svg
   :target: https://requires.io/github/GaretJax/docker-storage/requirements/?branch=master

``docker-storage`` is a command line tool and a library to easily manage Docker
data-only containers

* Free software: MIT license
* Documentation: http://docker-storage.rtfd.org (TODO)


Installation
============

::

  pip install docker-storage


Command line usage
==================

::

   $ docker-storage box create test-box /data

   $ docker-storage box
   Name      Path
   --------  ------
   test-box  /data

   $ docker-storage box exec test-box -- touch EXAMPLE

   $ docker-storage box ls test-box
   total 8
   drwxr-xr-x    2 root     root          4096 Sep 23 07:45 .
   drwxr-xr-x   30 root     root          4096 Sep 23 07:45 ..
   -rw-r--r--    1 root     root             0 Sep 23 07:45 EXAMPLE

   $ docker-storage box rm test-box

   $ docker-storage box
   Name    Path
   ------  ------
