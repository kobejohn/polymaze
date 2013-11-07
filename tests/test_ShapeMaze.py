import unittest
import os

from shapemaze import maze
from shapemaze import shapes


#noinspection PyProtectedMember
class TestShapeMaze(unittest.TestCase):
    #todo: to really test this, need to create a tree and verify no cycles

    def test_entrance_and_exit_are_available_after_creation(self):
        maze = generic_maze()
        self.assertTrue(hasattr(maze, 'entrance_space'))
        self.assertTrue(hasattr(maze, 'exit_space'))

    def test_mazify_map_returns_two_spaces(self):
        maze = generic_maze()
        returned_spaces = maze._mazify_grid()
        self.assertEqual(len(returned_spaces), 2)

    def test_is_pathable_returns_true_if_edges_are_all_walls(self):
        maze = generic_maze()
        # choose any space from the maze's grid and set all edges to wall
        some_index = tuple(maze._grid.shapes())[0].index()
        space = maze._grid.get(some_index)
        for _, edge in space.edges():
            edge.status = maze.WALL
        # confirm that the space is pathable
        self.assertTrue(maze._is_pathable(space))

    def test_is_pathable_returns_false_if_any_edge_is_a_path(self):
        maze = generic_maze()
        # choose any space from the maze's grid and set all edges to wall
        some_index = tuple(maze._grid.shapes())[0].index()
        space = maze._grid.get(some_index)
        for _, edge in space.edges():
            edge.status = maze.WALL
        # set any edge to path
        tuple(space.edges())[0][1].status = maze.PATH
        # confirm that the space is not pathable
        self.assertFalse(maze._is_pathable(space))

    def test_image_returns_image_with_same_rect_ratio_as_map_space(self):
        maze = generic_maze()
        all_xy = list()
        for edge in maze._grid.edges():
            xy_1, xy_2 = edge.endpoints()
            all_xy.append(xy_1)
            all_xy.append(xy_2)
        x_values, y_values = zip(*all_xy)
        height_in_shape_edges = max(x_values) - min(x_values)
        width_in_shape_edges = max(y_values) - min(y_values)
        ratio_spec = float(height_in_shape_edges) / width_in_shape_edges
        # get the image and size
        some_width_limit, some_height_limit = 1000, 1000
        image = maze.image(some_height_limit, some_width_limit)
        image_width, image_height = image.size
        ratio = float(image_height) / image_width
        # confirm the image size and specified size match
        self.assertAlmostEqual(ratio, ratio_spec, places=1)

    def test_image_is_bound_by_both_max_heigh_and_max_width(self):
        # create a maze
        maze = generic_maze()
        large_limit = 4000
        normal_limit = 400
        # create an image with a normal height and large width
        # and confirm it is bound by both limits
        wide_image = maze.image(normal_limit, large_limit)
        wide_image_width, wide_image_height = wide_image.size
        self.assertLessEqual(wide_image_width, large_limit)
        self.assertLessEqual(wide_image_height, normal_limit)
        # create an image with a normal width and large height
        # and confirm it is bound by both limits
        tall_image = maze.image(large_limit, normal_limit)
        tall_image_width, tall_image_height = tall_image.size
        self.assertLessEqual(tall_image_width, normal_limit)
        self.assertLessEqual(tall_image_height, large_limit)


def generic_maze():
    creator = shapes.Square
    return maze.Maze(creator)


if __name__ == '__main__':
    unittest.main()