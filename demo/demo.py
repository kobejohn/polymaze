# coding=utf-8
"""Demonstrate some ways to use polymaze."""
import polymaze as pmz


def demo():
    use_mazemakers()
    use_gridmakers_with_Maze()
    use_custom_grid_with_Maze()


def use_mazemakers():
    # use customizeable mazemakers for easy-to-make mazes with random shapes
    # put a custom font at resources/font
    s = u'PolyMazes;'
    for i, (c, maze) in enumerate(pmz.mazemakers.string(s, complexity=2)):
        filename = u'Demo_{:02} ({}).png'.format(i, c if c.isalnum() else u'-')
        maze.image().save(filename)
        print c,


def use_gridmakers_with_Maze():
    # use gridmakers + Maze to customize the grids used in mazemakers
    character_grid = pmz.gridmakers.character('c')
    rectangle_mze = pmz.Maze(character_grid)  # etc.


def use_custom_grid_with_Maze():
    # roll your own grid + Maze to make a completely custom maze
    custom_grid = pmz.PolyGrid()
    some_row_column = (5, 5)
    custom_grid.create(some_row_column)  # for whatever positions
    custom_maze = pmz.Maze(custom_grid)  # etc.


if __name__ == '__main__':
    demo()
