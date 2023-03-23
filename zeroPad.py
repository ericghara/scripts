import os
import math
import re
import sys

from typing import *
from os.path import isfile, join, isdir

"""
This script renames FILES which begin with a numeric character and have a following space to 0 padded filenames (i.e. "1 filename.pdf" -> "01 filename.pdf")

Usage:

zeroPad.py [optional PATH] [optional NUM_DIGITS]

default PATH = .
default NUM_DIGITS = 2

1) python3 zeroPad.py
    * PATH: ., NUM_DIGITS: 2
    
2) python3 zeroPad.py ~/test
    * PATH: ~/test, NUM_DIGITS: 2
    
3) python3 zeroPad.py ~/test 3
    * PATH: ~/test, NUM_DIGITS: 3

Verbose Example:
$ ls -A1
> 1 a
> 02 b
> c
$ python3 zeroPad.py . 3
> {status output}
$ ls -A1
> 001 a
> 002 b
> c
"""


def getNewFilename(filename: str, numDigits: int = 2) -> Optional[str]:
    fSplit = re.split(r"\s", filename, 1)
    if (len(fSplit) < 2 or not fSplit[0].isnumeric()):
        return None
    num = int(fSplit[0])
    if num >= math.pow(10, numDigits):
        raise ValueError(
            f"NumDigits: {numDigits} too small for {num}.  Perhaps you'd like to increase the numDigits argument?")
    paddedStr = f"{{:0{str(numDigits)}d}}".format(num)
    return f"{paddedStr} {fSplit[1]}"


def parseArgs() -> Tuple[str, int]:
    args = sys.argv[1:]  # first arg is zeroPad.py
    path = "." if len(args) == 0 else args[0]
    numDigits = "2" if len(args) < 2 else args[1]

    if (len(args) > 2):
        raise ValueError(
            "Arguments should be path to dir, followed by optional num digits for padding (2 if none provided)")

    if not isdir(path):
        raise ValueError(f"{path} is not a directory")

    if not numDigits.isnumeric():
        raise ValueError(f"Second arg should be number of digits padding, found {numDigits}")

    return path, int(numDigits)


def renameFiles(path: str, numDigits: int) -> None:
    for f in os.listdir(path):
        source = join(path, f)
        if not isfile(source):
            print(f"- Skipping: {source} - not a file.")
            continue
        if not (newName := getNewFilename(f, numDigits)):
            print(f"- Skipping file {source} - doesn't match pattern.")
        else:
            dest = join(path, newName)
            print(f"* Renaming {source} to {dest}")
            os.rename(source, dest)


if __name__ == "__main__":
    path, numDigits = parseArgs()
    renameFiles(path, numDigits)
