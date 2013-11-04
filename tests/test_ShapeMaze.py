import unittest


#noinspection PyProtectedMember
class TestShapeMaze(unittest.TestCase):
    pass


#    def test_entrance_and_exit_are_available_after_creation(self):
#        maze = generic_polymaze()
#        self.assertTrue(hasattr(maze, 'entrance_space'))
#        self.assertTrue(hasattr(maze, 'exit_space'))
#
#    def test_mazify_map_returns_two_spaces(self):
#        maze = generic_polymaze()
#        returned_spaces = maze._mazify_map(maze._map)
#        self.assertEqual(len(returned_spaces), 2)
#
#    #todo: to really test this, need to create a tree and verify no cycles
#
#    def test_is_pathable_returns_true_if_edges_are_walls_except_previous(self):
#        maze = generic_polymaze()
#        # replace the map with a simple neighborhood map
#        center, spec_data = triangle_with_neighbors_with_spec_data()
#        left = spec_data['left neighbor']
#        bottom = spec_data['bottom neighbor']
#        neighborhood_map = center.map()
#        maze._map = neighborhood_map
#        # set wall status on all edges
#        for edge in maze._map.all_edges():
#            setattr(edge, 'status', maze.WALL)
#        # confirm that all neighbor directions are pathable
#        self.assertTrue(maze._is_pathable(left, center))
#        self.assertTrue(maze._is_pathable(bottom, center))
#        self.assertTrue(maze._is_pathable(center, bottom))
#        self.assertTrue(maze._is_pathable(center, left))
#        # break a path from one side to the other of the neighborhood
#        LEFT, RIGHT, MIDDLE = center.LEFT, center.RIGHT, center.MIDDLE
#        left.edge(LEFT).status = maze.PATH
#        left.edge(RIGHT).status = maze.PATH
#        center.edge(MIDDLE).status = maze.PATH
#        bottom.edge(RIGHT).status = maze.PATH
#        # confirm that none of the spaces are pathable
#        self.assertFalse(maze._is_pathable(left, center))
#        self.assertFalse(maze._is_pathable(bottom, center))
#        self.assertFalse(maze._is_pathable(center, bottom))
#        self.assertFalse(maze._is_pathable(center, left))
#
#    def test_image_returns_image_with_same_rect_ratio_as_map_space(self):
#        maze = generic_polymaze()
#        # find min/max indexes of the maze's map
#        rows, cols = zip(*maze._map._map)
#        row_min, row_max = min(rows), max(rows)
#        col_min, col_max = min(cols), max(cols)
#        # convert the min/max indexes to side units
#        sides_per_row, sides_per_col = maze._map._polygon_class.SIDES_PER_INDEX
#        vert_size = sides_per_row * (row_max - row_min + 1)
#        horz_size = sides_per_col * (col_max - col_min + 1)
#        ratio_spec = float(vert_size) / horz_size
#        # get the image and size
#        some_width_limit, some_height_limit = 200, 100
#        image = maze.image(some_height_limit, some_width_limit)
#        image_width, image_height = image.size
#        ratio = float(image_height) / image_width
#        # confirm the image size and specified size match
#        self.assertAlmostEqual(ratio, ratio_spec, places=1)




if __name__ == '__main__':
    unittest.main()