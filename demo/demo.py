# coding=utf-8
"""Demonstrate some ways to use polymaze."""
import polymaze as pmz


def demo():
    print 'Saving demos:'
    rectangle_maze()
    string_maze()


def string_maze():
    s = u'Poly Maze'
    grid = pmz.PolyGrid()
    grid.create_string(s)
    maze = pmz.Maze(grid)
    filename = 'Demo Normal String.png'
    maze.image().save(filename, format='PNG')
    print filename


def rectangle_maze():
    easy = 1.0
    close_to_golden_rectangle = 0.625
    grid = pmz.PolyGrid()
    grid.create_rectangle(complexity=easy, aspect=close_to_golden_rectangle)
    maze = pmz.Maze(grid)
    filename = 'Demo Easy Rectangle.png'
    maze.image().save(filename, format='PNG')
    print filename


if __name__ == '__main__':
    demo()
