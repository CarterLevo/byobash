#!/usr/bin/env python3

r"""
usage: git.py [--help] VERB [ARG ...]
usage: git.py [--help] --for-shproc SHVERB [ARG ...]
usage: git.py [--help] --for-chdir CDVERB [ARG ...]

work over clones of source dirs of dirs of files

positional arguments:
  VERB                 choice of Git SubCommand
  ARG                  choice of Git Options and Arguments

options:
  --help               show this help message and exit
  --for-shproc SHVERB  unabbreviate this ShVerb and call on Git to do the work
  --for-chdir CDVERB   print the $(git rev-parse --show-toplevel) to tell Cd where to go

quirks:
  taller Screens come with larger default limits on lines
  Zsh and Bash take '(dirs -p |head -1)', but only Bash takes 'dirs +0'

advanced bash install:

  function 'git.py' () {
    : : 'Show Git Status, else change the Sh Working Dir, else do other Git Work' : :
    if [ "$#" = 1 ] && [ "$1" = "--" ]; then
      command git.py --for-shproc --
    elif [ "$#" = 1 ] && [ "$1" = "cd" ]; then
      'cd' "$(command git.py --for-chdir $@)" && (dirs -p |head -1)
    else
      command git.py --for-shproc "$@"
    fi
  }

  function qcd () {
    'cd' "$(command git.py --for-chdir cd $@)" && (dirs -p |head -1)
  }

examples:

  ls ~/.gitconfig
  ls .git/config

  git.py cd  &&: cd $(git rev-parse --show-toplevel)
  git.py d  &&: git diff
  git.py g  &&: git grep  &&: FIXME: g to grep -i, gi to grep
  git.py co  &&: git checkout  &&: the calmest kind of 'git status'
  git.py gl  &&: git grep -l
  git.py dh  &&: git diff HEAD~..., default HEAD~1
  git.py dhno  &&: git diff --name-only HEAD~..., default HEAD~1
  git.py dno  &&: git diff --name-only
  git.py lf  &&: git ls-files
  git.py s  &&: git show
  git.py sp  &&: git show --pretty=''
  git.py spno  &&: git show --pretty='' --name-only
  git.py ssi  &&: git status --short --ignored  &&: calmer than 'git status'
  git.py st  &&: git status
  git.py sun  &&: git status --untracked-files=no

  git.py b  &&: git branch  &&: and see also:  git rev-parse --abbrev-ref
  git.py ba  &&: git branch --all
  git.py cofrb  &&: git checkout ... && git fetch && git rebase
  git.py dad  &&: git describe --always --dirty
  git.py f  &&: git fetch
  git.py frb  &&: git fetch && git rebase
  git.py l  &&: git log
  git.py l1  &&: git log --decorate -1
  git.py lg  &&: git log --oneline --no-decorate --grep ...
  git.py lgg  &&: git log --oneline --no-decorate -G ...  &&: search for touches
  git.py lgs  &&: git log --oneline --no-decorate -S ...  &&: search for adds/ deletes
  git.py lq  &&: git log --oneline --no-decorate -...  &&: default lots, -0 for no limit
  git.py lqa  &&: git log --oneline --no-decorate --author=$USER -...
  git.py ls  &&: git log --stat  &&: but see also:  git show --name-only
  git.py lv  &&: git log --oneline --decorate -...  &&: default lots, -0 for no limit
  git.py rb  &&: git rebase
  git.py ri  &&: git rebase --interactive --autosquash HEAD~...  &&: default {@upstream}
  git.py rl  &&: git reflog  &&: show Commits
  git.py rpar  &&: git rev-parse --abbrev-ref  &&: show the key line of:  git.py b
  git.py rpsfn  &&: git rev-parse --symbolic-full-name @{-...}  &&: show:  git.py co -
  git.py rv  &&: git remote -v
  git.py ssn  &&: git shortlog --summary --numbered

  git.py a  &&: git add
  git.py ap  &&: git add --patch
  git.py c  &&: git commit
  git.py ca  &&: git commit --amend
  git.py caa  &&: git commit --all --amend
  git.py caf  &&: git commit --all --fixup
  git.py cf  &&: git commit --fixup
  git.py cm  &&: git commit -m wip
  git.py cl  &&: take ⌃D to mean:  git clean -ffxdq  &&: destroy files outside Git Add
  git.py cls  &&: take ⌃D to mean:  sudo true && sudo git clean -ffxdq
  git.py pfwl  &&: take ⌃D to mean:  git push --force-with-lease
  git.py rhu  &&: take ⌃D to mean:  git reset --hard @{upstream}  &&: hide Commits
  git.py s1  &&: git show :1:...  &&: common base
  git.py s2  &&: git show :2:...  &&: just theirs
  git.py s3  &&: git show :3:...  &&: juts ours

  git.py  &&: show these examples and exit
  git.py --h  &&: show this help message and exit
  git.py --  &&: 'git status' and then counts of:   git status --short --ignored
  command git.py --  &&: show the Advanced Bash Install of Git Py and exit
"""


