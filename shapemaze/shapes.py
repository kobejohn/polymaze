import math


def supershapes():
    """Generate all supershape classes in this module with their names."""
    for name, obj in globals().items():
        ss_suffix = '_supershape'
        ss_suffix_start = -1 * len(ss_suffix)
        # only pass something that meets the suffix requirement and is callable
        if (name[ss_suffix_start:] == ss_suffix) and callable(obj):
            ss_name = name[:ss_suffix_start]
            yield ss_name, obj


def Square_supershape(grid, index):
    return Square(grid, index)


def Hexagon_supershape(grid, index):
    row, col = index
    odd_col = col % 2
    if odd_col:
        return _Hexagon_UpRight(grid, index)
    else:
        return _Hexagon_DownLeft(grid, index)


def UpDownTriangle_supershape(grid, index):
    """Provides up or down triangle class."""
    odd = sum(index) % 2
    if odd:
        return _UpDownTriangle_Down(grid, index)
    else:
        return _UpDownTriangle_Up(grid, index)


class IndexedShapeBase(object):
    """A shape that fits by index into a grid of other shapes."""
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #          #          #          #          #          #          #
    # Begin supershape implementation requirements
    # standard scale to be used throughout all component shapes
    # just 1.0 will serve for probably all cases
    SIDE = None
    # multiplier describing how the supershape position changes per index
    SS_VERTEX_OFFSET_PER_ROW = None  # (y_offset_per_row, x_offset_per_row)
    SS_VERTEX_OFFSET_PER_COL = None  # (y_offset_per_col, x_offset_per_col)
    # End supershape implementation requirements
    #          #          #          #          #          #          #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #          #          #          #          #          #          #
    # Begin component implementation requirements
    # explain the index position of this component within the supershape
    INDEX_OFFSET_TO_SS_ANCHOR_SHAPE = None  # (row_offset, col_offset)
    # base data used to define a component at a specific index
    # {index_offset_to_neighbor: {'name': user_friendly_name,
    #                             'vertex in ss': vertex_from_origin_ss}
    _BASE_EDGE_DATA = None
    # for drawing polygons, the edge order is important, this should be a
    # sequence that tells the Base class how to orderer the named edges
    # in the base edge data
    _CLOCKWISE_EDGE_NAMES = None
    # End component implementation requirements
    #          #          #          #          #          #          #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __init__(self, grid, index):
        # confirm we are running within an implemented class
        if any((self._BASE_EDGE_DATA is None,
                self._CLOCKWISE_EDGE_NAMES is None,
                self.INDEX_OFFSET_TO_SS_ANCHOR_SHAPE is None,
                self.SIDE is None,
                self.SS_VERTEX_OFFSET_PER_COL is None,
                self.SS_VERTEX_OFFSET_PER_ROW is None)):
            raise NotImplementedError
        self._grid = grid
        self._index = index
        self._edge_data, self._ordered_n_indexes = self._calc_final_data(index)
        self._owned_edges = dict()
        self._owned_edges.update(self._grab_edges())

    def _calc_final_data(self, index):
        """Return final edge data and sorted neighbors based on index.

        Note: this is combined because the determination of the items is
              interconnected.
        """
        row, col = index
        # make the shell of the final edge data and get the ordered indexes
        final_edge_data = dict()
        ordered_n_indexes = [None] * len(self._BASE_EDGE_DATA)
        for n_index_offset, base_data in self._BASE_EDGE_DATA.items():
            n_index = sum_tuples((index, n_index_offset))
            # create the data dict for the edge shared with n_index neighbor
            final_edge_data[n_index] = dict()
            # name is just name
            name = final_edge_data[n_index]['name'] = base_data['name']
            # convert base vertex within the ss to full vertex at this index
            base_vertex = base_data['vertex in ss']
            anchor_rc = sum_tuples(((row, col),
                                    self.INDEX_OFFSET_TO_SS_ANCHOR_SHAPE))
            anchor_row, anchor_col = anchor_rc
            row_offset = scale_tuple(self.SS_VERTEX_OFFSET_PER_ROW, anchor_row)
            col_offset = scale_tuple(self.SS_VERTEX_OFFSET_PER_COL, anchor_col)
            final_vertex = sum_tuples((base_vertex, row_offset, col_offset))
            final_edge_data[n_index]['this vertex'] = final_vertex
            # put n_index into the order indicated by the specification
            i = self._CLOCKWISE_EDGE_NAMES.index(name)
            ordered_n_indexes[i] = n_index
        # go back and fill in the additional vertex data for ease of access
        for primary_i, primary_n_index in enumerate(ordered_n_indexes):
            # get each pair of edges
            next_i = (primary_i + 1) % len(ordered_n_indexes)
            next_n_index = ordered_n_indexes[next_i]
            next_vertex = final_edge_data[next_n_index]['this vertex']
            final_edge_data[primary_n_index]['next vertex'] = next_vertex
        return final_edge_data, ordered_n_indexes

    def index(self):
        return self._index

    def neighbors(self):
        """Generate each index-neighbor pair for this shape.

        Neighbor is None for nonexistent neighbors.
        """
        for n_index in self._ordered_n_indexes:
            yield n_index, self._grid.get(n_index)

    def edges(self):
        """Generate each index-edge pair for this shape."""
        for n_index in self._ordered_n_indexes:
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
        else:
            pass  # this is an undefined case. basically runtime error

    def _grab_edges(self):
        """Return a dict of new edges for ONLY those that don't exist yet.

        return: {neighbor_index: edge, ...}
        """
        grabbed_edges = dict()
        for n_index, neighbor in self.neighbors():
            # ignore self owned edges
            if n_index in self._owned_edges:
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
        for n_index, edge in self._owned_edges.items():
            neighbor = self._grid.get(n_index)
            if neighbor:
                # transfer the edge only when there is a neighbor
                neighbor._owned_edges[self.index()] = edge
                del self._owned_edges[n_index]


