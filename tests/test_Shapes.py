import math
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
class TestComponentShapeImplementations(unittest.TestCase):
    """Confirm that all implemented supershapes meet basic specifications."""
    def setUp(self):
        # make a neighborhood (grid) for each supershape
        # the neighborhood consists of a complete supershape plus a shape
        # on each outer border of the supershape (which ensures there are two
        # shapes sharing each possible edge of a supershape)
        self.shape_neighborhoods = [supershape_with_neighbors(ss)
                                    for _, ss in pmz.SUPERSHAPES_DICT.items()]

    def test_neighbors_have_each_others_indexes(self):
        """Confirm that all neighbor identifications are mutual."""
        for neighborhood in self.shape_neighborhoods:
            for shape in neighborhood.shapes():
                self_index = shape.index()
                for n_index, neighbor in shape.neighbors():
                    if neighbor is None:
                        continue  # skip empty borders
                    # confirm neighbor has self in its indexes
                    self.assertIn(self_index, neighbor._edge_data,
                                  'For SuperShape {},'
                                  '\nshape {} @ {}'
                                  '\nidentified {} @ {}'
                                  '\nas a neighbor but neighbor did not'
                                  ' identify shape as one.'
                                  ''.format(neighborhood.supershape_name(),
                                            shape.name(), shape.index(),
                                            neighbor.name(), neighbor.index()))

    def test_opposing_edge_vertexes_match(self):
        """Confirm that the vertices of an edge are the same from both shapes
        that share the edge."""
        for neighborhood in self.shape_neighborhoods:
            for shape in neighborhood.shapes():
                s_index = shape.index()
                for n_index, neighbor in shape.neighbors():
                    if neighbor is None:
                        continue  # skip empty borders
                    # confirm self vertexes match neighbor vertexes
                    # don't use .edge(index) which may use the data from the
                    # same object for both .edge() calls
                    # use the internal specification data
                    s_edge_data = shape._edge_data[n_index]
                    n_edge_data = neighbor._edge_data[s_index]
                    self_vertexes = [s_edge_data['counter_vertex'],
                                     s_edge_data['clock_vertex']]
                    n_vertexes = [n_edge_data['counter_vertex'],
                                  n_edge_data['clock_vertex']]
                    # sort so we can use AlmostEqual
                    self_vertexes.sort()
                    n_vertexes.sort()
                    for self_vertex, n_vertex in zip(self_vertexes, n_vertexes):
                        #convert to complex so AlmostEqual assertion possible
                        self_vertex = complex(*self_vertex)
                        n_vertex = complex(*n_vertex)
                        ss_name = neighborhood.supershape_name()
                        self.assertAlmostEqual(self_vertex, n_vertex, msg=
                                               'For SuperShape {},'
                                               '\nshape {} @ index {}'
                                               '\nvertex: {}'
                                               '\ndoes not seem to match'
                                               '\nneighbor {} @ index {}'
                                               '\nvertex: {},'
                                               ''.format(ss_name,
                                                         shape.name(),
                                                         shape.index(),
                                                         self_vertex,
                                                         neighbor.name(),
                                                         n_index, n_vertex))

    def test_internally_stored_vertexes_are_in_order_around_perimeter(self):
        """Confirm that the vertices for a shape are reported clockwise."""
        for neighborhood in self.shape_neighborhoods:
            for shape in neighborhood.shapes():
                edge_count = len(tuple(shape.n_indexes()))
                for i, n_index in enumerate(shape.n_indexes()):
                    next_i = (i + 1) % edge_count
                    next_n_index = tuple(shape.n_indexes())[next_i]
                    edge_data = shape._edge_data[n_index]
                    next_data = shape._edge_data[next_n_index]
                    # confirm points are like this: a -- b/c -- d
                    a, b = (edge_data['counter_vertex'],
                            edge_data['clock_vertex'])
                    c, d = (next_data['counter_vertex'],
                            next_data['clock_vertex'])
                    # convert to imaginary numbers so assertion possible
                    a, b = complex(*a), complex(*b)
                    c, d = complex(*c), complex(*d)
                    # confirm a and d are different
                    self.assertNotAlmostEqual(a, d)
                    # confirm b and c are the same
                    self.assertAlmostEqual(b, c)

    def test_avg_area_is_correct(self):
        # only consider some existing super shapes and assume it otherwise works
        triangle_area = math.sin(math.pi / 3.0) / 2.0
        hexagon_area = 1.5 * 3**0.5
        name_and_avg_areas_spec = {'Square': 1.0,
                                   'Triangle': triangle_area,
                                   'Hexagon': hexagon_area}
        tested_count = 0
        for neighborhood in self.shape_neighborhoods:
            ss = neighborhood._supershape
            if ss.name() not in name_and_avg_areas_spec:
                continue
            self.assertAlmostEqual(ss.avg_area(),
                                   name_and_avg_areas_spec[ss.name()])
            tested_count += 1
        # confirm all the specified shapes were tested
        self.assertEqual(tested_count, len(name_and_avg_areas_spec))


