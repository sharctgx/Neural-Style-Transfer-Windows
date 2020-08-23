from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import argparse
from PIL import Image

# from scipy.misc import imread, imresize, imsave, fromimage, toimage

parser = argparse.ArgumentParser(description='Dummy parser.')
parser.add_argument('base_image_path', metavar='base', type=str,
                    help='Path to the image to transform.')

parser.add_argument('style_image_path', metavar='ref', type=str,
                    help='Path to the style reference image.')

parser.add_argument('result_path', metavar='res', type=str,
                    help='Prefix for the saved results.')

args = parser.parse_args()
base_path = args.base_image_path
style_path = args.style_image_path
result_path = args.result_path

def merge_two_images(first_image, second_image):
    assert (first_image.width, first_image.height) == (second_image.width, second_image.height)
    width = first_image.width
    height = first_image.height
    img_merge = Image.new(first_image.mode, (width * 2, height))
    img_merge.paste(first_image, (0, 0))
    img_merge.paste(second_image, (width, 0))
    return img_merge


base_image = Image.open(base_path)
style_image = Image.open(style_path)

result_image = merge_two_images(base_image, style_image)
result_image.save(result_path)

