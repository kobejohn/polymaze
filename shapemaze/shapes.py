import math


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
            # create the data dict for this neighbor index
            final_edge_data[n_index] = dict()
            # name is just name
            name = final_edge_data[n_index]['name'] = base_data['name']
            # convert base vertex within the ss to full vertex at this index
            base_vertex = base_data['vertex in ss']
            row_offset = scale_tuple(self.SS_VERTEX_OFFSET_PER_ROW, row)
            col_offset = scale_tuple(self.SS_VERTEX_OFFSET_PER_COL, col)
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
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #          #          #          #          #          #          #
    # Begin supershape implementation requirements
    SIDE = 1.0
    SS_VERTEX_OFFSET_PER_ROW = (SIDE, 0.0)
    SS_VERTEX_OFFSET_PER_COL = (0.0, SIDE)
    # End supershape implementation requirements
    #          #          #          #          #          #          #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #          #          #          #          #          #          #
    # Begin component implementation requirements
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
    # End component implementation requirements
    #          #          #          #          #          #          #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


def _hexagon_startup_data():
    data = dict()
    # super shape data
    data['side'] = side = 1.0
    h = side * math.sin(math.pi / 3.0)
    data['ss vertex offset per row'] = (2.0 * h, 0.0)
    data['ss vertex offset per col'] = (-1.0 * h, 1.5 * side)
    # component shape data
    data['index offset to ss anchor shape'] = (0, 0)
    # vertex calculations
    # shared horizontal and vertical rails
    top_rail = -1.0 * h
    v_middle_rail = 0.0
    bottom_rail = 1.0 * h
    left_rail = 0.0
    h_midleft_rail = 0.5 * side
    h_midright_rail = 1.5 * side
    right_rail = 2.0 * side
    # point coordinates
    left_pt = (v_middle_rail, left_rail)
    top_left_pt = (top_rail, h_midleft_rail)
    top_right_pt = (top_rail, h_midright_rail)
    right_pt = (v_middle_rail, right_rail)
    bottom_right_pt = (bottom_rail, h_midright_rail)
    bottom_left_pt = (bottom_rail, h_midleft_rail)
    data['base edge data'] = {(-1, 0): {'name': 'up',
                                        'vertex in ss': top_left_pt},
                              (0, 1): {'name': 'up right',
                                       'vertex in ss': top_right_pt},
                              (1, 1): {'name': 'down right',
                                       'vertex in ss': right_pt},
                              (1, 0): {'name': 'down',
                                       'vertex in ss': bottom_right_pt},
                              (0, -1): {'name': 'down left',
                                        'vertex in ss': bottom_left_pt},
                              (-1, -1): {'name': 'up left',
                                         'vertex in ss': left_pt}}
    data['clockwise edge names'] = ('up', 'up right', 'down right',
                                    'down', 'down left', 'up left')
    return data


class Hexagon(IndexedShapeBase):
    __d = _hexagon_startup_data()  # avoid crowding the namespace
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #          #          #          #          #          #          #
    # Begin supershape implementation requirements
    SIDE = 1.0
    SS_VERTEX_OFFSET_PER_ROW = __d['ss vertex offset per row']
    SS_VERTEX_OFFSET_PER_COL = __d['ss vertex offset per col']
    # End supershape implementation requirements
    #          #          #          #          #          #          #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #          #          #          #          #          #          #
    # Begin component implementation requirements
    INDEX_OFFSET_TO_SS_ANCHOR_SHAPE = __d['index offset to ss anchor shape']
    _BASE_EDGE_DATA = __d['base edge data']
    _CLOCKWISE_EDGE_NAMES = __d['clockwise edge names']
    # End component implementation requirements
    #          #          #          #          #          #          #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


def UpDownTriangle_factory(grid, index):
    """Provides up or down triangle class."""
    odd = sum(index) % 2
    if odd:
        return _UpDownTriangle_Down(grid, index)
    else:
        return _UpDownTriangle_Up(grid, index)


class _UpDownTriangle_Base(IndexedShapeBase):
    # base calculations
    side = 1.0
    h = side * math.sin(math.pi / 3.0)


