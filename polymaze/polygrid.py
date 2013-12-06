# coding=utf-8
import math
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
_PIXEL_ON = 0  # PIL color value to indicate a shape should be used (black)
_PIXEL_OFF = 255  # PIL color value to indicate a shape is off (white)


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
        # make sure default has a value
        aspect = float(kwargs.pop('aspect', None)
                       or 2.0 / (1 + math.sqrt(5)))  # default golden rect
        # get an exact-aspect ratio and roughly-accurate size rectangle
        rough_ss_edgecount = float(self._supershape.avg_edge_count()) / 2.0
        rough_complexity = kwargs.get('complexity') or _DEFAULT_COMPLEXITY
        rough_edge_count = _BASE_EDGES * rough_complexity  # total edges
        rough_shape_count = float(rough_edge_count) * 2.0 / rough_ss_edgecount
        rough_h = int(round((rough_shape_count * aspect)**0.5))
        rough_w = int(round((float(rough_shape_count) / aspect)**0.5))
        rectangle_image = PIL.Image.new('L', (rough_w, rough_h),
                                        color=_PIXEL_ON)
        self.create_from_image(rectangle_image, **kwargs)

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
    grayscale = 'L'
    large = 1000
    height = 1400  # presumably large enough for any font @ large size
    width = int(round(height * 0.8 * len(string)))
    # make the background
    image = PIL.Image.new(grayscale, (width, height), color=_PIXEL_OFF)
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
    draw.text((10, 10), string, fill=_PIXEL_ON, font=font)
    # isolate the text
    c_box = PIL.ImageOps.invert(image).getbbox()
    image = image.crop(c_box)
    return image


if __name__ == '__main__':
    pass
