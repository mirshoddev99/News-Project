from datetime import datetime as DateTime
from io import TextIOWrapper
from itertools import chain
from pathlib import Path
import re
import sys
from typing import Any, Union
from types import EllipsisType
from .exceptions import ApplicationError
from .logging import get_logger


po_key_re = re.compile(
    r'^(?P<key>msg(?:id|id_plural|ctxt|str))(?:\[(?P<index>\d+)\])? '
    r'"(?P<text>.*)"')


PSPEC_TO_TFUNC = {
    "0": r"0",
    "(n != 0)": r"\ifnum #1=0 0\else1\fi",
    "(n != 1)": r"\ifnum #1=1 0\else1\fi",
    "(n > 1)": r"\ifnum #1>1 1\else0\fi",
    "(n%10!=1 || n%100==11)": (
        r"\ifnum \intcalcMod{#1}{10}=1 \ifnum \intcalcMod{#1}{100}=11 1\else0"
        r"\fi\else1\fi"
    ),
    "(n==0 ? 0 : n==1 ? 1 : 2)": (
        r"\ifnum #1=0 0\else\ifnum #1=1 1\else2\fi\fi"
    ),
    "(n%10==1 && n%100!=11 ? 0 : n != 0 ? 1 : 2)": (
        r"\ifnum \ifnum \intcalcMod{#1}{10}=1 \ifnum \intcalcMod{#1}{100}=11 0"
        r"\else1\fi\else0\fi=1 0\else \ifnum #1=0 2\else1\fi\fi"
    ),
    "(n%10==1 && n%100!=11 ? 0 : n%10>=2 && (n%100<10 || n%100>=20) " +
    "? 1 : 2)": (
        r"\ifnum \ifnum \intcalcMod{#1}{10}=1 \ifnum \intcalcMod{#1}{100}=11 0"
        r"\else1\fi\else0\fi=1 0\else \ifnum \ifnum \ifnum \intcalcMod{#1}{10"
        r"}>1 1\else0\fi=0 0\else\ifnum \ifnum \intcalcMod{#1}{100}<10 1\else"
        r"\ifnum \intcalcMod{#1}{100}>19 1\else0\fi\fi=0 0\else1\fi\fi=1 1"
        r"\else 2\fi\fi"
    ),
    "(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && " +
    "(n%100<10 || n%100>=20) ? 1 : 2)": (
        r"\ifnum \ifnum \intcalcMod{#1}{10}=1 \ifnum \intcalcMod{#1}{100}=11 0"
        r"\else1\fi\else0\fi=1 0\else \ifnum \ifnum \ifnum \intcalcMod{#1}{10"
        r"}>1 1\else0\fi=0 0\else\ifnum \ifnum \ifnum \intcalcMod{#1}{10}<5 1"
        r"\else0\fi=0 0\else\ifnum \ifnum \intcalcMod{#1}{100}<10 1\else\ifnum"
        r" \intcalcMod{#1}{100}>19 1\else0\fi\fi=0 0\else1\fi\fi=0 0\else1\fi"
        r"\fi=1 1\else 2\fi\fi"
    ),
    "n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && " +
    "(n%100<10 || n%100>=20) ? 1 : 2": (
        r"\ifnum \ifnum \intcalcMod{#1}{10}=1 \ifnum \intcalcMod{#1}{100}=11 0"
        r"\else1\fi\else0\fi=1 0\else \ifnum \ifnum \ifnum \intcalcMod{#1}{10"
        r"}>1 1\else0\fi=0 0\else\ifnum \ifnum \ifnum \intcalcMod{#1}{10}<5 1"
        r"\else0\fi=0 0\else\ifnum \ifnum \intcalcMod{#1}{100}<10 1\else\ifnum"
        r" \intcalcMod{#1}{100}>19 1\else0\fi\fi=0 0\else1\fi\fi=0 0\else1\fi"
        r"\fi=1 1\else 2\fi\fi"
    ),
    "(n==1 ? 0 : (n==0 || (n%100 > 0 && n%100 < 20)) ? 1 : 2)": (
        r"\ifnum #1=1 0\else\ifnum \ifnum \ifnum #1=0 1\else0\fi=0 \ifnum "
        r"\ifnum \intcalcMod{#1}{100}>0 \ifnum \intcalcMod{#1}{100}<20 1\else0"
        r"\fi\else0\fi=0 0\else1\fi\else1\fi=1 1\else 2\fi\fi"
    ),
    "(n==1 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2)": (
        r"\ifnum #1=1 0\else\ifnum \ifnum \ifnum \intcalcMod{#1}{10}>1 1\else0"
        r"\fi=0 0\else\ifnum \ifnum \ifnum \intcalcMod{#1}{10}<5 1\else0\fi=0 "
        r"0\else\ifnum \ifnum \intcalcMod{#1}{100}<10 1\else\ifnum \intcalcMod"
        r"{#1}{100}>19 1\else0\fi\fi=0 0\else1\fi\fi=0 0\else1\fi\fi=1 1\else "
        r"2\fi\fi"
    ),
    "(n==1) ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2": (
        r"\ifnum #1=1 0\else\ifnum \ifnum \ifnum \intcalcMod{#1}{10}>1 1\else0"
        r"\fi=0 0\else\ifnum \ifnum \ifnum \intcalcMod{#1}{10}<5 1\else0\fi=0 "
        r"0\else\ifnum \ifnum \intcalcMod{#1}{100}<10 1\else\ifnum \intcalcMod"
        r"{#1}{100}>19 1\else0\fi\fi=0 0\else1\fi\fi=0 0\else1\fi\fi=1 1\else "
        r"2\fi\fi"
    ),
    "(n==1) ? 0 : (n>=2 && n<=4) ? 1 : 2": (
        r"\ifnum #1=1 0\else\ifnum \ifnum #1>1 \ifnum #1<5 1\else0\fi\else0\fi"
        r"=1 1\else 2\fi\fi"
    ),
    "(n%100==1 ? 0 : n%100==2 ? 1 : n%100==3 || n%100==4 ? 2 : 3)": (
        r"\ifnum \intcalcMod{#1}{100}=1 0\else\ifnum \intcalcMod{#1}{100}=2 1"
        r"\else\ifnum \ifnum \intcalcMod{#1}{100}=3 1\else\ifnum \intcalcMod{#"
        r"1}{100}=4 1\else0\fi\fi=1 2\else 3\fi\fi\fi"
    ),
    "(n==1 ? 0 : n==0 || ( n%100>1 && n%100<11) ? 1 : " +
    "(n%100>10 && n%100<20 ) ? 2 : 3)": (
        r"\ifnum #1=1 0\else\ifnum \ifnum \ifnum #1=0 1\else0\fi=0 \ifnum "
        r"\ifnum \intcalcMod{#1}{100}>1 \ifnum \intcalcMod{#1}{100}<11 1\else0"
        r"\fi\else0\fi=0 0\else1\fi\else1\fi=1 1\else \ifnum \ifnum "
        r"\intcalcMod{#1}{100}>10 \ifnum \intcalcMod{#1}{100}<20 1\else0\fi"
        r"\else0\fi=1 2\else 3\fi\fi\fi"
    ),
    "(n==1) ? 0 : (n==2) ? 1 : (n == 3) ? 2 : 3": (
        r"\ifnum #1=1 0\else\ifnum #1=2 1\else\ifnum #1=3 2\else3\fi"
        r"\fi\fi"
    ),
    "(n==1) ? 0 : (n==2) ? 1 : (n != 8 && n != 11) ? 2 : 3": (
        r"\ifnum #1=1 0\else\ifnum #1=2 1\else\ifnum \ifnum #1=8 0\else\ifnum "
        r"#1=11 0\else1\fi\fi=1 2\else 3\fi\fi\fi"
    ),
    "(n==1 || n==11) ? 0 : (n==2 || n==12) ? 1 : (n > 2 && n < 20) ? 2 : 3": (
        r"\ifnum \ifnum #1=1 1\else\ifnum #1=11 1\else0\fi\fi=1 0\else \ifnum "
        r"\ifnum #1=2 1\else\ifnum #1=12 1\else0\fi\fi=1 1\else \ifnum \ifnum "
        r"#1>2 \ifnum #1<20 1\else0\fi\else0\fi=1 2\else 3\fi\fi\fi"
    ),
    "n==1 ? 0 : n==2 ? 1 : (n>2 && n<7) ? 2 :(n>6 && n<11) ? 3 : 4": (
        r"\ifnum #1=1 0\else\ifnum #1=2 1\else\ifnum \ifnum #1>2 \ifnum #1<7 1"
        r"\else0\fi\else0\fi=1 2\else \ifnum \ifnum #1>6 \ifnum #1<11 1\else0"
        r"\fi\else0\fi=1 3\else 4\fi\fi\fi\fi"
    ),
    "(n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 : " +
    "n%100>=11 ? 4 : 5)": (
        r"\ifnum #1=0 0\else\ifnum #1=1 1\else\ifnum #1=2 2\else\ifnum \ifnum "
        r"\intcalcMod{#1}{100}>2 \ifnum \intcalcMod{#1}{100}<11 1\else0\fi"
        r"\else0\fi=1 3\else \ifnum \intcalcMod{#1}{100}>10 4\else5\fi\fi"
        r"\fi\fi\fi"
    ),
}


