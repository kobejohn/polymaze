import inspect
import math
import random
import sys


def supershapes_dict():
    """Return a dict of all supershapes in this module keyed by name."""
    current_module = sys.modules[__name__]
    supershapes = dict()
    for name, obj in inspect.getmembers(current_module):
        try:
            if issubclass(obj, _SuperShape) and (name[0] != '_'):
                supershapes[name] = obj()
        except TypeError:
            pass  # issubclass complains for non class obj
    return supershapes


class _SuperShape(object):
    """A factory for the shapes that make up a tessellation."""
    # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Implementation Requirements
    # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def _make_specification(self):
        """Return a dict that describes this supershape.

        dict format:
        {'name': _,
         'reference_length': _,
         'graph_offset_per_row': _,
         'graph_offset_per_col': _,
         'components':
             {c_index1: {'name': _,
                         'clockwise_edge_names': _,
                         'edges': {n_index1: {'name': _,
                                              'counter_vertex': _},
                                   n_index2: {...}}},
              c_index2: {...}}}
        """
        raise NotImplementedError

    def origin_index(self, index):
        """Return the equivalent index when the supershape is at the origin."""
        raise NotImplementedError

    # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # below here shouldn't need to be touched
    # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def __init__(self):
        # store the top level of specification as properties for easy access
        d = self._make_specification()
        # apply specs to the obj for obvious access.
        # additionally remove each spec from the dict to avoid duplication
        self._name = d.pop('name')
        self._reference_length = d.pop('reference_length')
        self._components = d.pop('components')
        self._graph_offset_per_row = d.pop('graph_offset_per_row')
        self._graph_offset_per_col = d.pop('graph_offset_per_col')

    def name(self):
        return self._name

    def reference_length(self):
        return self._reference_length

    def components(self):
        return self._components

    def graph_offset_per_row(self):
        return self._graph_offset_per_row

    def graph_offset_per_col(self):
        return self._graph_offset_per_col

    def create_component(self, grid, index):
        """Return a new shape for the given index."""
        return _ComponentShape(self, grid, index)

    def avg_edge_count(self):
        """Return the average number of edges per shape.

        Note: this is a simple average, not accounting for shared edges.
        """
        component_specs = self.components().values()
        component_count = len(component_specs)
        edge_count = 0
        for component_spec in component_specs:
            edge_count += len(component_spec['edges'])
        avg_edges = float(edge_count) / component_count
        return avg_edges

    def avg_area(self):
        """Return the combined average graph area per shape."""
        components_data = self.components().values()
        shape_count = len(components_data)
        total_area = 0.0
        for component in components_data:
            vertex_by_name = {data['name']: data['counter_vertex']
                              for data in component['edges'].values()}
            cntr_edge_names = component['clockwise_edge_names']
            cntr_vertexes = [vertex_by_name[name] for name in cntr_edge_names]
            for i in range(-1, len(cntr_vertexes)-1):  # take v's in pairs
                (y0, x0), (y1, x1) = cntr_vertexes[i], cntr_vertexes[i+1]
                total_area += 0.5 * (x1*y0 - y1*x0)
        return abs(float(total_area) / shape_count)


