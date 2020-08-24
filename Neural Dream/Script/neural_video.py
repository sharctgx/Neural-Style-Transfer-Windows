from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import argparse
import sys
import cv2 as cv
import os
import subprocess

FRAME_PREFIX_BASE = "base"
FRAME_PREFIX_STYLE = "style"
FRAME_PREFIX_OUTPUT = "output"


def get_frame_path(folder, count, frame_prefix, frame_postfix = "", ext = "jpg"):
    return os.path.join(folder, f"{frame_prefix}_{count}{frame_postfix}.{ext}")


parser = argparse.ArgumentParser(description='Neural style transfer with Keras.')
parser.add_argument('base_video_path', metavar='base', type=str,
                    help='Path to the video to transform.')

parser.add_argument('style_video_path', metavar='ref', type=str,
                    help='Path to the style reference video.')

parser.add_argument('result_path', metavar='res_path', type=str,
                    help='Path for the saved results.')

parser.add_argument("network_path", metavar="network_path", type=str,
                    help="Path for the network script")

parser.add_argument("--style_masks", type=str, default=None, nargs='+',
                    help='Masks for style images')

parser.add_argument("--content_mask", type=str, default=None,
                    help='Masks for the content image')

parser.add_argument("--color_mask", type=str, default=None,
                    help='Mask for color preservation')

parser.add_argument("--image_size", dest="img_size", default=400, type=int,
                    help='Minimum image size')

parser.add_argument("--content_weight", dest="content_weight", default=0.025, type=float,
                    help="Weight of content")

parser.add_argument("--style_weight", dest="style_weight", nargs='+', default=[1], type=float,
                    help="Weight of style, can be multiple for multiple styles")

parser.add_argument("--style_scale", dest="style_scale", default=1.0, type=float,
                    help="Scale the weighing of the style")

parser.add_argument("--total_variation_weight", dest="tv_weight", default=8.5e-5, type=float,
                    help="Total Variation weight")

parser.add_argument("--num_iter", dest="num_iter", default=10, type=int,
                    help="Number of iterations")

parser.add_argument("--model", default="vgg16", type=str,
                    help="Choices are 'vgg16' and 'vgg19'")

parser.add_argument("--content_loss_type", default=0, type=int,
                    help='Can be one of 0, 1 or 2. Readme contains the required information of each mode.')

parser.add_argument("--rescale_image", dest="rescale_image", default="False", type=str,
                    help="Rescale image after execution to original dimentions")

parser.add_argument("--rescale_method", dest="rescale_method", default="bilinear", type=str,
                    help="Rescale image algorithm")

parser.add_argument("--maintain_aspect_ratio", dest="maintain_aspect_ratio", default="True", type=str,
                    help="Maintain aspect ratio of loaded images")

parser.add_argument("--content_layer", dest="content_layer", default="conv5_2", type=str,
                    help="Content layer used for content loss.")

parser.add_argument("--init_image", dest="init_image", default="content", type=str,
                    help="Initial image used to generate the final image. Options are 'content', 'noise', or 'gray'")

parser.add_argument("--pool_type", dest="pool", default="max", type=str,
                    help='Pooling type. Can be "ave" for average pooling or "max" for max pooling')

parser.add_argument('--preserve_color', dest='color', default="False", type=str,
                    help='Preserve original color in image')

parser.add_argument('--min_improvement', default=0.0, type=float,
                    help='Defines minimum improvement required to continue script')

rest_args = sys.argv[5:]

args = parser.parse_args()
base_video_path = args.base_video_path
style_video_path = args.style_video_path
result_path = args.result_path

folder_for_frames = "media"   # TODO: add temp folder as an argument

if os.path.exists(folder_for_frames):
    for f in os.listdir(folder_for_frames):
        os.remove(os.path.join(folder_for_frames, f))
else:
    os.mkdir(folder_for_frames)


def video_to_frames(video_path, folder_for_frames, frame_prefix):
    global success, image, count
    vidcap = cv.VideoCapture(video_path)
    success, image = vidcap.read()
    count = 0
    while success:
        frame_path = get_frame_path(folder_for_frames, count, frame_prefix)
        cv.imwrite(frame_path, image)  # save frame as JPEG file
        count += 1
        success, image = vidcap.read()

    return count


base_frames_count = video_to_frames(base_video_path, folder_for_frames, FRAME_PREFIX_BASE)
style_frames_count = video_to_frames(style_video_path, folder_for_frames, FRAME_PREFIX_STYLE)

print(f"base frames: {base_frames_count}, style frames: {style_frames_count}")

for i in range(base_frames_count):
    python_name = "python3"
    network_path = args.network_path
    base_frame = get_frame_path(folder_for_frames, i, FRAME_PREFIX_BASE)
    style_frame = get_frame_path(folder_for_frames, i % style_frames_count, FRAME_PREFIX_STYLE)
    print(f"Processing frame {i} from {base_frames_count}\n")
    subprocess.call([python_name, network_path, base_frame, style_frame,
                     os.path.join(folder_for_frames, f"{FRAME_PREFIX_OUTPUT}_{i}")]
                    + rest_args)

# Determine the width and height from the first image
image = get_frame_path(folder_for_frames, 0, FRAME_PREFIX_OUTPUT, f"_at_iteration_{args.num_iter}", "png")
print(f"Looking for {image}\n")
frame = cv.imread(image)
height, width, channels = frame.shape

# Define the codec and create VideoWriter object
fourcc = cv.VideoWriter_fourcc(*'mp4v')  # Be sure to use lower case
out = cv.VideoWriter(result_path, fourcc, 20.0, (width, height))

count = 0

while os.path.exists(image):
    frame = cv.imread(image)
    out.write(frame)  # Write out frame to video
    count += 1
    image = get_frame_path(folder_for_frames, count, FRAME_PREFIX_OUTPUT, f"_at_iteration_{args.num_iter}", "png")

# Release everything if job is finished
out.release()
cv.destroyAllWindows()
