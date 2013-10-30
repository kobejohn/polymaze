import unittest
import math
import os

import polymaze


class Testmain(unittest.TestCase):
    def test_creates_demo_image(self):
        image_name = 'polymaze demo.png'
        cwd = os.getcwd()
        image_path_spec = os.path.join(cwd, image_name)
        # remove the image first if it exists
        try:
            os.remove(image_path_spec)
        except Exception:
            pass
        # run main and check for demo
        polymaze.main()
        self.assertTrue(os.path.exists(image_path_spec))
        # remove the image when done
        try:
            os.remove(image_path_spec)
        except Exception:
            pass

#noinspection PyProtectedMember
class TestPolyMaze(unittest.TestCase):
    def test_entrance_and_exit_are_available_after_creation(self):
        maze = generic_polymaze()
        self.assertTrue(hasattr(maze, 'entrance_space'))
        self.assertTrue(hasattr(maze, 'exit_space'))

    def test_mazify_map_returns_two_spaces(self):
        maze = generic_polymaze()
        returned_spaces = maze._mazify_map(maze._map)
        self.assertEqual(len(returned_spaces), 2)

    #todo: to really test this, need to create a tree and verify no cycles

    def test_is_pathable_returns_true_if_edges_are_walls_except_previous(self):
        maze = generic_polymaze()
        # replace the map with a simple neighborhood map
        center, spec_data = triangle_with_neighbors_with_spec_data()
        left = spec_data['left neighbor']
        bottom = spec_data['bottom neighbor']
        neighborhood_map = center.map()
        maze._map = neighborhood_map
        # set wall status on all edges
        for edge in maze._map.all_edges():
            setattr(edge, 'status', maze.WALL)
        # confirm that all neighbor directions are pathable
        self.assertTrue(maze._is_pathable(left, center))
        self.assertTrue(maze._is_pathable(bottom, center))
        self.assertTrue(maze._is_pathable(center, bottom))
        self.assertTrue(maze._is_pathable(center, left))
        # break a path from one side to the other of the neighborhood
        LEFT, RIGHT, MIDDLE = center.LEFT, center.RIGHT, center.MIDDLE
        left.edge(LEFT).status = maze.PATH
        left.edge(RIGHT).status = maze.PATH
        center.edge(MIDDLE).status = maze.PATH
        bottom.edge(RIGHT).status = maze.PATH
        # confirm that none of the spaces are pathable
        self.assertFalse(maze._is_pathable(left, center))
        self.assertFalse(maze._is_pathable(bottom, center))
        self.assertFalse(maze._is_pathable(center, bottom))
        self.assertFalse(maze._is_pathable(center, left))

    def test_image_returns_image_with_same_rect_ratio_as_map_space(self):
        maze = generic_polymaze()
        # find min/max indexes of the maze's map
        rows, cols = zip(*maze._map._map)
        row_min, row_max = min(rows), max(rows)
        col_min, col_max = min(cols), max(cols)
        # convert the min/max indexes to side units
        sides_per_row, sides_per_col = maze._map._polygon_class.SIDES_PER_INDEX
        vert_size = sides_per_row * (row_max - row_min + 1)
        horz_size = sides_per_col * (col_max - col_min + 1)
        ratio_spec = float(vert_size) / horz_size
        # get the image and size
        some_width_limit, some_height_limit = 200, 100
        image = maze.image(some_height_limit, some_width_limit)
        image_width, image_height = image.size
        ratio = float(image_height) / image_width
        # confirm the image size and specified size match
        self.assertAlmostEqual(ratio, ratio_spec, places=1)


