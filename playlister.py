#!/bin/python3

from pathlib import Path, PurePath
from typing import *
import argparse

def number_priority_fn(file: str) -> int:
    return int(file.split(" ")[0])

def create_playlist(dir: PurePath, priority_names: List[Tuple[int, str]]) -> None:
    p = dir.joinpath(f"{dir.name}.m3u")
    with open(p,"w") as f:
        print("#EXTM3U", file=f)
        for priority, name in priority_names:
            print(name, file=f)
    print(p)


def create(start_dir: str, extension: str, priority_fn: Callable[[str], int]):
    query = f"**/*.{extension}"
    dirs = dict()
    for p in Path(start_dir).glob(query):
        pp = PurePath(p)
        dir = pp.parent
        file = pp.name
        try:
            priority = priority_fn(file)    
        except:
            print(f"Unparsable: {p}")
            priority = float('inf')
        dirs.setdefault(dir, list()).append((priority, file))

    for dir, files in dirs.items():
        files.sort(key=lambda e: e[0])
        create_playlist(dir, files)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="playlister",
        description="make ordered playlists"
    )
    parser.add_argument("-d", "--dir", type=str, help="dir to recursively search from", default=".")
    parser.add_argument("-e", "--extension", type=str, help="extension to add to playlist", default="mp4")
    
    args = parser.parse_args()

    create(start_dir=args.dir, extension=args.extension, priority_fn=number_priority_fn)
