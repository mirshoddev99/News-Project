from io import TextIOWrapper
from .logging import get_logger
from pathlib import Path
import sys
from typing import Any, Union
from types import EllipsisType
from .po_header import parse_previous_header, make_header
from .parsers.latex import MessageExtractor


def get_messages(files):
    result = {}
    for file in files:
        extractor = MessageExtractor(file)
        extractor.get_messages(result)
    return result.values()


class Renderer:
    def __init__(self, indent, location, width, **_):
        self.indent = indent
        self.add_location = location
        self.width = width

    def render_messages(self, messages):
        return "\n".join(self.render_message(msg) for msg in messages)

    def render_message(self, data):
        result = ""
        comments = data.pop("comments")
        locations = data.pop('locations')
        if self.add_location:
            for cmt, loc in zip(comments, locations):
                if cmt:
                    result += self.wrap_indent("#.", cmt, False)
                result += f"#: {loc}\n"
        else:
            for cmt in comments:
                if cmt:
                    result += self.wrap_indent("#.", cmt, False)
        for key, value in data.items():
            result += self.wrap_indent(key, value, True)
        return result

    def wrap_indent(self, key, value, quoted):
        if self.indent:
            key = key.ljust((len(key) // 8 + 1) * 8)
            indent = len(key) * " "
        else:
            key += " "
            indent = ""
        maxlen = max(1, self.width - len(key) - (2 if quoted else 0))
        result = [""]
        if not self.indent and len(value) > maxlen:
            result.append("")
        for word in value.split(" "):
            if result == [""] or result == ["", ""]:
                result[-1] += word
            elif len(result[-1]) + len(word) + 1 <= maxlen:
                result[-1] += " " + word
            else:
                if len(result[-1]) < maxlen:
                    result[-1] += " "
                else:
                    word = " " + word
                result.append(word)
        if quoted:
            result = [f'"{line}"' for line in result]
        return key + ("\n" + indent).join(result) + "\n"


def main(
        input_files: list[TextIOWrapper],
        output_file: Union[Path, EllipsisType],
        options: dict[str, Any]):
    logger = get_logger(options["verbose"])
    messages = get_messages(input_files)
    if not messages and not options["force_po"]:
        logger.info(
            "No messages - no output file. "
            "Use force-po to write an empty file")
        return
    rendered_messages = Renderer(**options).render_messages(messages)
    info = f"Wrote {len(messages)} messages"
    if options["header"]:
        info += " and the header"
        previous_header = {}
        if not isinstance(output_file, EllipsisType) and output_file.exists():
            previous_header = parse_previous_header(output_file)
        rendered_messages = \
            make_header(previous_header, **options) + rendered_messages
    if isinstance(output_file, EllipsisType):
        sys.stdout.write(rendered_messages)
        sys.stdout.flush()
    else:
        info += f" to {output_file}"
        output_file.write_text(rendered_messages)
    logger.info(info)