#noinspection PyProtectedMember
class TestPolygonMap(unittest.TestCase):
    def setUp(self):
        self.polygon_class = polymaze.IndexedTriangle
        self.map = polymaze.PolygonMap(self.polygon_class)

    def test_create_polygon_creates_based_on_the_class_stored_at_creation(self):
        # make a polygon
        some_index = (1, 2)
        polygon = self.map.create_polygon(some_index)
        # confirm that the provided class is stored in the class
        self.assertIsInstance(polygon, self.polygon_class)

    def test_get_polygon_returns_polygon_created_with_same_index(self):
        some_index = (1, 2)
        polygon_spec = self.map.create_polygon(some_index)
        polygon = self.map.get_polygon(some_index)
        self.assertIs(polygon, polygon_spec)

    def test_get_polygon_returns_None_for_nonexistent_indexes(self):
        unused_index = (1, 2)
        self.assertIsNone(self.map.get_polygon(unused_index))

    def test_all_indexes_generates_each_index_exactly_once(self):
        all_indexes_spec = ((1, 2), (3, 4))
        for index in all_indexes_spec:
            self.map.create_polygon(index)
        all_indexes = tuple(self.map.all_indexes())
        self.assertItemsEqual(all_indexes, all_indexes_spec)

    def test_all_edges_generates_each_edge_exactly_once(self):
        # get a neighborhood of triangles
        triangle, spec_data = triangle_with_neighbors_with_spec_data()
        edges = tuple(triangle.map().all_edges())
        edges_spec = spec_data['all map edges']
        self.assertItemsEqual(edges, edges_spec)

    def test_border_polygons_generates_all_polys_with_any_empty_neighbors(self):
        triangle, spec_data = triangle_with_neighbors_with_spec_data()
        # add another triangle to enclose the main triangle
        right_side_index = triangle._neighbor_index_by_edge(triangle.RIGHT)
        closing_triangle = triangle.map().create_polygon(right_side_index)
        # confirm that only the three outside triangles are in the border list
        border_spec = (closing_triangle,
                       spec_data['left neighbor'], spec_data['bottom neighbor'])
        border = tuple(triangle.map().border_polygons())
        self.assertItemsEqual(border, border_spec)


