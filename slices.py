#!/usr/bin/python


import argparse
import copy
import os
from random import shuffle

from PIL import Image


def main():
    parser = get_argparser()
    args = parser.parse_args()
    image = Image.open(os.path.expanduser(args.img))
    num_of_slices = int(args.slices)
    chop_size = image.size[0] / num_of_slices

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