#!/usr/bin/env python3

r"""
usage: byopyvm.py [--help] [WORD ...]

work quickly and concisely, over Dirs of Dirs of Files

positional arguments:
  WORD   a word of command

options:
  --help               show this help message and exit

advanced bash install:

  alias @='~/Public/byobash/bin/byopyvm.py buttonfile'

  function = {
    : : 'Show Stack, else else do other Stack Work' : :
    if [ "$#" = 0 ]; then
        ~/Public/byobash/bin/byopyvm.py =
    else
        ~/Public/byobash/bin/byopyvm.py "$@"
    fi
  }

quick start:

  git clone https://github.com/pelavarre/byobash.git
  cd byobash/

  function = { ~/Public/byobash/bin/byopyvm.py "$@"; }
  = 12 34 +

  alias @='~/Public/byobash/bin/byopyvm.py buttonfile'
  @ 1 2 , 3 4 +

  source dotfiles/dot.byo.bashrc

examples:

  byopyvm.py  # show these examples and exit
  byopyvm.py --h  # show this help message and exit
  command bin/byopyvm.py --  # show the Advanced Bash Install of ByoPyVM Py and exit

  # Maths

  =  pi
  =  2 *
  =  .

  =  pi 2 * .  # all at once

  # Debugger

  =  pdb.set_trace  # like to follow up with:  stack_peek(0)

  # Demos chosen from:  / * - + . , pi π over sqrt √ i e = clear

  =  e i pi * pow  # another calculation

  =  clear  pow , .  pow pow , .  pow pow , .  2>/dev/null  # 2, 4, 16, ...
  =  clear  / , .    / / , .      / / , .      2>/dev/null  # 0, inf, 0, ...
  =  clear  * , .    * * , .      * * , .      2>/dev/null  # 1, 2, 4, ...
  =  clear  + , .    + + , .      + + , .      2>/dev/null  # 0, 1, 2, ...
  =  clear  - , .    - - , .      - - , .      2>/dev/null  # 1, -1, 1, ...
"""

# todo:  # Files and Dirs
# todo:  = ls  # ls -1Frt |tail -4
# todo:  = cp  # cp -ip ... ...~$(date +%m%dpl%H%M%S)~
# todo:  = cp  # cp -ipR .../ ...~$(date +%m%dpl%H%M%S)~
# todo:  = mv  # mv -i ... ...~$(date +%m%dpl%H%M%S)~


import ast
import collections
import importlib
import json
import math
import os
import pathlib
import pdb
import re
import subprocess
import sys
import traceback

import byotools as byo

_ = math
_ = pdb


#
# Configure
#


EPSILON = 0  # last wins
EPSILON = 1e-15  # say how much to round off to make comparisons come out equal

FILENAME_PRECISION_3 = 3  # 3 digits means mention 'math.pi' as '3.142'

MATH_J = 1j  # work around for Python forgetting to define 'math.j'

SH_J = "j"  # last wins
SH_J = "i"  # choose the Char to mark 'str' of '.imag', from outside r"[-+.012345679Ee]"

STR_PI = "\N{Greek Small Letter Pi}"  # π
STR_SQRT = "\N{Square Root}"  # √


#
# Declare some of how to divide Chars into Words of Python
#


NAME_REGEX = r"[0-9A-Z_a-z]+"
CLOSED_NAME_REGEX = r"^" + NAME_REGEX + r"$"


DOTTED_NAME_REGEX = "({})([.]{})+".format(NAME_REGEX, NAME_REGEX)
CLOSED_DOTTED_NAME_REGEX = r"^" + DOTTED_NAME_REGEX + r"$"


DECINTEGER_REGEX = r"([1-9](_[0-9])*)|(0(_0)*)"
INT_REGEX = r"[-+]?" + r"({})".format(DECINTEGER_REGEX)
CLOSED_INT_REGEX = r"^" + DECINTEGER_REGEX + r"$"
# as per 2.4.5 'Integer literals' in Jun/2022 Python 3.10.5 at Docs Python Org


