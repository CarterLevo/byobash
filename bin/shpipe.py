#!/usr/bin/env python3

# FIXME: drop mention of Git
# FIXME: convert ',' to '|'

r"""
usage: shpipe.py [--help] PIPE_VERB [ARG ...]

compose a graph of pipes of shverb's

positional arguments:
  PIPE_VERB  choice of ShVerb
  ARG        choice of Options and Arguments

options:
  --help     show this help message and exit

quirks:
  dumps larger numbers of Lines into taller Screens, as defaults of:  head/tail -...
  Linux Terminal Stdin echoes ⌃D TTY EOF as "" w/out "\n", vs macOS as "^D" without "\n"

advanced bash install:

  source qb/env-path-append.source  &&: define 'c', 'cv', 'd', 'g', 'gi', and so on
  bash qb/env-path-append.source  &&: show how it works
  export PATH="${PATH:+$PATH:}~/Public/byobash/qb"  &&: get it done yourself

examples:

  shpipe.py  &&: show these examples and exit
  shpipe.py --h  &&: show this help message and exit
  shpipe.py --  &&: 'git status' and then counts of:   git status --short --ignored
  command shpipe.py --  &&: todo: run as you like it

  shpipe.py c  &&: cat -
  shpipe.py cv  &&: pbpaste, ...
  shpipe.py cv  &&: ... ,pbcopy
  shpipe.py cv  &&: ... ,tee >(pbcopy) ,...
  shpipe.py d  &&: diff -brpu A_FILE B_FILE  &&: default 'diff -brpu a b'
  shpipe.py e  &&: emacs -nw --no-splash --eval '(menu-bar-mode -1)'
  shpipe.py h  &&: head -16  &&: or whatever a third of a screen is
  shpipe.py hi  &&: history  &&: but include the files at the '~/.bash_histories/' dir
  shpipe.py m  &&: make
  shpipe.py mo  &&: less -FIRX
  shpipe.py n  &&: cat -tvn -, expand
  shpipe.py p  &&: popd
  shpipe.py s  &&: sort -
  shpipe.py sp  &&: sponge.py --
  shpipe.py t  &&: tail -16  &&: or whatever a third of a screen is
  shpipe.py u  &&: uniq -c -, expand
  shpipe.py v  &&: vim -
  shpipe.py w  &&: wc -l
  shpipe.py x  &&: hexdump -C
  shpipe.py xp  &&: expand
"""


import os
import pdb
import shlex
import subprocess
import sys

import byotools as byo

_ = pdb


def main():
    """Run from the Sh Command Line"""

    func_by_verb = form_func_by_verb()

    # Define some forms of 'shpipe.py'

    byo.exit_via_testdoc()  # shpipe.py
    byo.exit_via_argdoc()  # shpipe.py --help

    # Define many brutally cryptic abbreviations of ShVerb's

    parms = sys.argv[1:]
    shverb = parms[0] if parms else None

    main.prompter = None
    if shverb in func_by_verb.keys():
        func = func_by_verb[shverb]

        if hasattr(func, "prompter"):
            main.prompter = func.prompter

        func()  # these Func's mostly now exit here

    # Default to forward the Parms into a Git Subprocess

    byo.exit_via_shcommand()


#
# Wrap many many Shim's around Bash Pipe Filters
#


def form_func_by_verb():
    """Declare the Pipe Filter Abbreviations"""

    func_by_verb = dict(
        c=do_c,
        cv=do_cv,
        d=do_d,
        e=do_e,
        h=do_h,
        hi=do_hi,
        m=do_m,
        mo=do_mo,
        n=do_n,
        p=do_p,
        s=do_s,
        sp=do_sp,
        t=do_t,
        u=do_u,
        v=do_v,
        w=do_w,
        x=do_x,
        xp=do_xp,
    )

    do_c.prompter = True
    do_h.prompter = True
    do_mo.prompter = True
    do_n.prompter = True
    do_s.prompter = True
    do_sp.prompter = True
    do_t.prompter = True
    do_u.prompter = True
    do_w.prompter = True
    do_x.prompter = True
    do_xp.prompter = True

    return func_by_verb


def do_c():
    """cat -"""

    exit_via_shpipe_shproc("cat -")


def do_cv():
    """pbpaste from tty, pbcopy to tty, else tee to pbcopy"""

    stdin_isatty = sys.stdin.isatty()
    stdout_isatty = sys.stdout.isatty()

    if stdin_isatty and stdout_isatty:
        do_cv_tty()
    elif stdin_isatty:
        exit_via_shpipe_shproc("pbpaste")  # pbpaste |...
    elif stdout_isatty:
        exit_via_shpipe_shproc("pbcopy")  # ... |pbcopy
    else:
        exit_via_shpipe_shproc("tee >(pbcopy)")  # ... |tee >(pbcopy) |...


def do_cv_tty():
    """pbpaste |cat -n -etv |expand"""

    parms = sys.argv[2:]
    (options, seps, args) = byo.shlex_split_options(parms)

    if not options:
        options.append("-n")
        options.append("-etv")

    argv = ["cat"] + options + seps + args

    shline = " ".join(byo.shlex_min_quote(_) for _ in argv)
    shline = "pbpaste |{} |expand".format(shline)

    shshline = "bash -c '{}'".format(shline)

    exit_via_shline(shline=shshline)


