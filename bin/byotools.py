#!/usr/bin/env python3

# deffed in many packages  # missing from:  https://pypi.org

"""
usage: import byotools as byo  # define Func's
usage: python3 bin/byotools.py  # run Self-Test's

bundle the Python you need to make Sh welcome you sincerely and competently

examples:
  byo.exit()  # takes no Parms to print Examples, '--help' to print Help, else just work
  byo.exit(__name__)  # like 'byo.exit()' but returns without exit when imported
  byo.exit(shparms="--")  # like 'byo.exit()' but returns when the only Parm is '--'
"""


import __main__
import argparse
import datetime as dt
import difflib
import os
import pathlib
import pdb
import re
import select
import shlex
import shutil
import signal
import string
import subprocess
import sys
import textwrap

DEFAULT_NONE = None

_ = pdb

_ = subprocess.run  # new since Sep/2015 Python 3.5
_ = dt.datetime.now().astimezone()  # new since Dec/2016 Python 3.6
# _ = importlib.import_module("dataclasses")  # new since Jun/2018 Python 3.7
# _ = f"{sys.version_info[:3]=}"  # new since Oct/2019 Python 3.8
# _ = shlex.join  # new since Oct/2019 Python 3.8
# _ = str.removesuffix  # new since Oct/2020 Python 3.9
# _  = list(zip([], [], strict=True))  # since Oct/2021 Python 3.10


# todo: push 'def exit' variations as missing from 'import argparse/sys'


#
# Welcome Examples at 'p.py', Notes at 'p.py --h', & Preferences/ Setup at 'p.py --';
# else exit after calling Subprocess of Sh Path;
# else exit nonzero for rare usage
#


def exit(name=None, shparms=None):
    """Exit after printing TestDoc, or ArgDoc, or running a Subprocess, else return"""

    parms = sys.argv[1:]

    # Return if imported, not called to run as the Main Module

    if name is not None:
        if name != "__main__":

            return

    # Return if given ShParms that the Caller wants to take

    if shparms is not None:
        wants = shlex.split(shparms)
        if parms == wants:

            return

    # Exit after printing the Test Doc of the Arg Doc, for no Parms

    exit_if_testdoc()

    # Exit after printing the Arg Doc, for '--help' or '--hel' or ... '--h' before '--'

    exit_if_argdoc()

    # Exit after calling Subprocess of Sh Path, else exit nonzero for rare usage

    exit_after_shverb()


#
# Welcome Examples at 'p.py', Notes at 'p.py --h', & Preferences/ Setup at 'p.py --'
#


def exit_if_testdoc():
    """Exit after printing last Graf, if no Parms"""

    parms = sys.argv[1:]

    _ = fetch_testdoc()  # always fetches, sometimes prints

    if not parms:

        exit_after_testdoc()


def exit_after_testdoc():
    """Exit after printing a TestDoc of Examples"""

    testdoc = fetch_testdoc()

    print()
    print(testdoc.strip())  # frames with 1 Empty Line above, and 1 Empty Line below
    print()

    sys.exit(0)  # exits 0 after printing Help Lines


def fetch_testdoc():
    """Fetch the TestDoc of Examples"""

    # Collect many Args

    argdoc = fetch_argdoc()

    grafs = str_splitgrafs(argdoc)
    last_graf = grafs[-1]

    tests = str_ripgraf(last_graf)
    tests = list_strip(tests)
    testdoc = "\n".join(tests)

    # Choose a local End-of-ShLine Comment Style, for Paste of Sh Command Lines

    env_ps1 = os.environ.get("PS1", DEFAULT_NONE)
    env_zsh = env_ps1.strip().endswith("%#") if env_ps1 else False

    sh_testdoc = testdoc
    if env_zsh:
        sh_testdoc = _sh_testdoc_to_zsh_testdoc(testdoc)

    # Suceed

    return sh_testdoc


def _sh_testdoc_to_zsh_testdoc(testdoc):
    """Reformat a classic Sh TestDoc to work inside Zsh UnSetOpt InteractiveComments"""

    zsh_lines = list()
    for line in testdoc.splitlines():
        (before, mark, after) = line.partition("  # ")

        zsh_line = line
        if mark:
            enough = after
            enough = enough.replace("#", ".")
            enough = re.sub(r"'[^'\\]*'", repl=".", string=enough)
            enough = re.sub(r"{[^,]*}", repl=".", string=enough)

            rep_after = " # {!r}".format(after)
            try:
                enough_argv = shlex.split(enough)
                if enough_argv != list(shlex_dquote(_) for _ in enough_argv):
                    rep_after = after
            except ValueError:
                pass

            zsh_line = "{}  &&: {}".format(before, rep_after)

        zsh_lines.append(zsh_line)

    zsh_testdoc = "\n".join(zsh_lines)

    return zsh_testdoc


#
# Welcome Notes at 'p.py --h'
#