class _ComponentShape(object):
    """A component of a grid-supershape / tessellation."""
    def __init__(self, supershape, grid, index):
        self._ss = supershape
        self._grid = grid
        self._index = index
        self._name, self._edge_data, self._ordered_n_indexes =\
            self._calc_final_data(supershape, index)
        self._owned_edges = self._grab_edges(dict())
        self.viz_style = None

    @staticmethod
    def _calc_final_data(ss, index):
        """Return name, final edge data and sorted neighbors."""
        origin_index = ss.origin_index(index)
        # get all the specs that will be used
        component_spec = ss.components()[origin_index]
        edges_spec = component_spec['edges']
        edges_count = len(edges_spec)
        # make the shell of the final edge data and get the ordered indexes
        edges_data = dict()
        ordered_n_indexes = [None] * edges_count
        for origin_n_index, edge_spec in edges_spec.items():
            n_index_offset = _diff_tuples(origin_n_index, origin_index)
            n_index = sum_tuples((index, n_index_offset))
            # create the data dict for the edge shared with n_index neighbor
            edge_data = edges_data[n_index] = dict()
            # name is just name
            edge_data['name'] = edge_spec['name']
            # convert base vertex within the ss to full vertex at this index
            base_vertex = edge_spec['counter_vertex']
            anchor_row, anchor_col = _diff_tuples(index, origin_index)
            row_offset = _scale_tuple(ss.graph_offset_per_row(), anchor_row)
            col_offset = _scale_tuple(ss.graph_offset_per_col(), anchor_col)
            vertex = sum_tuples((base_vertex, row_offset, col_offset))
            edge_data['counter_vertex'] = vertex
            # put n_index into the order indicated by the specification
            i = component_spec['clockwise_edge_names'].index(edge_data['name'])
            ordered_n_indexes[i] = n_index
        # go back and fill in the additional vertex data for ease of access
        for primary_i, primary_n_index in enumerate(ordered_n_indexes):
            # get each pair of edges
            next_i = (primary_i + 1) % edges_count
            next_n_index = ordered_n_indexes[next_i]
            next_vertex = edges_data[next_n_index]['counter_vertex']
            edges_data[primary_n_index]['clock_vertex'] = next_vertex
        return component_spec['name'], edges_data, ordered_n_indexes

    def index(self):
        return self._index

    def grid(self):
        return self._grid

    def name(self):
        return self._name

    def n_indexes(self, randomize=False):
        """Generate all neighbor indexes.

        randomize: True: random order; False: sorted
        """
        if randomize:
            # get a random ordering of all n_indexes
            n_indexes = random.sample(self._ordered_n_indexes,
                                      len(self._ordered_n_indexes))
        else:
            # use the indexes in sorted order
            n_indexes = self._ordered_n_indexes
        for n_index in n_indexes:
            yield n_index

    def neighbors(self, randomize=False):
        """Generate each index-neighbor pair for this shape.

        randomize: True: random order; False: sorted
        generates: n_index, None for nonexistent neighbors.
        """
        for n_index in self.n_indexes(randomize=randomize):
            yield n_index, self._grid.get(n_index)

    def edges(self, randomize=False):
        """Generate each index-edge pair for this shape.

        randomize: True: random order; False: sorted
        """
        for n_index in self.n_indexes(randomize=randomize):
            yield n_index, self.edge(n_index)

    def edge(self, neighbor_index):
        """Return one edge of this shape by the index of the sharing neighbor.

        Note:
        When an edge is shared, both shapes will return the same edge.
        """
        # try to get from self
        try:
            return self._owned_edges[neighbor_index]
        except KeyError:
            pass
        # get from neighbor
        neighbor = self._grid.get(neighbor_index)
        if neighbor:
            # neighbor stores the shared edge under this shape's index
            return neighbor._owned_edges[self.index()]
        # if the code gets here, it's basically a runtime error

    def _grab_edges(self, currently_owned):
        """Return a dict of new edges for ONLY those that don't exist yet.

        return: {neighbor_index: edge, ...}
        """
        grabbed_edges = dict()
        for n_index, neighbor in self.neighbors():
            # ignore self owned edges
            if n_index in currently_owned:
                continue
            # ignore neighbor owned edges
            if neighbor:
                if self.index() in neighbor._owned_edges:
                    continue
            # create edges that didn't exist in self or neighbor
            grabbed_edges[n_index] = Edge(self._grid, self.index(), n_index)
        return grabbed_edges

    def _give_away_edges(self):
        """Give edges away to neighbors or keep them if no neighbor."""
        for n_index, edge in tuple(self._owned_edges.items()):
            neighbor = self._grid.get(n_index)
            if neighbor:
                # transfer the edge only when there is a neighbor
                neighbor._owned_edges[self.index()] = edge
                del self._owned_edges[n_index]


class Edge(object):
    def __init__(self, grid, neighbor_1_index, neighbor_2_index):
        self._grid = grid
        self._neighbor_1_index = neighbor_1_index
        self._neighbor_2_index = neighbor_2_index
        self.viz_style = None

    def endpoints(self, requesting_shape_index=None):
        """Return the xy, xy end points of this edge.

        kwargs: requesting_shape_index - if the clockwise order of vertices is
                    desired, provide this so the edge knows which way to sort
        """
        # default if the sorting doesn't matter
        other_side_lookup = {self._neighbor_1_index: self._neighbor_2_index,
                             self._neighbor_2_index: self._neighbor_1_index}
        if requesting_shape_index:
            # use only the provided index
            try:
                n_index = other_side_lookup[requesting_shape_index]
            except KeyError:
                raise ValueError('The requesting shape is not one of the'
                                 ' sharing neighbors of this edge.')
            requesting_shape = self._grid.get(requesting_shape_index)
        else:
            # use either index if not provided
            requesting_shape = self._grid.get(self._neighbor_1_index)
            if not requesting_shape:
                requesting_shape = self._grid.get(self._neighbor_2_index)
        n_index = other_side_lookup[requesting_shape.index()]
        v1, v2 = (requesting_shape._edge_data[n_index]['counter_vertex'],
                  requesting_shape._edge_data[n_index]['clock_vertex'])
        return v1, v2


def sum_tuples(sequence_of_tuples):
    # not efficient but works
    a_sum, b_sum = 0, 0  # will be converted to float if any floats added
    for a, b in sequence_of_tuples:
        a_sum += a
        b_sum += b
    return a_sum, b_sum


