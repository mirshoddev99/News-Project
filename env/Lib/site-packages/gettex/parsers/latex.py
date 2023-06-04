import logging
import re
from pylatexenc import latexwalker as lw  # type: ignore
from pylatexenc.macrospec import MacroSpec  # type: ignore


MACROSPECS = [
    MacroSpec("gettext", "[{"),
    MacroSpec("pgettext", "[{{"),
    MacroSpec("ngettext", "[{{{"),
    MacroSpec("pngettext", "[{{{{"),
]


class MessageExtractor:
    MACROS = [spec.macroname for spec in MACROSPECS]
    WHITESPACE_RE = re.compile(r"\s+", re.MULTILINE)

    def __init__(self, file):
        self.logger = logging.getLogger("gettex")
        self.file = file

    def unparse(self, node):
        if node is None:
            return None
        string = node.parsing_state.s[node.pos:node.pos + node.len]
        if isinstance(node, lw.LatexGroupNode):
            del1, del2 = node.delimiters
            string = string[len(del1):-len(del2)]
        return self.WHITESPACE_RE.sub(" ", string)

    def walk_nodelist(self, nodes):
        iterator = iter(nodes)
        for node in iterator:
            if isinstance(node, lw.LatexMacroNode):
                if node.macroname in self.MACROS:
                    arglist = [
                        self.unparse(argnode)
                        for argnode in node.nodeargd.argnlist]
                    yield node.pos, node.macroname, arglist
                else:
                    yield from self.walk_nodelist(node.nodeargd.argnlist)
            elif hasattr(node, "nodelist"):
                yield from self.walk_nodelist(node.nodelist)

    def make_walker(self):
        db = lw.get_default_latex_context_db()
        db.add_context_category("gettext", macros=MACROSPECS)
        return lw.LatexWalker(self.file.read(), db)

    def get_messages(self, messages):
        walker = self.make_walker()
        nodes = walker.get_latex_nodes(0)[0]
        for pos, cmd, args in self.walk_nodelist(nodes):
            line = walker.pos_to_lineno_colno(pos)[0]
            location = f"{self.file.name}:{line}"
            comment = args.pop(0)
            key = '|'.join(args)
            if key in messages:
                messages[key]["comments"].append(comment)
                messages[key]["locations"].append(location)
            else:
                data = {
                    "locations": [location],
                    "comments": [comment]}
                if "p" in cmd:
                    data["msgctxt"] = args.pop(0)
                data["msgid"] = args.pop(0)
                if "n" in cmd:
                    data["msgid_plural"] = args.pop(0)
                    data["msgstr[0]"] = ""
                    data["msgstr[1]"] = ""
                else:
                    data["msgstr"] = ""
                if data["msgid"] and data.get("msgid_plural") != "":
                    messages[key] = data
                else:
                    self.logger.warning(f"Unable to find msgid at {location}")
