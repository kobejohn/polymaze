import unittest

from shapemaze import shapes, shapegrid, gridmakers


class Testgridmakers(unittest.TestCase):
    def test_rectangle_makes_a_grid_with_indexes_in_provided_dimensions(self):
        v_shapes_spec = 23
        h_shapes_spec = 31
        rect_grid = gridmakers.rectangle(vertical_shapes=v_shapes_spec,
                                         horizontal_shapes=h_shapes_spec)
        all_indexes = (shape.index() for shape in rect_grid.shapes())
        all_indexes_spec = ((row, col)
                            for row in range(v_shapes_spec)
                            for col in range(h_shapes_spec))
        self.assertItemsEqual(all_indexes, all_indexes_spec)

    def test_character_grid_indexes_are_bound_by_provided_bounds(self):
        v_bound_spec = 23
        h_bound_spec = 31
        any_character = 'I'
        rect_grid = gridmakers.character(any_character,
                                         max_vertical_indexes=v_bound_spec,
                                         max_horizontal_indexes=h_bound_spec)
        all_indexes = (shape.index() for shape in rect_grid.shapes())
        all_rows, all_cols = zip(*all_indexes)
        row_range = max(all_rows) - min(all_rows) + 1
        col_range = max(all_cols) - min(all_cols) + 1
        self.assertLessEqual(row_range, v_bound_spec)
        self.assertLessEqual(col_range, h_bound_spec)


#noinspection PyProtectedMember
class TestShapeGrid(unittest.TestCase):
    def test_create_shape_uses_the_creator_stored_at_creation(self):
        creator = shapes.Square
        grid = generic_grid(creator=creator)
        some_index = (1, 2)
        shape = grid.create(some_index)
        # this is not true for super shapes. need a mock check to be complete
        self.assertIsInstance(shape, creator)

    def test_get_returns_shape_created_with_same_index(self):
        grid = generic_grid()
        some_index = (1, 2)
        shape_spec = grid.create(some_index)
        shape = grid.get(some_index)
        self.assertIs(shape, shape_spec)

    def test_get_returns_None_for_nonexistent_indexes(self):
        grid = generic_grid()
        unused_index = (1, 2)
        self.assertIsNone(grid.get(unused_index))

    def test_shapes_generates_each_shape_exactly_once(self):
        # make a grid with a center square and a neighbor on each side
        known_creator = shapes.Square  # 4 sides
        some_index = (1, 2)
        grid = generic_grid(creator=known_creator,
                            neighborhood_center_index=some_index)
        all_shapes_spec = grid._shapes.values()
        # confirm expected number of shapes (center + 4 neighbors)
        shape_count_spec = 5
        self.assertEqual(len(all_shapes_spec), shape_count_spec)
        all_shapes = tuple(grid.shapes())
        self.assertItemsEqual(all_shapes, all_shapes_spec)

    def test_edges_generates_each_edge_exactly_once(self):
        # make a grid with a center square and a neighbor on each side
        known_creator = shapes.Square  # 4 sides
        some_index = (1, 2)
        grid = generic_grid(creator=known_creator,
                            neighborhood_center_index=some_index)
        edges_spec = list()
        for shape in grid.shapes():
            for n_index, edge in shape.edges():
                # real set() didn't work well. ~set of all edges only once
                if edge not in edges_spec:
                    edges_spec.append(edge)
        # confirm number of edges correct (center 4 + (4 * neighbor 3))
        edge_count_spec = 16
        self.assertEqual(len(edges_spec), edge_count_spec)
        # confirm each edge appears exactly once
        edges = tuple(grid.edges())
        self.assertItemsEqual(edges, edges_spec)

    def test_border_shapes_generates_all_shapes_with_any_empty_neighbors(self):
        # make a grid with a center square and a neighbor on each side
        known_creator = shapes.Square
        center_index = (1, 1)
        grid = generic_grid(creator=known_creator,
                            neighborhood_center_index=center_index)
        # confirm that exactly each neighbor is a border (has empty neighbors)
        tblr_indexes = (0, 1), (2, 1), (1, 0), (1, 2)
        border_shapes_spec = (grid.get(index) for index in tblr_indexes)
        border_shapes = tuple(grid.border_shapes())
        self.assertItemsEqual(border_shapes, border_shapes_spec)

    def test_remove_removes_shape_from_the_grid(self):
        # create a grid with one shape
        grid = generic_grid()
        some_index = (1, 2)
        grid.create(some_index)
        # confirm shape is there
        shape_before_remove = grid.get(some_index)
        self.assertIsNotNone(shape_before_remove)
        # delete the center shape and confirm it is gone
        grid.remove(some_index)
        center_shape_after_remove = grid.get(some_index)
        self.assertIsNone(center_shape_after_remove)

    def test_remove_removes_the_grid_from_the_shape(self):
        # create a grid with one shape
        grid = generic_grid()
        some_index = (1, 2)
        grid.create(some_index)
        # confirm shape has a reference to grid
        removed_shape = grid.get(some_index)
        self.assertIs(removed_shape._grid, grid)
        # delete the center shape and confirm it has no reference to grid
        grid.remove(some_index)
        self.assertIsNone(removed_shape._grid)

    def test_remove_for_nonexistent_key_simply_returns(self):
        grid = generic_grid()
        # confirm there is no shape at a given index
        some_index = (1, 2)
        self.assertIsNone(grid.get(some_index))
        # remove the index and confirm no error
        self.assertIsNone(grid.remove(some_index))

    def test_remove_causes_unshared_edges_of_removed_shape_to_be_delisted(self):
        # create a grid with one shape
        grid = generic_grid()
        some_index = (1, 2)
        grid.create(some_index)
        # confirm the grid has some edges
        edges_before_remove = tuple(grid.edges())
        self.assertNotEqual(len(edges_before_remove), 0)
        # remove the shape and confirm that the grid no longer has any edges
        grid.remove(some_index)
        edges_after_remove = tuple(grid.edges())
        self.assertEqual(len(edges_after_remove), 0)

    def test_remove_pushes_shared_edges_of_removed_shape_to_neighbors(self):
        # create a neighborhood with center shape and a neighbor on each side
        center_index = (1, 2)
        grid = generic_grid(neighborhood_center_index=center_index)
        center_shape = grid.get(center_index)
        # confirm the center shape owns all its edges
        center_neighbor_edge_combos = list()
        for n_index, neighbor in center_shape.neighbors():
            self.assertTrue(n_index in center_shape._owned_edges)
            edge = center_shape.edge(n_index)
            center_neighbor_edge_combos.append((neighbor, edge))
        # remove the center shape and confirm the edges have moved to neighbors
        grid.remove(center_index)
        for neighbor, previously_unowned_edge in center_neighbor_edge_combos:
            owned_edges = neighbor._owned_edges.values()
            self.assertIn(previously_unowned_edge, owned_edges)


#noinspection PyProtectedMember
def generic_grid(creator=None, neighborhood_center_index=None):
    # provide defaults
    creator = creator or shapes.Square
    grid = shapegrid.ShapeGrid(creator)
    if neighborhood_center_index:
        # create a neighborhood based on whatever creator is being used
        # the neighborhood is defined as a central shape with a neighbor
        # on each edge
        center_shape = grid.create(neighborhood_center_index)
        for n_index in center_shape._ordered_n_indexes:
            grid.create(n_index)
    return grid


if __name__ == '__main__':
    unittest.main()