def _diff_tuples(positive, negative):
    (pa, pb), (na, nb) = positive, negative
    return pa-na, pb-nb


def _scale_tuple(t, scale):
    return scale * t[0], scale * t[1]


class Square(_SuperShape):
    """A simple square supershape."""
    @classmethod
    def _make_specification(cls):
        """Return a dict that describes this supershape."""
        side = 1.0
        c = {(0, 0): {'name': 'square',
                      'clockwise_edge_names': ('top', 'right',
                                               'bottom', 'left'),
                      'edges': {(-1, 0): {'name': 'top',
                                          'counter_vertex': (0.0, 0.0)},
                                (0, 1): {'name': 'right',
                                         'counter_vertex': (0.0, side)},
                                (1, 0): {'name': 'bottom',
                                         'counter_vertex': (side, side)},
                                (0, -1): {'name': 'left',
                                          'counter_vertex': (side, 0.0)}}}}
        d = {'name': 'Square',
             'reference_length': side,
             'graph_offset_per_row': (side, 0.0),
             'graph_offset_per_col': (0.0, side),
             'components': c}
        return d

    @classmethod
    def origin_index(cls, index):
        """Return the equivalent index when the supershape is at the origin."""
        return 0, 0


class Hexagon(_SuperShape):
    """A gridded hexagon."""
    @classmethod
    def _make_specification(cls):
        """Return a dict that describes this supershape."""
        side = 1.0
        h = side * math.sin(math.pi / 3.0)
        # vertex calculations
        # shared horizontal and vertical rails
        top_rail = 0.0
        vmid_rail = h
        bottom_rail = 2.0 * h
        left_rail = -1.5 * side
        midleft_rail = -1.0 * side
        midright_rail = 0.0
        right_rail = 0.5 * side
        # point coordinates
        left_pt = (vmid_rail, left_rail)
        topleft_pt = (top_rail, midleft_rail)
        topright_pt = (top_rail, midright_rail)
        right_pt = (vmid_rail, right_rail)
        bottomright_pt = (bottom_rail, midright_rail)
        bottomleft_pt = (bottom_rail, midleft_rail)
        # build components separately to avoid long lines
        c = {(0, 0): {'name': 'hexagon',
                      'clockwise_edge_names': ('top', 'top right',
                                               'bottom right', 'bottom',
                                               'bottom left', 'top left'),
                      'edges': {(-1, 0): {'name': 'top',
                                          'counter_vertex': topleft_pt},
                                (0, 1): {'name': 'top right',
                                         'counter_vertex': topright_pt},
                                (1, 1): {'name': 'bottom right',
                                         'counter_vertex': right_pt},
                                (1, 0): {'name': 'bottom',
                                         'counter_vertex': bottomright_pt},
                                (0, -1): {'name': 'bottom left',
                                          'counter_vertex': bottomleft_pt},
                                (-1, -1): {'name': 'top left',
                                           'counter_vertex': left_pt}}}}
        d = {'name': 'Hexagon',
             'reference_length': side,
             'graph_offset_per_row': (2.0 * h, 0.0),
             'graph_offset_per_col': (-1.0 * h, 1.5 * side),
             'components': c}
        return d

    @classmethod
    def origin_index(cls, index):
        """Return the equivalent index when the supershape is at the origin."""
        origin_row, origin_col = 0, 0  # there's only one shape so always origin
        return origin_row, origin_col


class Triangle(_SuperShape):
    """A horizontal arrangement of triangles pointing up / down."""
    @classmethod
    def _make_specification(cls):
        """Return a dict that describes this supershape."""
        side = 1.0
        h = side * math.sin(math.pi / 3.0)
        # vertex calculations
        # shared horizontal and vertical rails
        top_rail = 0.0
        bottom_rail = h
        left_rail = -0.5 * side
        midleft_rail = 0.0
        midright_rail = 0.5 * side
        right_rail = side
        # points
        left_pt = (bottom_rail, left_rail)
        topleft_pt = (top_rail, midleft_rail)
        bottomright_pt = (bottom_rail, midright_rail)
        topright_pt = (top_rail, right_rail)
        # build components separately to avoid long lines
        c = {(0, 0): {'name': 'up',
                      'clockwise_edge_names': ('left', 'right', 'bottom'),
                      'edges': {(0, -1): {'name': 'left',
                                          'counter_vertex': left_pt},
                                (0, 1): {'name': 'right',
                                         'counter_vertex': topleft_pt},
                                (1, -1): {'name': 'bottom',
                                          'counter_vertex': bottomright_pt}}},
             (0, 1): {'name': 'down',
                      'clockwise_edge_names': ('left', 'top', 'right'),
                      'edges': {(0, 0): {'name': 'left',
                                         'counter_vertex': bottomright_pt},
                                (-1, 2): {'name': 'top',
                                          'counter_vertex': topleft_pt},
                                (0, 2): {'name': 'right',
                                         'counter_vertex': topright_pt}}}}
        # make the data dict
        d = {'name': 'Triangle',
             'reference_length': side,
             'graph_offset_per_row': (h, 0.5 * side),
             'graph_offset_per_col': (0.0, 0.5 * side),
             'components': c}
        return d

    @classmethod
    def origin_index(cls, index):
        """Return the equivalent index when the supershape is at the origin."""
        row, col = index
        # there is up on the left of the supershape and down on the right
        origin_row = 0  # supershape is horizontally arranged only
        origin_col = col % 2
        return origin_row, origin_col


