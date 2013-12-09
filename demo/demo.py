# coding=utf-8
"""Demonstrate some ways to use polymaze."""
import polymaze as pmz


def demo():
    print 'Saving demos:'
    basic_string_maze()
    custom_rectangle_mazes()


def basic_string_maze():
    s = u'Poly Maze'
    grid = pmz.PolyGrid()
    grid.create_string(s, complexity=2)
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
