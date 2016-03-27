#!/usr/bin/python


# Copyright (C) 2016 Shea G Craig <shea.craig@sas.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""Slice an image and randomly put it back together."""


import argparse
import copy
import os
from random import shuffle

# Using the pillow fork of PIL.
from PIL import Image


def main():
    parser = get_argparser()
    args = parser.parse_args()
    image = Image.open(os.path.expanduser(args.img))
    num_of_slices = int(args.slices)
    chop_size = int(round(image.size[0] / float(num_of_slices)))

    output_image = slice_image(image, num_of_slices, chop_size)

    if args.ofile:
        output_image.save(os.path.expanduser(args.ofile))
    else:
        output_image.show()


def get_argparser():
    desc = ("Slice an image and randomly put it back together; then display "
            "with default image viewer or save.")
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("img", help="Path to image to slice.")
    parser.add_argument("-s", "--slices", help="Number of slices to make. "
                        "Default is 30.", default=30)
    parser.add_argument("-o", "--ofile", help="Path to save image.")
    return parser


def slice_image(image, num_of_slices, chop_size):
    indices = [x for x in xrange(num_of_slices)]
    offsets = copy.copy(indices)
    shuffle(offsets)
    slices = zip(indices, offsets)
    # Copy the original image for output; this is a sloppy way of
    # filling the remainder of width / slices (integer division).
    output_image = image.copy()

    for index, offset in slices:
        cut_rect = get_slice(offset, chop_size, image.height)
        paste_rect = get_slice(index, chop_size, image.height)
        # Copy the source image each time, because crop _sometimes_
        # affects the original.
        output_image.paste(image.copy().crop(cut_rect), paste_rect)

    return output_image


def get_slice(x_offset, width, height):
    return (x_offset * width, 0, x_offset * width + width, height)


if __name__ == "__main__":
    main()