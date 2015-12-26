import os
import sys
import unittest

sys.path.insert(0, os.path.abspath('..'))  # hack to allow simple test structure
import polymaze as pmz
from polymaze import polygrid as _polygrid_module


# silly workaround to allow tests to work in py2 or py3
try:
    _assertCountEqual = unittest.TestCase.assertCountEqual  # py3
    from unittest import mock
except (AttributeError, ImportError):
    _assertCountEqual = unittest.TestCase.assertItemsEqual  # py2
    import mock


# noinspection PyProtectedMember
# noinspection PyBroadException
class TestPolyGrid_Creation(unittest.TestCase):
    @mock.patch.object(_polygrid_module.PolyGrid, 'create_from_image')
    @mock.patch.object(_polygrid_module, '_string_image')
    def test_create_string_converts_to_image_then_uses_create_image(self,
                                                                    m_s_img,
                                                                    m_crt_im):
        grid = generic_grid()
        source_string_spec = 'asdf'
        grid.create_string(source_string_spec)
        # confirm image conversion was done with the source string
        m_s_img_args = m_s_img.call_args[0]
        self.assertIn(source_string_spec, m_s_img_args)
        # confirm the result image was then used to create shapes
        m_crt_im_args = m_crt_im.call_args[0]
        self.assertIn(m_s_img.return_value, m_crt_im_args)

    def test_string_image_returns_a_PIL_image(self):
        some_string = 'asdf'
        image = _polygrid_module._string_image(some_string)
        self.assertTrue(hasattr(image, 'resize'))

    @mock.patch('PIL.ImageFont.truetype')
    def test_string_image_uses_bundled_font_when_none_provided(self, m_tt):
        some_string = 'asdf'
        bundled_font_name = 'NotoSansCJK-Bold.ttc'
        try:
            _polygrid_module._string_image(some_string)
        except Exception:
            pass  # ignore fallout due to mock object blowing up later
        m_truetype_args = m_tt.call_args[0]
        m_truetype_arg = m_truetype_args[0]
        self.assertIn(bundled_font_name, m_truetype_arg)

    @mock.patch('PIL.ImageFont.truetype')
    def test_string_image_tries_provided_font_path(self, m_truetype):
        some_string = 'asdf'
        some_font = 'somefont'
        try:
            _polygrid_module._string_image(some_string, font_path=some_font)
        except Exception:
            pass  # ignore fallout
        m_truetype_args = m_truetype.call_args[0]
        self.assertIn(some_font, m_truetype_args)

    def test_string_image_raises_ValueError_if_provided_font_fails(self):
        nonexistent_font_path = 'asdfjkl'
        some_string = 'asdf'
        self.assertRaises(ValueError, _polygrid_module._string_image, some_string, font_path=nonexistent_font_path)

    def test_create_from_image_looks_like_provided_image(self):
        pass  # todo: too lazy to mock / test :(

    def test_string_image_is_about_double_height_with_newline(self):
        # get a string image without newline
        char = 'a'
        image_without_newline = _polygrid_module._string_image(char)
        # get a string image with 1 literal newline
        char_with_newline = char + '\\n' + char
        image_with_newline = _polygrid_module._string_image(char_with_newline)
        # confirm height is about double
        h_single_line = image_without_newline.size[1]
        h_min_spec = 2 * h_single_line
        h_max_spec = 3.5 * h_single_line  # since cropped, generous upper bound
        h_double = image_with_newline.size[1]
        self.assertTrue(h_min_spec <= h_double <= h_max_spec,
                        'Height of text with newline was unexpectedly not about'
                        ' double the height of a single line.\nExpected'
                        ' between {} and {} but got {}'
                        ''.format(h_min_spec, h_max_spec, h_double))

    def test_sized_grid_is_under_single_target_size_by_less_than_4_side_lengths(self):
        # establish the desired dimension size
        single_dimension_size_spec = {0: ('height', 15),
                                      1: ('width', 20)}

        # build a grid with the target size option
        for dimension, (kw, dimension_limit) in single_dimension_size_spec.items():
            sized_grid = generic_grid()
            sized_grid.create_string('?', **{kw: dimension_limit})

            # manually detect the actual size of the target dimension
            dimension_min = 99999
            dimension_max = -99999
            for edge in sized_grid.edges():
                for yx_units in edge.endpoints():
                    dimension_value = yx_units[dimension]
                    dimension_min = min(dimension_value, dimension_min)
                    dimension_max = max(dimension_value, dimension_max)
            size = dimension_max - dimension_min

            # confirm the actual size is under the target within the specified range
            max_delta_spec = 4 * sized_grid._supershape._reference_length
            size_max_spec = single_dimension_size_spec[dimension][1]
            size_min_spec = size_max_spec - max_delta_spec
            self.assertGreaterEqual(size, size_min_spec)
            self.assertLessEqual(size, size_max_spec)

    def test_sized_grid_is_under_double_target_size_by_less_than_4_side_lengths(self):
        # establish the desired dimension sizes
        dimensions_data = {0: {'size_spec': 15,
                               'actual_max': -99999,
                               'actual_min': 99999},
                           1: {'size_spec': 20,
                               'actual_max': -99999,
                               'actual_min': 99999}}

        # build a grid with the target size options both set
        sized_grid = generic_grid()
        sized_grid.create_string('?', height=dimensions_data[0]['size_spec'],
                                 width=dimensions_data[1]['size_spec'])

        # determine the actual min and max of each dimension
        for edge in sized_grid.edges():
            for yx_point in edge.endpoints():
                for dimension in (0, 1):
                    dimension_value = yx_point[dimension]
                    dimension_min = dimensions_data[dimension]['actual_min']
                    dimensions_data[dimension]['actual_min'] = min(dimension_value, dimension_min)
                    dimension_max = dimensions_data[dimension]['actual_max']
                    dimensions_data[dimension]['actual_max'] = max(dimension_value, dimension_max)

        # confirm the size of each dimension
        for dimension in (0, 1):
            size = dimensions_data[dimension]['actual_max'] - dimensions_data[dimension]['actual_min']
            max_delta_spec = 4 * sized_grid._supershape._reference_length
            size_max_spec = dimensions_data[dimension]['size_spec']
            size_min_spec = size_max_spec - max_delta_spec
            self.assertGreaterEqual(size, size_min_spec)
            self.assertLessEqual(size, size_max_spec)


