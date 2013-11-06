import unittest
import math

from shapemaze import shapes, shapegrid


# the spec functions below produce the data required for automated testing
# of each IndexedShape implementation.
# Details are in class TestIndexedShapeImplementations
def square_spec():
    s = {'super shape creator': shapes.Square,
         'shapes': {'only one': {'idx': (1, 1),
                                 'creator': shapes.Square,
                                 'edges': {'top': {'idx': (0, 1),
                                                   'pts': ((1.0, 1.0),
                                                           (1.0, 2.0))},
                                           'bottom': {'idx': (2, 1),
                                                      'pts': ((2.0, 1.0),
                                                              (2.0, 2.0))},
                                           'left': {'idx': (1, 0),
                                                    'pts': ((1.0, 1.0),
                                                            (2.0, 1.0))},
                                           'right': {'idx': (1, 2),
                                                     'pts': ((1.0, 2.0),
                                                             (2.0, 2.0))}}}}}
    return s


#noinspection PyProtectedMember
def up_down_triangle_spec():
    side = 1.0
    h = math.sin(math.pi / 3.0)
    up_top_pt = (0.0, 0.0)
    up_left_pt = (h, -1 * side / 2.0)
    up_right_pt = (h, side / 2.0)
    dn_bottom_pt = up_right_pt
    dn_left_pt = up_top_pt
    dn_right_pt = (0.0, side)
    s = {'super shape creator': shapes.UpDownTriangle_factory,
         'shapes': {'up': {'idx': (0, 0),
                           'creator': shapes._UpDownTriangle_Up,
                           'edges': {'left': {'idx': (0, -1),
                                              'pts': (up_left_pt,
                                                      up_top_pt)},
                                     'right': {'idx': (0, 1),
                                               'pts': (up_top_pt,
                                                       up_right_pt)},
                                     'down': {'idx': (1, 0),
                                              'pts': (up_right_pt,
                                                      up_left_pt)}}},
                    'dn': {'idx': (0, 1),
                           'creator': shapes._UpDownTriangle_Down,
                           'edges': {'up': {'idx': (-1, 1),
                                            'pts': (dn_left_pt,
                                                    dn_right_pt)},
                                     'right': {'idx': (0, 2),
                                               'pts': (dn_right_pt,
                                                       dn_bottom_pt)},
                                     'left': {'idx': (0, 0),
                                              'pts': (dn_bottom_pt,
                                                      dn_left_pt)}}}}}
    return s


# edit this to add new shapes to automated testing
all_shape_implementation_specs = (square_spec(),
                                  up_down_triangle_spec())


#noinspection PyProtectedMember
class TestIndexedShapeImplementations(unittest.TestCase):
    """Run all implemented shapes through standard verification tests.

    Each implemented shape requires a standard set of data to test it:

    {'super shape creator': super_shape_creator,
     'shapes': {component_name: {'idx': component_index,
                                 'creator': component_creator
                                 'edges': {edge_name: {'idx': edge_index,
                                                       'pts': edge_points},
                                           ...}}
                ...}}

    - super_shape_creator - top level callable for grid when creating shapes
    - component_name - semantic name for each component within a super shape
    - component_index - the index for each component shape
    - component_creator - creator callable for component shapes
    - edge_name - semantic name for each edge of a component shape
    - edge_index - the index for each edge
    - edge_points - a pair of hand-calculated values that define each edge
    """
    # all specifications in this list
    def test_confirm_neighbor_indexes_of_each_component(self):
        for super_shape_spec in all_shape_implementation_specs:
            super_shape_creator = super_shape_spec['super shape creator']
            grid = shapegrid.ShapeGrid(super_shape_creator)
            # create each component shape
            for part_name, part_spec in super_shape_spec['shapes'].items():
                part = grid.create(part_spec['idx'])
                # confirm the component creator is correct
                self.assertIsInstance(part, part_spec['creator'],
                                      'Looks like the super shape creator is'
                                      ' using the wrong part creator.'
                                      'Expected {} but got an instance of {}'
                                      ''.format(part_spec['creator'],
                                                type(part)))
                # confirm the neighbor indexes
                edges_spec = part_spec['edges']
                edges_indexes = tuple(n_idx for n_idx, _ in part.edges())
                edges_indexes_spec = tuple(edge_spec['idx'] for
                                           _, edge_spec in edges_spec.items())
                self.assertItemsEqual(edges_indexes, edges_indexes_spec,
                                      'Mismatch of neighbor indexes for'
                                      ' {} component ({} @ {})'
                                      '\nof {}:\nspec:{}\nactual:{}'
                                      ''.format(part_name, part,
                                                part.index(),
                                                super_shape_creator,
                                                edges_indexes_spec,
                                                edges_indexes))
                # confirm the edge endpoints
                edges_endpoints = tuple((set(edge.endpoints())
                                         for _, edge in part.edges()))
                #flattened = tuple(itertools.chain(edge_endpoints))
                edges_endpoints_spec = tuple((set(edge_data['pts'])
                                              for _, edge_data
                                              in edges_spec.items()))
                #flattened_spec = tuple(itertools.chain(edge_endpoints_spec))
                self.assertItemsEqual(edges_endpoints, edges_endpoints_spec,
                                      'The end points for the {} component'
                                      '({} @ {}) do not match the spec.'
                                      '\nExpected {}\nbut got {}'
                                      ''.format(part_name, part, part.index(),
                                                edges_endpoints_spec,
                                                edges_endpoints))

    def test_edge_endpoints_of_neighbors_coincide(self):
        for spec in all_shape_implementation_specs:
            grid = shapegrid.ShapeGrid(spec['super shape creator'])
            # create each component shape
            for _, part_spec in spec['shapes'].items():
                main = grid.create(part_spec['idx'])
                # confirm shared edges match INTERNALLY, not through edge object
                for n_index, neighbor in main.neighbors():
                    if neighbor is None:
                        # test weakness - doesn't test supershape boundaries
                        continue
                    endpoints_main = main._edge_endpoints[n_index]
                    endpoints_neighbor = neighbor._edge_endpoints[main.index()]
                    self.assertItemsEqual(endpoints_main, endpoints_neighbor)