#noinspection PyProtectedMember
class TestComponentShape(unittest.TestCase):
    def test_index_returns_same_index_provided_on_creation(self):
        index_spec = (10, 20)
        shape = generic_shape(index=index_spec)
        self.assertEqual(shape.index(), index_spec)

    def test_creation_takes_ownership_of_all_unowned_edges(self):
        shape = generic_shape()
        # confirm ownership of every edge for an independent shape
        owned_indexes = (n_index for n_index, edge in shape.edges())
        owned_indexes_spec = shape.n_indexes()
        _assertCountEqual(self, owned_indexes, owned_indexes_spec)

    def test_creation_does_not_take_ownership_of_claimed_edges(self):
        shape = generic_shape()
        # create a new neighbor which should only claim the new edges
        a_neighbor_index = tuple(shape.n_indexes())[0]  # any edge
        neighbor = shape._grid.create(a_neighbor_index)
        # confirm that the original shape still owns the shared edge
        self.assertIn(a_neighbor_index, shape._owned_edges)
        # confirm that the neighbor does not own the shared edge
        self.assertNotIn(shape.index(), neighbor._owned_edges)

    def test_grab_edges_does_not_include_edges_owned_by_self_or_neighbor(self):
        main_shape = generic_shape()
        # create a neighbor
        n_index = tuple(main_shape.n_indexes())[0]
        neighbor = main_shape._grid.create(n_index)
        # confirm that grab on either shape is empty
        for shape in (main_shape, neighbor):
            self.assertFalse(shape._grab_edges(shape._owned_edges))

    def test_give_away_edges_moves_ownership_of_edges_to_neighbors(self):
        index = (1, 1)
        original_owner = generic_shape(index=index)
        grid = original_owner.grid()
        n_index = tuple(original_owner.n_indexes())[0]
        neighbor = grid.create(n_index)
        # confirm ownership of the edge before giving it away
        self.assertIn(n_index, original_owner._owned_edges)
        self.assertNotIn(index, neighbor._owned_edges)
        # confirm ownership changes after giving away the edge
        original_owner._give_away_edges()
        self.assertNotIn(n_index, original_owner._owned_edges)
        self.assertIn(index, neighbor._owned_edges)

    def test_edge_returns_an_edge_for_each_neighbor_index(self):
        shape = generic_shape()
        for n_index in shape.n_indexes():
            self.assertIsNotNone(shape.edge(n_index))

    def test_neighbors_generates_the_index_and_neighbor_for_each_n_index(self):
        shape = generic_shape()
        # create neighbors on all edges
        indexed_neighbors_spec = list()
        for n_index in shape.n_indexes():
            neighbor = shape._grid.create(n_index)
            indexed_neighbors_spec.append((n_index, neighbor))
        # confirm that the correct index-neighbor combos are generated
        indexed_neighbors = list(shape.neighbors())
        _assertCountEqual(self, indexed_neighbors, indexed_neighbors_spec)

    def test_neighbors_generates_index_and_None_for_empty_neighbors(self):
        # make a shape with no neighbors
        shape = generic_shape()
        # confirm that each neighbor is generated as None
        for n_index, neighbor in shape.neighbors():
            self.assertIn(n_index, shape.n_indexes())
            self.assertIsNone(neighbor)


#noinspection PyProtectedMember
class TestEdge(unittest.TestCase):
    def test_endpoints_returns_endpoints(self):
        """Don't worry about the order if owner not indicated."""
        # make a shape and any neighbor
        index = (1, 2)
        shape = generic_shape(index=index)
        n_index = tuple(shape.n_indexes())[0]
        # get the shared edge and confirm the endpoints are correct
        edge = shape.edge(n_index)
        end_1_spec = shape._edge_data[n_index]['counter_vertex']
        end_2_spec = shape._edge_data[n_index]['clock_vertex']
        ends_spec = (end_1_spec, end_2_spec)
        ends = tuple(edge.endpoints())
        _assertCountEqual(self, ends, ends_spec)

    def test_endpoints_returns_endpoints_from_indicated_shape(self):
        """Each shape may/will have a different order for the same endpoints."""
        # make a shape and any neighbor
        main_index = (1, 2)
        main_shape = generic_shape(index=main_index)
        n_index = tuple(main_shape.n_indexes())[0]
        neighbor = main_shape._grid.create(n_index)
        # get the shared edge
        edge = main_shape.edge(n_index)
        for shape, other in ((main_shape, neighbor), (neighbor, main_shape)):
            # get the endpoints from the specified shape
            shape_end_1, shape_end_2 = edge.endpoints(shape.index())
            n_end_1, n_end_2 = edge.endpoints(other.index())
            # confirm the end points came from the indicated shape
            shape_end_1_spec = shape._edge_data[other.index()]['counter_vertex']
            shape_end_2_spec = shape._edge_data[other.index()]['clock_vertex']
            n_end_1_spec = other._edge_data[shape.index()]['counter_vertex']
            n_end_2_spec = other._edge_data[shape.index()]['clock_vertex']
            self.assertIs(shape_end_1, shape_end_1_spec)
            self.assertIs(shape_end_2, shape_end_2_spec)
            self.assertIs(n_end_1, n_end_1_spec)
            self.assertIs(n_end_2, n_end_2_spec)

    def test_endpoints_raises_valueerror_for_non_neighbor_index(self):
        # make a shape
        some_index = (1, 2)
        shape = generic_shape(index=some_index)
        # get a non neighboring index
        non_neighbor_index = (1000, 2000)
        self.assertNotIn(non_neighbor_index, shape.n_indexes())
        # confirm ValueError when non neighbor used to specify endpoint order
        _, any_edge = tuple(shape.edges())[0]
        self.assertRaises(ValueError,
                          any_edge.endpoints, *(non_neighbor_index,))


def generic_shape(supershape=None, index=None):
    # provide test defaults
    grid = pmz.PolyGrid(supershape=supershape)
    index = index or (1, 2)
    # get a shape
    shape = grid.create(index)
    return shape


def supershape_with_neighbors(ss):
    """Make a neighborhood of all component shapes + all border shapes."""
    grid = pmz.PolyGrid(supershape=ss)
    for comp_index, comp_data in ss.components().items():
        for n_index in comp_data['edges']:
            if grid.get(n_index) is None:
                grid.create(n_index)
    return grid


if __name__ == '__main__':
    unittest.main()
