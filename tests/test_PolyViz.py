import unittest

from tests.test_PolyGrid import generic_grid
from polymaze.polygrid import PolyGrid, PolyViz

# silly workaround to allow tests to work in py2 or py3
try:
    _assertCountEqual = unittest.TestCase.assertCountEqual  # py3
    from unittest import mock
except (AttributeError, ImportError):
    _assertCountEqual = unittest.TestCase.assertItemsEqual  # py2
    import mock


class TestPolyViz(unittest.TestCase):
    def test_provides_reference_to_related_grid(self):
        grid = generic_grid()
        viz = generic_viz(grid)
        self.assertIs(viz.grid, grid)

    def test_can_create_new_part_styles(self):
        viz = generic_viz()
        any_name = 'asdf'
        any_color = (0, 0, 0, 0)
        # confirm styles don't exist
        self.assertNotIn(any_name, viz._shape_styles)
        self.assertNotIn(any_name, viz._edge_styles)
        # make the new styles
        viz.new_shape_style(any_name, any_color)
        viz.new_edge_style(any_name, any_color)
        # confirm they were added
        self.assertIn(any_name, viz._shape_styles)
        self.assertIn(any_name, viz._edge_styles)

    def test_uses_get_x_style_when_drawing_each_part(self):
        viz = generic_viz()
        get_style_names = ('get_shape_style', 'get_edge_style')
        for get_style_name in get_style_names:
            with mock.patch.object(viz, get_style_name) as m_getstyle:
                # make the call
                try:
                    viz.image()
                except Exception:
                    pass  # it will probably die. that's fine.
                # confirm that the style was retrieved appropriately
                self.assertTrue(m_getstyle.called)

    def test_get_x_style_returns_default_when_part_has_no_style_setting(self):
        viz = generic_viz(generic_grid(neighborhood_center_index=(0, 0)))
        edge_default_spec = viz._edge_styles['default']
        shape_default_spec = viz._shape_styles['default']
        # get one of each type of part
        shape = next(iter(viz.grid.shapes()))
        edge = next(iter(viz.grid.edges()))
        # confirm no style setting
        self.assertIsNone(shape.viz_style)
        self.assertIsNone(edge.viz_style)
        # confirm the lookup matches the specification
        self.assertIs(viz.get_shape_style(shape), shape_default_spec)
        self.assertIs(viz.get_edge_style(edge), edge_default_spec)

    def test_get_x_style_returns_named_style_setting_when_part_has_it(self):
        viz = generic_viz()
        # create some named styles
        shape_style_name = '<<shape>>'
        edge_style_name = '<<edge>>'
        any_color = (1, 2, 3, 4)
        viz.new_shape_style(shape_style_name, color=any_color)
        viz.new_edge_style(edge_style_name, color=any_color)
        # apply style to some parts
        shape = next(iter(viz.grid.shapes()))
        edge = next(iter(viz.grid.edges()))
        shape.viz_style = shape_style_name
        edge.viz_style = edge_style_name
        # get the style container that should be returned
        shape_style_spec = viz._shape_styles[shape_style_name]
        edge_style_spec = viz._edge_styles[edge_style_name]
        # confirm correct style returned
        self.assertIs(viz.get_shape_style(shape), shape_style_spec)
        self.assertIs(viz.get_edge_style(edge), edge_style_spec)

    def test_image_returns_a_PIL_image(self):
        viz = generic_viz()
        im = viz.image()
        # confirm it has an image method
        self.assertTrue(hasattr(im, 'crop'))

    def test_image_returns_None_for_empty_grid(self):
        # make and confirm an empty grid
        empty_grid = PolyGrid()
        self.assertEqual(len(tuple(empty_grid.shapes())), 0)
        # confirm image is None
        viz = PolyViz(empty_grid)
        self.assertIsNone(viz.image())


def generic_viz(grid=None):
    grid = grid or generic_grid(neighborhood_center_index=(0,0))
    return PolyViz(grid)