class Message:
    msgctxt: str
    msgid: str
    msgid_plural: str
    msgstr: list[str]
    fuzzy: bool

    def __init__(self):
        self.msgctxt = None
        self.msgid = None
        self.msgid_plural = None
        self.msgstr = []
        self.fuzzy = False

    def valid(self, with_fuzzy):
        return (with_fuzzy or not self.fuzzy) and \
            self.msgid and self.msgstr

    def __str__(self):
        result = ("Fuzzy" if self.fuzzy else "") + "Message("
        for key in ["msgctxt", "msgid", "msgid_plural"]:
            if getattr(self, key):
                result += f"{key}='{getattr(self, key)}' "
        result += f"msgstr={str(self.msgstr)})"
        return result

    __repr__ = __str__

    def iter_renditions(self):
        base = self.msgctxt + "|" if self.msgctxt else ""
        if len(self.msgstr) == 1:
            return [(base + self.msgid, self.msgstr[0] or self.msgid)]
        return [
            (base + self.msgid + f"|{ii}", msgstr or self.msgid)
            for ii, msgstr in enumerate(self.msgstr)]

    @property
    def type(self):
        if self.fuzzy:
            return "fuzzy translation"
        if self.msgstr[0] == "":
            return "missing translation"
        return "translated message"


def read_messages(input_files, use_fuzzy):
    for file in input_files:
        message = Message()
        stage = None
        for line in file:
            line = line.strip()
            if line == "#, fuzzy":
                assert stage is None
                message.fuzzy = True
            elif line.startswith("#"):
                pass
            elif not line:
                if message.valid(use_fuzzy):
                    yield message
                message = Message()
                stage = None
            elif line.startswith('"'):
                assert stage is not None
                if stage == "msgstr":
                    text = message.msgstr[-1] + line[1:-1]
                    message.msgstr[-1] = text
                else:
                    text = getattr(message, stage) + line[1:-1]
                    setattr(message, stage, text)
            elif (mm := po_key_re.match(line)):
                data = mm.groupdict()
                if (stage := data["key"]) == "msgstr":
                    message.msgstr.append(data["text"])
                else:
                    setattr(message, stage, data["text"])
            else:
                raise ApplicationError(f"Invalid line in po: `{line}`")
        if message.valid(use_fuzzy):
            yield message