DIGITPART_REGEX = r"[0-9](_[0-9])*"
FRACTION_REGEX = r"." + DIGITPART_REGEX
EXPONENT_REGEX = r"[Ee][-+]" + DIGITPART_REGEX
POINTFLOAT_REGEX_1 = r"({})?".format(DIGITPART_REGEX) + FRACTION_REGEX
POINTFLOAT_REGEX_2 = DIGITPART_REGEX + r"[.]"
POINTFLOAT_REGEX = r"({})|({})".format(POINTFLOAT_REGEX_1, POINTFLOAT_REGEX_2)
EXPONENTFLOAT_REGEX = r"(({})|({})){}".format(
    DIGITPART_REGEX, POINTFLOAT_REGEX, EXPONENT_REGEX
)
FLOATNUMBER_REGEX = r"({})|({})".format(POINTFLOAT_REGEX, EXPONENTFLOAT_REGEX)
FLOAT_REGEX = r"[-+]?" + r"({})".format(FLOATNUMBER_REGEX)
CLOSED_FLOAT_REGEX = r"^" + FLOAT_REGEX + "$"
# as per 2.4.6 'Floating point literals' in Jun/2022 Python 3.10.5 at Docs Python Org


#
# Run from the Sh Command Line
#


def main():
    """Run from the Sh Command Line"""

    # Start up

    parms = sys.argv[1:]
    main.parms = parms

    collapse_star_parms(parms)

    patchdoc = """

      alias @='~/Public/byobash/bin/byopyvm.py buttonfile'

      function = {
        : : 'Show Stack, else else do other Stack Work' : :
        if [ "$#" = 0 ]; then
            ~/Public/byobash/bin/byopyvm.py =
        else
            ~/Public/byobash/bin/byopyvm.py "$@"
        fi
      }

    """

    # Quit conventionally

    byo.exit_if_patchdoc(patchdoc)  # command byopyvm.py --
    byo.exit_if_testdoc()  # byopyvm.py
    byo.exit_if_argdoc()  # byopyvm.py --help

    # Discard a lead word of "--"

    alt_parms = parms
    if parms and (parms[0] == "--"):
        alt_parms = parms[1:]

    # Run well

    parms_run(parms=alt_parms)


def collapse_star_parms(parms):
    """Reconstruct the Sh Input Line despite the presence of '*' as a word"""

    shline = "ls"

    run = byo.subprocess_run_stdio(shline, stdout=subprocess.PIPE)
    stdout = run.stdout.decode()
    lines = stdout.splitlines()

    length = len(lines)
    if length:

        index = 0
        while index < len(parms):
            stop = index + length

            if parms[index:][:length] == lines:
                parms[::] = parms[:index] + ["*"] + parms[stop:]

                # the Sh Input Line might, or might Not, have had a ' * ' here

            index += 1


#
# Parse input sourcelines
#


def parms_run(parms):
    """Run the Parms = Read a Word, Evaluate the Word, Print the Result, Loop"""

    # Take each word, one at a time

    take_by_word = form_take_by_word()

    while parms:

        word = parms[0]
        if word not in take_by_word.keys():
            word = to_fuzzed_word(word)

        assert word in take_by_word.keys(), (word, parms)
        take = take_by_word[word]

        if not isinstance(take, collections.abc.Callable):
            value = take
            stack_push(value)
        else:
            func = take
            if take.__name__.startswith("parms_"):
                func(parms)
            else:
                func()

        parms[::] = parms[1:]


def to_fuzzed_word(word):
    """Pick out what kind of Input Word this is"""

    if re.match(CLOSED_INT_REGEX, string=word):

        return "lit_int"

    if re.match(CLOSED_FLOAT_REGEX, string=word):

        return "lit_float"

    if re.match(CLOSED_DOTTED_NAME_REGEX, string=word):

        return "dotted_name"

    if re.match(CLOSED_NAME_REGEX, string=word):

        return "name"

    if word in NAME_BY_CHAR.keys():
        name = NAME_BY_CHAR[word]

        return name

    return "SyntaxError"


