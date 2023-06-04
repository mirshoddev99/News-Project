from argparse import ArgumentParser
from io import TextIOWrapper
from pathlib import Path
import os
import sys
from . import version
from .exceptions import ApplicationError
from .po_renderer import main


def parse_args(argv):
    parser = ArgumentParser(
        description="Extract translatable strings from given input files.",
        usage="xgettext [OPTION] [INPUTFILE]...",
        add_help=False)
    input_group = parser.add_argument_group(
        "Input file location", "If input file is -, standard input is read.")
    input_group.add_argument(
        "files", metavar="INPUTFILE", nargs="*",
        help="input files")
    input_group.add_argument(
        "-f", "--files-from", metavar="FILE",
        help="get list of input files from FILE")
    input_group.add_argument(
        "-D", "--directory",
        help="add DIRECTORY to list for input files search")
    output_group = parser.add_argument_group(
        "Output file location",
        "If output file is -, output is written to standard output.")
    output_group.add_argument(
        "-d", "--default-domain", metavar="NAME", default="messages",
        help="use NAME.po for output (instead of messages.po)")
    output_group.add_argument(
        "-o", "--output", metavar="FILE",
        help="write output to specified file")
    output_group.add_argument(
        "-p", "--output-dir", metavar="DIR",
        help="output files will be placed in directory DIR")
    interpretation_group = parser.add_argument_group(
        "Input file interpretation",
        "By default the input files are assumed to be in UTF-8")
    interpretation_group.add_argument(
        "--from-code", metavar="NAME", default="UTF-8",
        help="encoding of input files")
    outdetails_group = parser.add_argument_group(
        "Output details")
    outdetails_group.add_argument(
        "--force-po", action="store_true", default=False,
        help="write PO file even if empty")
    outdetails_group.add_argument(
        "-i", "--indent", action="store_true", default=False,
        help="write the .po file using indented style")
    location_group = outdetails_group.add_mutually_exclusive_group()
    location_group.add_argument(
        "--no-location", dest="location", action="store_false",
        help="do not write '#: filename:line' lines")
    location_group.add_argument(
        "-n", "--add-location", dest="location", action="store_true",
        help="generate '#: filename:line' lines (default)")
    outdetails_group.add_argument(
        "-w", "--width", metavar="NUMBER", default=80, type=int,
        help="set output page width")
    outdetails_group.add_argument(
        "--no-wrap", action="store_const", dest="width", const=4096,
        help="do not break long message lines, longer than "
             "the output page width, into several lines")
    outdetails_group.add_argument(
        "--omit-header", dest="header", action="store_false", default=True,
        help="""don't write header with 'msgid ""' entry""")
    outdetails_group.add_argument(
        "--copyright-holder", metavar="STRING",
        default="THE PACKAGE'S COPYRIGHT HOLDER",
        help="set copyright holder in output")
    outdetails_group.add_argument(
        "--package-name", metavar="PACKAGE", default="PACKAGE",
        help="set package name in output")
    outdetails_group.add_argument(
        "--package-version", metavar="VERSION", default="VERSION",
        help="set package version in output")
    outdetails_group.add_argument(
        "--msgid-bugs-address", metavar="EMAIL@ADDRESS",
        default="EMAIL@ADDRESS",
        help="set report address for msgid bugs")
    informative_group = parser.add_argument_group("Informative output")
    informative_group.add_argument(
        "-h", "--help", action="help",
        help="display this help and exit")
    informative_group.add_argument(
        "-V", "--version", action="version", version=version,
        help="output version information and exit")
    informative_group.add_argument(
        "-v", "--verbose", action="store_true", default=False,
        help="increase verbosity level")
    return vars(parser.parse_args(argv))


def extract_input_files(args):
    yield from args.pop("files")
    if (files_from := args.pop("files_from")):
        if not (index_file := Path(files_from)).exists():
            raise ApplicationError(f"Index file not found: {files_from}")
        for line in index_file.read_text().splitlines():
            if not line.strip().startswith("#"):
                yield line.strip()
    if (directory := args.pop("directory")):
        if not (inputdir := Path(directory)).is_dir():
            raise ApplicationError(f"Directory does not exist: {directory}")
        for file in inputdir.glob("**/*"):
            if file.is_file():
                yield str(file)


def open_code_input(iterator, args):
    encoding = args.pop("from_code")
    result = []
    for filename in iterator:
        if filename == "-":
            result.append(TextIOWrapper(sys.stdin.buffer, encoding=encoding))
        elif (file := Path(filename)).exists():
            if os.access(file, os.R_OK):
                result.append(file.open(encoding=encoding))
            else:
                raise ApplicationError(f"File not readable: {filename}")
        else:
            raise ApplicationError(f"File not found: {filename}")
    if not result:
        raise ApplicationError("No input files specified")
    return result


def extract_output_file(args):
    domain = args.pop("default_domain")
    filename = args.pop("output") or f"{domain}.po"
    if filename == "-":
        return ...
    file = Path(filename)
    if (output_dir := args.pop("output_dir")):
        file = Path(output_dir) / file
    if not file.parent.exists():
        raise ApplicationError(f"Output dir does not exist: {file.parent}")
    return file


def run(argv=sys.argv[1:]):
    args = parse_args(argv)
    try:
        main(
            input_files=open_code_input(extract_input_files(args), args),
            output_file=extract_output_file(args),
            options=args)
    except ApplicationError as ae:
        sys.stderr.write(f"{ae} - aborting\n")
        sys.exit(1)
