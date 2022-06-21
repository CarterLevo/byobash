#!/usr/bin/env python3

"""
usage: bash.py [--h] [--noprofile] [--norc] ...

shell out to a host

options:
  --help       show this help message and exit
  --noprofile  launch without running shared startup files
  --norc       launch without running personal startup files

examples:
  bash --noprofile --norc  &&: run with less local quirks
  export |grep SHLVL  &&: show how deeply incepted
  set |grep -e ^PS1= -e ^PS4=  &&: show the outer and incepted shell prompts
"""


import byotools as byo


if __name__ == "__main__":

    byo.exit()


# copied from:  git clone https://github.com/pelavarre/byobash.git