def form_name_by_char():
    """Choose Names for Chars that Python Names reject"""

    d = dict()

    d[" "] = "space"
    d["!"] = "bang"
    d['"'] = "quote"
    d["#"] = "hash"
    # d["$"]
    # d["%"]
    d["&"] = "amp"
    d["'"] = "tick"
    # d["("]
    # d[")"]
    d["*"] = "star"
    d["+"] = "plus"
    d[","] = "comma"
    d["-"] = "dash"
    d["."] = "dot"
    d["/"] = "slash"

    d["0"] = "zero"  # Decimal Digits alone are not Python Names
    d["1"] = "one"
    d["2"] = "two"
    d["3"] = "three"
    d["4"] = "four"
    d["5"] = "five"
    d["6"] = "six"
    d["7"] = "seven"
    d["8"] = "eight"
    d["9"] = "nine"

    d[":"] = "colon"
    d[";"] = "semi"
    # d["<"]
    d["="] = "equals"
    # d[">"]
    d["?"] = "query"

    d["@"] = "at"

    # d["["]
    d["\\"] = "backslant"  # two syllables
    # d["]"]
    d["^"] = "hat"
    d["_"] = "skid"  # aka underscore

    d["`"] = "backtick"  # two syllables

    # d["{"]
    d["|"] = "bar"
    # d["}"]
    d["~"] = "tilde"  # two syllables  # aka "squiggle"

    return d

    # https://unicode.org/charts/PDF/U0000.pdf
    # http://www.catb.org/jargon/html/A/ASCII.html
    # https://www.dourish.com/goodies/jargon.html

    # http://www.forth.org/svfig/Win32Forth/DPANS94.txt
    # https://aplwiki.com/wiki/Unicode


NAME_BY_CHAR = form_name_by_char()


#
# Define Verbs
#


def form_take_by_word():
    """Declare our Built-In Verbs and Nouns"""

    # Define Sh Nouns of Forth

    take_by_sh_noun = dict(
        e=math.e,
        i=MATH_J,  # Sci Folk
        j=MATH_J,  # Eng Folk
        pi=math.pi,
    )

    take_by_sh_noun[STR_PI] = math.pi  # π

    # Define Sh Adverbs of Forth

    take_by_sh_adverb = dict(
        buttonfile=parms_buttonfile,
        dotted_name=parms_dotted_name,
        lit_float=parms_lit_float,
        lit_int=parms_lit_int,
        name=parms_name,
        hash=parms_hash,  # this 'hash' is not 'builtins.hash'
    )

    # Define SH Verbs of Forth

    take_by_sh_verb = dict(
        clear=do_clear,
        comma=do_comma,
        dash=do_dash,  # invite Monosyllabic Folk to speak of the '-' Dash
        dot=do_dot,
        equals=do_equals,
        minus=do_dash,  # invite Calculator Folk to speak of the '-' Minus
        over=do_clone_y,
        pow=do_pow,  # this 'pow' is not 'builtins.pow'
        plus=do_plus,
        slash=do_slash,
        sqrt=do_sqrt,
        star=do_star,
        swap=do_swap_y_x,
    )

    take_by_sh_verb[STR_SQRT] = do_sqrt  # √

    # Merge the Dicts of Words of Command

    d = dict()
    for kvs in (take_by_sh_adverb, take_by_sh_verb, take_by_sh_noun):
        for (k, v) in kvs.items():
            assert k not in d.keys(), k
            d[k] = v

    take_by_word = d

    # Succeed

    return take_by_word


#
# Define Sh Verbs of Forth
#


def parms_dotted_name(parms):
    """Eval a Dotted Name and push its Value"""

    py = parms[0]

    evalled = stackable_dotted_eval(py)

    pushable = evalled  # todo: factor out commonalities with 'def parms_name'
    if isinstance(evalled, collections.abc.Callable):
        pushable = evalled()  # might be:  pdb.set_trace()

    stack_push(pushable)  # you might next:  stack_peek(0)


def parms_lit_float(parms):
    """Eval the Chars of a Float Literal"""

    str_x = parms[0]
    x = float(str_x)
    stack_push(x)


def parms_lit_int(parms):
    """Eval the Chars of an Int Literal"""

    str_x = parms[0]
    x = int(str_x)
    stack_push(x)


def parms_name(parms):
    """Eval a Name and push its Value"""

    py = parms[0]

    evalled = stackable_eval(py)

    pushable = evalled  # todo: factor out commonalities with 'def parms_dotted_name'
    if isinstance(evalled, collections.abc.Callable):
        pushable = evalled()

    stack_push(pushable)