#noinspection PyProtectedMember
class TestIndexedShapeBase(unittest.TestCase):
    def test_creating_raises_NotImplementedError(self):
        dummy_args = (None, None)
        self.assertRaises(NotImplementedError, shapes.IndexedShapeBase,
                          *dummy_args)

    def test_index_returns_same_index_set_on_creation(self):
        index_spec = (10, 20)
        #noinspection PyTypeChecker
        shape = generic_shape(index=index_spec)
        self.assertEqual(shape.index(), index_spec)

    def test_creation_takes_ownership_of_all_unowned_edges(self):
        shape = generic_shape()
        # confirm ownership of every edge for an independent shape
        owned_indexes = (n_index for n_index, edge in shape.edges())
        owned_indexes_spec = shape._neighbor_indexes
        self.assertItemsEqual(owned_indexes, owned_indexes_spec)

    def test_creation_does_not_take_ownership_of_claimed_edges(self):
        shape = generic_shape()
        # create a new neighbor which should only claim the new edges
        a_neighbor_index, _ = tuple(shape.neighbors())[0]  # any edge
        neighbor = shape._grid.create(a_neighbor_index)
        # confirm that the original shape still owns the shared edge
        self.assertIn(a_neighbor_index, shape._owned_edges)
        # confirm that the neighbor does not own the shared edge
        self.assertNotIn(shape.index(), neighbor._owned_edges)

    def test_give_away_edges_moves_ownership_of_edges_to_neighbors(self):
        index_1 = (1, 2)
        index_2 = (1, 3)
        original_owner = generic_shape(index=index_1)
        neighbor = generic_shape(index=index_2, grid=original_owner._grid)
        # confirm original owner actually owns the edge
        self.assertIn(index_2, original_owner._owned_edges)
        # confirm ownership changes after giving away the edge
        original_owner._give_away_edges()
        self.assertNotIn(index_2, original_owner._owned_edges)
        self.assertIn(index_1, neighbor._owned_edges)

    def test_edge_returns_an_edge_for_each_neighbor_index(self):
        shape = generic_shape()
        for n_index in shape._neighbor_indexes:
            self.assertIsNotNone(shape.edge(n_index))

    def test_edge_returns_same_edge_from_both_sides(self):
        # make a pair of neighbors
        first_index = (1, 2)
        second_index = (1, 3)
        first_shape = generic_shape(index=first_index)
        second_shape = generic_shape(index=second_index, grid=first_shape._grid)
        # get the shared edge from both sides
        shared_edge_from_first = first_shape.edge(second_index)
        shared_edge_from_second = second_shape.edge(first_index)
        self.assertIs(shared_edge_from_first, shared_edge_from_second)

    def test_neighbors_generates_the_neighbor_for_each_neighbor_index(self):
        shape = generic_shape()
        # create neighbors on all edges
        indexed_neighbors_spec = list()
        for n_index in shape._neighbor_indexes:
            neighbor = shape._grid.create(n_index)
            indexed_neighbors_spec.append((n_index, neighbor))
        # confirm that the correct index-neighbor combos are generated
        indexed_neighbors = list(shape.neighbors())
        self.assertItemsEqual(indexed_neighbors, indexed_neighbors_spec)

    def test_neighbors_generates_index_and_None_for_empty_neighbors(self):
        # make a shape with no neighbors
        shape = generic_shape()
        # confirm that each neighbor is generated as None
        for n_index, neighbor in shape.neighbors():
            self.assertIn(n_index, shape._neighbor_indexes)
            self.assertIsNone(neighbor)


