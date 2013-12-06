# coding=utf-8
import math
import os
import random

import PIL.Image
import PIL.ImageDraw
import PIL.ImageFilter
import PIL.ImageFont
import PIL.ImageOps

import shapes as _shapes

_SS_DICT = _shapes.supershapes_dict()
_BASE_EDGES = 1000.0
_DEFAULT_COMPLEXITY = 1.0
_DEFAULT_FONT = 'impact.ttf'  # common font with a high surface area
_BASE_DIR = os.path.dirname(__file__)


class PolyGrid(object):
    """Sparse grid of shapes."""
    def __init__(self, supershape=None):
        """Create an empty grid.

        kwargs:
        supershape - a supershape class that defines how the maze will look
                     (random if not provided)
        """
        self._shapes = dict()
        self._supershape = supershape or random.choice(_SS_DICT.values())

    def create(self, index):
        """Create (or replace) a shape at index."""
        ss = self._supershape
        self._shapes[index] = new_shape = ss.create_component(self, index)
        return new_shape

    def create_rectangle(self, **kwargs):
        """Create a rectangle of shapes.

        kwargs:
        complexity - scale the difficulty of the maze to any positive number
        aspect - aspect of the grid's graph (not indexes) (height / width)
        """
        rows, cols = _normalize_bounds_to_complexity(self._supershape, **kwargs)
        for row in range(rows):
            for col in range(cols):
                self.create((row, col))

    def create_string(self, string, font_path=None, **kwargs):
        """Create shapes in the form of the provided string.

        kwargs:
        font_path - just file name of any font in resources or full path
        complexity - scale the difficulty of the maze to any positive number
        aspect - aspect of the grid's graph (not indexes) (height / width)
        """
        string_image = _string_image(string, font_path=font_path)
        # cheat. multiply complexity by length of string
        base_complexity = kwargs.get('complexity') or _DEFAULT_COMPLEXITY
        kwargs['complexity'] = len(string) * base_complexity
        # create with the standard image method
        self.create_from_image(string_image, **kwargs)

    def create_from_image(self, image, **kwargs):
        """Create shapes that reproduce the shape of black pixels in image."""
        grid_im = _source_image_to_grid_image(image, self._supershape, **kwargs)
        grid_pixels = grid_im.load()
        width, height = grid_im.size
        for y in range(height):
            for x in range(width):
                if not grid_pixels[x, y]:
                    self.create((y, x))

    def supershape_name(self):
        return self._supershape.name()

    def remove(self, index):
        """Remove the shape at index and remove its link to the grid."""
        # get a reference to the shape or finish if it doesn't exist
        try:
            removed_shape = self._shapes[index]
        except KeyError:
            return  # no shape there, done
        # distribute any owned edges to neighbors
        removed_shape._give_away_edges()
        # remove the shape from the grid
        del(self._shapes[index])
        # remove the grid from the shape
        removed_shape._grid = None

    def get(self, index):
        """Return the shape at index or None if no shape there."""
        try:
            return self._shapes[index]
        except KeyError:
            return None

    def shapes(self):
        """Generate each edge in the map exactly once."""
        for shape in self._shapes.itervalues():
            yield shape

    def edges(self):
        """Generate each edge in the map exactly once."""
        for shape in self._shapes.itervalues():
            for edge in shape._owned_edges.itervalues():
                yield edge

    def border_shapes(self):
        """Generate all shapes on the grid that have at least one open edge."""
        for shape in self._shapes.itervalues():
            for n_index, neighbor in shape.neighbors():
                if neighbor is None:
                    yield shape
                    break  # only yield a shape once


def _normalize_bounds_to_complexity(supershape, complexity=None, aspect=None):
    """Normalize the difficulty of mazes based on number of edges per shape.

    This approach allows the complexity/difficulty of a maze using any shape
    to be similar by having more simple shapes and fewer complex shapes. If
    the number of shapes is standardized instead, the complexity varies greatly
    between shapes with few and many edges.
    """
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # outline:
    #   a) edges
    #       --> adjust base edges for general complexity
    #       --> adjust edges for shape complexity (down for more edges)
    #       --> convert edges to shape count
    #           (tesselation internal shape --> 1 shape per (shape edges)/2
    #   b) y/x ratio --> row/col ratio
    #       --> convert the desired h/w ratio to a row/col ratio
    #           such that the row/col ratio for this supershape will yield
    #           the desired h/w ratio when graphed
    #           start: Ah/Aw = rows*row_offset[0] + cols*col_offset[0]
    #                          -----------------------------------------
    #                          rows*row_offset[1] + cols*col_offset[1]
    #           assume A = Ah/Aw
    #           end: rows/cols = A*col_offset[1] - col_offset[0]
    #                            -------------------------------
    #                            row_offset[0] - A*row_offset[1]
    #   c) combine
    #       --> calculate out how many rows/cols it takes to fill the given
    #           supershape ratio with shape count
    #           start: r * c = shape_count
    #           end: r = sqrt(shape_count * rows_per_col)
    #                c = shapes / r
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # provide defaults
    ss = supershape  # for brevity
    complexity = complexity if complexity is not None else _DEFAULT_COMPLEXITY
    # a) edges
    edge_count = _BASE_EDGES * complexity
    edge_count = float(edge_count) / ss.avg_edge_count()
    shape_count = float(edge_count) * 2.0 / ss.avg_edge_count()
    # b) aspect ratio --> grid ratio
    aspect = aspect or 2.0 / (1 + math.sqrt(5))  # default golden rect
    aspect = float(aspect)
    y_offset_per_col = ss.graph_offset_per_col()[0]
    x_offset_per_col = ss.graph_offset_per_col()[1]
    y_offset_per_row = ss.graph_offset_per_row()[0]
    x_offset_per_row = ss.graph_offset_per_row()[1]
    rows_per_col = ((aspect * x_offset_per_col - y_offset_per_col)
                    / (y_offset_per_row - aspect * x_offset_per_row))
    # c) combine everything
    rows = (shape_count * rows_per_col) ** 0.5
    cols = float(shape_count) / rows
    rows = int(round(rows))
    cols = int(round(cols))
    return rows, cols