def exit_if_argdoc():
    """Exit after printing ArgDoc, if '--help' or '--hel' or ... '--h' before '--'"""

    parms = sys.argv[1:]

    _ = fetch_argdoc()  # always fetches, sometimes prints

    if shlex_parms_want_help(parms):

        exit_after_argdoc()


def fetch_argdoc():
    """Fetch the ArgDoc of Help Lines"""

    main_doc = __main__.__doc__

    filename = os.path.basename(__main__.__file__)
    alt_main_doc = ALT_MAIN_DOC.replace("p.py", filename)

    argdoc = alt_main_doc if (main_doc is None) else main_doc

    return argdoc


def exit_after_argdoc():
    """Exit after printing an ArgDoc of Help Lines"""

    argdoc = fetch_argdoc()  # always fetches, sometimes prints

    print()
    print()
    print(argdoc.strip())  # frames with 2 Empty Lines above, and 2 Empty Lines below
    print()
    print()

    sys.exit(0)  # exits 0 after printing Help Lines


#
# Welcome Preferences at 'p.py --', and Preference else Setup at 'command p.py --'
#


def exit_if_patchdoc(fetched_patchdoc):
    """Exit after printing PatchDoc, if "--" is the only Parm"""

    parms = sys.argv[1:]

    _ = fetch_patchdoc(fetched_patchdoc)  # always fetches, sometimes prints

    if parms == ["--"]:

        exit_after_patchdoc(fetched_patchdoc)


def exit_after_patchdoc(fetched_patchdoc):
    """Exit after printing a PatchDoc of how to poke the Memory of the Sh Process"""

    patchdoc = fetch_patchdoc(fetched_patchdoc)

    print()
    print(patchdoc.strip())  # frames with  1 Empty Line above, and 1 Empty Line below
    print()

    sys.exit(0)  # exits 0 after printing Help Lines


def fetch_patchdoc(fetched_patchdoc):  # todo: pick the PatchDoc out of the ArgDoc
    """Fetch the PatchDoc of how to poke the Memory of the Sh Process"""

    # Collect many Args

    argdoc = fetch_argdoc()

    patchdoc = fetched_patchdoc
    patchdoc = textwrap.dedent(patchdoc)
    patchdoc = patchdoc.strip()
    dented_patchdoc = textwrap.indent(patchdoc, "  ")

    # Demand one accurate copy of the PatchDoc in the ArgDoc
    # Hope it doesn't have more Lines before or after it that we wrongly drop here

    assert dented_patchdoc in argdoc

    # Demand one accurate copy of the PatchDoc in the DotFiles
    # Again hope it doesn't have more Lines before or after it that we wrongly drop here

    bin_dir = os.path.dirname(__file__)
    dotfiles_dir = os.path.join(bin_dir, os.pardir, "dotfiles")
    pathname = os.path.join(dotfiles_dir, "dot.byo.bashrc")

    path = pathlib.Path(pathname)
    dotfiles_doc = path.read_text()

    assert patchdoc in dotfiles_doc  # else you need:  vi dotfiles/dot.byo.bashrc

    # Succeed

    return patchdoc


#
# Else exit after calling Subprocess of Sh Path, else exit nonzero for rare usage
#


def exit_if_rare_parms(shline, parms):
    """Exit 2 for rare usage if Parms truthy, else return"""

    if not parms:

        return

    shparms = shlex_djoin(parms)
    stderr_print("{}: ERROR: unrecognized arguments: {}".format(shline, shparms))

    sys.exit(2)  # exits 2 for rare usage


def exit_after_shverb():
    """Exit after calling Subprocess of Sh Path, else exit nonzero for rare usage"""

    # Exit after calling Subprocess, if dropping the Py Ext Mark finds a Sh Verb

    exit_if_shverb(argv=sys.argv)

    # Else complain and exit 2 for rare usage

    main_py_basename = os.path.basename(sys.argv[0])
    shverb = str_removesuffix(main_py_basename, suffix=".py")

    stderr_print(
        "{}: ERROR: called while no {!r} found in Sh Path".format(
            main_py_basename, shverb
        )
    )

    sys.exit(2)  # exits 2 for rare usage


def exit_if_shverb(argv):
    """Exit after calling Subprocess, if dropping the Py Ext Mark finds a Sh Verb"""

    alt_argv = sys.argv if (argv is None) else argv

    # Drop the Py Ext Mark

    main_py_basename = os.path.basename(alt_argv[0])

    (root, ext) = os.path.splitext(main_py_basename)  # Ext may be empty

    shverb = root
    shverb_argv = [shverb] + list(alt_argv[1:])

    # Actually quit early, don't exit, when Sh Verb not found in Sh Path

    which = shutil.which(shverb)
    if which is None:

        return

    if os.path.realpath(which) == os.path.realpath(sys.argv[0]):
        stderr_print(
            "byotools.py: declining to recurse through:  which -a {!r}".format(shverb)
        )

        return

    # Else exit after calling Subprocess

    exit_after_one_argv(argv=shverb_argv)


