PolyMaze - Create mazes from a variety of sources
=================================================

This utility converts several different kinds of inputs into mazes.

Allowed Inputs:

- Aspect ratio (height / width) of a rectangular maze
- String - convert the content of the string into a maze / mazes
- Image - convert the dark parts of an image into a maze / mazes

Options:

- Complexity - adjust the difficulty
- Font - use your own font (especially for unicode strings)
- Shape - explicitly choose the type of tesselation used in the maze

.. image:: http://raw.githubusercontent.com/kobejohn/polymaze/master/demo/Globe%20%28Polycat%29.png
   :width: 400 px

Installation:
=============

`polymaze` should work with Py2 or Py3.

    pip install polymaze

If you get the error `decoder zip not available` when using it, then probably
`PIL`/`PILLOW` did not install completely. You can try:

    pip install -use-wheel pillow

Commandline Usage:
==================

To make a generic rectangular maze:

    python polymaze.py

To see all options:

    python polymaze.py -h

For example, to make a string into a maze with some extra options:

    python polymaze.py --string "Happy Birthday!" --complexity 10 --shape Polycat

Library Usage:
==============

Please see demo/demo.py for examples of how to use the different parts.

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
in linux, etc.

License:
========

MIT. See LICENSE
