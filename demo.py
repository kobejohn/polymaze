# coding=utf-8
"""Demonstrate some ways to use polymaze."""
import shapemaze as smz


def demo():
    use_mazemakers()
    use_gridmakers_with_Maze()
    use_custom_grid_with_Maze()


def use_mazemakers():
    # use customizeable mazemakers for easy-to-make mazes with random shapes
    # put a custom font at resources/font
    s = u'Shapes?'
    for i, (c, maze) in enumerate(smz.mazemakers.string(s, complexity=2)):
        filename = u'Demo_{:02} ({}).png'.format(i, c if c.isalnum() else u'-')
        maze.image().save(filename)
        print c,


def use_gridmakers_with_Maze():
    # use gridmakers + Maze to customize the grids used in mazemakers
    character_grid = smz.gridmakers.character('c')
    rectangle_mze = smz.Maze(character_grid)  # etc.


def use_custom_grid_with_Maze():
    # roll your own grid + Maze to make a completely custom maze
    custom_grid = smz.ShapeGrid()
    some_row_column = (5, 5)
    custom_grid.create(some_row_column)  # for whatever positions
    custom_maze = smz.Maze(custom_grid)  # etc.


if __name__ == '__main__':
    demo()
