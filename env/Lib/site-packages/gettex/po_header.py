from datetime import datetime as DateTime
import re


po_header_re = re.compile(
    '\\A(?P<comments>(?:^# .*\n)*)(?:^#\n)?(?:^#, fuzzy\n)?'
    '^msgid ""\n'
    '^msgstr ""\n'
    '(?P<defs>(?:^".*: .*\\\\n"\n)+)',
    re.MULTILINE)


def parse_previous_header(file):
    if (exp := po_header_re.match(file.read_text())):
        comments, defs = exp.groups()
        return {
            "comments": [line[2:] for line in comments.splitlines()],
            **dict(line[1:-3].split(": ", 1) for line in defs.splitlines())
        }
    return {}


def make_header(
        previous_header, copyright_holder, package_name,
        package_version, msgid_bugs_address, **_):
    aware_now = DateTime.now().astimezone()
    data = previous_header
    data.setdefault("comments", [
        "SOME DESCRIPTIVE TITLE.",
        f"Copyright (C) YEAR {copyright_holder}",
        "This file is distributed under the same license "
        f"as the {package_name} package.",
        "FIRST AUTHOR <EMAIL@ADDRESS>, YEAR."])
    data.setdefault("Project-Id-Version", f"{package_name} {package_version}")
    data.setdefault("Report-Msgid-Bugs-To", msgid_bugs_address)
    data["POT-Creation-Date"] = aware_now.strftime("%Y-%m-%d %H:%M%z")
    data.setdefault("PO-Revision-Date", "YEAR-MO-DA HO:MI+ZONE")
    data.setdefault("Last-Translator", "FULL NAME <EMAIL@ADDRESS>")
    data.setdefault("Language-Team", "LANGUAGE <LL@li.org>")
    data.setdefault("Language", "")
    data.setdefault("MIME-Version", "1.0")
    data.setdefault("Content-Type", "text/plain; charset=UTF-8")
    data.setdefault("Content-Transfer-Encoding", "8bit")
    return "\n".join(
        [f"# {val}" for val in data.pop("comments")] +
        ["#", "#, fuzzy", 'msgid ""', 'msgstr ""'] +
        [f'"{key}: {value}\\n"' for key, value in data.items()] +
        ["", ""])