class Square(IndexedShapeBase):
    """A square that fits by index into a regular grid of squares."""
    SIDE = 1.0
    SS_VERTEX_OFFSET_PER_ROW = (SIDE, 0.0)
    SS_VERTEX_OFFSET_PER_COL = (0.0, SIDE)
    INDEX_OFFSET_TO_SS_ANCHOR_SHAPE = (0, 0)
    _BASE_EDGE_DATA = {(-1, 0): {'name': 'top',
                                 'vertex in ss': (0.0, 0.0)},
                       (0, 1): {'name': 'right',
                                'vertex in ss': (0.0, SIDE)},
                       (1, 0): {'name': 'bottom',
                                'vertex in ss': (SIDE, SIDE)},
                       (0, -1): {'name': 'left',
                                 'vertex in ss': (SIDE, 0.0)}}
    _CLOCKWISE_EDGE_NAMES = 'top', 'right', 'bottom', 'left'


def __hexagon_startup_data():
    data = dict()
    # super shape data
    data['side'] = side = 1.0
    h = side * math.sin(math.pi / 3.0)
    data['ss vertex offset per row'] = (2.0 * h, 0.0)
    data['ss vertex offset per col'] = (0.0, 1.5 * side)
    # component shape data
    data['index offset to ss anchor shape'] = {'dleft': (0, 0),
                                               'uright': (0, -1)}
    # vertex calculations
    # shared horizontal and vertical rails
    top_rail = -1.0 * h
    midtop_rail = 0.0
    midbottom_rail = h
    bottom_rail = 2.0 * h
    left_rail = -1.5 * side
    midleft_left_rail = -1.0 * side
    midleft_rail = 0.0
    midright_rail = 0.5 * side
    midright_right_rail = 1.5 * side
    right_rail = 2.0 * side
    # point coordinates
    dleft_left_pt = (midbottom_rail, left_rail)
    dleft_topleft_pt = (midtop_rail, midleft_left_rail)
    dleft_topright_pt = (midtop_rail, midleft_rail)
    dleft_right_pt = (midbottom_rail, midright_rail)
    dleft_bottomright_pt = (bottom_rail, midleft_rail)
    dleft_bottomleft_pt = (bottom_rail, midleft_left_rail)
    uright_left_pt = dleft_topright_pt
    uright_topleft_pt = (top_rail, midright_rail)
    uright_topright_pt = (top_rail, midright_right_rail)
    uright_right_pt = (midtop_rail, right_rail)
    uright_bottomright_pt = (midbottom_rail, midright_right_rail)
    uright_bottomleft_pt = dleft_right_pt
    dleft = {(-1, 0): {'name': 'up',
                       'vertex in ss': dleft_topleft_pt},
             (0, 1): {'name': 'up right',
                      'vertex in ss': dleft_topright_pt},
             (1, 1): {'name': 'down right',
                      'vertex in ss': dleft_right_pt},
             (1, 0): {'name': 'down',
                      'vertex in ss': dleft_bottomright_pt},
             (1, -1): {'name': 'down left',
                       'vertex in ss': dleft_bottomleft_pt},
             (0, -1): {'name': 'up left',
                       'vertex in ss': dleft_left_pt}}
    uright = {(-1, 0): {'name': 'up',
                        'vertex in ss': uright_topleft_pt},
              (-1, 1): {'name': 'up right',
                        'vertex in ss': uright_topright_pt},
              (0, 1): {'name': 'down right',
                       'vertex in ss': uright_right_pt},
              (1, 0): {'name': 'down',
                       'vertex in ss': uright_bottomright_pt},
              (0, -1): {'name': 'down left',
                        'vertex in ss': uright_bottomleft_pt},
              (-1, -1): {'name': 'up left',
                         'vertex in ss': uright_left_pt}}
    data['base edge data'] = {'dleft': dleft,
                              'uright': uright}
    data['clockwise edge names'] = ('up', 'up right', 'down right',
                                    'down', 'down left', 'up left')
    return data