def parms_hash(parms):
    """Discard the remaining Parms as Commentary"""  # traditional in Sh at ': '

    parms[::] = list()


#
# Define Calculator Buttons
#


def do_dash():
    """Push Y - X in place of Y X"""

    if not stack_has_x():
        stack_push(1)  # suggest 0 1 -, else 0 X -
    elif not stack_has_y():
        stack_push(0)
        do_swap_y_x()  # push -X in place of X, when run twice  # a la HP "CHS"
    else:

        (y, x) = stack_peek(2)

        try:
            x_ = y - x
        except Exception as exc:  # todo: indeed we could subtract Str, List, Tuple, ...

            byo.exit_after_print_raise(exc)

        stack_pop(2)
        stack_push(x_)


def do_dot():  # kin to Python's '-i' doing nothing after each None result
    """Pop X but print its Value, or do nothing if Stack is Empty"""

    if stack_has_x():
        x = stack_pop(asif_before_rm="cat {} && ")
        print(x)


def do_equals():
    """Show the Keys of the T Z Y X Stack, not its Values"""

    shline = "ls -1Frt |... |tail -4"
    byo.stderr_print("+ {}".format(shline))

    depth = min(4, stack_depth())
    if not depth:
        print()
    else:
        pairs = stack_pairs_peek(depth)
        for pair in pairs:
            (basename, _) = pair

            print(basename)


def do_pow():
    """Push Y ** X in place of Y X, by way of 'pow(y, exp=x)'"""

    if not stack_has_x():
        stack_push(2)  # suggest 2 2 **, else 2 **
    elif not stack_has_y():
        stack_push(2)
    else:

        (y, x) = stack_peek(2)

        try:
            x_ = pow(y, exp=x)
        except Exception as exc:

            byo.exit_after_print_raise(exc)

        stack_pop(2)
        stack_push(x_)


def do_plus():
    """Push Y + X in place of Y X"""

    if not stack_has_x():
        stack_push(0)  # suggest 0 1 +, else 1 +
    elif not stack_has_y():
        stack_push(1)
    else:

        (y, x) = stack_peek(2)

        try:
            x_ = y + x
        except Exception as exc:

            byo.exit_after_print_raise(exc)

        stack_pop(2)
        stack_push(x_)


def do_slash():
    """Push Y / X in place of Y X, and slide into -Inf, NaN, InF when X zeroed"""

    if not stack_has_x():
        stack_push(0)  # suggest  1 0 /, else 1 X /
    elif not stack_has_y():
        stack_push(1)
        do_swap_y_x()  # push (1 / X) in place of X, when run twice  # a la HP "1/X"
    else:

        (y, x) = stack_peek(2)

        if y == x == 0:
            x_ = float("NaN")
        elif x == 0:
            x_ = float("-Inf") if (repr(y).startswith("-")) else float("InF")
        else:

            try:
                x_ = y / x
            except Exception as exc:

                byo.exit_after_print_raise(exc)

        stack_pop(2)
        stack_push(x_)


def do_sqrt():
    """Push (X ** (1 / 2)) in place of X, and slide into Complex when X negative"""

    if not stack_has_x():
        stack_push(-1)  # suggest -1 Sqrt
    else:

        x = stack_peek()

        try:
            x_ = x ** (1 / 2)
        except Exception as exc:

            byo.exit_after_print_raise(exc)

        stack_pop()
        stack_push(x_)


def do_star():
    """Push Y * X in place of Y X"""

    if not stack_has_x():
        stack_push(1)  # suggest 1 2 *, else 2 *
    elif not stack_has_y():
        stack_push(2)
    else:

        (y, x) = stack_peek(2)

        try:
            x_ = y * x
        except Exception as exc:

            byo.exit_after_print_exc(exc)

        stack_pop(2)
        stack_push(x_)


#
# Define Calculator Stack Ops
#


def do_clear():  # a la GForth "clearstack"
    """Pop X till no more X"""

    stack_pairs_pop(depth=0)


def do_clone_x():  # a la Forth "DUP", a la HP "Enter"
    """Push X X in place of X"""

    if not stack_has_x():
        stack_push(0)  # suggest:  0 Dup
    else:

        x = stack_peek()
        stack_push(x)


