#!/usr/bin/env python3

# stty -a
# stty -ixon
# stty ixon
#
# stty cols 89  # and you can lie
# stty rows 50  # and you can lie
#
# echo -n $'\e[8;'$(stty size |cut -d' ' -f1)';101t'  &&: 'one-hundred one (101) cols'
# echo -n $'\e[8;'$(stty size |cut -d' ' -f1)';89t'  &&: 'eighty-nine (89) cols'
#
# echo -n $'\e[8;50;89t'  # revert Terminal to a familiar Window Size

"""
usage: todo

todo

options:
  --help       show this help message and exit

examples:
  :
"""


import byotools as byo


if __name__ == "__main__":

    byo.exit()


# copied from:  git clone https://github.com/pelavarre/byobash.git