def exit_after_some_argv(argvs):
    """Run the ArgV's in order, till exit nonzero, else exit zero after the last one"""

    for argv in argvs:
        subprocess_run_loud(argv, stdin=None)  # todo: when to chop off Tty Stdin

    sys.exit()  # exits None after every ArgV exits Falsey


def exit_after_one_argv(argv):
    """Call a Subprocess to run the ArgV, and then exit"""

    subprocess_run_loud(argv, stdin=None)  # todo: when to chop off Tty Stdin

    sys.exit()  # exits None after an ArgV exits Falsey


def exit_after_print_raise(exc):
    """Stderr Print the Exec and then Exit Nonzero"""

    typename = class_fullname(type(exc))
    str_exc = str(exc)
    if not str_exc:
        str_raise = "byotools.py: {}".format(typename)
    else:
        str_raise = "byotools.py: {}: {}".format(typename, exc)

    stderr_print(str_raise)

    sys.exit(1)  # exits 1 for Unhandled Exception


#
# Start dreaming of compacting ShLine's well
#


# todo: def shlex_compact(shline), shlex_compact(argv)


def os_path_homepath(path):
    """Return the Path relative to Env Home if below Env Home, else the AbsPath"""

    absname = os.path.abspath(path)

    env_home = os.environ["HOME"]
    if (absname == env_home) or absname.startswith(env_home + os.sep):
        home_relname = "~" + os.sep + os.path.relpath(absname, start=env_home)

        return home_relname

    return absname


def os_path_shortpath(path):
    """Return the shortest of the AbsPath, the RelPath, and the HomePath"""

    names = list()

    absname = os.path.abspath(path)
    names.append(absname)

    cwd = os.getcwd()
    if (absname == cwd) or absname.startswith(cwd + os.sep):
        cwd_relname = os.path.relpath(absname, start=cwd)
        names.append(cwd_relname)

    env_home = os.environ["HOME"]
    if (absname == env_home) or absname.startswith(env_home + os.sep):
        home_relname = "~" + os.sep + os.path.relpath(absname, start=env_home)
        names.append(home_relname)

    names.sort(key=lambda _: (len(_), _))

    concise = names[0]
    return concise


class ShPath:
    """Wrap a Sh Path to print it more concisely"""

    def __init__(self, pathname):
        self.pathname = pathname

    def __str__(self):
        shortpath = os_path_shortpath(self.pathname)
        shpath = shlex.quote(shortpath)

        return shpath

    # could depend on '@dataclasses.dataclass', since Jun/2018 Python 3.7


#
# Add some Def's to Class'es
#


# deffed in many files  # missing from docs.python.org
def class_fullname(cls):
    """Return the 'module.type' name for most types, but 'type' for 'builtins.type's"""

    modulename = cls.__module__
    typename = cls.__name__
    wholename = "{}.{}".format(modulename, typename)

    fullname = typename
    if modulename != "builtins":
        fullname = wholename

    return fullname

    # such as the fullname 'OSError', or the dotted fullname 'io.UnsupportedOperation',
    # but never the whole name 'builtins.OSError'


# deffed in many files  # missing from docs.python.org
def class_mro_join(cls):
    """Format the list of Class'es searched for Attributes missing from the Instance"""

    mro = cls.__mro__
    join = " else ".join(class_fullname(_) for _ in mro)

    return join

    # such as 'io.UnsupportedOperation else OSError else ValueError ... else object'


#
# Add some Def's to List's
#


# deffed in many files  # missing from docs.python.org
def list_strip(items):
    """Drop the leading and trailing Falsey Items"""

    # Find the leftmost Truthy Item, else 0

    index = 0
    while items[index:]:
        if items[index]:

            break

        index += 1

    # Find the rightmost Truthy Item, else -1

    rindex = -1
    while items[:rindex]:
        if items[rindex]:

            break

        rindex -= 1

    # Drop the leading and trailing Falsey Items,
    # by way of picking all the Items from leftmost through rightmost Truthy Item

    lstrip = items[index:]
    strip = lstrip[: (rindex + 1)] if (rindex < -1) else lstrip

    return strip


#
# Add some Def's to Str's and Byte's,
# partly because not found in 'import textwrap'
#


# deffed in many files  # missing from docs.python.org
def str_ldent(chars):  # kin to 'str.lstrip'
    """Pick out the Spaces etc, at left of some Chars"""

    lstrip = chars.lstrip()
    length = len(chars) - len(lstrip)
    dent = chars[:length] if lstrip else ""

    return dent


def str_ripgraf(graf):
    """Pick the lines below the head line of a paragraph, and dedent them"""

    grafdoc = "\n".join(graf[1:])
    grafdoc = textwrap.dedent(grafdoc)
    graf = grafdoc.splitlines()

    return graf


