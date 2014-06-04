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

Commandline Usage:
==================

`python polymaze.py` to make a generic rectangular maze.
`python polymaze.py -h` for help with all options

Library Usage:
==============

Please see demo/demo.py for examples of how to use the different parts.

The primary components are PolyGrid (the geometric core of the whole package),
and PolyMaze which converts a PolyGrid into a maze.

Background and Feedback:
========================

I'd like to be a professional developer but this is just a hobby for me. I
developed this to regain some of my basic trigonometry skills which I have lost
over the years. It has been reasonably successful at that.

If you find this useful or have any feedback, please let me know!

License:
========

MIT. See LICENSE.