class _UpDownTriangle_Up(_UpDownTriangle_Base):
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Begin Implementation requirements
    def _identify_and_sort_neighbors(self):
        """Implements base class requirements."""
        row, col = self.index()
        left, right, down = ((row, col - 1),
                             (row, col + 1),
                             (row + 1, col))
        return ({left: 'left', right: 'right', down: 'down'},
                (left, right, down))

    def _calc_edge_endpoints(self):
        """Implements base class requirements."""
        row, col = self.index()
        # origin-based coordinates
        origin_left_pt = (self.h, -1.0 * self.side / 2.0)
        origin_right_pt = (self.h, self.side / 2.0)
        origin_top_pt = (0.0, 0.0)
        # offset within the super shape
        ss_offset = (0.0, 0.0)
        # index-based offset
        index_offset = (row * self.h, col * self.side / 2.0)
        # final coordinates
        left_pt = sum_tuples((origin_left_pt, ss_offset, index_offset))
        right_pt = sum_tuples((origin_right_pt, ss_offset, index_offset))
        top_pt = sum_tuples((origin_top_pt, ss_offset, index_offset))
        # paired points per edge
        named_lookup = {'left': (left_pt, top_pt),
                        'right': (top_pt, right_pt),
                        'down': (right_pt, left_pt)}
        edge_endpoints = {n_index: named_lookup[n_name] for n_index, n_name
                          in self._edge_names.items()}
        return edge_endpoints
    # End implementation requirements
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class _UpDownTriangle_Down(_UpDownTriangle_Base):
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Begin Implementation requirements
    def _identify_and_sort_neighbors(self):
        """Implements base class requirements."""
        row, col = self.index()
        left, right, up = ((row, col - 1),
                           (row, col + 1),
                           (row - 1, col))  # key difference row +/- 1
        return ({left: 'left', right: 'right', up: 'up'},
                (up, right, left))

    def _calc_edge_endpoints(self):
        """Implements base class requirements."""
        row, col = self.index()
        # origin-based coordinates
        origin_left_pt = (0.0, 0.0)
        origin_right_pt = (0.0, self.side)
        origin_bottom_pt = (self.h, self.side / 2.0)
        # offset within the super shape
        ss_offset = (0.0, 0.0)
        # index-based offset
        index_offset = (row * self.h, (col - 1) * self.side / 2.0)
        # final coordinates
        left_pt = sum_tuples((origin_left_pt, ss_offset, index_offset))
        right_pt = sum_tuples((origin_right_pt, ss_offset, index_offset))
        middle_pt = sum_tuples((origin_bottom_pt, ss_offset, index_offset))
        # paired points per edge
        named_lookup = {'up': (left_pt, right_pt),
                        'right': (right_pt, middle_pt),
                        'left': (middle_pt, left_pt)}
        edge_endpoints = {n_index: named_lookup[n_name] for n_index, n_name
                          in self._edge_names.items()}
        return edge_endpoints
    # End implementation requirements
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


def OctaDiamond_factory(grid, index):
    row, col = index
    odd = col % 2
    if odd:
        return _OctaDiamond_Diamond(grid, index)
    else:
        return _OctaDiamond_Octagon(grid, index)

class _OctaDiamond_Base(IndexedShapeBase):
    # base values
    side = 1.0
    h = side / math.sqrt(2.0)
    # origin-based coordinates
    # vertical line reference values
    oct_left = -1.0 * (side + h)
    oct_midleft = -1.0 * side
    oct_midright = 0.0
    oct_right = h
    dmd_left = oct_midright
    dmd_h_mid = oct_right
    dmd_right = 2.0 * h
    # horiztonal line reference values
    oct_top = 0.0
    oct_midtop = h
    oct_midbottom = side + h
    oct_bottom = side + 2.0 * h
    dmd_top = -1.0 * h
    dmd_v_mid = oct_top
    dmd_bottom = oct_midtop
    # use a clock analogy to build octagon points
    clk_1_pt = (oct_top, oct_midright)
    clk_2_pt = (oct_midtop, oct_right)
    clk_4_pt = (oct_midbottom, oct_right)
    clk_5_pt = (oct_bottom, oct_midright)
    clk_7_pt = (oct_bottom, oct_midleft)
    clk_8_pt = (oct_midbottom, oct_left)
    clk_10_pt = (oct_midtop, oct_left)
    clk_11_pt = (oct_top, oct_midleft)
    # use a diamong analogy for the rotated square
    dmd_left_pt = clk_1_pt
    dmd_top_pt = (dmd_top, dmd_h_mid)
    dmd_right_pt = (dmd_v_mid, dmd_right)
    dmd_bottom_pt = clk_2_pt