import __main__
import collections
import getpass
import glob
import os
import pdb
import re
import shlex
import signal
import subprocess
import sys

import byotools as byo

_ = pdb


GitLikeAlias = collections.namedtuple("GitLikeAlias", "shlines authed".split())


def main():  # FIXME  # noqa C901 complex
    """Run from the Sh Command Line"""

    rm_fr_import_byotools_pyc()  # Give the Illusion of a Sh Alias without PyC

    aliases_by_verb = load_configuration()

    patchdoc = """

  function 'git.py' () {
    : : 'Show Git Status, else change the Sh Working Dir, else do other Git Work' : :
    if [ "$#" = 1 ] && [ "$1" = "--" ]; then
      command git.py --for-shproc --
    elif [ "$#" = 1 ] && [ "$1" = "cd" ]; then
      'cd' "$(command git.py --for-chdir $@)" && (dirs -p |head -1)
    else
      command git.py --for-shproc "$@"
    fi
  }

  function qcd () {
    'cd' "$(command git.py --for-chdir cd $@)" && (dirs -p |head -1)
  }

    """

    # Drop the "--for-shproc" Parm
    # if it's followed by no more Parms, or
    # if it's followed one of "--help", "--hel", "--he", "--h"

    parms = sys.argv[1:]

    if parms and (parms[0] == "--for-shproc"):
        if not parms[1:]:
            sys.argv[1:] = parms[1:]
        else:
            parm_1 = parms[1]
            if parm_1.startswith("--h") and "--help".startswith(parm_1):
                sys.argv[1:] = parms[1:]
            elif parm_1 == "--":  # here emulate Sh Function:  git.py --
                sys.argv[1:] = ["--for-shproc", "co"]

        parms = sys.argv[1:]

    # Define some forms of 'git.py'

    byo.exit_via_patchdoc(patchdoc)  # command git.py --
    byo.exit_via_testdoc()  # git.py
    byo.exit_via_argdoc()  # git.py --help

    # Define many GitLikeAlias'es

    if parms[1:]:
        option = parms[0]
        if option.startswith("--for-"):
            unevalled_parms = parms[2:]

            # Define 'git.py --for-chdir cd ...'
            # to do only the 'git rev-parse --show-toplevel' work here,
            # while trusting the caller to the the 'cd $(...)' work

            if "--for-chdir".startswith(option):
                cdverb = parms[1]
                if cdverb == "cd":

                    alias = aliases_by_verb[cdverb]
                    authed = alias.authed
                    shlines = ["git rev-parse --show-toplevel"]

                    git_cd_shlines = ["cd $(git rev-parse --show-toplevel)"]
                    assert alias.shlines == git_cd_shlines, alias.shlines

                    exit_via_git_shproc(
                        shverb=cdverb,
                        parms=unevalled_parms,
                        authed=authed,
                        shlines=shlines,
                    )

            # Define 'git.py --for-shproc SHVERB ...'

            if "--for-shproc".startswith(option):
                shverb = parms[1]
                if shverb in aliases_by_verb.keys():

                    alias = aliases_by_verb[shverb]
                    authed = alias.authed
                    shlines = alias.shlines

                    exit_via_git_shproc(
                        shverb, parms=unevalled_parms, authed=authed, shlines=shlines
                    )

    # Default to forward the Parms into a Git Subprocess

    byo.exit_via_shcommand()