def _source_image_to_grid_image(source, supershape,
                                complexity=None, aspect=None):
    """Convert the image to 0/1 and produce shapes to fill zero regions."""
    # get some fundamental data
    source_w, source_h = source.size
    ref_length = supershape.reference_length()  # not needed? feels like it is
    ss = supershape  # for brevity
    complexity = complexity if complexity is not None else _DEFAULT_COMPLEXITY
    # setup base translation factors
    # a) b) c) etc. below - calculate scale, skew before changing anything

    # a) calculate skew due to shapes that are not tiled perfectly vert/horiz
    x_skew = ss.graph_offset_per_row()[1]
    y_skew = ss.graph_offset_per_col()[0]

    # b) calculate all adjustments due to aspect changes
    #    1) shape: e.g. Hexagon is wider than it is tall so the grid must be
    #       compressed horizontally / expanded vertically
    #    2) either match source image (no change) or use aspect argument
    source_aspect = float(source_h) / source_w
    shape_aspect = (float(ss.graph_offset_per_row()[0])
                    / ss.graph_offset_per_col()[1])
    target_aspect = float(aspect or source_aspect)  # default is source aspect
    grid_aspect = target_aspect / shape_aspect

    # c) calculate how to scale the target aspect to fit the desired number of
    #    shapes. This is an important step to having normalized complexity
    #    for any shape, aspect, etc.
    #    note: the 2.0 factor accounts for grid internal edges being shared
    edge_count = _BASE_EDGES * complexity  # total edges
    shape_count = float(edge_count) * 2.0 / ss.avg_edge_count()
    grid_h = int(round((shape_count * grid_aspect)**0.5 + y_skew))
    grid_w = int(round((float(shape_count) / grid_aspect)**0.5 + x_skew))

    # 1st operation - affine skew before resizing (usually shrinking)
    # PIL affine transformation parameter notes (a, b, c, d, e, f):
    # a-xscale (.5 is double, 2 is half)
    # b-xskew (negative 1.0 swings the bottom right full width)
    # c-xtranslate
    # d-yskew (negative 1.0 swings the rigth down full height)
    # e-yscale (.5 is double)
    # f-ytranslate
    skew_only_coeffs = (1.0, x_skew, 0.0, y_skew, 1.0, 0.0)
    skewed_h = int(round(source_h + abs(y_skew)))
    skewed_w = int(round(source_w + abs(x_skew)))
    # have to invert before/after transform since it fills with black
    skewed = PIL.ImageOps.invert(source)
    skewed = skewed.transform((skewed_w, skewed_h), PIL.Image.AFFINE,
                              skew_only_coeffs, PIL.Image.BICUBIC)
    skewed = PIL.ImageOps.invert(skewed)  # undo the inversion
    # 2nd Operation: perform combined scaling
    final = skewed.resize((grid_w, grid_h), PIL.Image.ANTIALIAS)

    # convert to black/white with tweakable threshold

    white_threshold = 128  # tweakable
    final = final.point(lambda i: 255 * (i > white_threshold))
    bilevel = '1'
    final = final.convert(bilevel)
    return final


def _string_image(string, font_path=None):
    """Return a grayscale image with black characters on a white background."""
    # setup common parts
    black = 0
    white = 255
#    bilevel_image_type = '1'
    grayscale = 'L'
    large = 1000
    height = 1400  # presumably large enough for any font @ large size
    width = int(round(height * 0.8 * len(string)))
    # make the background
    image = PIL.Image.new(grayscale, (width, height), color=white)
    # draw the text
    draw = PIL.ImageDraw.Draw(image)
    # choose a font
    font_priority = list()
    if font_path:
        # if font path was provided, it might work in three ways
        # 1) path completely defines location of a font
        # 2) just a file name works for a font in the current working directory
        # 3) just a file name works for a font somewhere in the system path
        font_priority.append(font_path)
    #todo: how to list this font for linux? windows automatically looks in fonts
    # always try the default font last
    font_priority.append(_DEFAULT_FONT)
    for font_path in font_priority:
        try:
            font = PIL.ImageFont.truetype(font_path, size=large)
            break  # break when a font works
        except IOError:
            pass
    else:
        # nothing worked. give up and use whatever PIL decides
        font = None
        print 'Unable to find custom or standard font. Using default.'
    draw.text((10, 10), string, fill=black, font=font)
    # isolate the text
    c_box = PIL.ImageOps.invert(image).getbbox()
    image = image.crop(c_box)
    return image


if __name__ == '__main__':
    pass
