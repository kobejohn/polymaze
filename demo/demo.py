# coding=utf-8
"""Demonstrate some ways to use polymaze."""
import PIL.Image

import polymaze as pmz


def demo():
    print 'Saving demos:'
    basic_string_maze()
    custom_rectangle_mazes()
    image_maze()


def image_maze():
    image = PIL.Image.open('source_image.png')
    grid = pmz.PolyGrid(supershape=pmz.SUPERSHAPES_DICT['HexaFlower'])
    grid.create_from_image(image, complexity=100)
    maze = pmz.Maze(grid)
    filename = 'globe.png'
    maze.image().save(filename, format='PNG')


def basic_string_maze():
    s = u'迷路'
    grid = pmz.PolyGrid(supershape=pmz.SUPERSHAPES_DICT['OctaDiamond'])
    grid.create_string(s, complexity=50, font_path='meiryob.ttc')
    maze = pmz.Maze(grid)
    filename = 'Demo Normal String.png'
    maze.image().save(filename, format='PNG')
    print filename


def custom_rectangle_mazes():
    # prepare some custom items
    aspect_close_to_golden_rectangle = 0.625
    for i, (ss_name, ss) in enumerate(pmz.SUPERSHAPES_DICT.items()):
        complexity = i + 1
        grid = pmz.PolyGrid(supershape=ss)
        grid.create_rectangle(complexity=complexity,
                              aspect=aspect_close_to_golden_rectangle)
        maze = pmz.Maze(grid)
        filename = 'Demo (complexity {}) ({}).png'.format(complexity,
                                                          ss_name)
        maze.image().save(filename, format='PNG')
        print filename


if __name__ == '__main__':
    demo()