# deffed in many files  # missing from docs.python.org
def str_removeprefix(chars, prefix):  # missing from Python till Oct/2020 Python 3.9
    """Remove Prefix from Chars if present"""

    result = chars
    if chars.startswith(prefix):
        result = chars[len(prefix) :]

    return result


# deffed in many files  # missing from docs.python.org
bytes_removeprefix = str_removeprefix


# deffed in many files  # missing from docs.python.org
def str_removesuffix(chars, suffix):  # missing from Python till Oct/2020 Python 3.9
    """Remove Suffix from Chars if present"""

    result = chars
    if chars.endswith(suffix):
        result = chars[: -len(suffix)]

    return result


# deffed in many files  # missing from docs.python.org
bytes_removesuffix = str_removesuffix


def str_splitgrafs(doc, keepends=False):  # todo:
    """Form a List of every Paragraph of Lines, out of a DocString"""

    assert not keepends  # todo: develop keepends=True

    grafs = list()

    lines = doc.splitlines()

    graf = list()
    for line in lines:

        # Add an Empty Line

        if not line:
            if graf:

                graf.append(line)

        # Add a More Dented Line

        elif graf and (len(str_ldent(line)) > len(str_ldent(graf[0]))):

            graf.append(line)

        # Strip and close this Graf, and pick it up if it's not Empty

        else:
            strip = list_strip(graf)
            if strip:

                grafs.append(strip)

            # Open the next Graf, with a No More Dented Line, else as Empty

            graf = list()
            if line:

                graf.append(line)

    # Strip and close the last Graf too, and pick it up too if it's not Empty

    strip = list_strip(graf)
    if strip:

        grafs.append(strip)

    return grafs


#
# Add some Def's that 'import argparse' forgot
#


# deffed in many files  # missing from docs.python.org
def compile_epi_argdoc(epi, add_help=True):
    """Form an ArgumentParser from Main Doc, without Positional Args or Options"""

    doc = __main__.__doc__
    doclines = doc.strip().splitlines()
    usage = doclines[0]

    prog = usage.split()[1]  # second word of leading line of first paragraph

    doc_headlines = list(_ for _ in doclines if _ and (_ == _.lstrip()))
    description = doc_headlines[1]  # leading line of second paragraph

    epilog_at = doc.index(epi)
    epilog = doc[epilog_at:]

    parser = argparse.ArgumentParser(
        prog=prog,
        description=description,
        add_help=add_help,  # without Options other than the "-h". "--h", "--he", etc
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=epilog,
    )

    return parser


def compile_pos_argdoc(epi, add_help=True):
    """Form an ArgumentParser from Main Doc, with exactly 1 Positional Arg"""

    # Form an ArgumentParser from Main Doc, without Positional Args or Options

    parser = compile_epi_argdoc(epi)

    # Fetch Main Doc

    doc = __main__.__doc__
    doclines = doc.strip().splitlines()

    usage = doclines[0]
    prog = usage.split()[1]

    # Require 1 Positional Arg

    matched = re.match(r"^usage: {} \[-h\] [^ ]*$".format(prog), string=usage)
    assert matched, usage

    argname = usage.split()[-1]
    argname = argname.strip("[").strip("]")

    # Pick out the 1 Positional Arg Line

    wordlines = list(_ for _ in doclines if _.split())
    arglines = list(_ for _ in wordlines if _.split()[0] == argname)

    assert arglines
    assert len(arglines) == 1, arglines
    argline = arglines[-1]

    # Pick out the Help Words

    arghelp = argline
    prefix = "  " + argname
    arghelp = str_removeprefix(arghelp, prefix=prefix)
    arghelp = arghelp.strip()

    # Pick out the NArgs

    nargs_one = argname
    nargs_query = "[{}]".format(argname)

    if usage.endswith(nargs_one):
        nargs = 1
    elif usage.endswith(nargs_query):
        nargs = argparse.OPTIONAL  # "?"
    else:
        assert False

    # Declare the 1 Positional Arg

    if nargs == 1:
        parser.add_argument(argname.casefold(), metavar=argname, help=arghelp)
    else:
        parser.add_argument(
            argname.casefold(), nargs=argparse.OPTIONAL, metavar=argname, help=arghelp
        )

    # Succeed

    return parser