def rm_fr_import_byotools_pyc():
    """Cancel the Dirt apparently tossed into this Git Clone by Import ByoTools"""

    cwd = os.getcwd()

    bin_dirname = os.path.dirname(byo.__file__)

    byobash_dirname = os.path.join(bin_dirname, os.pardir)
    pyc_dirname = os.path.join(bin_dirname, "__pycache__")
    pyc_glob = os.path.join(pyc_dirname, "byotools.cpython-*.pyc")

    real_cwd = os.path.realpath(cwd)
    real_byobash_dirname = os.path.realpath(byobash_dirname)

    eq = real_cwd == real_byobash_dirname
    startswith = real_cwd.startswith(real_byobash_dirname + os.sep)
    if eq or startswith:

        hits = list(glob.glob(pyc_glob))
        if len(hits) == 1:
            hit = hits[-1]

            os.remove(hit)
            if not os.listdir(pyc_dirname):
                os.rmdir(pyc_dirname)


def exit_via_git_shproc(shverb, parms, authed, shlines):  # FIXME  # noqa: C901 complex
    """Forward Augmented Parms into a Git Subprocess and exit, else return"""

    halfscreen = 19  # FIXME

    alt_shlines = list(_ for _ in shlines if _ != "cat -")
    alt_parms = parms
    if not parms:
        if alt_shlines == ["git commit --all --fixup {}"]:
            alt_parms = ["HEAD"]
        elif alt_shlines == ["git commit --fixup {}"]:
            alt_parms = ["HEAD"]
        elif alt_shlines == ["git rebase --interactive --autosquash HEAD~{}"]:
            alt_shlines = ["git rebase --interactive --autosquash @{{upstream}}"]

    parms_minus = alt_parms[1:]
    shquoted_parms = " ".join(byo.shlex_min_quote(_) for _ in alt_parms)
    shquoted_parms_minus = " ".join(byo.shlex_min_quote(_) for _ in parms_minus)

    # Distinguish a leading Int parm, without requiring it

    intparm = None
    if alt_parms:
        chars = alt_parms[0]
        if re.match(r"^[-+]?[0-9]+$", string=chars):
            intparm = int(chars)

    # Form each ShLine, and split each ShLine apart into an ArgV

    argvs = list()
    for shline in alt_shlines:

        # At most once, accept a request to forward Parms

        parmed_shline = None

        if "{}" not in shline:

            parmed_shline = shline.format()

        else:

            assert shquoted_parms is not None

            # Count off 0..N below HEAD, default 1, else take complex Parms

            if " HEAD~{}" in shline:

                if not shquoted_parms:
                    parmed_shline = shline.format(1)
                elif intparm is None:
                    alt_shline = shline.replace(" HEAD~{}", " HEAD~{} {}")
                    parmed_shline = alt_shline.format(1, shquoted_parms)
                else:
                    absparm = abs(intparm)
                    alt_shline = shline.replace(" HEAD~{}", " HEAD~{} {}")
                    parmed_shline = alt_shline.format(absparm, shquoted_parms_minus)

            # Count off 1..N of "git checkout -", default 1, else take complex Parms

            elif " @{{-{}}}" in shline:

                if not shquoted_parms:
                    parmed_shline = shline.format(1)
                elif intparm is None:
                    alt_shline = shline.replace(" @{{-{}}}", " @{{-{}}} {}")
                    parmed_shline = alt_shline.format(1, shquoted_parms)
                else:
                    absparm = abs(intparm)
                    alt_shline = shline.replace(" @{{-{}}}", " @{{-{}}} {}")
                    parmed_shline = alt_shline.format(absparm, shquoted_parms_minus)

            # Count off Lines of Output, default half Screen, else take complex Parms
            # but take any of '-0', '0', '+0' to mean No Limit Parm

            elif " -{}" in shline:

                if not shquoted_parms:
                    parmed_shline = shline.format(halfscreen)
                elif intparm is None:
                    alt_shline = shline.replace(" -{}", " -{} {}")
                    parmed_shline = alt_shline.format(halfscreen, shquoted_parms)
                elif intparm == 0:
                    alt_shline = shline.replace(" -{}", " {}")
                    parmed_shline = alt_shline.format(shquoted_parms_minus)
                else:
                    absparm = abs(intparm)
                    alt_shline = shline.replace(" -{}", " -{} {}")
                    parmed_shline = alt_shline.format(absparm, shquoted_parms_minus)

            # Default to take complex Parms

            else:
                parmed_shline = shline.format(shquoted_parms)

            # Reject subsequent requests to forward Parms, if any

            shquoted_parms = None

        # Fix it up some more and ship it out

        argv_shline = parmed_shline

        shguest = byo.shlex_min_quote(getpass.getuser())
        guest_key = " --author=$USER"
        guest_repl = " --author={}".format(shguest)

        argv_shline = argv_shline.replace(guest_key, guest_repl)

        argv = shlex.split(argv_shline)
        argvs.append(argv)

    # Actually return, actually don't exit, if Parms present but not forwarded

    if shquoted_parms:

        return

    # Join the ShLines

    auth_shlines = list()
    for argv in argvs:
        shline = " ".join(byo.shlex_min_quote(_) for _ in argv)

        overquoted = "git reset --hard '@{upstream}'"  # because of the {} Braces
        shline = shline.replace(overquoted, "git reset --hard @{upstream}")

        auth_shlines.append(shline)

    auth_shline = " && ".join(auth_shlines)

    # Demand authorization

    if not authed:
        sys.stderr.write("did you mean:  {}\n".format(auth_shline))
        sys.stderr.write("press ⌃D to execute, or ⌃C to quit\n")
        try:
            _ = sys.stdin.read()
        except KeyboardInterrupt:
            sys.stderr.write("\n")
            sys.stderr.write("KeyboardInterrupt\n")

            returncode = 0x80 | signal.SIGINT
            assert returncode == 130, (returncode, signal.SIGINT)

            sys.exit(returncode)

    # Run the code, and exit

    for argv in argvs:

        if False:
            argv = list(argv)
            argv.insert(0, "echo")

        shline = " ".join(byo.shlex_min_quote(_) for _ in argv)

        sys.stderr.write("+ {}\n".format(shline))
        run = subprocess.run(argv)
        if run.returncode:  # Exit early, at the first NonZero Exit Status ReturnCode
            sys.stderr.write("+ exit {}\n".format(run.returncode))

            sys.exit(run.returncode)

    sys.exit()


