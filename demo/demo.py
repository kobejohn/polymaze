# coding=utf-8
"""Demonstrate some ways to use polymaze."""
import polymaze as pmz


def demo():
    print 'Saving demos:'
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
    easy = 1.0
    close_to_golden_rectangle = 0.625
    grid = pmz.PolyGrid(complexity=easy, aspect=close_to_golden_rectangle)
    maze = pmz.Maze(grid)
    filename = 'Demo Easy Rectangle.png'
    maze.image().save(filename, format='PNG')
    print filename


if __name__ == '__main__':
    demo()