def do_clone_y():  # a la Forth "OVER", a la HP "RCL Y"
    """Push Y X Y in place of Y X"""  # chain bin ops at:  Y X  Over %  Over %  ...

    if not stack_has_x():
        stack_push(1)  # suggest:  1 0 Over, else 0 Over
    elif not stack_has_y():
        stack_push(0)
    else:

        (y, x) = stack_peek(2)
        stack_push(y)


def do_swap_y_x():
    """Drag the 2nd-to-Last Value to Top of Stack"""

    if not stack_has_x():
        stack_push(0)
    elif not stack_has_y():
        stack_push(0)
    else:

        pairs = stack_pairs_peek(2)
        pair = pairs[0]
        (basename, _) = pair

        shbasename = byo.shlex_dquote(basename)

        shline = "touch {}".format(shbasename)
        if basename.startswith("-"):
            shline = "touch -- {}".format(shbasename)

        byo.stderr_print("+ {}".format(shline))
        byo.subprocess_run_stdio(shline)


def stack_has_x():
    """Say when the Stack contains one or more Values (that is, when it is Truthy)"""

    has_x = bool(stack_depth())

    return has_x


def stack_has_y():
    """Say when the Stack contains two or more Values"""

    has_y = stack_depth() >= 2

    return has_y


def stack_depth():
    """Count the Values in the Stack"""

    pairs = stack_pairs_peek(0)  # todo: cache vs evalling for depth and again for use
    depth = len(pairs)

    return depth


#
# Adapt the Json File Format
#
#   Serialize what 'json.dumps' knows how to serialize
#   Serialize some of what Python Repr knows how to serialize too
#   Give out some of the Basenames that Python Str knows how to choose
#


def stackable_dotted_eval(py):
    """Call 'stackable_eval' but lazily import the Module it most obviously needs"""

    # Accept a few established Module Nicknames

    by_nickname = dict()

    by_nickname["D"] = "decimal"
    by_nickname["dt"] = "datetime"
    by_nickname["pd"] = "pandas"

    # Import the module now, if not cached earlier

    words = py.split(".")

    nickname = words[0]
    modulename = by_nickname[nickname] if (nickname in by_nickname.keys()) else nickname

    if nickname not in globals().keys():
        imported = None

        if modulename in sys.modules.keys():

            imported = sys.modules[modulename]

        else:

            try:
                imported = importlib.import_module(modulename)
            except ImportError:
                pass

        if imported:
            assert imported is sys.modules[modulename], imported
            globals()[nickname] = imported

    # Eval the Dotted Name and push its Value

    evalled = stackable_eval(py)

    return evalled


def stackable_eval(py):
    """Eval a Python expression & return its Value, else Stderr Print & Exit Nonzero"""

    try:
        evalled = eval(py)
    except Exception as exc:

        byo.exit_after_print_raise(exc)

    return evalled


def stackable_dumps(value):
    """Format an Object as Chars"""

    try:
        poke = json.dumps(value)
    except TypeError:
        repr_value = repr(value)

        poke = repr_value
        if not isinstance(value, complex):
            repr_py = repr(repr_value)
            poke = "eval({})".format(repr_py)
            # such as eval('datetime.datetime(2022, 7, 24, 16, 4, 7, 624925)')

    return poke


def stackable_loads(chars):
    """Unwrap the Object inside the Chars, else return None"""

    try:
        peek = json.loads(chars)
    except json.JSONDecodeError:

        prefix = "eval("
        suffix = ")"
        if chars.startswith(prefix) and chars.endswith(suffix):
            repr_py = chars[len(prefix) : -len(suffix)]

            py = ast.literal_eval(repr_py)

            peek = stackable_dotted_eval(py)

        else:  # todo:  much too weak reasons to conclude is Rep of Complex

            try:
                peek = complex(chars)
            except ValueError:
                peek = None  # todo: could:  raise ValueError(chars)

    return peek