#
# Wrap many many Shim's around Git
#


#
# FIXME put these Comments somewhere good
#
# Radically abbreviate common Sh Git Lines
# thus emulate '~/.gitconfig' '[alias]'es,
# except don't hide the work of unabbreviation,
# away from our newer people trying to learn over your shoulder, by watching you work
#
# Block the more disruptive Sh Git Lines, unless authorized by ⌃D Tty Eof
#


def load_configuration():
    """Declare the GitLikeAlias'es"""

    doc = __main__.__doc__

    # Visit each GitLike Alias

    aliases_by_verb = dict()
    for (k, v) in ALIASES.items():
        verb = k

        shline = "git.py {k}  &&: {v}".format(k=k, v=v)
        shlines = v.split(" && ")

        # Compile-time option for a breakpoint on a ShVerb or CdVerb

        if False:
            if verb == "cd":
                pdb.set_trace()

        # Separate kinds of Alias'es
        # todo: Require the DocLine found in full, with only zero or more Comments added

        docline_0 = shline
        docline_0 = byo.str_removesuffix(docline_0, " {}")
        docline_1 = docline_0.replace("  &&: cat - && ", "  &&: take ⌃D to mean:  ")
        docline_2 = docline_0.format("...")
        docline_3 = docline_1.format("...")

        alias = GitLikeAlias(shlines, authed=True)
        if "  &&: cat - && " in shline:
            alias = GitLikeAlias(shlines, authed=None)

        if docline_3 in doc:  # add interlock before, and place Parms explicitly
            pass
        elif docline_2 in doc:  # place Parms explicitly, in the middle or at the end
            pass
        elif docline_1 in doc:  # add interlock before, but no Parms
            pass
        elif docline_0 in doc:  # add optional Parms past the end
            pass
        else:
            assert False, (shlines, docline_0, docline_1)

        # Declare this GitLike Alias

        assert verb not in aliases_by_verb.keys(), repr(verb)

        aliases_by_verb[verb] = alias

    return aliases_by_verb


