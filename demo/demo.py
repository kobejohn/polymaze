# coding=utf-8
"""Demonstrate some ways to use polymaze."""
import polymaze as pmz

EASY = 1.0


def demo():
    rectangle_maze()
    #string_maze()


#def string_maze():
#    # use customizeable mazemakers for easy-to-make mazes with random shapes
#    # put a custom font at resources/font
#    s = u'PolyMazes;'
#    for i, (c, maze) in enumerate(pmz.mazemakers.string(s, complexity=2)):
#        filename = u'Demo_{:02} ({}).png'.format(i, c if c.isalnum() else u'-')
#        maze.image().save(filename)
#        print c,


def rectangle_maze():
    grid = pmz.PolyGrid(complexity=EASY)
    maze = pmz.Maze(grid)
    maze.image().save('Demo Easy Rectangle.png', format='PNG')


if __name__ == '__main__':
    demo()