_hexagon_startup_data = __hexagon_startup_data()


class _Hexagon_DownLeft(IndexedShapeBase):
    __d = _hexagon_startup_data  # avoid crowding the namespace
    SIDE = __d['side']
    SS_VERTEX_OFFSET_PER_ROW = __d['ss vertex offset per row']
    SS_VERTEX_OFFSET_PER_COL = __d['ss vertex offset per col']
    INDEX_OFFSET_TO_SS_ANCHOR_SHAPE = __d['index offset to ss anchor shape']['dleft']
    _BASE_EDGE_DATA = __d['base edge data']['dleft']
    _CLOCKWISE_EDGE_NAMES = __d['clockwise edge names']


class _Hexagon_UpRight(IndexedShapeBase):
    __d = _hexagon_startup_data  # avoid crowding the namespace
    SIDE = __d['side']
    SS_VERTEX_OFFSET_PER_ROW = __d['ss vertex offset per row']
    SS_VERTEX_OFFSET_PER_COL = __d['ss vertex offset per col']
    INDEX_OFFSET_TO_SS_ANCHOR_SHAPE = __d['index offset to ss anchor shape']['uright']
    _BASE_EDGE_DATA = __d['base edge data']['uright']
    _CLOCKWISE_EDGE_NAMES = __d['clockwise edge names']


def __updowntriangle_startup_data():
    data = dict()
    # super shape data
    data['side'] = side = 1.0
    h = side * math.sin(math.pi / 3.0)
    data['ss vertex offset per row'] = (h, 0.0)
    data['ss vertex offset per col'] = (0.0, 0.5 * side)
    # component shape data
    data['index offset to ss anchor shape'] = {'up': (0, 0),
                                               'down': (0, -1)}
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
    midleft_pt = (top_rail, midleft_rail)
    midright_pt = (bottom_rail, midright_rail)
    right_pt = (top_rail, right_rail)
    data['base edge data'] = {'up': {(0, -1): {'name': 'left',
                                               'vertex in ss': left_pt},
                                     (0, 1): {'name': 'right',
                                              'vertex in ss': midleft_pt},
                                     (1, 0): {'name': 'down',
                                              'vertex in ss': midright_pt}},
                              'down': {(0, -1): {'name': 'left',
                                                 'vertex in ss': midright_pt},
                                       (-1, 0): {'name': 'up',
                                                 'vertex in ss': midleft_pt},
                                       (0, 1): {'name': 'right',
                                                'vertex in ss': right_pt}}}
    data['clockwise edge names'] = {'up': ('left', 'right', 'down'),
                                    'down': ('left', 'up', 'right')}
    return data
_updowntriangle_startup_data = __updowntriangle_startup_data()