ALIASES = {
    "a": "git add {}",
    "ap": "git add --patch {}",
    "b": "git branch",
    "ba": "git branch --all",
    "c": "git commit {}",
    "ca": "git commit --amend {}",
    "caa": "git commit --all --amend {}",
    "caf": "git commit --all --fixup {}",
    "cd": "cd $(git rev-parse --show-toplevel)",
    "cf": "git commit --fixup {}",
    "cl": "cat - && git clean -ffxdq",
    "cls": "cat - && sudo true && sudo git clean -ffxdq",
    "cm": "git commit -m wip",
    "co": "git checkout {}",
    "cofrb": "git checkout {} && git fetch && git rebase",  # auth'ed!
    "d": "git diff {}",
    "dad": "git describe --always --dirty",
    "dh": "git diff HEAD~{}",
    "dhno": "git diff --name-only HEAD~{}",
    "dno": "git diff --name-only {}",
    "f": "git fetch",
    "frb": "git fetch && git rebase",
    "g": "git grep {}",  # todo: default Grep of $(-gdhno)
    "gl": "git grep -l {}",  # todo: default Grep of $(-gdhno)
    "l": "git log {}",
    "l1": "git log --decorate -1 {}",
    "lf": "git ls-files {}",
    "lg": "git log --oneline --no-decorate --grep {}",
    "lgg": "git log --oneline --no-decorate -G {}",  # touches, aka Grep Source
    "lgs": "git log --oneline --no-decorate -S {}",  # adds/deletes, aka Pickaxe
    "lq": "git log --oneline --no-decorate -{}",
    "lqa": "git log --oneline --no-decorate --author=$USER -{}",
    "ls": "git log --stat {}",
    "lv": "git log --oneline --decorate -{}",
    "pfwl": "cat - && git push --force-with-lease",
    "rb": "git rebase",  # auth'ed!
    "rhu": "cat - && git reset --hard @{{upstream}}",
    "ri": "git rebase --interactive --autosquash HEAD~{}",
    "rl": "git reflog",
    "rpar": "git rev-parse --abbrev-ref",
    "rpsfn": "git rev-parse --symbolic-full-name @{{-{}}}",
    "rv": "git remote -v",
    "s": "git show {}",
    "s1": "git show :1:{}",
    "s2": "git show :2:{}",
    "s3": "git show :3:{}",
    "sp": "git show --pretty='' {}",
    "spno": "git show --pretty='' --name-only {}",
    "ssi": "git status --short --ignored",
    "ssn": "git shortlog --summary --numbered",
    "st": "git status {}",
    "sun": "git status --untracked-files=no",
}

# Mac HFS FileSystem's don't accept 'qlG' and 'qlg' existing inside one Dir
# Mac HFS FileSystem's don't accept 'qlS' and 'qls' existing inside one Dir


#
# Run from the Command Line, when not imported into some other Main module
#


if __name__ == "__main__":
    main()


# 'todo.txt' for 'git.py' =>

#
# FIXME
# trace what they mean - with inverse globs for concision, like at:  -ga bin/*.py
#

#
# FIXME
# git.py em
# git.py emacs
# git.py vi
#
# add '-h' into 'git log grep' => grep -h def.shlex_quote $(-ggl def.shlex_quote)

#
# todo
#
# --pretty=format:'%h %aE %s'  |cat - <(echo) |sed "s,@$DOMAIN,,"
# git blame/log --abbrev=3
#

# todo
#
# git push origin HEAD:people/jqdoe/project/1234
# git checkout -b people/jqdoe/project/1234 origin/people/jqdoe/project/1234
# git push origin --delete people/jqdoe/project/12345
# git branch -D people/jqdoe/project/12345
#

#
# todo
#
# git log --oneline --decorate --decorate-refs-exclude '*/origin/guests/??/*' -15
#
# -gd origin  # that's not precisely it, but abbreviate Diff's vs the Pushed Code
#

# todo
#
# persist a focus larger than $(qdhno) for 'qg', maybe
# persist a history of what qb, qlq, qlv did say
# persist notes onto each -gco, for display by -gbq and -gb
#
# compare
# git commit $(qdhno)
# git commit --all
#
# compare
# git show --name-only
# git diff-tree --no-commit-id --name-only -r
#


# posted into:  https://github.com/pelavarre/byobash/blob/main/bin/git.py
# copied from:  git clone https://github.com/pelavarre/byobash.git
