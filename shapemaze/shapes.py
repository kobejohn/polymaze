import math


def supershapes_dict():
    """Return a dict of all supershapes in this module keyed by name."""
    supershapes = dict()
    for name, obj in globals().items():
        ss_suffix = '_supershape'
        ss_suffix_start = -1 * len(ss_suffix)
        # only pass something that meets the suffix requirement and is callable
        if (name[ss_suffix_start:] == ss_suffix) and callable(obj):
            ss_name = name[:ss_suffix_start]
            supershapes[ss_name] = obj
    return supershapes


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


def OctaDiamond_supershape(grid, index):
    row, col = index
    odd_col = col % 2
    if odd_col:
        return _OctaDiamond_Diamond(grid, index)
    else:
        return _OctaDiamond_Octagon(grid, index)


def Polycat_supershape(grid, index):
    row, col = index
    # offset the index back to the supershape at the origin index
    origin_based_index = (row % 2, col % 6)
    component_lookup = {(0, 0): _Polycat_LU_Whiskers,
                        (1, 0): _Polycat_LD_Whiskers,
                        (0, 1): _Polycat_L_Eye,
                        (1, 1): _Polycat_LD_Square,
                        (0, 2): _Polycat_L_Ear,
                        (1, 2): _Polycat_L_Nose,
                        (0, 3): _Polycat_Forehead,
                        (1, 3): _Polycat_Chin,
                        (0, 4): _Polycat_R_Ear,
                        (1, 4): _Polycat_R_Nose,
                        (0, 5): _Polycat_R_Eye,
                        (1, 5): _Polycat_RD_Square}
    return component_lookup[origin_based_index](grid, index)


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
        # if the code gets here, it's basically a runtime error

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
    __component_name = 'dleft'
    SIDE = __d['side']
    SS_VERTEX_OFFSET_PER_ROW = __d['ss vertex offset per row']
    SS_VERTEX_OFFSET_PER_COL = __d['ss vertex offset per col']
    INDEX_OFFSET_TO_SS_ANCHOR_SHAPE = \
        __d['index offset to ss anchor shape'][__component_name]
    _BASE_EDGE_DATA = __d['base edge data'][__component_name]
    _CLOCKWISE_EDGE_NAMES = __d['clockwise edge names']


class _Hexagon_UpRight(IndexedShapeBase):
    __d = _hexagon_startup_data  # avoid crowding the namespace
    __component_name = 'uright'
    SIDE = __d['side']
    SS_VERTEX_OFFSET_PER_ROW = __d['ss vertex offset per row']
    SS_VERTEX_OFFSET_PER_COL = __d['ss vertex offset per col']
    INDEX_OFFSET_TO_SS_ANCHOR_SHAPE = \
        __d['index offset to ss anchor shape'][__component_name]
    _BASE_EDGE_DATA = __d['base edge data'][__component_name]
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
    __component_name = 'up'
    SIDE = __d['side']
    SS_VERTEX_OFFSET_PER_ROW = __d['ss vertex offset per row']
    SS_VERTEX_OFFSET_PER_COL = __d['ss vertex offset per col']
    INDEX_OFFSET_TO_SS_ANCHOR_SHAPE =\
        __d['index offset to ss anchor shape'][__component_name]
    _BASE_EDGE_DATA = __d['base edge data'][__component_name]
    _CLOCKWISE_EDGE_NAMES = __d['clockwise edge names'][__component_name]


class _UpDownTriangle_Down(IndexedShapeBase):
    __d = _updowntriangle_startup_data  # avoid crowding the namespace
    __component_name = 'down'
    SIDE = __d['side']
    SS_VERTEX_OFFSET_PER_ROW = __d['ss vertex offset per row']
    SS_VERTEX_OFFSET_PER_COL = __d['ss vertex offset per col']
    INDEX_OFFSET_TO_SS_ANCHOR_SHAPE =\
        __d['index offset to ss anchor shape'][__component_name]
    _BASE_EDGE_DATA = __d['base edge data'][__component_name]
    _CLOCKWISE_EDGE_NAMES = __d['clockwise edge names'][__component_name]


