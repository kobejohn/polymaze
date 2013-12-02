import mock
import unittest

import PIL.Image

import polymaze as pmz


#todo move these into main PolyGrid specification
class Testgridmakers(unittest.TestCase):
    def test_by_default_produces_a_rectangular_grid(self):
        grid = pmz.PolyGrid(complexity=0.5)
        # get the bounds to be checked
        all_indexes = [s.index() for s in grid.shapes()]
        all_rows, all_cols = zip(*all_indexes)
        row_min, row_max = min(all_rows), max(all_rows)
        col_min, col_max = min(all_cols), max(all_cols)
        # confirm that the shape count is exactly the index area of rectangle
        shape_count_spec = (row_max - row_min + 1) * (col_max - col_min + 1)
        shape_count = len(all_indexes)
        self.assertEqual(shape_count, shape_count_spec)
        # confirm that every index exists
        for row in range(row_min, row_max + 1):
            for col in range(col_min, col_max + 1):
                self.assertIsNotNone(grid.get((row, col)))

    #todo: reopen this when character implemented
    #def test_character_gets_a_char_image_for_provided_char(self):
    #    character_spec = 'C'
    #    with mock.patch('polymaze.gridmakers._character_image') as m_c_image:
    #        try:
    #            _gridmakers.character(character_spec)
    #        except Exception:
    #            pass  # ignore fallout....
    #        self.assertIsNone(m_c_image.assert_called_with(character_spec))

    #todo: reopen this when character implemented
    #def test_character_calcs_grid_bounds_with_aspect_if_provided(self):
    #    any_char = 'c'
    #    aspect_h_spec = 3
    #    aspect_w_spec = 5
    #    with mock.patch('polymaze.gridmakers._calc_index_bounds') as m_bounds:
    #        try:
    #            _gridmakers.character(any_char, aspect_h=aspect_h_spec,
    #                                  aspect_w=aspect_w_spec)
    #        except Exception:
    #            pass  # ignore fallout.... haven't considered the risks
    #        call_kwargs = m_bounds.call_args[1]
    #        self.assertIn(('aspect_h', aspect_h_spec), call_kwargs.items())
    #        self.assertIn(('aspect_w', aspect_w_spec), call_kwargs.items())

    #todo: reopen this when character implemented
    #def test_character_calcs_grid_bounds_with_image_if_aspct_not_provided(self):
    #    any_char = 'c'
    #    image_w_spec, image_h_spec = 113, 237
    #    with mock.patch('polymaze.gridmakers._calc_index_bounds') as m_bounds:
    #        with mock.patch('polymaze.gridmakers._character_image') as m_c_im:
    #            m_c_im.return_value.size = (image_w_spec, image_h_spec)
    #            try:
    #                _gridmakers.character(any_char)
    #            except Exception:
    #                pass  # ignore fallout.... haven't considered the risks
    #            call_kwargs = m_bounds.call_args[1]
    #            self.assertIn(('aspect_h', image_h_spec), call_kwargs.items())
    #            self.assertIn(('aspect_w', image_w_spec), call_kwargs.items())

    #todo: reopen this when character implemented
    #def test_character_converts_image_to_shapes(self):
    #    character_spec = 'C'
    #    with mock.patch('polymaze.gridmakers._image_white_to_shapes') as m_i2s:
    #        try:
    #            _gridmakers.character(character_spec)
    #        except Exception:
    #            pass  # ignore fallout....
    #        self.assertEqual(m_i2s.call_count, 1)

    #todo: reopen this when character implemented
    #def test_image_white_to_shapes_returns_grid_with_max_provided_size(self):
    #    rows_spec, cols_spec = 20, 30
    #    _image_size = 200, 300  # not part of spec
    #    _white_im = PIL.Image.new('L', _image_size, color=255)
    #    grid = _polygrid.PolyGrid()
    #    grid = _gridmakers._image_white_to_shapes(_white_im, grid,
    #                                              rows_spec, cols_spec)
    #    # confirm that the shape count is exactly the index area of rectangle
    #    shape_count_spec = rows_spec * cols_spec
    #    all_indexes = [s.index() for s in grid.shapes()]
    #    shape_count = len(all_indexes)
    #    self.assertEqual(shape_count, shape_count_spec)
    #    # confirm that every index exists
    #    for row in range(rows_spec):
    #        for col in range(cols_spec):
    #            self.assertIsNotNone(grid.get((row, col)))

    #todo: reopen this when character implemented
    #def test_image_white_to_shapes_converts_multi_channels_to_mono(self):
    #    _some_dim = 20  # not part of spec
    #    not_mono = 'RGB'
    #    mono = 'L'
    #    grid = _polygrid.PolyGrid()
    #    m_image = mock.MagicMock()
    #    m_image.getbands.return_value = not_mono
    #    try:
    #        _gridmakers._image_white_to_shapes(m_image, grid,
    #                                           _some_dim, _some_dim)
    #    except Exception:
    #        pass
    #    m_image.assert_has_calls(mock.call.convert(mono))


#noinspection PyProtectedMember
class TestShapeGrid(unittest.TestCase):
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
        known_creator = pmz.SUPERSHAPES_DICT['Square']
        some_index = (1, 2)
        grid = generic_grid(supershape=known_creator,
                            neighborhood_center_index=some_index)
        all_shapes_spec = grid._shapes.values()
        # confirm expected number of shapes (center + 4 neighbors)
        shape_count_spec = 5
        self.assertEqual(len(all_shapes_spec), shape_count_spec)
        all_shapes = tuple(grid.shapes())
        self.assertItemsEqual(all_shapes, all_shapes_spec)

    def test_edges_generates_each_edge_exactly_once(self):
        # make a grid with a center square and a neighbor on each side
        known_creator = pmz.SUPERSHAPES_DICT['Square']
        some_index = (1, 2)
        grid = generic_grid(supershape=known_creator,
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
        center_index = (1, 1)
        grid = generic_grid(neighborhood_center_index=center_index)
        center = grid.get(center_index)
        # confirm that exactly each neighbor is a border (has empty neighbors)
        n_indexes = tuple(center.n_indexes())
        border_shapes_spec = (grid.get(n_index) for n_index in n_indexes)
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
def generic_grid(supershape=None, neighborhood_center_index=None):
    grid = pmz.PolyGrid(supershape=supershape)
    if neighborhood_center_index:
        # create a neighborhood based on whatever creator is being used
        # the neighborhood is defined as a central shape with a neighbor
        # on each edge
        center_shape = grid.create(neighborhood_center_index)
        for n_index in center_shape.n_indexes():
            grid.create(n_index)
    return grid


if __name__ == '__main__':
    unittest.main()