def stackable_pair(value):
    """Name the Print's of an Object"""

    if isinstance(value, complex):
        assert not isinstance(value, collections.abc.Container)
        pair = stackable_pair_of_complex(value)

        return pair

    if isinstance(value, float):
        assert not isinstance(value, collections.abc.Container)
        pair = stackable_pair_of_float(value)

        return pair

    if isinstance(value, str):
        assert isinstance(value, collections.abc.Container)
        basename = value
        pair = (basename, value)

        return pair

    if isinstance(value, collections.abc.Container):
        basename = byo.dotted_typename(type(value))
        pair = (basename, value)

        return pair

    basename = str(value)
    pair = (basename, value)

    return pair


def stackable_pair_of_float(value):
    """Give a Basename to Float's, and snap out extreme precision"""

    basename = None
    alt_value = value

    # Give mixed case Basename's to the named Float's

    for str_float in ("-Inf", "NaN", "Inf"):
        if str(value) == str_float.lower():
            basename = str_float

    # Snap Float to Int

    if basename is None:
        int_value = int(value)
        if abs(value - int_value) < EPSILON:
            alt_value = int_value
            basename = str(alt_value)

    # Snap most of the precision out of the Basename

    if basename is None:
        basename = str(round(value, FILENAME_PRECISION_3))

    # Succeed

    assert basename

    pair = (basename, alt_value)

    return pair

    # such as '-0.0' to 0, at:  = 0 -1 /
    # such as '...' to 2.0000000000000004 at:  = 2 , sqrt , * -


def stackable_pair_of_complex(value):
    """Give a Basename to Complex'es, and snap out extreme precision"""

    alt_value = value

    # Snap the Complex to Int, in its Real dimension, in its Imag, or in both

    real = value.real
    alt_real = int(real) if (abs(real - int(real)) < EPSILON) else real

    imag = value.imag
    alt_imag = int(imag) if (abs(imag - int(imag)) < EPSILON) else imag

    # Drop the Imag when it bumps against Zero

    if not alt_imag:
        alt_value = alt_real
    elif (alt_real != value.real) or (alt_imag != value.imag):
        alt_value = complex(alt_real, imag=alt_imag)

    basename = str(alt_value).replace("j", SH_J)

    # Succeed

    pair = (basename, alt_value)

    return pair

    # such as '(-1+0j)' to -1, at:  = j j *
    # such as '-1+1.2246467991473532e-16' to -1 at:  = e i pi * pow
    # such as '2.220446049250313e-16+1j' to 1j at:  = j sqrt , *


#
# Build a Stack out of Recently Touched Files in Cwd that contain Stackable LoadS
#


def stack_pop(depth=1, asif_before_rm=""):
    """Peek and eval and remove some of the Values most recently pushed"""

    peeks = stack_peek(depth)

    _ = stack_pairs_pop(depth, asif_before_rm=asif_before_rm)

    return peeks  # will be 'one_peek' in the corner of 'depth=1'


def stack_peek(depth=1):
    """Peek and eval some of the Values most recently pushed"""

    assert depth >= 0

    alt_depth = depth if depth else stack_depth()

    pairs = stack_pairs_peek(alt_depth)
    values = list(_[-1] for _ in pairs)

    peeks = list()
    for value in values:
        peek = stackable_loads(chars=value)
        peeks.append(peek)

    assert len(peeks) == alt_depth, (len(peeks), alt_depth)
    if depth == 1:  # only if 'depth == 1', not also if 'alt_depth == 1'
        one_peek = peeks[-1]

        return one_peek  # is 'one_peek' in the corner of 'depth=1'

    return peeks  # is zero, two, or more Peeks, in the corners of 'depth != 1'


def stack_pairs_pop(depth, asif_before_rm=""):
    """Peek and remove some of the Basename-Chars Pairs most recently pushed"""

    assert depth >= 0

    # Collect the work to do

    pairs = stack_pairs_peek(depth)

    paths = list(_[0] for _ in pairs)
    shpaths = " ".join(byo.shlex_dquote(_) for _ in paths if _ is not None)
    if shpaths:
        if any(_.startswith("-") for _ in paths):
            shline = "rm -f -- {}".format(shpaths)
        else:
            shline = "rm -f {}".format(shpaths)

        # Trace the work, and do the work

        byo.stderr_print("+ {}{}".format(asif_before_rm.format(shpaths), shline))
        byo.subprocess_run_stdio(shline, stdout=subprocess.PIPE, check=True)

    return pairs


