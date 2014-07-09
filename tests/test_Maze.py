import os
import sys
import unittest

sys.path.insert(0, os.path.abspath('..'))  # hack to allow simple test structure
import polymaze as pmz

# silly workaround to allow tests to work in py2 or py3
try:
    _assertCountEqual = unittest.TestCase.assertCountEqual  # py3
except AttributeError:
    _assertCountEqual = unittest.TestCase.assertItemsEqual  # py2


#noinspection PyProtectedMember
class TestMaze(unittest.TestCase):
    #todo: to really test this, need to confirm all graph nodes lead to in/out

    def test_shape_name_provides_it(self):
        ss = next(iter(pmz.SUPERSHAPES_DICT.values()))  # test any value
        maze = generic_maze(supershape=ss)
        ss_name = maze.shape_name()
        ss_name_spec = ss.name()
        self.assertEqual(ss_name, ss_name_spec)

    def test_mazify_grid_eliminates_isolated_shapes(self):
        grid = pmz.PolyGrid()
        neighbor_1_index = (1, 1)  # any index
        isolated_index = (30, 30)  # no way these are connected
        # create the neighbors and the isolated shape
        grid.create(isolated_index)
        neighbor_1 = grid.create(neighbor_1_index)
        neighbor_2_index, _ = tuple(neighbor_1.neighbors())[0]
        neighbor_2 = grid.create(neighbor_2_index)
        # mazify and confirm the isolated shape has been removed
        pmz.Maze(grid)
        final_shapes = tuple(grid.shapes())
        final_shapes_spec = (neighbor_1, neighbor_2)
        _assertCountEqual(self, final_shapes, final_shapes_spec)

    def test_entrance_exit_pairs_are_available_after_creation(self):
        maze = generic_maze()
        self.assertIsNotNone(maze.entrance_exit_pairs())

    def test_mazify_grid_generates_sequence_of_entrance_and_exit_spaces(self):
        maze = generic_maze()
        entrance_exit_pairs = tuple(maze._mazify_grid())
        for entrance_exit_pair in entrance_exit_pairs:
            self.assertEqual(len(entrance_exit_pair), 2)

    def test_has_paths_returns_false_if_edges_are_all_walls(self):
        maze = generic_maze()
        # choose any space from the maze's grid and set all edges to wall
        some_index = tuple(maze._grid.shapes())[0].index()
        space = maze._grid.get(some_index)
        for _, edge in space.edges():
            edge.viz_style = maze._WALL_STYLE
        # confirm that the space is pathable
        self.assertFalse(maze._has_paths(space))

    def test_has_paths_returns_true_if_any_edge_is_a_path(self):
        maze = generic_maze()
        # choose any space from the maze's grid and set all edges to wall
        some_index = tuple(maze._grid.shapes())[0].index()
        space = maze._grid.get(some_index)
        for _, edge in space.edges():
            edge.status = maze._WALL_STYLE
        # set any edge to path
        tuple(space.edges())[0][1].status = maze._PATH_STYLE
        # confirm that the space is not pathable
        self.assertTrue(maze._has_paths(space))

    def test_image_returns_a_PIL_image(self):
        maze = generic_maze()
        im = maze.image()
        # confirm it has an image method
        self.assertTrue(hasattr(im, 'crop'))

    def test_image_returns_None_for_empty_grid(self):
        # make and confirm an empty grid
        empty_grid = pmz.PolyGrid()
        self.assertEqual(len(tuple(empty_grid.shapes())), 0)
        # confirm image is None
        maze = pmz.Maze(empty_grid)
        self.assertIsNone(maze.image())


def generic_maze(**kwargs):
    supershape = kwargs.pop('supershape', None)
    grid = pmz.PolyGrid(supershape=supershape)
    if 'complexity' not in kwargs:
        kwargs['complexity'] = .5  # speed things up when possible
    grid.create_rectangle(**kwargs)
    return pmz.Maze(grid)


if __name__ == '__main__':
    unittest.main()
