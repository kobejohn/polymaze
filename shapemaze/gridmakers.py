import os
import random

import PIL.Image

import shapes as _shapes
import shapegrid as _shapegrid


_base_dir = os.path.dirname(__file__)
_content_dir = os.path.join(_base_dir, 'content')
_supershapes_dict = _shapes.supershapes_dict()


# todo: try with IMPACT font which should be common and http://stackoverflow.com/a/5430111/377366
#todo: from below code make a grid_from_textgrid

def rectangle(vertical_shapes=40, horizontal_shapes=80, supershape=None):
    # provide defaults
    supershape = supershape or random.choice(_supershapes_dict.values())
    # create a grid
    grid = _shapegrid.ShapeGrid(supershape)
    for row in range(vertical_shapes):
        for col in range(horizontal_shapes):
            index = (row, col)
            grid.create(index)
    return grid


        #if text_map:
        #    for row, text_row in enumerate(text_map.splitlines()):
        #        for col, char in enumerate(text_row):
        #            if char == '#':
        #                self._grid.create((row, col))
        #elif vertical_shapes and horizontal_shapes:


def character(c, max_vertical_indexes=None, max_horizontal_indexes=None,
              supershape=None,):
    # get a copy of the relevant image
    im = _character_images[c].copy()
    # provide defaults
    supershape = supershape or random.choice(_supershapes_dict.values())
    max_vertical_indexes = max_vertical_indexes or 50
    max_horizontal_indexes = max_horizontal_indexes or 30
    # shrink the image with aspect
    im.thumbnail((max_horizontal_indexes, max_vertical_indexes),
                 PIL.Image.ANTIALIAS)
    # convert to black/white
    im = im.convert('1')
    # get the pixels and build the grid based on each pixel's position and value
    pixels = im.load()
    grid = _shapegrid.ShapeGrid(supershape)
    width, height = im.size
    for y in range(height):
        for x in range(width):
            if not pixels[x, y]:
                grid.create((y, x))
    return grid


def _character_images():
    character_dir = os.path.join(_content_dir, 'letter_images')
    character_images = {}
    print character_dir
    for name in os.listdir(character_dir):
        full_path = os.path.join(character_dir, name)
        if name[-3:] == 'png':
            c = name[:1]
            im = PIL.Image.open(full_path)
            character_images[c] = im
    return character_images
_character_images = _character_images()


if __name__ == '__main__':
    pass