class OctaDiamond(_SuperShape):
    """Octagons and diamonds living together. Oh my!"""
    @classmethod
    def _make_specification(cls):
        """Return a dict that describes this supershape."""
        side = 1.0
        h = side / math.sqrt(2.0)
        # component shape data
        # vertex calculations
        # shared horizontal and vertical rails
        oct_left_rail = -1.0 * (side + h)
        oct_midleft_rail = -1.0 * side
        oct_midright_rail = 0.0
        oct_right_rail = h
        #dmd_left_rail = oct_midright_rail  # never used. here for reference
        dmd_h_mid_rail = oct_right_rail
        dmd_right_rail = 2.0 * h
        oct_top_rail = 0.0
        oct_midtop_rail = h
        oct_midbottom_rail = side + h
        oct_bottom_rail = side + 2.0 * h
        dmd_top_rail = -1.0 * h
        dmd_v_mid_rail = oct_top_rail
        #dmd_bottom_rail = oct_midtop_rail  # never used. here for reference
        # points
        # origin-based coordinates
        # use a clock analogy to build octagon points
        clk_1_pt = (oct_top_rail, oct_midright_rail)
        clk_2_pt = (oct_midtop_rail, oct_right_rail)
        clk_4_pt = (oct_midbottom_rail, oct_right_rail)
        clk_5_pt = (oct_bottom_rail, oct_midright_rail)
        clk_7_pt = (oct_bottom_rail, oct_midleft_rail)
        clk_8_pt = (oct_midbottom_rail, oct_left_rail)
        clk_10_pt = (oct_midtop_rail, oct_left_rail)
        clk_11_pt = (oct_top_rail, oct_midleft_rail)
        # use a diamong analogy for the rotated square
        dmd_left_pt = clk_1_pt
        dmd_top_pt = (dmd_top_rail, dmd_h_mid_rail)
        dmd_right_pt = (dmd_v_mid_rail, dmd_right_rail)
        dmd_bottom_pt = clk_2_pt
        # build components separately to avoid long lines
        c = {(0, 0): {'name': 'octagon',
                      'clockwise_edge_names': ('left', 'top left', 'top',
                                               'top right', 'right',
                                               'bottom right', 'bottom',
                                               'bottom left'),
                      'edges': {(0, -2): {'name': 'left',
                                          'counter_vertex': clk_8_pt},
                                (0, -1): {'name': 'top left',
                                          'counter_vertex': clk_10_pt},
                                (-1, 0): {'name': 'top',
                                          'counter_vertex': clk_11_pt},
                                (0, 1): {'name': 'top right',
                                         'counter_vertex': clk_1_pt},
                                (0, 2): {'name': 'right',
                                         'counter_vertex': clk_2_pt},
                                (1, 1): {'name': 'bottom right',
                                         'counter_vertex': clk_4_pt},
                                (1, 0): {'name': 'bottom',
                                         'counter_vertex': clk_5_pt},
                                (1, -1): {'name': 'bottom left',
                                          'counter_vertex': clk_7_pt}}},
             (0, 1): {'name': 'diamond',
                      'clockwise_edge_names': ('top left', 'top right',
                                               'bottom right', 'bottom left'),
                      'edges': {(-1, 0): {'name': 'top left',
                                          'counter_vertex': dmd_left_pt},
                                (-1, 2): {'name': 'top right',
                                          'counter_vertex': dmd_top_pt},
                                (0, 2): {'name': 'bottom right',
                                         'counter_vertex': dmd_right_pt},
                                (0, 0): {'name': 'bottom left',
                                         'counter_vertex': dmd_bottom_pt}}}}
        d = {'name': 'OctaDiamond',
             'reference_length': side,
             'graph_offset_per_row': (side + 2.0 * h, 0.0),
             'graph_offset_per_col': (0.0, 0.5 * (side + 2.0 * h)),
             'components': c}
        return d

    @classmethod
    def origin_index(cls, index):
        """Return the equivalent index when the supershape is at the origin."""
        row, col = index
        # Octadiamond is a simple horizontal 2 shapes so only need to check col
        origin_row = 0
        origin_col = col % 2
        return origin_row, origin_col