#noinspection PyProtectedMember
class TestIndexedPolygonBase(unittest.TestCase):
    def test_implementation_methods_raise_NotImplementedError(self):
        pbase = generic_indexedpolygonbase()
        DUMMY_NAME = 'edge name'
        self.assertRaises(NotImplementedError,
                          pbase._neighbor_index_by_edge,
                          (DUMMY_NAME,))
        self.assertRaises(NotImplementedError,
                          pbase._shared_edge_lookup,
                          (DUMMY_NAME,))
        self.assertRaises(NotImplementedError,
                          pbase._edge_end_points,
                          (DUMMY_NAME,))

    def test_implementation_constants_are_empty_sequences(self):
        empty_sequence = tuple()
        pbase = generic_indexedpolygonbase()
        self.assertItemsEqual(pbase.EDGE_NAMES, empty_sequence)
        self.assertItemsEqual(pbase.SIDES_PER_INDEX, empty_sequence)

    def test_index_returns_same_index_set_on_creation(self):
        index_spec = (10, 20)
        #noinspection PyTypeChecker
        pbase = generic_indexedpolygonbase(index=index_spec)
        self.assertEqual(pbase.index(), index_spec)

    def test_map_returns_same_map_set_on_creation(self):
        some_index = (1, 2)
        original_map = polymaze.PolygonMap(polymaze.IndexedTriangle)
        triangle = polymaze.IndexedTriangle(original_map, some_index)
        self.assertIs(triangle.map(), original_map)

    def test_creation_takes_ownership_of_all_unowned_edges(self):
        triangle, _ = triangle_row1_col2_with_specification_data()
        LEFT, RIGHT, MIDDLE = triangle.LEFT, triangle.RIGHT, triangle.MIDDLE
        # confirm ownership on original triangle
        original_owned_edges_spec = (LEFT, RIGHT, MIDDLE)
        self.assertItemsEqual(triangle._owned_edges.keys(),
                              original_owned_edges_spec)

    def test_creation_does_not_take_ownership_of_claimed_edges(self):
        triangle, _ = triangle_row1_col2_with_specification_data()
        LEFT, MIDDLE = triangle.LEFT, triangle.MIDDLE
        # create a neighbor on left edge
        index = triangle.index()
        left_index = (index[0], index[1] - 1)
        neighbor = triangle.map().create_polygon(left_index)
        # confirm that the neighbor only owns its left and middle edges
        new_owned_edges_spec = (LEFT, MIDDLE)
        self.assertItemsEqual(neighbor._owned_edges.keys(),
                              new_owned_edges_spec)

    def test_edges_and_neighbors_produces_correct_edge_neighbor_pairs(self):
        triangle, spec_data = triangle_with_neighbors_with_spec_data()
        edge_neighbor_pairs = list(triangle.edges_and_neighbors())
        # right edge not produced. only left and bottom. no neighbor on right
        edge_neighbor_pairs_spec = [(spec_data['left edge'],
                                     spec_data['left neighbor']),
                                    (spec_data['bottom edge'],
                                     spec_data['bottom neighbor']),
                                    (spec_data['right edge'],
                                     None)]
        self.assertItemsEqual(edge_neighbor_pairs, edge_neighbor_pairs_spec)

    def test_edge_returns_an_edge_for_each_edgename(self):
        triangle, _ = triangle_row1_col2_with_specification_data()
        for edge_name in triangle.EDGE_NAMES:
            edge = triangle.edge(edge_name)
            self.assertTrue(isinstance(edge, polymaze.Edge))

    def test_neighbor_returns_each_neighbor_and_shared_name(self):
        triangle, spec_data = triangle_with_neighbors_with_spec_data()
        # only get neighbors that exist on left and bottom
        neighbor_shared_name = [triangle.neighbor(triangle.LEFT),
                                triangle.neighbor(triangle.MIDDLE)]
        # confirm the neighbors on the left and bottom are correct
        neighbor_shared_name_spec = [(spec_data['left neighbor'],
                                      triangle.RIGHT),
                                     (spec_data['bottom neighbor'],
                                      triangle.MIDDLE)]
        self.assertItemsEqual(neighbor_shared_name, neighbor_shared_name_spec)

    def test_neighbor_returns_None_and_shared_name_for_empty_neighbor(self):
        triangle, spec_data = triangle_with_neighbors_with_spec_data()
        empty_neighbor = triangle.neighbor(triangle.RIGHT)
        # neighbor should be empty (None)
        # neighbor's perspective of RIGHT side is LEFT
        # ==> (None, LEFT)
        empty_neighbor_spec = (None, triangle.LEFT)
        self.assertEqual(empty_neighbor, empty_neighbor_spec)


#todo: need to DRY the polynomial design so it works for any regular grid
#noinspection PyProtectedMember
class TestIndexedTriangle(unittest.TestCase):
    def test_has_edges_left_right_middle(self):
        triangle, _ = triangle_row1_col2_with_specification_data()
        left_right_middle = ('left', 'right', 'middle')
        self.assertItemsEqual(triangle.EDGE_NAMES, left_right_middle)

    def test_neighbor_index_by_edge_returns_each_neighbor_correctly(self):
        triangle, spec_data = triangle_with_neighbors_with_spec_data()
        # confirm neighbors are correct
        left_neighbor_spec = spec_data['left neighbor']
        bottom_neighbor_spec = spec_data['bottom neighbor']
        right_neighbor_index = (triangle.index()[0], triangle.index()[1] + 1)
        self.assertEqual(triangle._neighbor_index_by_edge(triangle.LEFT),
                         left_neighbor_spec.index())
        self.assertEqual(triangle._neighbor_index_by_edge(triangle.MIDDLE),
                         bottom_neighbor_spec.index())
        self.assertEqual(triangle._neighbor_index_by_edge(triangle.RIGHT),
                         right_neighbor_index)

    def test_shared_edge_lookup_returns_neighbors_name_for_shared_edge(self):
        triangle, _ = triangle_row1_col2_with_specification_data()
        # left edge: neighbor calls it right
        self.assertEqual(triangle._shared_edge_lookup(triangle.LEFT),
                         triangle.RIGHT)
        # right edge: neighbor calls it left
        self.assertEqual(triangle._shared_edge_lookup(triangle.RIGHT),
                         triangle.LEFT)
        # middle edge: neighbor calls it middle
        self.assertEqual(triangle._shared_edge_lookup(triangle.MIDDLE),
                         triangle.MIDDLE)

    def test_edge_end_points_returns_same_points_as_hand_calculation(self):
        triangle, spec_data = triangle_row1_col2_with_specification_data()
        # get the actual points
        left_edge_points = triangle._edge_end_points(triangle.LEFT)
        middle_edge_points = triangle._edge_end_points(triangle.MIDDLE)
        right_edge_points = triangle._edge_end_points(triangle.RIGHT)
        # confirm they are as expected
        self.assertItemsEqual(spec_data['left edge points'],
                              left_edge_points)
        self.assertItemsEqual(spec_data['middle edge points'],
                              middle_edge_points)
        self.assertItemsEqual(spec_data['right edge points'],
                              right_edge_points)