# deffed in many files  # missing from docs.python.org
def exit_unless_doc_eq(doc, parser):
    """Exit nonzero, unless Doc equals Parser Format_Help"""

    # Fetch the Parser Doc from a fitting virtual Terminal
    # Fetch from a Black Terminal of 89 columns, not current Terminal width
    # Fetch from later Python of "options:", not earlier Python of "optional arguments:"

    with_columns = os.getenv("COLUMNS")
    os.environ["COLUMNS"] = str(89)
    try:

        parser_doc = parser.format_help()

    finally:
        if with_columns is None:
            os.environ.pop("COLUMNS")
        else:
            os.environ["COLUMNS"] = with_columns

    parser_doc = parser_doc.replace("optional arguments:", "options:")

    # Fetch the Main Doc

    file_filename = os.path.split(__file__)[-1]

    main_doc = __main__.__doc__.strip()

    got = main_doc
    got_filename = "{} --help".format(file_filename)
    want = parser_doc
    want_filename = "argparse.ArgumentParser(..."

    # Print the Diff to Parser Doc from Main Doc and exit, if Diff exists

    difflines = list(
        difflib.unified_diff(
            a=got.splitlines(),
            b=want.splitlines(),
            fromfile=got_filename,
            tofile=want_filename,
        )
    )

    if difflines:
        print("\n".join(difflines))

        sys.exit(1)  # trusts the caller to log SystemExit exceptions well


def parse_epi_args(epi):
    """Parse Sh Command Line as per Main Doc, except Exit for Help or No Args"""

    # Scrape the Parser out of the Main Doc

    parser = compile_pos_argdoc(epi)

    doc = __main__.__doc__
    try:
        exit_unless_doc_eq(doc, parser=parser)
    except SystemExit:
        print("byotools.py: ERROR: Main Doc and ArgParse Parser disagree")

        raise

    # Exit after Print of TestDoc, if given no Sh Parms

    parms = sys.argv[1:]
    if not parms:

        exit_after_testdoc()

    # Parse the Sh Parms

    args = parser.parse_args(args=parms)

    # Succeed

    return args


#
# Add some Def's that 'import datetime' forgot
#


DTZ_FORMAT_ISO_ISH = "%Y-%m-%d %H:%M:%S.%f%z"
# such as '1999-12-31 12:59:59.999999+00:00'
# per https://en.wikipedia.org/wiki/ISO_8601


def dtz_datetime_now(tzinfo=None):  # default to local, not to 'dt.datetime.now()' naive
    """Say when Now is, in the Time Zone, else locally"""

    now = dt.datetime.now(dt.timezone.utc).astimezone(tz=tzinfo)

    return now

    # now = byo.dtz_datetime_now()
    # print(now.utcoffset(), now.tzname())  # -1 day, 17:00:00 PDT
    # print(now.replace(tzinfo=None))  # 2022-09-03 15:22:42.099651


def dtz_datetime_today_morning(tzinfo=None):
    """Say when Midnight was, in the Time Zone, else locally"""

    now = dt.datetime.now(dt.timezone.utc).astimezone(tzinfo)
    replace = now.replace(hour=0, minute=0, second=0, microsecond=0)

    return replace

    # today_morning = byo.dtz_datetime_today_morning()
    # print(today_morning)  # 2022-09-03 00:00:00-07:00  # local midnight, zoned
    # print(dt.datetime.today())  # 2022-09-03 15:51:21.128116  # naive, & not midnight

    # print(byo.dtz_datetime_today_morning(tzinfo=dt.timezone(dt.timedelta(hours=5.5))))
    # 2022-09-04 00:00:00+05:30  # midnight in chosen timezone


def dtz_strftime(dtz_self, format=DTZ_FORMAT_ISO_ISH):
    """Form a Date String from the DateTime by Format (inverse of StrPTime)"""

    strftime = dtz_self.strftime(format)

    return strftime

    # print(byo.dtz_strftime(dt.datetime.now()))  # 2022-09-03 15:46:59.890232
    # print(byo.dtz_strftime(byo.dtz_datetime_now()))  # 2022-09-03 15:47:00.762070-0700


def dtz_strptime(date_string, format=DTZ_FORMAT_ISO_ISH):
    """Parse a DateTime from the Date String by Format (inverse of StrFTime)"""

    strptime = dt.datetime.strptime(date_string, format)

    return strptime

    # print(byo.dtz_strptime("1999-12-31 12:59:59.999999+00:00"))
    # 1999-12-31 12:59:59.999999+00:00

    # print(byo.dtz_strftime(byo.dtz_strptime("1999-12-31 12:59:59.999999+00:00")))
    # 1999-12-31 12:59:59.999999+0000


#
# Add some Def's that 'import pdb' forgot
#


# deffed in many files  # missing from docs.python.org
def pdb_iobreak_if(flag):
    """Breakpoint after reconnecting Py Stdio to Dev Tty, if Flag is Truthy"""

    if flag:
        pdb_iobreak()


# deffed in many files  # missing from docs.python.org
def pdb_iobreak():
    """Breakpoint after reconnecting Py Stdio to Dev Tty"""

    reading = open("/dev/tty", "r")
    writing = open("/dev/tty", "w")

    sys.stdin = reading
    sys.stdout = writing

    pdb.set_trace()


#
# Add some Def's that 'import shlex' and 'import string' forgot
#