class Polycat(_SuperShape):
    """Multi-shape tessellation with tiling that look like a cat face."""
    @classmethod
    def _make_specification(cls):
        """Return a dict that describes this supershape."""
        side = 1.0
        h = side * math.sin(math.pi / 3.0)
        d_s_partial2 = side * (1.0 - math.tan(math.pi / 6.0))
        d_corner_h = d_s_partial2 * math.cos(math.pi / 6.0)
        d_corner_v = d_s_partial2 * math.sin(math.pi / 6.0)
        d_i_partialv = side / math.sin(math.pi / 3.0)
        # component shape data
        # vertex calculations
        # shared vertical rails
        l_dmd_left_rail = 0.0
        l_dmd_mid_rail = 0.5 * side
        m_dmd_left_rail = side
        m_dmd_mleft_rail = side + d_corner_h
        m_dmd_mid_rail = side + h
        m_dmd_mright_rail = side + 2.0 * h - d_corner_h
        m_dmd_right_rail = side + 2.0 * h
        r_dmd_mid_rail = 1.5 * side + 2.0 * h
        # shared horizontal rails
        v_mid_rail = 0.0
        l_dmd_top_rail = -1.0 * h
        l_dmd_bottom_rail = -1.0 * l_dmd_top_rail
        m_dmd_top_rail = -0.5 * side
        m_dmd_bottom_rail = -1.0 * m_dmd_top_rail
        ear_v_mid_rail = -1.0 * (d_i_partialv + d_corner_v)
        top_rail = -1.0 * (h + side)
        bottom_rail = -1.0 * ear_v_mid_rail
        # points
        l_dmd_left_pt = (v_mid_rail, l_dmd_left_rail)
        l_dmd_top_pt = (l_dmd_top_rail, l_dmd_mid_rail)
        l_dmd_bottom_pt = (l_dmd_bottom_rail, l_dmd_mid_rail)
        l_ear_right_pt = (ear_v_mid_rail, m_dmd_mleft_rail)
        l_ear_top_pt = (top_rail, l_dmd_mid_rail)
        r_ear_left_pt = (ear_v_mid_rail, m_dmd_mright_rail)
        r_ear_top_pt = (top_rail, r_dmd_mid_rail)
        m_dmd_left_pt = (v_mid_rail, m_dmd_left_rail)
        m_dmd_top_pt = (m_dmd_top_rail, m_dmd_mid_rail)
        m_dmd_right_pt = (v_mid_rail, m_dmd_right_rail)
        m_dmd_bottom_pt = (m_dmd_bottom_rail, m_dmd_mid_rail)
        chin_left_pt = (bottom_rail, m_dmd_mleft_rail)
        chin_right_pt = (bottom_rail, m_dmd_mright_rail)
        r_dmd_top_pt = (l_dmd_top_rail, r_dmd_mid_rail)
        r_dmd_bottom_pt = (l_dmd_bottom_rail, r_dmd_mid_rail)
        # build components separately to avoid long lines
        c = {(0, 0): {'name': 'left ear',
                      'clockwise_edge_names': ('left', 'right', 'bottom'),
                      'edges': {(0, -1): {'name': 'left',
                                          'counter_vertex': l_dmd_top_pt},
                                (-2, 1): {'name': 'right',
                                          'counter_vertex': l_ear_top_pt},
                                (1, 0): {'name': 'bottom',
                                         'counter_vertex': l_ear_right_pt}}},
             (0, 2): {'name': 'right ear',
                      'clockwise_edge_names': ('left', 'right', 'bottom'),
                      'edges': {(-1, 2): {'name': 'left',
                                          'counter_vertex': r_ear_left_pt},
                                (0, 3): {'name': 'right',
                                         'counter_vertex': r_ear_top_pt},
                                (1, 2): {'name': 'bottom',
                                         'counter_vertex': r_dmd_top_pt}}},
             (0, 1): {'name': 'forehead',
                      'clockwise_edge_names': ('left', 'top', 'right'),
                      'edges': {(1, 0): {'name': 'left',
                                         'counter_vertex': m_dmd_top_pt},
                                (-1, 1): {'name': 'top',
                                          'counter_vertex': l_ear_right_pt},
                                (1, 2): {'name': 'right',
                                         'counter_vertex': r_ear_left_pt}}},
             (1, 0): {'name': 'left eye',
                      'clockwise_edge_names': ('top left', 'top right',
                                               'bottom right', 'bottom left'),
                      'edges': {(0, 0): {'name': 'top left',
                                         'counter_vertex': l_dmd_top_pt},
                                (0, 1): {'name': 'top right',
                                         'counter_vertex': l_ear_right_pt},
                                (1, 1): {'name': 'bottom right',
                                         'counter_vertex': m_dmd_top_pt},
                                (2, 0): {'name': 'bottom left',
                                         'counter_vertex': m_dmd_left_pt}}},
             (1, 2): {'name': 'right eye',
                      'clockwise_edge_names': ('top left', 'top right',
                                               'bottom right', 'bottom left'),
                      'edges': {(0, 1): {'name': 'top left',
                                         'counter_vertex': m_dmd_top_pt},
                                (0, 2): {'name': 'top right',
                                         'counter_vertex': r_ear_left_pt},
                                (2, 3): {'name': 'bottom right',
                                         'counter_vertex': r_dmd_top_pt},
                                (2, 2): {'name': 'bottom left',
                                         'counter_vertex': m_dmd_right_pt}}},
             (2, 0): {'name': 'leftup whiskers',
                      'clockwise_edge_names': ('left', 'right', 'bottom'),
                      'edges': {(1, -1): {'name': 'left',
                                          'counter_vertex': l_dmd_left_pt},
                                (1, 0): {'name': 'right',
                                         'counter_vertex': l_dmd_top_pt},
                                (3, 0): {'name': 'bottom',
                                         'counter_vertex': m_dmd_left_pt}}},
             (3, 0): {'name': 'leftdown whiskers',
                      'clockwise_edge_names': ('left', 'top', 'right'),
                      'edges': {(3, -1): {'name': 'left',
                                          'counter_vertex': l_dmd_bottom_pt},
                                (2, 0): {'name': 'top',
                                         'counter_vertex': l_dmd_left_pt},
                                (2, 1): {'name': 'right',
                                         'counter_vertex': m_dmd_left_pt}}},
             (1, 1): {'name': 'left nose',
                      'clockwise_edge_names': ('bottom', 'top', 'right'),
                      'edges': {(2, 1): {'name': 'bottom',
                                         'counter_vertex': m_dmd_bottom_pt},
                                (1, 0): {'name': 'top',
                                         'counter_vertex': m_dmd_left_pt},
                                (2, 2): {'name': 'right',
                                         'counter_vertex': m_dmd_top_pt}}},
             (2, 2): {'name': 'right nose',
                      'clockwise_edge_names': ('left', 'top', 'bottom'),
                      'edges': {(1, 1): {'name': 'left',
                                         'counter_vertex': m_dmd_bottom_pt},
                                (1, 2): {'name': 'top',
                                         'counter_vertex': m_dmd_top_pt},
                                (3, 2): {'name': 'bottom',
                                         'counter_vertex': m_dmd_right_pt}}},
             (2, 1): {'name': 'left cheek',
                      'clockwise_edge_names': ('top left', 'top right',
                                               'bottom right', 'bottom left'),
                      'edges': {(3, 0): {'name': 'top left',
                                         'counter_vertex': l_dmd_bottom_pt},
                                (1, 1): {'name': 'top right',
                                         'counter_vertex': m_dmd_left_pt},
                                (3, 1): {'name': 'bottom right',
                                         'counter_vertex': m_dmd_bottom_pt},
                                (4, 0): {'name': 'bottom left',
                                         'counter_vertex': chin_left_pt}}},
             (3, 2): {'name': 'right cheek',
                      'clockwise_edge_names': ('top left', 'top right',
                                               'bottom right', 'bottom left'),
                      'edges': {(2, 2): {'name': 'top left',
                                         'counter_vertex': m_dmd_bottom_pt},
                                (3, 3): {'name': 'top right',
                                         'counter_vertex': m_dmd_right_pt},
                                (4, 2): {'name': 'bottom right',
                                         'counter_vertex': r_dmd_bottom_pt},
                                (3, 1): {'name': 'bottom left',
                                         'counter_vertex': chin_right_pt}}},
             (3, 1): {'name': 'chin',
                      'clockwise_edge_names': ('left', 'right', 'bottom'),
                      'edges': {(2, 1): {'name': 'left',
                                         'counter_vertex': chin_left_pt},
                                (3, 2): {'name': 'right',
                                         'counter_vertex': m_dmd_bottom_pt},
                                (4, 1): {'name': 'bottom',
                                         'counter_vertex': chin_right_pt}}}}
        # make the data dict
        d = {'name': 'Polycat',
             'reference_length': side,
             'graph_offset_per_row': (float(side + 2 * h) / 4, 0.0),
             'graph_offset_per_col': (0.0, float(side + 2.0 * h) / 3),
             'components': c}
        return d

    @classmethod
    def origin_index(cls, index):
        """Return the equivalent index when the supershape is at the origin."""
        row, col = index
        # Polycat is a 4-row, 3-column shape so both row and column are needed
        origin_row = row % 4
        origin_col = col % 3
        return origin_row, origin_col


