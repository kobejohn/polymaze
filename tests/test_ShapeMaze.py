import unittest

from shapemaze import gridmakers, mazemakers
from shapemaze import maze


class Testmazemakers(unittest.TestCase):
    def test_rectangle_maze_is_a_rectangle(self):
        v_shapes_spec = 23
        h_shapes_spec = 31
        rect_maze = mazemakers.rectangle(grid_v_bound=v_shapes_spec,
                                         grid_h_bound=h_shapes_spec)
        grid = rect_maze._grid
        all_indexes = (shape.index() for shape in grid.shapes())
        all_indexes_spec = ((row, col)
                            for row in range(v_shapes_spec)
                            for col in range(h_shapes_spec))
        self.assertItemsEqual(all_indexes, all_indexes_spec)

    def test_string_to_mazes_generates_a_maze_for_non_whitespace_chars(self):
        string_with_whitespace = 'A STRING WITH WHITESPACE'
        non_ws_chars = tuple(c for s in string_with_whitespace.split()
                             for c in s)
        small_maze = 10
        all_mazes = tuple(mazemakers.string(string_with_whitespace,
                                            grid_v_bound=small_maze,
                                            grid_h_bound=small_maze))
        maze_count = len(all_mazes)
        maze_count_spec = len(non_ws_chars)
        self.assertEqual(maze_count, maze_count_spec)


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
    grid = gridmakers.rectangle(vertical_shapes=5, horizontal_shapes=5)
    return maze.Maze(grid)


if __name__ == '__main__':
    unittest.main()
