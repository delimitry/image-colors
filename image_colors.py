#!/usr/bin/env python
#-*- coding:utf-8 -*-
#----------------------------------------------------------------------- 
# Author: delimitry
#-----------------------------------------------------------------------

from operator import itemgetter
from PIL import Image

class ImageColorsInfo:
  '''Get color information from an image'''

	def __init__(self, filename):
		self.image = Image.open(filename)
		self.pixels = self.image.load()

	def get_image_colors_frequency_sorted(self, reduce_val=1):
		'''Get colors frequency sorted in descending order'''
		try:
			rval = reduce_val
			width, height = self.image.size		
			colors = {}			
			for y in xrange(height):
				for x in xrange(width):
					color_init = self.pixels[x, y]
					# reduce similar colors
					color = ((color_init[0] / rval) * rval, (color_init[1] / rval) * rval, (color_init[2] / rval) * rval)
					colors[color] = colors.get(color, 0) + 1					
			sorted_colors = sorted(colors.items(), key=itemgetter(1), reverse=True)
			return sorted_colors
		except Exception, ex:
			print ex

	def get_rgb_info(self):
		'''Get RGB info'''
		all_colors = (0, 0, 0)
		width, height = self.image.size
		for y in xrange(height):
			for x in xrange(width):
				color = self.pixels[x, y]
				all_colors = (all_colors[0] + color[0], all_colors[1] + color[1], all_colors[2] + color[2])
		return all_colors
		
	def save_top_n_colors_to_html_file(self, filename, top_number, reduce_val=1):
		'''Save top number of colors-freq to HTML file'''
		try:
			number = top_number
			sorted_colors = self.get_image_colors_frequency_sorted(reduce_val)

			out = ''
			out += '<p>Top %d colors:</p>' % (number)
			out += '<table>\n'
			out += '<tr style="text-align: center">\n'
			out += '<td>Color</td>\n'
			out += '<td>Frequency</td>\n'		
			out += '</tr>\n'		
			for d in sorted_colors[:number]:
				color = d[0]
				frequency = d[1]
				hex_color = hex(color[0] * 256 * 256 + color[1] * 256 + color[2])[2:]
				out += '<tr>\n'
				out += '<td bgcolor="#%s"></td>' % (hex_color)
				out += '<td>%d</td>' % (frequency)
				out += '</tr>\n'
			out += '</table>\n'
			data = '<html>\n<body style="font-family: Arial">%s\n</body>\n</html>' % (out)

			f = open(filename, 'w')
			f.write(data)
			f.close()

		except Exception, ex:
			print ex

	def save_average_to_html_file(self, filename, divider_ratio):
		'''Save image divided to size divider_ratio x divider_ratio with average color to HTML file'''
		try:
			div_ratio = divider_ratio
			width, height = self.image.size	
			nwidth = width / div_ratio
			nheight = height / div_ratio
			pixels_in_nrect = nwidth * nheight

			average_pixels = {}
			for ny in xrange(div_ratio):
				for nx in xrange(div_ratio):				
					average_pixels[(nx, ny)] = self.__get_average_color_from_rect(self.pixels, nx * nwidth, ny * nheight, nwidth, nheight)

			out = ''
			out += '<table>\n'
			for iy in xrange(div_ratio):
				out += '<tr  height="%d">\n' % (nheight)
				for ix in xrange(div_ratio):
					color = average_pixels[ix, iy]
					hex_color = hex(color[0] * 256 * 256 + color[1] * 256 + color[2])[2:]
					out += '<td width="%d" bgcolor="#%s" ></td>' % (nwidth, hex_color)
				out += '</tr>\n'
			out += '</table>\n'

			data = '<html>\n<body style="font-family: Arial">%s\n</body>\n</html>' % (out)
			
			f = open(filename, 'w')
			f.write(data)
			f.close()

		except Exception, ex:
			print ex

	def __get_average_color_from_rect(self, pixels, x, y, width, height):
		'''Get average color from pixels in specified rect (x,y,x+width,y+height)'''
		pixels_in_rect = width * height
		sum_color = (0, 0, 0)
		for iy in xrange(y, y + height):
			for ix in xrange(x, x + width):
				color = pixels[ix, iy]
				sum_color = (sum_color[0] + color[0], sum_color[1] + color[1], sum_color[2] + color[2])
		average_color = ((sum_color[0] / pixels_in_rect) % 255, (sum_color[1] / pixels_in_rect) % 255, (sum_color[2] / pixels_in_rect) % 255) 
		return average_color

def main():
	image_colors_info = ImageColorsInfo('image.png')
	c = image_colors_info.get_rgb_info()
	print 'Total RGB info:'
	print 'R: %d' % (c[0])
	print 'G: %d' % (c[1])
	print 'B: %d' % (c[2])

	image_colors_info.save_top_n_colors_to_html_file('top_colors.html', 20, reduce_val=32) # get top 20 colors, with reduce 32
	image_colors_info.save_average_to_html_file('average_colors.html', 10) # image as 8 x 8 of average colors


if __name__ == '__main__':
	main()