#noinspection PyProtectedMember
class TestEdge(unittest.TestCase):
    def test_endpoints_returns_endpoints_from_indicated_shape(self):
        """Each shape may/will have a different order for the same endpoints."""
        # make a shape and any neighbor
        some_index = (1, 2)
        shape_1 = generic_shape(index=some_index)
        n_index = shape_1._neighbor_indexes[0]
        shape_2 = shape_1._grid.create(n_index)
        # get the shared edge
        edge = shape_1.edge(shape_2.index())
        # get the endpoints from the edge
        endpoints_1 = edge.endpoints(shape_1.index())
        endpoints_2 = edge.endpoints(shape_2.index())
        # confirm the end points came from the indicated shape
        self.assertIs(endpoints_1, shape_1._edge_endpoints[shape_2.index()])
        self.assertIs(endpoints_2, shape_2._edge_endpoints[shape_1.index()])

    def test_endpoints_returns_from_neighbor_1_if_not_specified(self):
        # make a shape and any neighbor
        some_index = (1, 2)
        shape_a = generic_shape(index=some_index)
        n_index = shape_a._neighbor_indexes[0]
        shape_b = shape_a._grid.create(n_index)
        grid = shape_a._grid
        # get the shared edge
        edge = shape_a.edge(shape_b.index())
        # get the endpoints from the edge without specifying the shape index
        endpoints = edge.endpoints()
        # confirm the end points came from neighbor_1
        neighbor_1 = grid.get(edge._neighbor_1_index)
        neighbor_2 = grid.get(edge._neighbor_2_index)
        self.assertIs(endpoints, neighbor_1._edge_endpoints[neighbor_2.index()])

    def test_endpoints_returns_from_neighbor_2_if_not_specified_and_1None(self):
        # make a shape and any neighbor
        some_index = (1, 2)
        shape_a = generic_shape(index=some_index)
        n_index = shape_a._neighbor_indexes[0]
        shape_b = shape_a._grid.create(n_index)
        grid = shape_a._grid
        # get the shared edge
        edge = shape_a.edge(shape_b.index())
        # find and remove the shape at index stored for neighbor_1
        neighbor_1_index = edge._neighbor_1_index
        grid.remove(neighbor_1_index)
        # get the endpoints from the edge without specifying the shape index
        endpoints = edge.endpoints()
        # confirm the end points came from neighbor_2 (since neighbor_1 gone)
        neighbor_2 = grid.get(edge._neighbor_2_index)
        self.assertIs(endpoints, neighbor_2._edge_endpoints[neighbor_1_index])

    def test_endpoints_raises_valueerror_for_non_neighbor_index(self):
        # make a shape
        some_index = (1, 2)
        shape = generic_shape(index=some_index)
        # get a non neighboring index
        non_neighbor_index = (1000, 2000)
        self.assertNotIn(non_neighbor_index, shape._neighbor_indexes)
        # confirm ValueError when non neighbor used to specify endpoint order
        _, any_edge = tuple(shape.edges())[0]
        self.assertRaises(ValueError,
                          any_edge.endpoints, *(non_neighbor_index,))


def generic_shape(shape_maker=None, index=None, grid=None):
    # provide test defaults
    shape_maker = shape_maker or shapes.Square
    grid = grid or shapegrid.ShapeGrid(shape_maker)
    index = index or (1, 2)
    # get a shape
    shape = grid.create(index)
    return shape


if __name__ == '__main__':
    unittest.main()