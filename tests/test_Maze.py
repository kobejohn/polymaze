import mock
import unittest

from shapemaze import gridmakers as _gridmakers
from shapemaze import mazemakers as _mazemakers
from shapemaze import maze as _maze


@mock.patch('shapemaze.mazemakers._gridmakers')
@mock.patch('shapemaze.mazemakers._maze')
class Testmazemakers(unittest.TestCase):
    def test_rectangle_returns_maze_from_gridmaker_rectangle(self, m_maze,
                                                             m_gridmakers):
        returned_maze = _mazemakers.rectangle()
        self.assertIsNone(m_gridmakers.rectangle.assert_any_call())
        self.assertIsNone(m_maze.Maze.assert_called_with(m_gridmakers.rectangle.return_value))
        self.assertIs(returned_maze, m_maze.Maze.return_value)

    def test_string_gens_non_whitespace_characters(self, m_maze, m_gridmakers):
        string_with_whitespace = ' a b\tc\nd'
        non_whitespace_spec = 'abcd'
        list(_mazemakers.string(string_with_whitespace))
        # confirm a) ALL non whitespace characters created
        for c in non_whitespace_spec:
            self.assertIsNone(m_gridmakers.character.assert_any_call(c))
        # confirm b) ONLY the non whitespace characters were created
        self.assertEqual(m_gridmakers.character.call_count,
                         len(non_whitespace_spec))

    def test_string_gens_chars_and_mazes_from_gridmaker_rectangle(self,
                                                                  m_maze,
                                                                  m_gridmakers):
        chars_spec = 'abcd'
        for c, maze in _mazemakers.string(chars_spec):
            # confirm that the data proceeded as expected
            self.assertIsNone(m_gridmakers.character.assert_called_with(c))
            self.assertIsNone(m_maze.Maze.assert_called_with(m_gridmakers.character.return_value))
            self.assertIs(maze, m_maze.Maze.return_value)


#noinspection PyProtectedMember
class TestMaze(unittest.TestCase):
    #todo: to really test this, need to create a forest and verify no cycles

    def test_entrance_exit_pairs_are_available_after_creation(self):
        maze = generic_maze()
        self.assertIsNotNone(maze.entrance_exit_pairs())

    def test_mazify_map_generates_sequence_of_entrance_and_exit_spaces(self):
        maze = generic_maze()
        entrance_exit_pairs = tuple(maze._mazify_grid())
        for entrance_exit_pair in entrance_exit_pairs:
            self.assertEqual(len(entrance_exit_pair), 2)

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

    def test_image_scales_to_limiting_dimension_when_both_provided(self):
        small_spec, large_spec = 200, 2000
        square_maze = generic_maze(aspect_h=1, aspect_w=1)

        for limiting_dim, nonlimiting_dim in (('w_limit', 'h_limit'),
                                              ('h_limit', 'w_limit')):
            kwargs = {limiting_dim: small_spec, nonlimiting_dim: large_spec}
            image = square_maze.image(**kwargs)
            image_w, image_h = image.size
            tolerance = 0.05 * small_spec
            self.assertAlmostEqual(image_w, small_spec, delta=tolerance)
            self.assertAlmostEqual(image_h, small_spec, delta=tolerance)

    def test_image_scales_to_provided_dimension_when_one_provided(self):
        dimension_spec = 200
        square_maze = generic_maze(aspect_h=1, aspect_w=1)
        for limit in ('w_limit', 'h_limit'):
            kwargs = {limit: dimension_spec}
            image = square_maze.image(**kwargs)
            image_w, image_h = image.size
            tolerance = 0.05 * dimension_spec
            self.assertAlmostEqual(image_w, dimension_spec, delta=tolerance)
            self.assertAlmostEqual(image_h, dimension_spec, delta=tolerance)


def generic_maze(**kwargs):
    if 'complexity' not in kwargs:
        kwargs['complexity'] = .3  # speed things up when possible
    grid = _gridmakers.rectangle(**kwargs)
    return _maze.Maze(grid)


if __name__ == '__main__':
    unittest.main()
