#!/usr/bin/env python3

r"""
usage: sponge.py [--h]

read all of Stdin, echo its Eof into Stderr, write it all to Stdout

options:
  --help  show this help message and exit

quirks:
  Linux Terminal Stdin echoes ⌃D EOF as "" without "\n", vs macOS as "^D" without "\n"
  GShell comes with 'sponge' defined, as if by:  apt install moreutils

examples:
  cat |sponge.py --  &&: let you finish typing, and press ⌃D EOF, before echoing it all
  sponge.py --  &&: same effect
  echo $'\xC0\x80' |sponge.py -- |hexdump -C  &&: forward UnicodeDecodeError accurately
"""


import sys

import byotools as byo


def main():

    # Parse the Command Line

    parms = sys.argv[1:]
    if parms != "--".split():

        byo.exit()

    # Read all of Stdin, echo its Eof into Stderr, write it all to Stdout

    isatty = sys.stdin.isatty()
    if isatty:
        sys.stderr.write("sponge.py: Press ⌃D EOF to quit\n")

    in_bytes = sys.stdin.buffer.read()

    if isatty:
        sys.stderr.write("\n")
        sys.stderr.flush()

    sys.stdout.buffer.write(in_bytes)


if __name__ == "__main__":
    main()


# posted into:  https://github.com/pelavarre/byobash/blob/main/bin/sponge.py
# copied from:  git clone https://github.com/pelavarre/byobash.git