# noinspection PyProtectedMember
class TestShapeGrid(unittest.TestCase):
    def test_produces_an_empty_grid(self):
        grid = pmz.PolyGrid()
        self.assertEqual(len(tuple(grid.shapes())), 0)

    def test_create_rectangle_produces_a_rectangular_graph(self):
        # the graph should be rectangular though the grid may be skewed
        grid = generic_grid()
        grid.create_rectangle(complexity=3)
        # test by checking the rectangular area determined by extrema
        # is about the same as the number of shapes * average area
        # get the extrema first
        all_vertexes = list()
        for edge in grid.edges():
            all_vertexes.extend(edge.endpoints())
        y_all, x_all = zip(*all_vertexes)
        top, bottom = min(y_all), max(y_all)
        left, right = min(x_all), max(x_all)
        rectangular_area = (bottom - top) * (right - left)
        # get the total area by shapes
        shape_count = len(tuple(s for s in grid.shapes()))
        rectangular_shape_area_spec = shape_count * grid._supershape.avg_area()
        # confirm the approximate match
        tolerance = 0.1 * rectangular_shape_area_spec
        self.assertAlmostEqual(rectangular_area, rectangular_shape_area_spec,
                               delta=tolerance)

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
        _assertCountEqual(self, all_shapes, all_shapes_spec)

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
        _assertCountEqual(self, edges, edges_spec)

    def test_border_shapes_generates_all_shapes_with_any_empty_neighbors(self):
        # make a grid with a center square and a neighbor on each side
        center_index = (1, 1)
        grid = generic_grid(neighborhood_center_index=center_index)
        center = grid.get(center_index)
        # confirm that exactly each neighbor is a border (has empty neighbors)
        n_indexes = tuple(center.n_indexes())
        border_shapes_spec = (grid.get(n_index) for n_index in n_indexes)
        border_shapes = tuple(grid.border_shapes())
        _assertCountEqual(self, border_shapes, border_shapes_spec)

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