SH_PLAIN = (  # all printable Ascii except not " !#$&()*;<>?[]^`{|}~" and " and ' and \
    "%+,-./"
    + string.digits
    + ":=@"
    + string.ascii_uppercase
    + "_"
    + string.ascii_lowercase
)


SH_QUOTABLE = SH_PLAIN + " " + "!#&()*;<>?[]^{|}~"
# all printable Ascii except not $ Dollar and ` Backtick, and not " and ' and \


# deffed in many files  # missing from docs.python.org
def shlex_djoin(parms):  # see also 'shlex.join' since Oct/2019 Python 3.8
    """Quote, but quote compactly despite '"' and '~', when that's still easy"""

    shline = " ".join(shlex_dquote(_) for _ in parms)

    return shline  # such as:  echo "let's" speak freely, even casually


# deffed in many files  # missing from docs.python.org
def shlex_dquote(parm):
    """Quote 1 Parm, but quote compactly despite '"' and '~', when that's still easy"""

    # Follow the Library, when they agree no quote marks required

    quoted = shlex_quote(parm)
    if quoted[:1] not in ("'", '"'):

        return quoted

    # Accept the ^ Caret when the Parm does start with the ^ Caret
    # Accept the ~ Tilde when the Parm does Not start with the ~ Tilde

    unplain_set = set(parm) - set(SH_PLAIN)

    if parm.startswith("^"):  # forwards the ^ Caret as start of Parm
        unplain_set = set(parm[1:]) - set(SH_PLAIN)

    if not parm.startswith("~"):  # forwards the ~ Tilde if after start of Parm
        unplain_set = unplain_set - set("~")

    if (parm.count("{") == 1) and (parm.count("}") == 1):  # forwards {} wout ,
        head = parm.partition("{")[0]
        tail = parm.rpartition("}")[-1]
        if "," not in (head + tail):  # todo: overly restrictive for:  echo ,}{,
            unplain_set = unplain_set - set("{}")

    unplain_ascii_set = "".join(_ for _ in unplain_set if ord(_) < 0x80)
    if not unplain_ascii_set:

        return parm

    # Try the " DoubleQuote to shrink it

    unquotable_set = set(parm) - set(SH_QUOTABLE) - set("'")
    unquotable_ascii_set = "".join(_ for _ in unquotable_set if ord(_) < 0x80)
    if not unquotable_ascii_set:
        doublequoted = '"' + parm + '"'
        if len(doublequoted) < len(quoted):

            return doublequoted

            # such as:  print(shlex_dquote("i just can't"))  # "i just can't"

    # Give up and settle for the Library's work

    return quoted

    # todo: figure out when the ^ Caret is plain enough to need no quoting
    # todo: figure out when the {} Braces are plain enough to need no quoting
    # todo: figure out when the ! Bang is plain enough to need no quoting

    # todo: figure out when the * ? [ ] are plain enough to need no quoting
    # so long as we're calling Bash not Zsh
    # and the Dirs don't change out beneath us


# deffed in many files  # missing from docs.python.org
def shlex_quote(parm):  # missing from Python till Oct/2019 Python 3.8
    """Mark up 1 Parm with Quote Marks and Backslants, so Sh agrees it is 1 Word"""

    # Trust the library, if available

    if hasattr(shlex, "quote"):
        quoted = shlex.quote(parm)

        return quoted

        # see also:  git rev-parse --sq-quote "i just can't"  # 'i just can'\''t'

    # Emulate the library roughly, because often good enough

    unplain_set = set(parm) - set(SH_PLAIN)
    if not unplain_set:

        return parm

    quoted = repr(parm)  # as if the Py rules agree with Sh rules

    return quoted  # such as:  print(shlex_quote("<=>"))  # the 5 chars '<=>'

    # test results with:  python3 -c 'import sys; print(sys.argv)' ...


def shlex_parms_want_help(parms):
    """Return Truthy if '--help' or '--hel' or ... '--h' before '--'"""

    for parm in parms:
        if parm == "--":  # ignores '--help' etc after '--'

            break

        if parm.startswith("--h") and "--help".startswith(parm):

            return True


def shlex_parms_pop_opt_count(parms, opt):  # todo: add tests of this
    """Pop the usage '[-opt]' out of the Parms"""

    count = 0

    # Visit each Parm, except quit before first "--" Dash-Dash

    for (index, parm) in enumerate(parms):  # commonly taken from:  parms = sys.argv[1:]
        if parm == "--":

            break

        # Find and count and pop the wanted Option

        if parm == opt:

            stop = index + 1
            parms[::] = parms[:index] + parms[stop:]

            count += 1

    # Succeed

    return count


