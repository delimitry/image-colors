#!/usr/bin/env python
# coding: utf-8
# -----------------------------------------------------------------------
# Author: delimitry
# -----------------------------------------------------------------------

import math
import os
import traceback
from argparse import ArgumentParser
from operator import itemgetter
from PIL import Image


class ImageColorsInfo(object):
    """Get color information from an image"""

    def __init__(self, filename):
        self.image = Image.open(filename)
        self.pixels = self.image.load()

    def get_image_colors_frequency_sorted(self, reduce_val=1):
        """Get colors frequency sorted in descending order"""
        try:
            width, height = self.image.size
            colors = {}
            for y in range(height):
                for x in range(width):
                    color_init = self.pixels[x, y]
                    # reduce similar colors
                    color = (
                        int((color_init[0] / reduce_val) * reduce_val),
                        int((color_init[1] / reduce_val) * reduce_val),
                        int((color_init[2] / reduce_val) * reduce_val),
                    )
                    colors[color] = colors.get(color, 0) + 1
            sorted_colors = sorted(colors.items(), key=itemgetter(1), reverse=True)
            return sorted_colors
        except Exception:
            traceback.print_exc()
        return []

    def get_rgb_info(self):
        """Get RGB info"""
        all_colors = (0, 0, 0)
        width, height = self.image.size
        for y in range(height):
            for x in range(width):
                color = self.pixels[x, y]
                all_colors = (all_colors[0] + color[0], all_colors[1] + color[1], all_colors[2] + color[2])
        return all_colors

    def save_top_n_colors_to_html_file(self, filename, top_number, reduce_val=1):
        """Save top number of colors-freq to HTML file"""
        try:
            number = top_number
            sorted_colors = self.get_image_colors_frequency_sorted(reduce_val)

            out = ''
            out += '<p>Top {} colors:</p>'.format(number)
            out += '<table>\n'
            out += '<tr style="text-align: center">\n'
            out += '<td>Color</td>\n'
            out += '<td>Frequency</td>\n'
            out += '</tr>\n'
            for d in sorted_colors[:number]:
                color = d[0]
                frequency = d[1]
                hex_color = (color[0] << 16) + (color[1] << 8) + color[2]
                out += '<tr>\n'
                out += '<td bgcolor="#{:06x}"></td>'.format(hex_color)
                out += '<td>{}</td>'.format(frequency)
                out += '</tr>\n'
            out += '</table>\n'

            data = '<html>\n<body style="font-family: Arial">{}\n</body>\n</html>'.format(out)
            with open(filename, 'w') as f:
                f.write(data)

        except Exception:
            traceback.print_exc()

    def save_average_to_html_file(self, filename, divider_ratio):
        """Save image divided to size divider_ratio x divider_ratio with average color to HTML file"""
        try:
            if divider_ratio <= 0:
                print('Divider value must be >= 0')
                return
            if divider_ratio > min(self.image.size):
                divider_ratio = min(self.image.size)
            div_ratio = divider_ratio
            width, height = self.image.size
            nwidth = width / float(div_ratio)
            nheight = height / float(div_ratio)
            # pixels_in_nrect = nwidth * nheight
            average_pixels = {}
            for ny in range(div_ratio):
                for nx in range(div_ratio):
                    average_color = self.__get_average_color_from_rect(
                        int(nx * nwidth), int(ny * nheight), int(math.ceil(nwidth)), int(math.ceil(nheight)))
                    average_pixels[(nx, ny)] = average_color

            out = ''
            out += '<table>\n'
            for iy in range(div_ratio):
                out += '<tr height="{}">\n'.format(nheight)
                for ix in range(div_ratio):
                    color = average_pixels[ix, iy]
                    hex_color = (color[0] << 16) + (color[1] << 8) + color[2]
                    out += '<td width="{}" bgcolor="#{:06x}" ></td>'.format(nwidth, hex_color)
                out += '</tr>\n'
            out += '</table>\n'

            data = '<html>\n<body style="font-family: Arial">{}\n</body>\n</html>'.format(out)
            with open(filename, 'w') as f:
                f.write(data)

        except Exception:
            traceback.print_exc()

    def __get_average_color_from_rect(self, x, y, width, height):
        """Get average color from pixels in specified rect (x,y,x+width,y+height)"""
        pixels_in_rect = width * height
        if not pixels_in_rect:
            pixels_in_rect = 1
        sum_color = (0, 0, 0)
        for iy in range(y, y + height):
            for ix in range(x, x + width):
                color = self.pixels[ix, iy]
                sum_color = (sum_color[0] + color[0], sum_color[1] + color[1], sum_color[2] + color[2])
        average_color = (
            int(sum_color[0] / pixels_in_rect) & 255,
            int(sum_color[1] / pixels_in_rect) & 255,
            int(sum_color[2] / pixels_in_rect) & 255,
        )
        return average_color


def main():
    # prepare arguments parser
    parser = ArgumentParser(description='Image colors information')
    parser.add_argument('-i', '--input', dest='input', help='image filename')
    parser.add_argument('-o', '--output', dest='output', help='output directory (by default current one)', default='./')
    parser.add_argument('-d', '--divider', dest='divider', help='value to divide image to blocks', type=int, default=8)
    parser.add_argument('-t', '--top_colors', dest='top_colors', help='top N colors in image', type=int, default=20)
    parser.add_argument('-r', '--reduce_val', dest='reduce_val', help='color reduce value', type=int, default=32)

    args = parser.parse_args()
    if not args.input:
        parser.print_help()
        exit(1)

    if not os.path.isfile(args.input):
        exit('File "{}" is not found!'.format(args.input))

    if args.divider <= 0:
        exit('Divider value must be >= 0!')

    image_colors_info = ImageColorsInfo(args.input)
    colors = image_colors_info.get_rgb_info()
    print('Total RGB info:')
    print('R sum: {}'.format(colors[0]))
    print('G sum: {}'.format(colors[1]))
    print('B sum: {}'.format(colors[2]))

    output_folder = '.'
    if args.output:
        output_folder = args.output
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

    # get top colors, with reduce
    image_colors_info.save_top_n_colors_to_html_file(
        os.path.join(output_folder, 'top_colors.html'), args.top_colors, reduce_val=args.reduce_val)
    # image divided into blocks with average colors
    image_colors_info.save_average_to_html_file(os.path.join(output_folder, 'average_colors.html'), args.divider)


if __name__ == '__main__':
    main()
