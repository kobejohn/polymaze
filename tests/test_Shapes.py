import unittest

from shapemaze import shapes, shapegrid

supershapes_dict = shapes.supershapes_dict()


#noinspection PyProtectedMember
class TestIndexedShapeImplementations(unittest.TestCase):
    """Run all implemented shapes through standard verification tests."""
    def setUp(self):
        self.shape_neighborhoods = [generic_supershape_neighborhood(ss)
                                    for ss_name, ss in supershapes_dict.items()]

    def test_neighbors_have_each_others_indexes(self):
        for neighborhood in self.shape_neighborhoods:
            for shape in neighborhood.shapes():
                self_index = shape.index()
                for n_index, neighbor in shape.neighbors():
                    if neighbor is None:
                        continue  # skip empty borders
                    # confirm neighbor has self in its indexes
                    self.assertIn(self_index, neighbor._edge_data,
                                  'Shape {} @ {}'
                                  '\nidentified {} @ {}'
                                  '\nas a neighbor but neighbor did not'
                                  ' identify shape as one.'
                                  ''.format(shape, shape.index(),
                                            neighbor, neighbor.index()))

    def test_opposing_edge_vertexes_match(self):
        for neighborhood in self.shape_neighborhoods:
            for shape in neighborhood.shapes():
                s_index = shape.index()
                for n_index, neighbor in shape.neighbors():
                    if neighbor is None:
                        continue  # skip empty borders
                    # confirm self vertexes match neighbor vertexes
                    # don't use .edge(index) which may use the data from the
                    # same object for both .edge() calls
                    self_vertexes = [shape._edge_data[n_index]['this vertex'],
                                     shape._edge_data[n_index]['next vertex']]
                    n_vertexes = [neighbor._edge_data[s_index]['this vertex'],
                                  neighbor._edge_data[s_index]['next vertex']]
                    # sort so we can use AlmostEqual
                    self_vertexes.sort()
                    n_vertexes.sort()
                    for self_vertex, n_vertex in zip(self_vertexes, n_vertexes):
                        #convert to complex so AlmostEqual assertion possible
                        self_vertex = complex(*self_vertex)
                        n_vertex = complex(*n_vertex)
                        self.assertAlmostEqual(self_vertex, n_vertex, msg=
                                               'Shape {} @ index {}'
                                               '\nvertex: {}'
                                               '\ndoes not seem to match'
                                               '\nneighbor {} @ index {}'
                                               '\nvertex: {},'
                                               ''.format(shape, shape.index(),
                                                         self_vertex,
                                                         neighbor, n_index,
                                                         n_vertex))

    def test_internally_stored_vertexes_are_in_order_around_perimeter(self):
        for neighborhood in self.shape_neighborhoods:
            for shape in neighborhood.shapes():
                edge_count = len(shape._ordered_n_indexes)
                for i, n_index in enumerate(shape._ordered_n_indexes):
                    next_i = (i + 1) % edge_count
                    next_n_index = shape._ordered_n_indexes[next_i]
                    edge_data = shape._edge_data[n_index]
                    next_data = shape._edge_data[next_n_index]
                    # confirm points are like this: a -- b/c -- d
                    a, b = edge_data['this vertex'], edge_data['next vertex']
                    c, d = next_data['this vertex'], next_data['next vertex']
                    # convert to imaginary numbers so assertion possible
                    a, b = complex(*a), complex(*b)
                    c, d = complex(*c), complex(*d)
                    # confirm a and d are different
                    self.assertNotAlmostEqual(a, d)
                    # confirm b and c are the same
                    self.assertAlmostEqual(b, c)


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
        owned_indexes_spec = shape._ordered_n_indexes
        self.assertItemsEqual(owned_indexes, owned_indexes_spec)

    def test_creation_does_not_take_ownership_of_claimed_edges(self):
        shape = generic_shape()
        # create a new neighbor which should only claim the new edges
        a_neighbor_index = shape._ordered_n_indexes[0]  # any edge
        neighbor = shape._grid.create(a_neighbor_index)
        # confirm that the original shape still owns the shared edge
        self.assertIn(a_neighbor_index, shape._owned_edges)
        # confirm that the neighbor does not own the shared edge
        self.assertNotIn(shape.index(), neighbor._owned_edges)

    def test_grab_edges_does_not_include_edges_owned_by_self_or_neighbor(self):
        main_shape = generic_shape()
        # create a neighbor
        n_index = main_shape._ordered_n_indexes[0]
        neighbor = main_shape._grid.create(n_index)
        # confirm that grab on either shape is empty
        for shape in (main_shape, neighbor):
            self.assertFalse(shape._grab_edges())

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
        for n_index in shape._ordered_n_indexes:
            self.assertIsNotNone(shape.edge(n_index))

    def test_neighbors_generates_the_index_and_neighbor_for_each_n_index(self):
        shape = generic_shape()
        # create neighbors on all edges
        indexed_neighbors_spec = list()
        for n_index in shape._ordered_n_indexes:
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
            self.assertIn(n_index, shape._ordered_n_indexes)
            self.assertIsNone(neighbor)


#noinspection PyProtectedMember
class TestEdge(unittest.TestCase):
    def test_endpoints_returns_endpoints_from_indicated_shape(self):
        """Each shape may/will have a different order for the same endpoints."""
        # make a shape and any neighbor
        main_index = (1, 2)
        main_shape = generic_shape(index=main_index)
        n_index = main_shape._ordered_n_indexes[0]
        neighbor = main_shape._grid.create(n_index)
        # get the shared edge
        edge = main_shape.edge(n_index)
        for shape, other in ((main_shape, neighbor), (neighbor, main_shape)):
            # get the endpoints from the specified shape
            shape_end_1, shape_end_2 = edge.endpoints(shape.index())
            n_end_1, n_end_2 = edge.endpoints(other.index())
            # confirm the end points came from the indicated shape
            shape_end_1_spec = shape._edge_data[other.index()]['this vertex']
            shape_end_2_spec = shape._edge_data[other.index()]['next vertex']
            n_end_1_spec = other._edge_data[shape.index()]['this vertex']
            n_end_2_spec = other._edge_data[shape.index()]['next vertex']
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
        self.assertNotIn(non_neighbor_index, shape._ordered_n_indexes)
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


def generic_supershape_neighborhood(creator):
    """Make a neighborhood big enough to include any super shape. Lazy."""
    grid = shapegrid.ShapeGrid(creator)
    enough_rows = 10
    enough_cols = 10
    for row in range(enough_rows):
        for col in range(enough_cols):
            grid.create((row, col))
    return grid


if __name__ == '__main__':
    unittest.main()
