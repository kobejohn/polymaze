# coding=utf-8
"""Demonstrate some ways to use polymaze."""
import itertools
import random
import os

import PIL.Image

import polymaze as pmz

_image_directory = os.path.join('.', 'demo_images')


def demo():
    print('Saving demos:')
    custom_rectangle_mazes()
    ascii_string_maze()
    unicode_string_maze()
    image_maze()


def ascii_string_maze():
    s = 'Mazes.'
    supershape_name, supershape = next(_supershapes_cycle)
    grid = pmz.PolyGrid(supershape=supershape)
    grid.create_string(s, height=50)
    maze = pmz.Maze(grid)
    filename = os.path.join(_image_directory,
                            'ASCII String ({}).png'.format(supershape_name))
    maze.image().save(filename, format='PNG')
    print('Saved {}'.format(filename))


def unicode_string_maze():
    s = u'迷\\n路'  # note literal \n is interpreted as newline
    supershape_name, supershape = next(_supershapes_cycle)
    grid = pmz.PolyGrid(supershape=supershape)
    grid.create_string(s, complexity=20)
    maze = pmz.Maze(grid)
    filename = os.path.join(_image_directory,
                            'Unicode String ({}).png'.format(supershape_name))
    maze.image().save(filename, format='PNG')
    print('Saved {}'.format(filename))


def image_maze():
    image = PIL.Image.open(os.path.join(_image_directory, 'globe_source.png'))
    supershape_name, supershape = next(_supershapes_cycle)
    grid = pmz.PolyGrid(supershape=supershape)
    grid.create_from_image(image, complexity=100)
    maze = pmz.Maze(grid)
    filename = os.path.join(_image_directory,
                            'Globe ({}).png'.format(supershape_name))
    maze.image().save(filename, format='PNG')
    print('Saved {}'.format(filename))


def custom_rectangle_mazes():
    aspect_close_to_golden_rectangle = 0.625
    for complexity in (1, 1.5, 2, 4):
        supershape_name, supershape = next(_supershapes_cycle)
        grid = pmz.PolyGrid(supershape=supershape)
        grid.create_rectangle(complexity=complexity,
                              aspect=aspect_close_to_golden_rectangle)
        maze = pmz.Maze(grid)
        filename = os.path.join(_image_directory,
                                'Rectangle (Complexity {}) ({}).png'
                                ''.format(complexity, supershape_name))
        maze.image().save(filename, format='PNG')
        print('Saved {}'.format(filename))


# instead of simple random shapes, use a randomized cycle so they are not
# repeated until all have been used
_supershapes_cycle = list(pmz.SUPERSHAPES_DICT.items())
random.shuffle(_supershapes_cycle)
_supershapes_cycle = itertools.cycle(_supershapes_cycle)


if __name__ == '__main__':
    demo()
