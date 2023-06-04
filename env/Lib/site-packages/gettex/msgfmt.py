from argparse import ArgumentParser
from io import TextIOWrapper
from pathlib import Path
import re
import sys
from . import version
from .exceptions import ApplicationError
from .sty_renderer import main


po_header_re = re.compile(b'"([^:]+): (.*)"')


def parse_args(argv):
    parser = ArgumentParser(
        description="Generate message catalog as tex library.",
        usage="msgfmt [OPTION] filename.po ...",
        add_help=False)
    input_group = parser.add_argument_group(
        "Input file location", "If input file is -, standard input is read.")
    input_group.add_argument(
        "files", metavar="filename.po ...", nargs="+",
        help="input files")
    input_group.add_argument(
        "-D", "--directory",
        help="add DIRECTORY to list for input files search")
    output_group = parser.add_argument_group(
        "Output file location",
        "If output file is -, output is written to standard output.")
    output_group.add_argument(
        "-o", "--output-file", metavar="FILE",
        help="write output to specified file")
    interpretation_group = parser.add_argument_group(
        "Input file interpretation")
    interpretation_group.add_argument(
        "-f", "--use-fuzzy", action="store_true", default=False,
        help="use fuzzy entries in output")
    informative_group = parser.add_argument_group("Informative output")
    informative_group.add_argument(
        "-h", "--help", action="help",
        help="display this help and exit")
    informative_group.add_argument(
        "-V", "--version", action="version", version=version,
        help="output version information and exit")
    informative_group.add_argument(
        "--statistics", action="store_true", default=False,
        help="print statistics about translations")
    informative_group.add_argument(
        "-v", "--verbose", action="store_true", default=False,
        help="increase verbosity level")
    return vars(parser.parse_args(argv))


def extract_input_files(args):
    result = []
    input_dir = Path(".")
    if (dirname := args.pop("directory")):
        if not (input_dir := Path(dirname)).is_dir():
            raise ApplicationError(f"Directory does not exist: {dirname}")
    for file in args.pop("files"):
        if file == "-":
            result.append(...)
        elif (path := input_dir / file).exists():
            result.append(path)
        else:
            raise ApplicationError(f"File not found: {path}")
    return result


def consume_header(stream):
    result = {}
    last_key = None
    while True:
        line = stream.readline().strip()
        if not line:
            break
        if line.startswith(b"#") or line.startswith(b"msg"):
            continue
        if last_key in result and not result[last_key].endswith(b"\\n"):
            result[last_key] = result[last_key] + line.strip(b'"')
        elif (mm := po_header_re.match(line)) is not None:
            key, value = mm.groups()
            last_key = key.decode()
            result[last_key] = value
        else:
            raise ValueError(f"Invalid line: {line}")
    result = {key: value[:-2] for key, value in result.items()}
    for entry in ["Content-Type", "Language", "Plural-Forms"]:
        if entry not in result:
            raise ValueError(f"Missing header entry: {entry}")
    if not result["Content-Type"].startswith(b"text/plain; charset="):
        raise ValueError(
            f"Cannot find charset in: {result['Content-Type']}")
    charset = result["Content-Type"].split(b"charset=")[1].decode()
    result = {key: value.decode(charset) for key, value in result.items()}
    result["Encoding"] = charset
    return result


def parse_header(input_files):
    language, plural_spec = None, None
    open_files = []
    for file in input_files:
        stream = sys.stdin.buffer if file == ... else file.open("rb")
        try:
            header = consume_header(stream)
        except ValueError as ve:
            raise ApplicationError(f"Error reading {file}: {ve}")
        if language is None:
            language = header["Language"]
        elif language != header["Language"]:
            raise ApplicationError(
                "Input files have mixed languages: "
                f"{language} / {header['Language']}")
        plural_spec = header["Plural-Forms"].split("plural=")[1].strip(";")
        charset = header["Encoding"]
        if file == ...:
            open_files.append(
                TextIOWrapper(sys.stdin.buffer, encoding=charset))
        else:
            open_files.append(file.open("rt", encoding=charset))
    return language, plural_spec, open_files


def determine_output_file(language, args):
    default_output_file = f"gettext-{language}.sty"
    match args.pop("output_file"):
        case None:
            return Path(default_output_file)
        case "-":
            return ...
        case dirname if Path(dirname).is_dir():
            return Path(dirname) / default_output_file
        case filename:
            return Path(filename)


def run(argv=sys.argv[1:]):
    args = parse_args(argv)
    try:
        input_files = extract_input_files(args)
        language, args["plural_spec"], open_files = parse_header(input_files)
        output_file = determine_output_file(language, args)
        main(
            input_files=open_files,
            output_file=output_file,
            options=args)
    except ApplicationError as ae:
        sys.stderr.write(f"{ae} - aborting\n")
        sys.exit(1)