def __octadiamond_startup_data():
    data = dict()
    # super shape data
    data['side'] = side = 1.0
    h = side / math.sqrt(2.0)
    data['ss vertex offset per row'] = (side + 2.0 * h, 0.0)
    data['ss vertex offset per col'] = (0.0, 0.5 * (side + 2.0 * h))
    # component shape data
    data['index offset to ss anchor shape'] = {'octagon': (0, 0),
                                               'diamond': (0, -1)}
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
    octagon_base_data = {(-1, 0): {'name': 'up',
                                   'vertex in ss': clk_11_pt},
                         (0, 1): {'name': 'uright',
                                  'vertex in ss': clk_1_pt},
                         (0, 2): {'name': 'right',
                                  'vertex in ss': clk_2_pt},
                         (1, 1): {'name': 'dright',
                                  'vertex in ss': clk_4_pt},
                         (1, 0): {'name': 'down',
                                  'vertex in ss': clk_5_pt},
                         (1, -1): {'name': 'dleft',
                                   'vertex in ss': clk_7_pt},
                         (0, -2): {'name': 'left',
                                   'vertex in ss': clk_8_pt},
                         (0, -1): {'name': 'uleft',
                                   'vertex in ss': clk_10_pt}}
    diamond_base_data = {(-1, -1): {'name': 'uleft',
                                    'vertex in ss': dmd_left_pt},
                         (-1, 1): {'name': 'uright',
                                   'vertex in ss': dmd_top_pt},
                         (0, 1): {'name': 'dright',
                                  'vertex in ss': dmd_right_pt},
                         (0, -1): {'name': 'dleft',
                                   'vertex in ss': dmd_bottom_pt}}
    data['base edge data'] = {'octagon': octagon_base_data,
                              'diamond': diamond_base_data}
    data['clockwise edge names'] = {'octagon': ('up', 'uright', 'right',
                                                'dright', 'down', 'dleft',
                                                'left', 'uleft'),
                                    'diamond': ('uleft', 'uright',
                                                'dright', 'dleft')}
    return data
_octadiamond_startup_data = __octadiamond_startup_data()


class _OctaDiamond_Octagon(IndexedShapeBase):
    __d = _octadiamond_startup_data  # avoid crowding the namespace
    __component_name = 'octagon'
    SIDE = __d['side']
    SS_VERTEX_OFFSET_PER_ROW = __d['ss vertex offset per row']
    SS_VERTEX_OFFSET_PER_COL = __d['ss vertex offset per col']
    INDEX_OFFSET_TO_SS_ANCHOR_SHAPE =\
        __d['index offset to ss anchor shape'][__component_name]
    _BASE_EDGE_DATA = __d['base edge data'][__component_name]
    _CLOCKWISE_EDGE_NAMES = __d['clockwise edge names'][__component_name]


class _OctaDiamond_Diamond(IndexedShapeBase):
    __d = _octadiamond_startup_data  # avoid crowding the namespace
    __component_name = 'diamond'
    SIDE = __d['side']
    SS_VERTEX_OFFSET_PER_ROW = __d['ss vertex offset per row']
    SS_VERTEX_OFFSET_PER_COL = __d['ss vertex offset per col']
    INDEX_OFFSET_TO_SS_ANCHOR_SHAPE =\
        __d['index offset to ss anchor shape'][__component_name]
    _BASE_EDGE_DATA = __d['base edge data'][__component_name]
    _CLOCKWISE_EDGE_NAMES = __d['clockwise edge names'][__component_name]