def stack_pairs_peek(depth=1):
    """Peek at some of the Basename-Chars Pairs most recently pushed"""

    assert depth >= 0

    # List Filenames by Modified Ascending

    shline = "ls -1art"
    run = byo.subprocess_run_stdio(shline, stdout=subprocess.PIPE, check=True)
    stdout = run.stdout.decode()
    lines = stdout.splitlines()

    filenames = lines

    # Visit each File

    pairs = list()

    for filename in filenames:
        path = pathlib.Path(filename)
        if path.is_file():

            chars = path.read_text()
            chars = chars.rstrip()

            # Count the File only if it holds an intelligible Value

            peek = stackable_loads(chars)
            if peek is None:  # such as json.JSONDecodeError

                continue

            pair = (str(path), chars)
            pairs.append(pair)

    # Limit the Depth peeked, except reserve Depth 0 to mean No Limit

    if depth:
        pairs = pairs[-depth:]  # todo: stop evalling more Pairs than needed

        assert len(pairs) == depth, len(pairs)

    return pairs


def stack_push(value):
    """Push the Json Chars of a Value, into a new Autonamed File"""

    (basename, alt_value) = stackable_pair(value)

    stack_push_basename_alt_value(basename, value=value, alt_value=alt_value)


def stack_push_basename_alt_value(basename, value, alt_value):
    """Push the Json Chars of a Value, into a fresh File"""

    # Choose the given Basename, else the next that doesn't already exist

    path = pathlib.Path(basename)

    alt_path = path
    if path.exists():
        alt_path = find_alt_path(path)

    alt_shpath = byo.shlex_dquote(str(alt_path))

    # Trace and run

    alt_chars = stackable_dumps(alt_value)
    alt_shvalue = byo.shlex_dquote(alt_chars)

    alt_shcomment = "  # {!r}".format(value) if (repr(alt_value) != repr(value)) else ""

    echo_shline = "echo {} >{}{}".format(alt_shvalue, alt_shpath, alt_shcomment)
    byo.stderr_print("+ {}".format(echo_shline))

    with open(alt_path, "w") as writing:
        writing.write("{}\n".format(alt_chars))


def find_alt_path(path):
    """Find the next Basename that doesn't already exist in the Dir"""

    alt_path = pathlib.Path("{}~".format(path))  # the 0th Alt

    index = 1
    while alt_path.exists():
        alt_path = pathlib.Path("{}~{}~".format(path, index))

        index += 1

    return alt_path


#
# Take Double-Click's of Dot-Command ButtonFile's
#


def parms_buttonfile(parms):
    """Take one Double-Click of a Dot-Command ButtonFile"""

    while parms[1:]:

        try:

            try_buttonfile(parms)

        except Exception:
            byo.stderr_print()
            traceback.print_exc()
            byo.stderr_print("Press ⌃D TTY EOF to quit\n")

            sys.stdin.read()

            raise

        parms[::] = parms[1:]

        parms.insert(0, "buttonfile")


def try_buttonfile(parms):
    """Run the Name of a Dot-Command ButtonFile, without its Ext, as a Word"""

    assert parms

    # Take the Name, without its Ext, as a Word

    main_file = parms.pop(1)

    basename = os.path.basename(main_file)
    (root, ext) = os.path.splitext(basename)
    _ = ext

    # Run the Word

    entry = peek_entry_else()

    word = root
    ch = word if (len(word) == 1) else None

    if (entry is not None) and (word in ("pi", STR_PI)):  # π
        entry_write_char("π")
    elif ch and (ch in "0123456789IJij"):  # FIXME: E e + -
        entry_write_char("j" if (ch.lower() in "ij") else ch.lower())
    elif word in (".", "dot"):
        entry_write_char(".")
    elif word in (",", "comma"):
        do_comma()  # does its own 'entry_close_if_open()'

    elif word == "clear":

        try_buttonfile_clear()

    else:

        entry_close_if_open()
        parms_run(parms=[word])


def try_buttonfile_clear():
    """Pop X till no more X, else push 3, 2, 1, 0"""

    pairs = stack_pairs_pop(depth=0)
    if not pairs:
        stack_push(3)
        stack_push(2)
        stack_push(1)
        stack_push(0)