def shlex_parms_pop_option_value(parms, option, enough, const):
    """Pop the usage '[--option [VALUE]]' out of the Parms"""

    main_py_basename = os.path.basename(__main__.__file__)

    # Visit each Parm, except quit before first "--" Dash-Dash

    for (index, parm) in enumerate(parms):  # commonly taken from:  parms = sys.argv[1:]
        if parm == "--":

            break

        # Find the wanted Option, or enough of its Leftmost Chars

        comparable = parm.split("=")[0]
        if comparable.startswith(enough) and option.startswith(comparable):

            # Pick out the Value of this Option

            option_index = index
            option_value = "=".join(parm.split("=")[1:])
            if not option_value:
                if const is not None:
                    option_value = const
                else:
                    option_index = index + 1
                    if option_index < len(parms):
                        option_value = parms[option_index]

                    else:

                        stderr_print(
                            "{}: ERROR: argument {}: expected one argument".format(
                                main_py_basename, option
                            )
                        )

                        sys.exit(2)  # exits 2 for rare usage

            # Pop the Option and its Value too

            stop = option_index + 1
            parms[::] = parms[:index] + parms[stop:]

            # Succeed

            return option_value


def shlex_parms_partition(parms):
    """Split Options from Positional Args, in the classic way of ArgParse and Sh"""

    options = list()
    seps = list()
    words = list()

    for (index, parm) in enumerate(parms):

        # Pick out the First Sep
        # and take the remaining Parms as Positional Args, not as Options

        if parm == "--":
            seps.append(parm)

        # Pick out each Option, before the First Sep

        elif (not seps) and (parm != "-") and parm.startswith("-"):
            options.append(parm)

        # Pick out each Arg, before the First Sep

        else:
            words.append(parm)

    return (options, seps, words)

    #   look deeper into when '---' is an option, like Grep votes '---' is an Arg
    #
    #       % qd |g -e +++ -e ---
    #       + git diff
    #       ('+ grep -i -e +++ -e ---',)
    #       --- a/bin/byotools.py
    #       +++ b/bin/byotools.py
    #       --- a/bin/git.py
    #       +++ b/bin/git.py
    #       --- a/bin/shpipes.py
    #       +++ b/bin/shpipes.py
    #       --- a/todo.txt
    #       +++ b/todo.txt
    #       %
    #


#
# Add some Def's that 'import shutil' forgot
#


# deffed in many files  # missing from docs.python.org
def shutil_get_tty_height():  # from $LINES, else Stdout, else DevTty
    """Count Screen Rows from exported $LINES, else Stdout, else Dev Tty"""

    size = shutil_get_tty_size()

    return size.lines


# deffed in many files  # missing from docs.python.org
def shutil_get_tty_width():  # from $COLUMNS, else Stdout, else DevTty
    """Count Screen Columns from exported $COLUMNS, else Stdout, else Dev Tty"""

    size = shutil_get_tty_size()

    return size.columns


# deffed in many files  # missing from docs.python.org
def shutil_get_tty_size():
    """Count Screen Rows & Columns from $LINES & $COLUMNS, else Stdout, else Dev Tty"""

    if sys.__stdout__.isatty():  # shows how to call simpler 'os.' in place of 'shutil.'
        _ = os.get_terminal_size(sys.__stdout__.fileno())

    with open("/dev/tty", "r") as tty:  # replaces the cheap Fallback of (80, 24)
        fallback_size = os.get_terminal_size(tty.fileno())

    size = shutil.get_terminal_size(fallback=fallback_size)
    # from 'sys.__stdout__', else 'os.environ["LINES"], ["COLUMNS"]', else Fallback

    return size  # (.lines, .columns)


#
# Add some Def's that 'import subprocess' forgot
#


# deffed in many files  # missing from docs.python.org
def subprocess_run_loud(argv, shpipe=None, stdin=subprocess.PIPE, stdout=None):
    """Call a Subprocess to run the ArgV and return, except exit if exit nonzero"""

    main_py_basename = os.path.basename(sys.argv[0])

    alt_shpipe = shpipe if shpipe else shlex_djoin(argv)
    stderr_print("+ {}".format(alt_shpipe))  # no 'main_py_basename' here

    run = subprocess.run(argv, stdin=stdin, stdout=stdout)
    if run.returncode:  # as if 'check=True'
        stderr_print("{}: + exit {}".format(main_py_basename, run.returncode))

        sys.exit(run.returncode)  # exits same NonZero


# deffed in many files  # missing from docs.python.org
def subprocess_run_oneline(shline, *args, **kwargs):
    """Call 'subprocess_run_stdio' but require one line of Stdout and exit zero"""

    lines = subprocess_run_somelines(shline, *args, **kwargs)

    assert len(lines) == 1, (shline, args, kwargs, lines)
    line = lines[0]

    return line