def do_d():
    """diff -brpu a b"""

    parms = sys.argv[2:]
    (options, seps, args) = byo.shlex_split_options(parms)

    if not options:
        options.append("-brpu")
    if len(args) < 2:
        args.insert(0, "a")
    if len(args) < 2:
        args.append("b")

    argv = ["diff"] + options + seps + args
    shline = " ".join(byo.shlex_min_quote(_) for _ in argv)

    exit_via_shline(shline)


def do_e():
    """emacs -nw --no-splash --eval '(menu-bar-mode -1)'"""

    exit_via_shpipe_shproc("emacs -nw --no-splash --eval '(menu-bar-mode -1)'")


def do_h():
    """head -16"""

    parms = sys.argv[2:]
    (options, seps, args) = byo.shlex_split_options(parms)

    thirdrows = 16  # FIXME
    if not options:
        options.append("-{}".format(thirdrows))

    argv = ["head"] + options + seps + args
    shline = " ".join(byo.shlex_min_quote(_) for _ in argv)

    exit_via_shline(shline)


def do_hi():
    """history  &&: but include the files at the '~/.bash_histories/' dir"""


def do_m():
    """make"""

    exit_via_shpipe_shproc("make")


def do_mo():
    """less -FIRX"""

    exit_via_shpipe_shproc("less -FIRX")


def do_n():
    """cat -n -etv |expand"""

    parms = sys.argv[2:]
    (options, seps, args) = byo.shlex_split_options(parms)

    if not options:
        options.append("-n")
        options.append("-etv")

    argv = ["cat"] + options + seps + args

    shline = " ".join(byo.shlex_min_quote(_) for _ in argv)
    shline = "{} |expand".format(shline)

    shshline = "bash -c '{}'".format(shline)

    exit_via_shline(shline=shshline)


def do_p():
    """popd"""

    exit_via_shpipe_shproc("popd")


def do_s():
    """sort"""

    exit_via_shpipe_shproc("sort")


def do_sp():
    """sponge.py --"""

    exit_via_shpipe_shproc("sponge.py --")


def do_t():
    """tail -16"""

    parms = sys.argv[2:]
    (options, seps, args) = byo.shlex_split_options(parms)

    thirdrows = 16  # FIXME
    if not options:
        options.append("-{}".format(thirdrows))

    argv = ["tail"] + options + seps + args
    shline = " ".join(byo.shlex_min_quote(_) for _ in argv)

    exit_via_shline(shline)


def do_u():
    """uniq -c - |expand"""

    exit_via_shpipe_shproc("uniq -c - |expand")


def do_v():
    """vim"""

    exit_via_shpipe_shproc("vim")


def do_w():
    """wc -l"""

    exit_via_shpipe_shproc("wc -l")


def do_x():
    """hexdump -C"""

    exit_via_shpipe_shproc("hexdump -C")


def do_xp():
    """expand"""

    exit_via_shpipe_shproc("expand")


#
# In the same-same old way, wrap many many Shim's around Bash Pipe Filters
#


def exit_via_shpipe_shproc(shline):
    """Forward Augmented Parms into a Bash Subprocess and exit, else return"""

    parms = sys.argv[2:]
    shparms = " ".join(byo.shlex_min_quote(_) for _ in parms)

    # Pick a RIndex of the ShLine to forward Parms into

    marks = ["", " |", " >("]

    rindices = list()
    for mark in marks:
        find = shline.find(mark)
        if find >= 0:
            rindex = shline.rindex(mark)
            rindices.append(rindex)

    rindex = min(rindices)  # Place the Parms inside the ShLine, else at its End

    shell = rindex != len(shline)

    # Forward the Parms

    parmed_shline = shline
    if parms:
        if rindex < len(shline):
            parmed_shline = shline[:rindex] + " " + shparms + shline[rindex:]
        else:
            parmed_shline = shline + " " + shparms

    # Call another layer of Bash for an 'a |c' Pipe, or for 'a |tee >(b) |c' Pipe of Tee

    shshline = "bash -c '{}'".format(parmed_shline)
    alt_shline = shshline if shell else parmed_shline

    # Run a line of Sh and then exit

    exit_via_shline(shline=alt_shline)


def exit_via_shline(shline):
    """Run a line of Sh and then exit"""

    argv = shlex.split(shline)

    sys.stderr.write("+ {}\n".format(shline))

    isatty = sys.stdin.isatty()
    if main.prompter:
        if isatty:
            sys.stderr.write("shpipe.py: Press ⌃D TTY EOF to quit\n")

    sys.stderr = open(os.devnull, "w")
    run = subprocess.run(argv)
    if run.returncode:  # Exit early, at the first NonZero Exit Status ReturnCode
        sys.stderr.write("+ exit {}\n".format(run.returncode))

        sys.exit(run.returncode)

    sys.exit()


#
# Track an example Terminal Qb ShPipe Transcript
#


_ = """

%
%
% python3 -c 'import this' |h -5 |cv
+ pbcopy
+ head -5
%
% cv |sed -n -e '3,$p' |sed 's,[.]$,,' |cv
+ pbpaste
+ pbcopy
%
% cv -ntv
+ bash -c 'pbpaste |cat -ntv |expand'
     1  Beautiful is better than ugly
     2  Explicit is better than implicit
     3  Simple is better than complex
%
%
% cv |t -2
+ pbpaste
+ tail -2
Explicit is better than implicit
Simple is better than complex
%

"""


#
# Run from the Command Line, when not imported into some other Main module
#


if __name__ == "__main__":
    main()


# posted into:  https://.com/pelavarre/byobash/blob/main/bin/shpipe.py
# copied from:  git clone https://github.com/pelavarre/byobash.git