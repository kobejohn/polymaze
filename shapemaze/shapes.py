import math


class IndexedShapeBase(object):
    """A shape that fits by index into a grid of other shapes."""

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Begin Implementation requirements

    def _identify_and_sort_neighbors(self):
        """Return a dict identifying each neighbor with a semantic edge name
        and a tuple indicating the clockwise order of the edges.

        return: ({neighbor_index: semantic_name, ...},
                 ('semantic_name1', 'semantic_name2', ...))
        """
        raise NotImplementedError

    def _calc_edge_endpoints(self):
        """Return a dict identifying the end points for the edge between
        self and each neighbor.

        return: {neighbor_index: (float_yx, float_yx), ...}

        Note regarding units:
            All shapes in grid must agree on the units of the point values.
            If all shapes have the same edge length, that's a good unit value.
        """
        raise NotImplementedError
    # End implementation requirements
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __init__(self, grid, index):
        self._grid = grid
        self._index = index
        edge_names, clockwise_indexes = self._identify_and_sort_neighbors()
        self._edge_names = edge_names
        self._neighbor_indexes = clockwise_indexes
        self._edge_endpoints = self._calc_edge_endpoints()
        self._owned_edges = dict()
        self._grab_edges()

    def index(self):
        return self._index

    def neighbors(self):
        """Generate each index-neighbor pair for this shape.

        Neighbor is None for nonexistent neighbors.
        """
        for n_index in self._neighbor_indexes:
            yield n_index, self._grid.get(n_index)

    def edges(self):
        """Generate each index-edge pair for this shape."""
        for n_index in self._neighbor_indexes:
            edge = self.edge(n_index)
            yield n_index, edge

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

    def _grab_edges(self):
        """Return a dict of new edges for ONLY those that don't exist yet.

        return: {neighbor_index: edge, ...}
        """
        grabbed_edges = dict()
        for n_index, neighbor in self.neighbors():
            # not strictly necessary so removed
            ## ignore self owned edges
            #if n_index in self._owned_edges:
            #    continue
            # ignore neighbor owned edges
            if neighbor:
                if self.index() in neighbor._owned_edges:
                    continue
            # create edges that didn't exist in self or neighbor
            grabbed_edges[n_index] = Edge(self._grid, self.index(), n_index)
        self._owned_edges.update(grabbed_edges)

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

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Begin Implementation requirements
    def _identify_and_sort_neighbors(self):
        """Implements base class requirements."""
        row, col = self.index()
        top, bottom, left, right = ((row - 1, col),
                                    (row + 1, col),
                                    (row, col - 1),
                                    (row, col + 1))
        return ({top: 'top', right: 'right', bottom: 'bottom', left: 'left'},
                (top, right, bottom, left))

    def _calc_edge_endpoints(self):
        """Implements base class requirements."""
        row, col = self.index()
        # shared side coordinates
        top = float(row)
        bottom = float(row + 1)
        left = float(col)
        right = float(col + 1)
        # point coordinates
        top_left = (top, left)
        top_right = (top, right)
        bottom_left = (bottom, left)
        bottom_right = (bottom, right)
        # paired points per edge
        named_lookup = {'top': (top_left, top_right),
                        'right': (top_right, bottom_right),
                        'bottom': (bottom_right, bottom_left),
                        'left': (bottom_left, top_left)}
        edge_endpoints = {n_index: named_lookup[n_name] for n_index, n_name
                          in self._edge_names.items()}
        return edge_endpoints
    # End implementation requirements
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class Hexagon(IndexedShapeBase):
    # base calculations
    side = 1.0
    h = side * math.sin(math.pi / 3.0)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Begin Implementation requirements
    def _identify_and_sort_neighbors(self):
        """Implements base class requirements."""
        row, col = self.index()
        up, uright, dright, down, dleft, uleft = ((row - 1, col),
                                                  (row, col + 1),
                                                  (row + 1, col + 1),
                                                  (row + 1, col),
                                                  (row, col - 1),
                                                  (row - 1, col - 1))
        return ({up: 'up', uright: 'uright', dright: 'dright',
                 down: 'down', dleft: 'dleft', uleft: 'uleft'},
                (up, uright, dright, down, dleft, uleft))

    def _calc_edge_endpoints(self):
        """Implements base class requirements."""
        row, col = self.index()
        x_offset = col * 1.5 * self.side
        y_offset = row * 2.0 * self.h - col * 1.0 * self.h
        # shared side coordinates
        top = -1.0 * self.h + y_offset
        v_middle = 0.0 + y_offset
        bottom = 1.0 * self.h + y_offset
        left = 0.0 + x_offset
        h_midleft = 0.5 * self.side + x_offset
        h_midright = 1.5 * self.side + x_offset
        right = 2.0 * self.side + x_offset
        # point coordinates
        left_pt = (v_middle, left)
        top_left_pt = (top, h_midleft)
        top_right_pt = (top, h_midright)
        right_pt = (v_middle, right)
        bottom_right_pt = (bottom, h_midright)
        bottom_left_pt = (bottom, h_midleft)
        # paired points per edge
        named_lookup = {'uleft': (left_pt, top_left_pt),
                        'up': (top_left_pt, top_right_pt),
                        'uright': (top_right_pt, right_pt),
                        'dright': (right_pt, bottom_right_pt),
                        'down': (bottom_right_pt, bottom_left_pt),
                        'dleft': (bottom_left_pt, left_pt)}
        edge_endpoints = {n_index: named_lookup[n_name] for n_index, n_name
                          in self._edge_names.items()}
        return edge_endpoints
    # End implementation requirements
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


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
            # use neighbor_1 UNLESS it doesn't exist in the grid
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
        return self._grid.get(requesting_shape_index)._edge_endpoints[n_index]


def sum_tuples(sequence_of_tuples):
    # not efficient but works
    a_sum, b_sum = 0, 0  # will be converted to float if any floats added
    for a, b in sequence_of_tuples:
        a_sum += a
        b_sum += b
    return a_sum, b_sum


if __name__ == '__main__':
    pass