def __polycat_startup_data():
    data = dict()
    # super shape data
    data['side'] = side = 1.0
    h = side * math.sin(math.pi / 3.0)
    d_s_partial2 = side * (1.0 - math.tan(math.pi / 6.0))
    d_corner_h = d_s_partial2 * math.cos(math.pi / 6.0)
    d_corner_v = d_s_partial2 * math.sin(math.pi / 6.0)
    d_i_partialv = side / math.sin(math.pi / 3.0)
    # component shape data
    data['index offset to ss anchor shape'] = {'l ear': (0, -2),
                                               'r ear': (0, -4),
                                               'forehead': (0, -3),
                                               'l eye': (0, -1),
                                               'r eye': (0, -5),
                                               'lu whiskers': (0, 0),
                                               'ld whiskers': (-1, 0),
                                               'l nose': (-1, -2),
                                               'r nose': (-1, -4),
                                               'ld square': (-1, -1),
                                               'rd square': (-1, -5),
                                               'chin': (-1, -3)}
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
    # supershape origin offset per index
    data['ss vertex offset per row'] = (bottom_rail, 0.0)
    data['ss vertex offset per col'] = (0.0, (side + 2.0 * h) / 6.0)
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
    # origin-based coordinates
    l_ear_base_data = {(0, -4): {'name': 'left',
                                 'vertex in ss': l_dmd_top_pt},
                       (-1, -1): {'name': 'right',
                                  'vertex in ss': l_ear_top_pt},
                       (0, -1): {'name': 'bottom',
                                 'vertex in ss': l_ear_right_pt}}
    r_ear_base_data = {(-1, 1): {'name': 'left',
                                 'vertex in ss': r_ear_left_pt},
                       (0, 4): {'name': 'right',
                                'vertex in ss': r_ear_top_pt},
                       (0, 1): {'name': 'bottom',
                                'vertex in ss': r_dmd_top_pt}}
    forehead_base_data = {(0, -2): {'name': 'left',
                                    'vertex in ss': m_dmd_top_pt},
                          (-1, 0): {'name': 'top',
                                    'vertex in ss': l_ear_right_pt},
                          (0, 2): {'name': 'right',
                                   'vertex in ss': r_ear_left_pt}}
    l_eye_base_data = {(0, 1): {'name': 'uleft',
                                'vertex in ss': l_dmd_top_pt},
                       (0, 2): {'name': 'uright',
                                'vertex in ss': l_ear_right_pt},
                       (1, 1): {'name': 'dright',
                                'vertex in ss': m_dmd_top_pt},
                       (0, -1): {'name': 'dleft',
                                 'vertex in ss': m_dmd_left_pt}}
    r_eye_base_data = {(0, -2): {'name': 'uleft',
                                 'vertex in ss': m_dmd_top_pt},
                       (0, -1): {'name': 'uright',
                                 'vertex in ss': r_ear_left_pt},
                       (0, 1): {'name': 'dright',
                                'vertex in ss': r_dmd_top_pt},
                       (1, -1): {'name': 'dleft',
                                 'vertex in ss': m_dmd_right_pt}}
    lu_whiskers_base_data = {(0, -1): {'name': 'left',
                                       'vertex in ss': l_dmd_left_pt},
                             (0, 1): {'name': 'right',
                                      'vertex in ss': l_dmd_top_pt},
                             (1, 0): {'name': 'bottom',
                                      'vertex in ss': m_dmd_left_pt}}
    ld_whiskers_base_data = {(0, -1): {'name': 'left',
                                       'vertex in ss': l_dmd_bottom_pt},
                             (-1, 0): {'name': 'top',
                                       'vertex in ss': l_dmd_left_pt},
                             (0, 1): {'name': 'right',
                                      'vertex in ss': m_dmd_left_pt}}
    l_nose_base_data = {(0, -1): {'name': 'bottom',
                                  'vertex in ss': m_dmd_bottom_pt},
                        (-1, -1): {'name': 'top',
                                   'vertex in ss': m_dmd_left_pt},
                        (0, 2): {'name': 'right',
                                 'vertex in ss': m_dmd_top_pt}}
    r_nose_base_data = {(0, -2): {'name': 'left',
                                  'vertex in ss': m_dmd_bottom_pt},
                        (-1, 1): {'name': 'top',
                                  'vertex in ss': m_dmd_top_pt},
                        (0, 1): {'name': 'bottom',
                                 'vertex in ss': m_dmd_right_pt}}
    ld_square_base_data = {(0, -1): {'name': 'uleft',
                                     'vertex in ss': l_dmd_bottom_pt},
                           (0, 1): {'name': 'uright',
                                    'vertex in ss': m_dmd_left_pt},
                           (0, 2): {'name': 'dright',
                                    'vertex in ss': m_dmd_bottom_pt},
                           (1, 1): {'name': 'dleft',
                                    'vertex in ss': chin_left_pt}}
    rd_square_base_data = {(0, -1): {'name': 'uleft',
                                     'vertex in ss': m_dmd_bottom_pt},
                           (0, 1): {'name': 'uright',
                                    'vertex in ss': m_dmd_right_pt},
                           (1, -1): {'name': 'dright',
                                     'vertex in ss': r_dmd_bottom_pt},
                           (0, -2): {'name': 'dleft',
                                     'vertex in ss': chin_right_pt}}
    chin_base_data = {(0, -2): {'name': 'left',
                                'vertex in ss': chin_left_pt},
                      (0, 2): {'name': 'right',
                               'vertex in ss': m_dmd_bottom_pt},
                      (1, 0): {'name': 'bottom',
                               'vertex in ss': chin_right_pt}}
    data['base edge data'] = {'l ear': l_ear_base_data,
                              'r ear': r_ear_base_data,
                              'forehead': forehead_base_data,
                              'l eye': l_eye_base_data,
                              'r eye': r_eye_base_data,
                              'lu whiskers': lu_whiskers_base_data,
                              'ld whiskers': ld_whiskers_base_data,
                              'l nose': l_nose_base_data,
                              'r nose': r_nose_base_data,
                              'ld square': ld_square_base_data,
                              'rd square': rd_square_base_data,
                              'chin': chin_base_data}
    data['clockwise edge names'] = {'l ear': ('left', 'right', 'bottom'),
                                    'r ear': ('left', 'right', 'bottom'),
                                    'forehead': ('left', 'top', 'right'),
                                    'l eye': ('uleft', 'uright', 'dright',
                                              'dleft'),
                                    'r eye': ('uleft', 'uright', 'dright',
                                              'dleft'),
                                    'lu whiskers': ('left', 'right', 'bottom'),
                                    'ld whiskers': ('left', 'top', 'right'),
                                    'l nose': ('bottom', 'top', 'right'),
                                    'r nose': ('left', 'top', 'bottom'),
                                    'ld square': ('uleft', 'uright', 'dright',
                                                  'dleft'),
                                    'rd square': ('uleft', 'uright', 'dright',
                                                  'dleft'),
                                    'chin': ('left', 'right', 'bottom')}
    return data