r'''
\NewDocumentCommand{\getenv}{mm}
 {
  \sys_get_shell:nnN { kpsewhich ~ --var-value ~ LANG } { } \gettext_locale
  \tl_trim_spaces:N \gettext_locale
 }
'''
#  \tl_trim_spaces:N \l_tmpa_tl
#  \tl_set_eq:NN #1 \l_tmpa_tl


def render_tex_library(package_name, plural_code, messages):
    translations = [
        "\\defineTranslation{%s}{%s}" % entry
        for entry in chain(*[msg.iter_renditions() for msg in messages])]
    date = DateTime.now().strftime("%Y/%m/%d")
    return '\n'.join([
        r'\ProvidesPackage{%s}[%s]' % (package_name, date),
        r'\usepackage[utf8]{inputenc}',
        r'\usepackage{xifthen}',
        r'\usepackage{expl3}',
        r'\usepackage{xparse}',
        r'\usepackage{intcalc}',
        '',
        r'\newcommand{\getPluralIndex}[1]{%s}' % plural_code,
        '',
        r'\ExplSyntaxOn',
        r'\prop_new:N \TMap',
        r'\newcommand{\defineTranslation}[2]{\prop_gput:Nnn \TMap {#1} {#2}}',
        r'\newcommand{\TGet}[1]{\prop_item:Nn \TMap {#1}}',
        r'\ExplSyntaxOff',
        r'\newcommand{\gettext}[2][]{\TGet{#2}}',
        r'\newcommand{\ngettext}[4][]{\TGet{#2|\getPluralIndex{#4}}}',
        r'\newcommand{\pgettext}[3][]{\TGet{#2|#3}}',
        r'\newcommand{\pngettext}[5][]{\TGet{#2|#3|\getPluralIndex{#5}}}',
        '',
        *translations])


def main(
        input_files: list[TextIOWrapper],
        output_file: Union[Path, EllipsisType],
        options: dict[str, Any]):
    logger = get_logger(options["verbose"])
    if (plural_spec := PSPEC_TO_TFUNC.get(options["plural_spec"])) is None:
        raise ApplicationError(
            "Unknown plural specification: "
            f"{options['plural_spec']} - aborting")
    messages = list(read_messages(input_files, options["use_fuzzy"]))
    if not messages:
        logger.info("No messages - no output file.")
        return
    if isinstance(output_file, EllipsisType):
        package_name = "gettext"
    else:
        package_name = output_file.stem
    output = render_tex_library(package_name, plural_spec, messages)
    if options["statistics"]:
        stats = {"translated message": 0}
        for msg in messages:
            stats.setdefault(msg.type, 0)
            stats[msg.type] += 1
        statistics = []
        for type, amount in stats.items():
            if amount != 1:
                type += "s"
            statistics.append(f"{amount} {type}")
        logger.info(", ".join(statistics))
    if isinstance(output_file, EllipsisType):
        sys.stdout.write(output)
        sys.stdout.flush()
    else:
        output_file.write_text(output)