# deffed in many files  # missing from docs.python.org
def subprocess_run_somelines(shline, *args, **kwargs):
    """Call 'subprocess_run_stdio' but require lines of Stdout and exit zero"""

    run = subprocess_run_stdio(
        shline, *args, stdout=subprocess.PIPE, check=True, **kwargs
    )

    stdout = run.stdout.decode()
    lines = stdout.splitlines()

    assert lines, (shline, args, kwargs, lines)

    return lines


# deffed in many files  # missing from docs.python.org
def subprocess_run_stdio(shline, *args, **kwargs):
    """Flush Stdout, flush Stderr, and then call without Stdin"""

    argv = shlex.split(shline)

    alt_kwargs = dict(kwargs)
    if "stdin" not in kwargs.keys():
        alt_kwargs["stdin"] = subprocess.PIPE

    sys.stdout.flush()
    sys.stderr.flush()

    run = subprocess.run(argv, *args, **kwargs)

    return run


#
# Add some Def's that 'import select' and 'import sys' forgot
#


# deffed in many files  # missing from docs.python.org
def select_select(stdio):
    """Return truthy if 'stdio.read(1)' won't now hang till more Input comes"""

    rlist = [stdio]
    wlist = list()
    xlist = list()
    timeout = 0
    (r, w, x) = select.select(rlist, wlist, xlist, timeout)

    assert not w, w
    assert not x, x

    return r


# deffed in many files  # missing from docs.python.org
def stderr_print(*args, **kwargs):
    """Work like Print, but write Stderr in place of Stdout"""

    sys.stdout.flush()
    print(*args, file=sys.stderr, **kwargs)  # todo: what if "file" in kwargs.keys() ?
    sys.stderr.flush()


# deffed in many files  # missing from docs.python.org
def stdin_readline_else():
    """Block till the Chars of an Input Line arrive, else exit zero or nonzero"""

    SIGINT_RETURNCODE_130 = 0x80 | signal.SIGINT
    assert SIGINT_RETURNCODE_130 == 130, SIGINT_RETURNCODE_130

    try:
        line = sys.stdin.readline()
    except KeyboardInterrupt:
        sys.stderr.write("\n")
        sys.stderr.write("KeyboardInterrupt\n")

        sys.exit(SIGINT_RETURNCODE_130)  # exits 130 to say KeyboardInterrupt SIGINT

    if not line:  # echoes as "^D\n" at Mac, echoes as "\n" at Linux

        sys.exit(0)  # exits 0 to say Stdin Closed

    chars = line.splitlines()[0]

    return chars


class BrokenPipeSink:  # todo: add calls of it, don't just define it
    """
    Exit nonzero, but leave Stderr empty, at unhandled BrokenPipeError's

    Test with large Stdout cut sharply, such as:

        python3 -c 'for _ in range(54321): print(_)' |head -3

    as per:  https://docs.python.org/3/library/signal.html#note-on-sigpipe
    """

    RETURN_CODE_141 = 141  # Mac & Linux convention for Signal SigPipe
    assert RETURN_CODE_141 == (0x80 | signal.SIGPIPE), (0x80, signal.SIGPIPE)

    def __enter__(self, returncode=RETURN_CODE_141):
        self.returncode = returncode

        return self

    def __exit__(self, *exc_info):
        (_, exc, _) = exc_info

        if exc is None:
            try:
                sys.stderr.flush()
                sys.stdout.flush()
            except BrokenPipeError as broken_pipe_error:
                exc = broken_pipe_error

        if isinstance(exc, BrokenPipeError):  # catches this one Exception
            null_fileno = os.open(os.devnull, flags=os.O_WRONLY)
            os.dup2(null_fileno, sys.stdout.fileno())  # ducks the other Exceptions

            sys.exit(self.returncode)  # exits 141, or as chosen, after BrokenPipeError

        # intervenes more narrowly than:
        #
        #   signal.signal(signal.SIGPIPE, handler=signal.SIG_DFL)
        #


#
# Define the Arg Doc to fall back on, when no Arg Doc found at:  __main.__doc__
#


QUOTED_ALT_MAIN_DOC = """

    usage: cd bin/ && python3 p.py [--h]

    demo how to fork ByoBash by downloading 1 File and writing 3 Lines of Code

    options:
      --help  show this help message and exit

    examples:

      ls -1 byotools.py p.py  # shows you have come to work here with us

      python3 p.py  # shows these examples and exit
      python3 p.py --h  # shows this help message and exit
      python3 p.py --  # does your choice of some other work for you

      less -N -FIRX p.py  # shows how this works

"""

ALT_MAIN_DOC = textwrap.dedent(QUOTED_ALT_MAIN_DOC)
ALT_MAIN_DOC = ALT_MAIN_DOC.strip()


#
# Run from the Command Line, when not imported into some other Main module
#


if __name__ == "__main__":

    # Run some Self-Test's

    _ = shutil_get_tty_size()


# posted into:  https://github.com/pelavarre/byobash/blob/main/bin/byotools.py
# copied from:  git clone https://github.com/pelavarre/byobash.git