_polycat_startup_data = __polycat_startup_data()


class _Polycat_L_Ear(IndexedShapeBase):
    __d = _polycat_startup_data  # avoid crowding the namespace
    __component_name = 'l ear'
    SIDE = __d['side']
    SS_VERTEX_OFFSET_PER_ROW = __d['ss vertex offset per row']
    SS_VERTEX_OFFSET_PER_COL = __d['ss vertex offset per col']
    INDEX_OFFSET_TO_SS_ANCHOR_SHAPE =\
        __d['index offset to ss anchor shape'][__component_name]
    _BASE_EDGE_DATA = __d['base edge data'][__component_name]
    _CLOCKWISE_EDGE_NAMES = __d['clockwise edge names'][__component_name]


class _Polycat_R_Ear(IndexedShapeBase):
    __d = _polycat_startup_data  # avoid crowding the namespace
    __component_name = 'r ear'
    SIDE = __d['side']
    SS_VERTEX_OFFSET_PER_ROW = __d['ss vertex offset per row']
    SS_VERTEX_OFFSET_PER_COL = __d['ss vertex offset per col']
    INDEX_OFFSET_TO_SS_ANCHOR_SHAPE = \
        __d['index offset to ss anchor shape'][__component_name]
    _BASE_EDGE_DATA = __d['base edge data'][__component_name]
    _CLOCKWISE_EDGE_NAMES = __d['clockwise edge names'][__component_name]


class _Polycat_Forehead(IndexedShapeBase):
    __d = _polycat_startup_data  # avoid crowding the namespace
    __component_name = 'forehead'
    SIDE = __d['side']
    SS_VERTEX_OFFSET_PER_ROW = __d['ss vertex offset per row']
    SS_VERTEX_OFFSET_PER_COL = __d['ss vertex offset per col']
    INDEX_OFFSET_TO_SS_ANCHOR_SHAPE = \
        __d['index offset to ss anchor shape'][__component_name]
    _BASE_EDGE_DATA = __d['base edge data'][__component_name]
    _CLOCKWISE_EDGE_NAMES = __d['clockwise edge names'][__component_name]


class _Polycat_L_Eye(IndexedShapeBase):
    __d = _polycat_startup_data  # avoid crowding the namespace
    __component_name = 'l eye'
    SIDE = __d['side']
    SS_VERTEX_OFFSET_PER_ROW = __d['ss vertex offset per row']
    SS_VERTEX_OFFSET_PER_COL = __d['ss vertex offset per col']
    INDEX_OFFSET_TO_SS_ANCHOR_SHAPE = \
        __d['index offset to ss anchor shape'][__component_name]
    _BASE_EDGE_DATA = __d['base edge data'][__component_name]
    _CLOCKWISE_EDGE_NAMES = __d['clockwise edge names'][__component_name]


class _Polycat_R_Eye(IndexedShapeBase):
    __d = _polycat_startup_data  # avoid crowding the namespace
    __component_name = 'r eye'
    SIDE = __d['side']
    SS_VERTEX_OFFSET_PER_ROW = __d['ss vertex offset per row']
    SS_VERTEX_OFFSET_PER_COL = __d['ss vertex offset per col']
    INDEX_OFFSET_TO_SS_ANCHOR_SHAPE = \
        __d['index offset to ss anchor shape'][__component_name]
    _BASE_EDGE_DATA = __d['base edge data'][__component_name]
    _CLOCKWISE_EDGE_NAMES = __d['clockwise edge names'][__component_name]


