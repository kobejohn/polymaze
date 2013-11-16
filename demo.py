"""Demonstrate some ways to use polymaze."""
import shapemaze as smz


def demo():
    use_mazemakers()
    use_gridmakers_with_Maze()
    use_custom_grid_with_Maze()


def use_mazemakers():
    # use customizeable mazemakers for easy-to-make mazes with random shapes
    for i, (c, maze) in enumerate(smz.mazemakers.string_to_mazes('Maze!')):
        image = maze.image()
        filename = 'Demo - Maze!-{}-{}.png'.format(i, c)
        image.save(filename, 'PNG', **image.info)
        print 'Saved: {}'.format(filename)
        # note: the PIL needs the **image.info to save transparency

    # use mazemakers with custom options
    hexagon = smz.supershapes_dict['Hexagon']  # Square, UpDownTriangle, etc.
    easy_maze = 20
    rectangle_maze = smz.mazemakers.rectangle_maze(supershape=hexagon,
                                                   vertical_shapes=easy_maze,
                                                   horizontal_shapes=easy_maze)
    # etc.

def use_gridmakers_with_Maze():
    # use gridmakers + Maze to customize the grids used in mazemakers
    rectangle_grid = smz.gridmakers.rectangle()
    rectangle_mze = smz.Maze(rectangle_grid)  # etc.


def use_custom_grid_with_Maze():
    # roll your own grid + Maze to make a completely custom maze
    custom_grid = smz.ShapeGrid()
    some_row_column = (5, 5)  # for whatever positions
    custom_grid.create(some_row_column)
    maze = smz.Maze(custom_grid)  # etc.


if __name__ == '__main__':
    demo()