class _OctaDiamond_Octagon(_OctaDiamond_Base):
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Begin Implementation requirements
    def _identify_and_sort_neighbors(self):
        """Implements base class requirements."""
        row, col = self.index()
        up = (row - 1, col)  # octagon of super shape above
        uright = (row, col + 1)  # same super shape diamond
        right = (row, col + 2)  # octagon of supershape to the right
        dright = (row + 1, col + 1)  # diamond of supershape below
        down = (row + 1, col)  # octagon of supershape below
        dleft = (row + 1, col - 1)  # diamond of super shape below and left
        left = (row, col - 2)  # octagon of supershape to the left
        uleft = (row, col - 1)  # diamond of supershape to the left
        return ({up: 'up', uright: 'uright', right: 'right', dright: 'dright',
                 down: 'down', dleft: 'dleft', left: 'left', uleft: 'uleft'},
                (up, uright, right, dright, down, dleft, left, uleft))

    def _calc_edge_endpoints(self):
        """Implements base class requirements."""
        row, col = self.index()
        # offset within the super shape
        ss_offset = (0.0, 0.0)
        # index-based offset
        index_offset = (row * (self.side + 2 * self.h),
                        (col // 2) * (self.side + 2 * self.h))
        # total offset
        offset = sum_tuples((ss_offset, index_offset))
        # final coordinates
        clk_1_pt = sum_tuples((self.clk_1_pt, offset))
        clk_2_pt = sum_tuples((self.clk_2_pt, offset))
        clk_4_pt = sum_tuples((self.clk_4_pt, offset))
        clk_5_pt = sum_tuples((self.clk_5_pt, offset))
        clk_7_pt = sum_tuples((self.clk_7_pt, offset))
        clk_8_pt = sum_tuples((self.clk_8_pt, offset))
        clk_10_pt = sum_tuples((self.clk_10_pt, offset))
        clk_11_pt = sum_tuples((self.clk_11_pt, offset))
        # paired points per edge
        named_lookup = {'up': (clk_11_pt, clk_1_pt),
                        'uright': (clk_1_pt, clk_2_pt),
                        'right': (clk_2_pt, clk_4_pt),
                        'dright': (clk_4_pt, clk_5_pt),
                        'down': (clk_5_pt, clk_7_pt),
                        'dleft': (clk_7_pt, clk_8_pt),
                        'left': (clk_8_pt, clk_10_pt),
                        'uleft': (clk_10_pt, clk_11_pt)}
        edge_endpoints = {n_index: named_lookup[n_name] for n_index, n_name
                          in self._edge_names.items()}
        return edge_endpoints
    # End implementation requirements
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class _OctaDiamond_Diamond(_OctaDiamond_Base):
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Begin Implementation requirements
    def _identify_and_sort_neighbors(self):
        """Implements base class requirements."""
        row, col = self.index()
        uleft = (row - 1, col - 1)  # octagon of supershape above
        uright = (row - 1, col + 1)  # octagon of supershape above and left
        dright = (row, col + 1)  # octagon of supershape left
        dleft = (row, col - 1)  # octagon of same supershape
        return ({uleft: 'uleft', uright: 'uright',
                 dright: 'dright', dleft: 'dleft'},
                (uleft, uright, dright, dleft))

    def _calc_edge_endpoints(self):
        """Implements base class requirements."""
        row, col = self.index()
        # offset within the super shape
        ss_offset = (0.0, 0.0)
        # index-based offset
        index_offset = (row * (self.side + 2 * self.h),
                        (col // 2) * (self.side + 2 * self.h))
        # total offset
        offset = sum_tuples((ss_offset, index_offset))
        # final coordinates
        dmd_left_pt = sum_tuples((self.dmd_left_pt, offset))
        dmd_top_pt = sum_tuples((self.dmd_top_pt, offset))
        dmd_right_pt = sum_tuples((self.dmd_right_pt, offset))
        dmd_bottom_pt = sum_tuples((self.dmd_bottom_pt, offset))
        # paired points per edge
        named_lookup = {'uleft': (dmd_left_pt, dmd_top_pt),
                        'uright': (dmd_top_pt, dmd_right_pt),
                        'dright': (dmd_right_pt, dmd_bottom_pt),
                        'dleft': (dmd_bottom_pt, dmd_left_pt)}
        edge_endpoints = {n_index: named_lookup[n_name] for n_index, n_name
                          in self._edge_names.items()}
        return edge_endpoints
    # End implementation requirements
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


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
        if requesting_shape_index is None:
            # neighbor_1 is default unless it doesn't exist in the grid
            requesting_shape_index = self._neighbor_1_index
            requesting_shape = self._grid.get(requesting_shape_index)
            if requesting_shape is None:
                requesting_shape_index = self._neighbor_2_index
        if requesting_shape_index == self._neighbor_1_index:
            n_index = self._neighbor_2_index
        elif requesting_shape_index == self._neighbor_2_index:
            n_index = self._neighbor_1_index
        else:
            raise ValueError('The requesting shape is not one of the sharing'
                             ' neighbors of this edge.')
        requesting_shape = self._grid.get(requesting_shape_index)
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
