# -*- coding: future_fstrings -*-
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import argparse
import sys
import cv2 as cv
import os
import subprocess
import shutil

FRAME_PREFIX_BASE = "base"
FRAME_PREFIX_STYLE = "style"
FRAME_PREFIX_OUTPUT = "output"


def get_frame_path(folder, count, frame_prefix):
    return os.path.join(folder, f"{frame_prefix}{count}.jpg")


parser = argparse.ArgumentParser(description='Neural style transfer with Keras.')
parser.add_argument('base_video_path', metavar='base', type=str,
                    help='Path to the video to transform.')

parser.add_argument('style_video_path', metavar='ref', type=str,
                    help='Path to the style reference video.')

parser.add_argument('result_path', metavar='res_path', type=str,
                    help='Path for the saved results.')

rest_args = sys.argv[4:]  # TODO: use it later for a real neural network

args = parser.parse_args()
base_video_path = args.base_video_path
style_video_path = args.style_video_path
result_path = args.result_path

folder_for_frames = "../../media"

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

for i in range(min(base_frames_count, style_frames_count)):
    python_name = "python3"
    network_path = "Dummy.py"
    base_frame = get_frame_path(folder_for_frames, i, FRAME_PREFIX_BASE)
    style_frame = get_frame_path(folder_for_frames, i, FRAME_PREFIX_STYLE)
    output_frame = get_frame_path(folder_for_frames, i, FRAME_PREFIX_OUTPUT)

    subprocess.call([python_name, network_path, base_frame, style_frame, output_frame])

# Determine the width and height from the first image
image = os.path.join(folder_for_frames, get_frame_path(folder_for_frames, 0, FRAME_PREFIX_OUTPUT))
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
    image = get_frame_path(folder_for_frames, count, FRAME_PREFIX_OUTPUT)

# Release everything if job is finished
out.release()
cv.destroyAllWindows()

shutil.rmtree(folder_for_frames)