class Qube(_SuperShape):
    """Watch your step."""
    @classmethod
    def _make_specification(cls):
        """Return a dict that describes this supershape."""
        side = 1.0
        w = 0.5 * side * 3**0.5  # width of the hex
        # component shape data
        # shared horizontal and vertical rails
        left_rail = -w
        h_mid_rail = 0.0
        right_rail = w
        top_rail = -side
        midtop_rail = -0.5 * side
        v_mid_rail = 0.0
        midbottom_rail = 0.5 * side
        bottom_rail = side
        # points
        top_pt = (top_rail, h_mid_rail)
        top_right_pt = (midtop_rail, right_rail)
        bottom_right_pt = (midbottom_rail, right_rail)
        bottom_pt = (bottom_rail, h_mid_rail)
        bottom_left_pt = (midbottom_rail, left_rail)
        top_left_pt = (midtop_rail, left_rail)
        center_pt = (v_mid_rail, h_mid_rail)
        # build components separately to avoid long lines
        c = {(0, 0): {'name': 'left',
                      'clockwise_edge_names': ('left', 'top',
                                               'right', 'bottom'),
                      'edges': {(0, -1): {'name': 'left',
                                          'counter_vertex': bottom_left_pt},
                                (-1, 1): {'name': 'top',
                                          'counter_vertex': top_left_pt},
                                (0, 2): {'name': 'right',
                                         'counter_vertex': top_pt},
                                (0, 1): {'name': 'bottom',
                                         'counter_vertex': center_pt}}},
             (0, 2): {'name': 'right',
                      'clockwise_edge_names': ('left', 'top',
                                               'right', 'bottom'),
                      'edges': {(0, 0): {'name': 'left',
                                         'counter_vertex': center_pt},
                                (-1, 4): {'name': 'top',
                                          'counter_vertex': top_pt},
                                (0, 3): {'name': 'right',
                                         'counter_vertex': top_right_pt},
                                (0, 1): {'name': 'bottom',
                                         'counter_vertex': bottom_right_pt}}},
             (0, 1): {'name': 'bottom',
                      'clockwise_edge_names': ('top_left', 'top_right',
                                               'bottom_right', 'bottom_left'),
                      'edges': {(0, 0): {'name': 'top_left',
                                         'counter_vertex': bottom_left_pt},
                                (0, 2): {'name': 'top_right',
                                         'counter_vertex': center_pt},
                                (1, 0): {'name': 'bottom_right',
                                         'counter_vertex': bottom_right_pt},
                                (1, -1): {'name': 'bottom_left',
                                          'counter_vertex': bottom_pt}}}}
        d = {'name': 'Qube',
             'reference_length': side,
             'graph_offset_per_row': (bottom_rail + midbottom_rail, right_rail),
             'graph_offset_per_col': (0, float(2 * right_rail) / 3),
             'components': c}
        return d

    @classmethod
    def origin_index(cls, index):
        """Return the equivalent index when the supershape is at the origin."""
        row, col = index
        # Qube supershape is only in one row so only need the column
        origin_row = 0
        origin_col = col % 3
        return origin_row, origin_col