def do_comma():
    """Open Entry if no Entry open, else dupe Top of Stack"""

    entry = entry_close_if_open()

    if entry is None:
        if not stack_has_x():
            entry_write_char("")
        else:
            do_clone_x()  # a la Forth "DUP", a la HP "Enter"


def entry_write_char(ch):
    """Take a Char into the Entry"""

    # Peek the Entry

    entry = peek_entry_else()
    old_entry = "" if (entry is None) else entry

    # Shrink or Edit or Start or Grow the Entry

    if ch == STR_PI:  # π
        new_entry = old_entry[:-1]  # Pi = Delete = Backspace = Drop the last Char

    elif ch in ".j":  # Keep at most 1 of a "." Decimal Dot or a "j" Math J
        if not old_entry:
            new_entry = ch  # Start it on
        elif not old_entry.endswith(ch):
            new_entry = old_entry.replace(ch, "") + ch  # Warp it to the tail end
        else:
            new_entry = old_entry[:-1]  # Toggle it off

    elif not old_entry:  # Start the Entry
        new_entry = ch

    else:  # Grow the Entry
        new_entry = old_entry + ch

    # Keep the "j", if any, at the far end of the Entry

    evallable = new_entry
    if "j" in new_entry:
        if not new_entry.endswith("j"):
            evallable = new_entry.replace("j", "") + "j"

    # Mark the Entry apart, as an Entry, by ending it with "_"

    pushable = evallable + "_"
    if evallable == ".":
        pushable = "_._"

    # Replace the Entry, else start the Entry

    if entry is not None:
        _ = stack_pop(1)

    stack_push(pushable)


def entry_close_if_open():
    """Return an Unevalled Copy of the Entry, but replace it with its Eval"""

    # Report either of the two kinds of Got No Entry

    if not stack_has_x():  # Empty Stack

        return None

    entry = peek_entry()  # Top of Stack is Not an Entry
    if entry is None:

        return None

    # Replace the Entry with its Eval
    # Accept its whole precision, don't snap off excess precision this early

    try:
        evalled = int(entry)
    except ValueError:
        try:
            evalled = float(entry)
        except ValueError:
            try:
                evalled = complex(entry)
            except ValueError:
                assert entry == "", repr(entry)

                evalled = None  # Delete the Entry and don't replace it, if Empty Entry

    _ = stack_pop(1)

    if evalled is not None:
        stack_push(evalled)

    # Return an Unevalled Copy of the Entry

    return entry


def peek_entry_else():
    """Peek the collected Chars and return them, else None"""

    entry = None
    if stack_has_x():
        entry = peek_entry()

    return entry


def peek_entry():
    """Peek the collected Chars and return them"""

    ENTRY_REGEX = "({}|{}|[.]|[Jj]|)?".format(FLOAT_REGEX, INT_REGEX)
    CLOSED_ENTRY_REGEX = r"^" + ENTRY_REGEX + r"$"

    if stack_has_x():

        pair = stack_pairs_peek()[-1]
        (basename, value) = pair

        if basename is not None:
            if basename.endswith("_"):
                basename_json = stackable_dumps(basename)
                if basename_json == value:

                    entry_chars = stackable_loads(value)
                    assert entry_chars is not None, repr(value)

                    entry = byo.str_removesuffix(entry_chars, suffix="_")
                    if entry_chars == "_._":
                        entry = "."

                    if re.match(CLOSED_ENTRY_REGEX, string=entry):

                        return entry


#
# Track dreams
#


_ = """

leading data type for the result
trailing data type for the op

bits = hex, oct, or bin

bits / to rotate right & >> |
bits * to rotate left & << |
bits + for bits |
bits - for bits &

bits √ for bits ~

bits y^x pow for bits ^
dec y^x pow for **

"""


_ = """

dot plus = dec
dot minus = hex
dot star = oct
dot slash = bin

changing base
reopens as entry
closes as tuple of (type, value)

0x_
lower 'x' but upper nybbles

A B C D E F keys - first class, not mapped

"""


#
# Run from the Command Line, when not imported into some other Main module
#


if __name__ == "__main__":
    main()


# posted into:  https://github.com/pelavarre/byobash/blob/main/bin/byopyvm.py
# copied from:  git clone https://github.com/pelavarre/byobash.git