class _UpDownTriangle_Up(IndexedShapeBase):
    __d = _updowntriangle_startup_data  # avoid crowding the namespace
    SIDE = __d['side']
    SS_VERTEX_OFFSET_PER_ROW = __d['ss vertex offset per row']
    SS_VERTEX_OFFSET_PER_COL = __d['ss vertex offset per col']
    INDEX_OFFSET_TO_SS_ANCHOR_SHAPE =\
        __d['index offset to ss anchor shape']['up']
    _BASE_EDGE_DATA = __d['base edge data']['up']
    _CLOCKWISE_EDGE_NAMES = __d['clockwise edge names']['up']


class _UpDownTriangle_Down(IndexedShapeBase):
    __d = _updowntriangle_startup_data  # avoid crowding the namespace
    SIDE = __d['side']
    SS_VERTEX_OFFSET_PER_ROW = __d['ss vertex offset per row']
    SS_VERTEX_OFFSET_PER_COL = __d['ss vertex offset per col']
    INDEX_OFFSET_TO_SS_ANCHOR_SHAPE =\
        __d['index offset to ss anchor shape']['down']
    _BASE_EDGE_DATA = __d['base edge data']['down']
    _CLOCKWISE_EDGE_NAMES = __d['clockwise edge names']['down']



#def OctaDiamond_supershape(grid, index):
#    row, col = index
#    odd = col % 2
#    if odd:
#        return _OctaDiamond_Diamond(grid, index)
#    else:
#        return _OctaDiamond_Octagon(grid, index)
#
#class _OctaDiamond_Base(IndexedShapeBase):
#    # base values
#    side = 1.0
#    h = side / math.sqrt(2.0)
#    # origin-based coordinates
#    # vertical line reference values
#    oct_left = -1.0 * (side + h)
#    oct_midleft = -1.0 * side
#    oct_midright = 0.0
#    oct_right = h
#    dmd_left = oct_midright
#    dmd_h_mid = oct_right
#    dmd_right = 2.0 * h
#    # horiztonal line reference values
#    oct_top = 0.0
#    oct_midtop = h
#    oct_midbottom = side + h
#    oct_bottom = side + 2.0 * h
#    dmd_top = -1.0 * h
#    dmd_v_mid = oct_top
#    dmd_bottom = oct_midtop
#    # use a clock analogy to build octagon points
#    clk_1_pt = (oct_top, oct_midright)
#    clk_2_pt = (oct_midtop, oct_right)
#    clk_4_pt = (oct_midbottom, oct_right)
#    clk_5_pt = (oct_bottom, oct_midright)
#    clk_7_pt = (oct_bottom, oct_midleft)
#    clk_8_pt = (oct_midbottom, oct_left)
#    clk_10_pt = (oct_midtop, oct_left)
#    clk_11_pt = (oct_top, oct_midleft)
#    # use a diamong analogy for the rotated square
#    dmd_left_pt = clk_1_pt
#    dmd_top_pt = (dmd_top, dmd_h_mid)
#    dmd_right_pt = (dmd_v_mid, dmd_right)
#    dmd_bottom_pt = clk_2_pt
#
#class _OctaDiamond_Octagon(_OctaDiamond_Base):
#    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#    # Begin Implementation requirements
#    def _identify_and_sort_neighbors(self):
#        """Implements base class requirements."""
#        row, col = self.index()
#        up = (row - 1, col)  # octagon of super shape above
#        uright = (row, col + 1)  # same super shape diamond
#        right = (row, col + 2)  # octagon of supershape to the right
#        dright = (row + 1, col + 1)  # diamond of supershape below
#        down = (row + 1, col)  # octagon of supershape below
#        dleft = (row + 1, col - 1)  # diamond of super shape below and left
#        left = (row, col - 2)  # octagon of supershape to the left
#        uleft = (row, col - 1)  # diamond of supershape to the left
#        return ({up: 'up', uright: 'uright', right: 'right', dright: 'dright',
#                 down: 'down', dleft: 'dleft', left: 'left', uleft: 'uleft'},
#                (up, uright, right, dright, down, dleft, left, uleft))
#
#    def _calc_edge_endpoints(self):
#        """Implements base class requirements."""
#        row, col = self.index()
#        # offset within the super shape
#        ss_offset = (0.0, 0.0)
#        # index-based offset
#        index_offset = (row * (self.side + 2 * self.h),
#                        (col // 2) * (self.side + 2 * self.h))
#        # total offset
#        offset = sum_tuples((ss_offset, index_offset))
#        # final coordinates
#        clk_1_pt = sum_tuples((self.clk_1_pt, offset))
#        clk_2_pt = sum_tuples((self.clk_2_pt, offset))
#        clk_4_pt = sum_tuples((self.clk_4_pt, offset))
#        clk_5_pt = sum_tuples((self.clk_5_pt, offset))
#        clk_7_pt = sum_tuples((self.clk_7_pt, offset))
#        clk_8_pt = sum_tuples((self.clk_8_pt, offset))
#        clk_10_pt = sum_tuples((self.clk_10_pt, offset))
#        clk_11_pt = sum_tuples((self.clk_11_pt, offset))
#        # paired points per edge
#        named_lookup = {'up': (clk_11_pt, clk_1_pt),
#                        'uright': (clk_1_pt, clk_2_pt),
#                        'right': (clk_2_pt, clk_4_pt),
#                        'dright': (clk_4_pt, clk_5_pt),
#                        'down': (clk_5_pt, clk_7_pt),
#                        'dleft': (clk_7_pt, clk_8_pt),
#                        'left': (clk_8_pt, clk_10_pt),
#                        'uleft': (clk_10_pt, clk_11_pt)}
#        edge_endpoints = {n_index: named_lookup[n_name] for n_index, n_name
#                          in self._edge_names.items()}
#        return edge_endpoints
#    # End implementation requirements
#    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#
#class _OctaDiamond_Diamond(_OctaDiamond_Base):
#    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#    # Begin Implementation requirements
#    def _identify_and_sort_neighbors(self):
#        """Implements base class requirements."""
#        row, col = self.index()
#        uleft = (row - 1, col - 1)  # octagon of supershape above
#        uright = (row - 1, col + 1)  # octagon of supershape above and left
#        dright = (row, col + 1)  # octagon of supershape left
#        dleft = (row, col - 1)  # octagon of same supershape
#        return ({uleft: 'uleft', uright: 'uright',
#                 dright: 'dright', dleft: 'dleft'},
#                (uleft, uright, dright, dleft))
#
#    def _calc_edge_endpoints(self):
#        """Implements base class requirements."""
#        row, col = self.index()
#        # offset within the super shape
#        ss_offset = (0.0, 0.0)
#        # index-based offset
#        index_offset = (row * (self.side + 2 * self.h),
#                        (col // 2) * (self.side + 2 * self.h))
#        # total offset
#        offset = sum_tuples((ss_offset, index_offset))
#        # final coordinates
#        dmd_left_pt = sum_tuples((self.dmd_left_pt, offset))
#        dmd_top_pt = sum_tuples((self.dmd_top_pt, offset))
#        dmd_right_pt = sum_tuples((self.dmd_right_pt, offset))
#        dmd_bottom_pt = sum_tuples((self.dmd_bottom_pt, offset))
#        # paired points per edge
#        named_lookup = {'uleft': (dmd_left_pt, dmd_top_pt),
#                        'uright': (dmd_top_pt, dmd_right_pt),
#                        'dright': (dmd_right_pt, dmd_bottom_pt),
#                        'dleft': (dmd_bottom_pt, dmd_left_pt)}
#        edge_endpoints = {n_index: named_lookup[n_name] for n_index, n_name
#                          in self._edge_names.items()}
#        return edge_endpoints
#    # End implementation requirements
#    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class Edge(object):
    def __init__(self, grid, neighbor_1_index, neighbor_2_index):
        self._grid = grid
        self._neighbor_1_index = neighbor_1_index
        self._neighbor_2_index = neighbor_2_index

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
        v1, v2 = (requesting_shape._edge_data[n_index]['this vertex'],
                  requesting_shape._edge_data[n_index]['next vertex'])
        return v1, v2


def sum_tuples(sequence_of_tuples):
    # not efficient but works
    a_sum, b_sum = 0, 0  # will be converted to float if any floats added
    for a, b in sequence_of_tuples:
        a_sum += a
        b_sum += b
    return a_sum, b_sum


def diff_tuples(positive, negative):
    # not efficient but works
    a = positive[0] - negative[0]
    b = positive[1] - negative[1]
    return a, b


def scale_tuple(t, scale):
    return scale * t[0], scale * t[1]


if __name__ == '__main__':
    pass
