#!/usr/bin/env python3

r"""
usage: clear.py [--h] [-x]

wipe the Screen, delete the Scrollback, leave the Cursor at Top Left

options:
  --help  show this help message and exit
  -x      do Not delete the Scrollback, just scroll the Rows of the Screen up into it

quirks:
  at GShell: ignores ⌘K, ignores \e[3J in default TMux, and ⌃L deletes Rows on Screen

examples:

  clear.py --  &&: delete Scrollback, like ⌘K at Mac of Mac or Linux

  echo -ne '\e[H\e[2J\e[3J'  &&: delete Scrollback, like ⌘K
  echo -ne '\e[3J\e[H\e[2J'  &&: keep one Screen, but blank that Screen if called twice
  echo -ne '\e[H\e[2J'  &&: scroll Screen away, but keep Scrollback, like ⌃L

  echo -ne '\e[8;'$(stty size | cut -d' ' -f1)';89t'  &&: 89 cols
  echo -ne '\e[8;'$(stty size | cut -d' ' -f1)';101t'  &&: 101 cols

  reset  &&: sleep 100ms and delete all Scrollback (but not from GShell TMux)

  echo && seq 40 && echo && seq 50 && echo && seq 60 && echo  &&: fill Screens for test

  clear 2>&1 |tee >(hexdump -C)  &&: call and trace Clear
  tput clear 2>&1 |tee >(hexdump -C)  &&: call and trace TPut Clear
  diff -u <(clear |hexdump -C) <(tput clear |hexdump -C)  &&: commonly no difference
  reset 2>&1 |tee >(hexdump -C)  &&: call and trace Reset, at Linux
"""
# todo: find a Clear or Reset that deletes Scrollback, inside GShell default TMux
# todo: call and trace Reset, at Mac


import sys

import byotools as byo


def main():

    parms = sys.argv[1:]
    if parms != "--".split():

        byo.exit()

    esc = "\x1B"
    print(r"\e[H\e[2J\e[3J".replace(r"\e", esc), end="")


if __name__ == "__main__":
    main()


# copied from:  git clone https://github.com/pelavarre/byobash.git