class HexaFlower(_SuperShape):
    """Looks round on paper."""
    @classmethod
    def _make_specification(cls):
        """Return a dict that describes this supershape."""
        side = 1.0
        hex_w = 0.5 * side * 3**0.5  # width of the hex
        hex_v_cap = side * math.sin(math.pi / 6.0)
        s_partial_long = float(side) / math.tan(math.pi / 3.0)
        s_partial_short = side - s_partial_long
        dmd_h_offset = s_partial_short * math.cos(math.pi / 6.0)
        dmd_v_offset = s_partial_short * math.sin(math.pi / 6.0)
        dmd_v_partial = float(side) / math.cos(math.pi / 6.0)
        # component shape data
        # shared horizontal and vertical rails
        hex_top_rail = -hex_v_cap
        hex_midtop_rail = 0.0
        hex_midbottom_rail = side
        hex_bottom_rail = side + hex_v_cap
        dmd_outer_v_mid = -side * math.sin(math.pi / 3.0)
        top_rail = -dmd_v_partial - dmd_v_offset
        hex_left_rail = 0.0
        hex_h_mid_rail = hex_w
        hex_right_rail = 2 * hex_w
        left_rail = -side
        dmd_left_rail = -side * math.cos(math.pi / 3.0)
        dmd_right_rail = hex_right_rail + side * math.cos(math.pi / 3.0)
        # points
        hex_bottom_pt = (hex_bottom_rail, hex_h_mid_rail)
        hex_btm_left_pt = (hex_midbottom_rail, hex_left_rail)
        hex_top_left_pt = (hex_midtop_rail, hex_left_rail)
        hex_top_pt = (hex_top_rail, hex_h_mid_rail)
        hex_top_right_pt = (hex_midtop_rail, hex_right_rail)
        hex_btm_right_pt = (hex_midbottom_rail, hex_right_rail)
        sqr_btm_left_pt = (hex_midbottom_rail, left_rail)
        sqr_top_left_pt = (hex_midtop_rail, left_rail)
        ldmd_left_pt = (dmd_outer_v_mid, dmd_left_rail)
        ldmd_top_pt = (top_rail, hex_left_rail + dmd_h_offset)
        rdmd_top_pt = (top_rail, hex_right_rail - dmd_h_offset)
        rdmd_right_pt = (dmd_outer_v_mid, dmd_right_rail)
        # build components separately to avoid long lines
        c = {(0, 0): {'name': 'left_triangle',
                      'clockwise_edge_names': ('left', 'right', 'bottom'),
                      'edges': {(1, -1): {'name': 'left',
                                          'counter_vertex': sqr_top_left_pt},
                                (0, 1): {'name': 'right',
                                         'counter_vertex': ldmd_left_pt},
                                (1, 0): {'name': 'bottom',
                                         'counter_vertex': hex_top_left_pt}}},
             (0, 1): {'name': 'left_diamond',
                      'clockwise_edge_names': ('top_left', 'top_right',
                                               'bottom_right', 'bottom_left'),
                      'edges': {(-1, 1): {'name': 'top_left',
                                          'counter_vertex': ldmd_left_pt},
                                (0, 2): {'name': 'top_right',
                                         'counter_vertex': ldmd_top_pt},
                                (1, 1): {'name': 'bottom_right',
                                         'counter_vertex': hex_top_pt},
                                (0, 0): {'name': 'bottom_left',
                                         'counter_vertex': hex_top_left_pt}}},
             (0, 2): {'name': 'top_triangle',
                      'clockwise_edge_names': ('left', 'top', 'right'),
                      'edges': {(0, 1): {'name': 'left',
                                         'counter_vertex': hex_top_pt},
                                (-1, 3): {'name': 'top',
                                          'counter_vertex': ldmd_top_pt},
                                (1, 2): {'name': 'right',
                                         'counter_vertex': rdmd_top_pt}}},
             (1, 0): {'name': 'square',
                      'clockwise_edge_names': ('left', 'top',
                                               'right', 'bottom'),
                      'edges': {(1, -2): {'name': 'left',
                                          'counter_vertex': sqr_btm_left_pt},
                                (0, 0): {'name': 'top',
                                         'counter_vertex': sqr_top_left_pt},
                                (1, 1): {'name': 'right',
                                         'counter_vertex': hex_top_left_pt},
                                (2, -1): {'name': 'bottom',
                                          'counter_vertex': hex_btm_left_pt}}},
             (1, 1): {'name': 'hexagon',
                      'clockwise_edge_names': ('left',
                                               'top_left', 'top_right',
                                               'right',
                                               'bottom_right', 'bottom_left'),
                      'edges': {(1, 0): {'name': 'left',
                                         'counter_vertex': hex_btm_left_pt},
                                (0, 1): {'name': 'top_left',
                                         'counter_vertex': hex_top_left_pt},
                                (1, 2): {'name': 'top_right',
                                         'counter_vertex': hex_top_pt},
                                (1, 3): {'name': 'right',
                                         'counter_vertex': hex_top_right_pt},
                                (2, 1): {'name': 'bottom_right',
                                         'counter_vertex': hex_btm_right_pt},
                                (3, -1): {'name': 'bottom_left',
                                          'counter_vertex': hex_bottom_pt}}},
             (1, 2): {'name': 'right_diamond',
                      'clockwise_edge_names': ('top_left', 'top_right',
                                               'bottom_right', 'bottom_left'),
                      'edges': {(0, 2): {'name': 'top_left',
                                         'counter_vertex': hex_top_pt},
                                (-1, 4): {'name': 'top_right',
                                          'counter_vertex': rdmd_top_pt},
                                (0, 3): {'name': 'bottom_right',
                                         'counter_vertex': rdmd_right_pt},
                                (1, 1): {'name': 'bottom_left',
                                         'counter_vertex': hex_top_right_pt}}}}
        d = {'name': 'HexaFlower',
             'reference_length': side,
             'graph_offset_per_row': (float(hex_bottom_rail +
                                            abs(dmd_outer_v_mid)) / 2,
                                      float(2 * hex_w - dmd_h_offset) / 2),
             'graph_offset_per_col': (0.0, float(2 * hex_w + side) / 3),
             'components': c}
        return d

    @classmethod
    def origin_index(cls, index):
        """Return the equivalent index when the supershape is at the origin."""
        row, col = index
        # Hexaflower is 2 rows, 3 cols
        origin_row = row % 2
        origin_col = col % 3
        return origin_row, origin_col


if __name__ == '__main__':
    pass
