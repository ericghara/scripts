#!/bin/python3

from PIL import Image
import glob
from typing import *
import numpy as np
import os.path
import subprocess

IGNORE = []

class KeyedImage(NamedTuple):
    key: str
    img: 'Image.Image' 

def load_files(path: str) -> List['np.array']:
    keyed_frames = list()
    for f in glob.glob("./*.png"):
        f_name = os.path.basename(f)
        if f_name in IGNORE:
            continue
        pil_img = Image.open(f)
        pil_img = pil_img.crop((240,0,1680,1080)).resize((800,600))
        keyed_frames.append(KeyedImage(key=f_name, img=pil_img))
    keyed_frames.sort(key=lambda x: x.key)
    return [frame.img for frame in keyed_frames]


def dump_vid(path: str) -> None:
    subprocess.run(["ffmpeg", "-i", path, "-vf", "fps=10", "thumb%04d.png"])

if __name__ == '__main__':
    #dump_vid("./vid.mp4")
    ims = load_files('./')
    durations = [250]*len(ims)
    print(f"Found: {len(ims)} images.")
    handle = ims[0]
    handle.save(fp="exploit.gif", format='GIF', append_images=ims[0:-1],
                save_all=True, duration=durations, loop=0)
