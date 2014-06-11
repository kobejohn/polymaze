=================================================
PolyMaze - Create mazes from a variety of sources
=================================================

This utility converts several different kinds of inputs into mazes.

Allowed Inputs:

- Aspect ratio (height / width) of a rectangular maze
- String - convert the content of the string into a maze / mazes
- Image - convert the dark parts of an image into a maze / mazes

Options:

- Complexity - adjust the difficulty
- Font - use your own font when making a String maze (especially for unicode strings)
- Shape - explicitly choose the type of tesselation used in the maze

.. image:: https://github.com/kobejohn/polymaze/raw/master/docs/Globe_Polycat_small.png

.. image:: https://github.com/kobejohn/polymaze/raw/master/docs/String_small.png

Installation:
=============

``polymaze`` should work with Py2 or Py3.

.. code:: sh

    pip install polymaze

If you get the error ``decoder zip not available`` when using it, then probably
``PILLOW`` did not install completely. Try to upgrade or reinstall
``PILLOW`` and make sure it says png support was installed.

Commandline Usage:
==================

To make a generic rectangular maze, at the command line:

.. code:: sh

    polymaze

To see all options:

.. code:: sh

    polymaze -h

For example, to make a string into a maze with some extra options (note the \n
gets converted to a real newline internally):

.. code:: sh

    polymaze --string "Happy\nBirthday!" --complexity 10 --shape Polycat

Everything above assumes the command line entry point (named polymaze) works
after installation. If not, then you will need to replace "polymaze ..." with

.. code:: sh

    python /your_install_location/polymaze/cli.py ...


Library Usage:
==============

Please see demo/demo.py for examples of how to use the components.

The primary components are PolyGrid (the geometric core of the whole package),
and PolyMaze which converts a PolyGrid into a maze.

Extension:
==========

If anyone is interested, I can document how to specify new tessellations.

Background and Feedback:
========================

I developed this to regain some of my basic trigonometry skills which I have
lost over the years.

If you find this useful or have any feedback, please let me know! Specifically
I have only tested this on Windows so please make an issue if it doesn't work
in Linux, etc.

License:
========

MIT. See LICENSE