class _Polycat_LU_Whiskers(IndexedShapeBase):
    __d = _polycat_startup_data  # avoid crowding the namespace
    __component_name = 'lu whiskers'
    SIDE = __d['side']
    SS_VERTEX_OFFSET_PER_ROW = __d['ss vertex offset per row']
    SS_VERTEX_OFFSET_PER_COL = __d['ss vertex offset per col']
    INDEX_OFFSET_TO_SS_ANCHOR_SHAPE = \
        __d['index offset to ss anchor shape'][__component_name]
    _BASE_EDGE_DATA = __d['base edge data'][__component_name]
    _CLOCKWISE_EDGE_NAMES = __d['clockwise edge names'][__component_name]


class _Polycat_LD_Whiskers(IndexedShapeBase):
    __d = _polycat_startup_data  # avoid crowding the namespace
    __component_name = 'ld whiskers'
    SIDE = __d['side']
    SS_VERTEX_OFFSET_PER_ROW = __d['ss vertex offset per row']
    SS_VERTEX_OFFSET_PER_COL = __d['ss vertex offset per col']
    INDEX_OFFSET_TO_SS_ANCHOR_SHAPE = \
        __d['index offset to ss anchor shape'][__component_name]
    _BASE_EDGE_DATA = __d['base edge data'][__component_name]
    _CLOCKWISE_EDGE_NAMES = __d['clockwise edge names'][__component_name]


class _Polycat_L_Nose(IndexedShapeBase):
    __d = _polycat_startup_data  # avoid crowding the namespace
    __component_name = 'l nose'
    SIDE = __d['side']
    SS_VERTEX_OFFSET_PER_ROW = __d['ss vertex offset per row']
    SS_VERTEX_OFFSET_PER_COL = __d['ss vertex offset per col']
    INDEX_OFFSET_TO_SS_ANCHOR_SHAPE = \
        __d['index offset to ss anchor shape'][__component_name]
    _BASE_EDGE_DATA = __d['base edge data'][__component_name]
    _CLOCKWISE_EDGE_NAMES = __d['clockwise edge names'][__component_name]


class _Polycat_R_Nose(IndexedShapeBase):
    __d = _polycat_startup_data  # avoid crowding the namespace
    __component_name = 'r nose'
    SIDE = __d['side']
    SS_VERTEX_OFFSET_PER_ROW = __d['ss vertex offset per row']
    SS_VERTEX_OFFSET_PER_COL = __d['ss vertex offset per col']
    INDEX_OFFSET_TO_SS_ANCHOR_SHAPE = \
        __d['index offset to ss anchor shape'][__component_name]
    _BASE_EDGE_DATA = __d['base edge data'][__component_name]
    _CLOCKWISE_EDGE_NAMES = __d['clockwise edge names'][__component_name]


class _Polycat_LD_Square(IndexedShapeBase):
    __d = _polycat_startup_data  # avoid crowding the namespace
    __component_name = 'ld square'
    SIDE = __d['side']
    SS_VERTEX_OFFSET_PER_ROW = __d['ss vertex offset per row']
    SS_VERTEX_OFFSET_PER_COL = __d['ss vertex offset per col']
    INDEX_OFFSET_TO_SS_ANCHOR_SHAPE = \
        __d['index offset to ss anchor shape'][__component_name]
    _BASE_EDGE_DATA = __d['base edge data'][__component_name]
    _CLOCKWISE_EDGE_NAMES = __d['clockwise edge names'][__component_name]


class _Polycat_RD_Square(IndexedShapeBase):
    __d = _polycat_startup_data  # avoid crowding the namespace
    __component_name = 'rd square'
    SIDE = __d['side']
    SS_VERTEX_OFFSET_PER_ROW = __d['ss vertex offset per row']
    SS_VERTEX_OFFSET_PER_COL = __d['ss vertex offset per col']
    INDEX_OFFSET_TO_SS_ANCHOR_SHAPE = \
        __d['index offset to ss anchor shape'][__component_name]
    _BASE_EDGE_DATA = __d['base edge data'][__component_name]
    _CLOCKWISE_EDGE_NAMES = __d['clockwise edge names'][__component_name]


class _Polycat_Chin(IndexedShapeBase):
    __d = _polycat_startup_data  # avoid crowding the namespace
    __component_name = 'chin'
    SIDE = __d['side']
    SS_VERTEX_OFFSET_PER_ROW = __d['ss vertex offset per row']
    SS_VERTEX_OFFSET_PER_COL = __d['ss vertex offset per col']
    INDEX_OFFSET_TO_SS_ANCHOR_SHAPE = \
        __d['index offset to ss anchor shape'][__component_name]
    _BASE_EDGE_DATA = __d['base edge data'][__component_name]
    _CLOCKWISE_EDGE_NAMES = __d['clockwise edge names'][__component_name]


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


def scale_tuple(t, scale):
    return scale * t[0], scale * t[1]


if __name__ == '__main__':
    pass