class TestEdge(unittest.TestCase):
    def test_points_returns_same_points_as_hand_calculation(self):
        triangle, spec_data = triangle_row1_col2_with_specification_data()
        # get the actual points
        left_edge_points = polymaze.Edge(triangle, triangle.LEFT).points()
        middle_edge_points = polymaze.Edge(triangle, triangle.MIDDLE).points()
        right_edge_points = polymaze.Edge(triangle, triangle.RIGHT).points()
        # confirm they are as expected
        self.assertItemsEqual(spec_data['left edge points'],
                              left_edge_points)
        self.assertItemsEqual(spec_data['middle edge points'],
                              middle_edge_points)
        self.assertItemsEqual(spec_data['right edge points'],
                              right_edge_points)


UNSPECIFIED = '<<unspecified>>'


def generic_polymaze():
    return polymaze.PolyMaze()


def generic_indexedpolygonbase(index=UNSPECIFIED):
    if index == UNSPECIFIED:
        index = (1, 2)
    p = polymaze.IndexedPolygonBase(UNSPECIFIED, index)
    return p


def triangle_with_neighbors_with_spec_data():
    # base parts
    left_index, right_index, bottom_index = (0, 1), (0, 2), (1, 2)
    _map = polymaze.PolygonMap(polymaze.IndexedTriangle)
    # create the neighborhood
    left = _map.create_polygon(left_index)
    main = _map.create_polygon(right_index)
    bottom = _map.create_polygon(bottom_index)
    # get the edges of the main triangle
    LEFT, RIGHT, MIDDLE = main.LEFT, main.RIGHT, main.MIDDLE
    left_edge = main.edge(LEFT)
    right_edge = main.edge(RIGHT)
    bottom_edge = main.edge(MIDDLE)
    # get the remaining edges
    all_edges = (left_edge, right_edge, bottom_edge,
                 left.edge(LEFT), left.edge(MIDDLE),
                 bottom.edge(LEFT), bottom.edge(RIGHT))
    spec_data = {'left neighbor': left,
                 'left edge': left_edge,
                 'bottom neighbor': bottom,
                 'bottom edge': bottom_edge,
                 'right neighbor': None,
                 'right edge': right_edge,
                 'all map edges': all_edges}
    return main, spec_data


def triangle_row1_col2_with_specification_data():
    index = (1, 2)
    # base assumptions
    row_height = math.sin(math.pi / 3)
    col_width = 1.0
    # point coordinates
    left_point = (row_height, col_width)
    middle_point = (2 * row_height, 1.5 * col_width)
    right_point = (row_height, 2 * col_width)
    # edge points
    left_edge_points = (left_point, middle_point)
    middle_edge_points = (left_point, right_point)
    right_edge_points = (middle_point, right_point)
    spec_data = {'index': index,
                 'left point': left_point,
                 'middle point': middle_point,
                 'right point': right_point,
                 'left edge points': left_edge_points,
                 'middle edge points': middle_edge_points,
                 'right edge points': right_edge_points}
    # also return the real thing to be used in tests
    _map = polymaze.PolygonMap(polymaze.IndexedTriangle)
    triangle = _map.create_polygon(index)
    return triangle, spec_data
