#!/usr/bin/env python3
"""
TSPMO Language Server with run‐file support
"""

import sys
import re
import threading
from pathlib import Path
from urllib.parse import urlparse, unquote

from pygls.server import LanguageServer
from lsprotocol.types import (
    TEXT_DOCUMENT_COMPLETION,
    TEXT_DOCUMENT_HOVER,
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_CHANGE,
    CompletionParams,
    CompletionList,
    CompletionItem,
    CompletionItemKind,
    HoverParams,
    Hover,
    MarkupContent,
    MarkupKind,
    DidOpenTextDocumentParams,
    DidChangeTextDocumentParams,
    Diagnostic,
    DiagnosticSeverity,
    Range,
    Position
)

# ──────────────────────────────────────────────────────────────────────────────
# Import your interpreter’s run_file() from interpreter.py
root = Path(__file__).resolve().parent
sys.path.insert(0, str(root))
from interpreter import run_file
# ──────────────────────────────────────────────────────────────────────────────

def parse_docstrings(text: str) -> dict[str, str]:
    """
    Map function names to the first -> ... <- comment block in their body.
    """
    docs: dict[str, str] = {}
    for fn in re.finditer(r'\bLEBRON\s+(\w+)(?:\s+\w+)*\s+ngl\b', text):
        name = fn.group(1)
        start = fn.end()
        tail = text[start:]
        goat_m = re.search(r'\bGOAT\b', tail)
        end = goat_m.start() if goat_m else len(tail)
        body = tail[:end]
        cm = re.search(r'->([\s\S]*?)<-', body)
        if cm:
            docs[name] = cm.group(1).strip()
    return docs

KEYWORD_DOCS = {
    "tun": "**tun**: Integer incrementer.",
    "sahur": "**sahur**: Integer declaration closer.",
    "sigma": "**sigma**: Boolean true value.",
    "beta": "**beta**: Boolean false value.",
    "legit": "**legit**: String literal opener.",
    "bro": "**bro**: String literal closer.",
    "ts": "**ts**: statement opener.",
    "pmo": "**pmo**: statement closer.",
    "ls": "**ls**: Initialize an empty list.",
    "rizz": "**rizz [id] [expr]**: Declare a variable.",
    "yap": "**yap [expr]**: Print the result of an expression.",
    "sybau": "**sybau [expr]**: NoOp. Useful for in-place operations.",
    "dih": "**dih [expr]**: Set return value of function.",
    "chat?": "**chat? [prompt: str] -> str**: Request user input.",
    "spill": "**spill [expr] -> int**: Converts from expression to integer.",
    "sayong": "**sayong [expr] -> bool**: Converts from expression to bool.",
    "tf": "**tf [expr] -> float**: Converts from expression to float.",
    "lowkey": "**lowkey [expr] -> str**: Converts from expression to string.",
    "touch": "**touch [a: int, float] [b: int, float] -> int, float**: Returns a + b.",
    "#shrink": "**#shrink [a: int, float] [b: int, float] -> int, float**: Returns a - b.",
    "cavendish": "**cavendish [a: int, float] [b: int, float] -> int, float**: Returns a * b.",
    "big25": "**big25 [a: int, float] [b: int, float] -> int**: Returns a / b (integer division).",
    "bigf": "**bigf [a: int, float] [b: int, float] -> float**: Returns a / b (float division).",
    "crockpot": "**crockpot [a: int, float] [b: int, float] -> int**: Returns a % b.",
    "chill": "**chill [a: bool] [b: bool] -> bool**: Returns a or b.",
    "grind": "**grind [a: bool] [b: bool] -> bool**: Returns a and b.",
    "L": "**L [a: bool] -> bool**: Returns not a.",
    "mogs": "**mogs [a: int, float] [b: int, float] -> bool**: Returns a > b.",
    "vibes": "**vibes [a: any] [b: any] -> bool**: Returns a == b.",
    "stroke": "**stroke [a: str] [b: str] -> str**: Concatenates two strings.",
    "BOOM": "**BOOM [a: str] -> list**: Splits a by whitespace.",
    "ad": "**ad [a: list] [b] -> list**: Appends b to list a.",
    "rm": "**rm [a: list]**: Removes the last item of a.",
    "pt": "**pt [a: list] [b: int] [c]**: Sets index b of list a to c.",
    "girth": "**girth [a: list, str] -> int**: Returns the length of a.",
    "hawk": "**hawk [expr]**: Opens a flag for a conditional.",
    "lion": "**lion**: Fires a conditional branch if last flag was true.",
    "tiger": "**tiger**: Fires a conditional branch if last flag was false.",
    "fr": "**fr**: Closes a conditional branch.",
    "ong": "**ong**: Pops the last flag.",
    "yo": "**[expr] yo**: Saves expr as loop condition.",
    "kid": "**kid**: Opens a loop bounded by last condition.",
    "gurt": "**gurt**: Closes a loop.",
    "REF": "**REF [modules] DO SOMETHING**: Imports modules.",
    "LEBRON": "**LEBRON [name] [params] ngl**: Declares a function.",
    "GOAT": "**GOAT**: Ends a function declaration.",
}

# timers for debounced lint
debouncers: dict[str, threading.Timer] = {}

# 1) Instantiate the language server
server = LanguageServer('tspmo-language-server', '0.1.0')
server.user_docs: dict[str, str] = {}

# 2) Keyword/operator groups for completion
CONTROL   = ["LEBRON","ngl","GOAT","hawk","lion","tiger","fr","ong","kid","gurt","REF","DO SOMETHING"]
DECL      = ["rizz","yap","sybau","dih","yo"]
SEC_OP    = ["chat?","spill","sayong","tf","lowkey"]
ARITH     = ["touch","#shrink","cavendish","big25","crockpot","bigf"]
BOOL_OP   = ["chill","grind","L"]
CMP_OP    = ["mogs","vibes"]
STR_OP    = ["stroke"]
BOOLEANS  = ["sigma","beta"]

def make_completions() -> CompletionList:
    items: list[CompletionItem] = []
    for kw in CONTROL:
        items.append(CompletionItem(label=kw,
                                    kind=CompletionItemKind.Keyword,
                                    detail="control"))
    for kw in DECL:
        items.append(CompletionItem(label=kw,
                                    kind=CompletionItemKind.Keyword,
                                    detail="declaration"))
    for kw in SEC_OP + ARITH + BOOL_OP + CMP_OP + STR_OP:
        items.append(CompletionItem(label=kw,
                                    kind=CompletionItemKind.Operator))
    for lit in BOOLEANS:
        items.append(CompletionItem(label=lit,
                                    kind=CompletionItemKind.Value))
    return CompletionList(is_incomplete=False, items=items)

def pos_from_idx(text: str, idx: int) -> Position:
    line = text.count('\n', 0, idx)
    col  = idx - (text.rfind('\n', 0, idx) + 1)
    return Position(line, col)

def lint_text(text: str) -> list[Diagnostic]:
    diags: list[Diagnostic] = []
    # count tokens
    hawk_count  = len(re.findall(r'\bhawk\b', text))
    ong_count   = len(re.findall(r'\bong\b', text))
    cond_count  = len(re.findall(r'\b(?:lion|tiger)\b', text))
    fr_count    = len(re.findall(r'\bfr\b', text))
    yo_count    = len(re.findall(r'\byo\b', text))
    kid_count   = len(re.findall(r'\bkid\b', text))
    gurt_count  = len(re.findall(r'\bgurt\b', text))
    ts_count    = len(re.findall(r'\bts\b', text))
    pmo_count   = len(re.findall(r'\bpmo\b', text))
    legit_count = len(re.findall(r'\blegit\b', text))
    bro_count   = len(re.findall(r'\bbro\b', text))

    if ts_count != pmo_count:
        diags.append(Diagnostic(
            Range(pos_from_idx(text,0), pos_from_idx(text,1)),
            f"'ts' count ({ts_count}) != 'pmo' count ({pmo_count})",
            DiagnosticSeverity.Error
        ))
    if legit_count != bro_count:
        diags.append(Diagnostic(
            Range(pos_from_idx(text,0), pos_from_idx(text,1)),
            f"'legit' count ({legit_count}) != 'bro' count ({bro_count})",
            DiagnosticSeverity.Error
        ))
    if hawk_count > ong_count:
        diags.append(Diagnostic(
            Range(pos_from_idx(text,0), pos_from_idx(text,1)),
            f"Unpopped flags: {hawk_count} hawk(s) vs {ong_count} ong(s)",
            DiagnosticSeverity.Warning
        ))
    if cond_count > fr_count:
        diags.append(Diagnostic(
            Range(pos_from_idx(text,0), pos_from_idx(text,1)),
            f"{cond_count} conditional(s) but only {fr_count} 'fr'",
            DiagnosticSeverity.Error
        ))
    if kid_count != gurt_count:
        diags.append(Diagnostic(
            Range(pos_from_idx(text,0), pos_from_idx(text,1)),
            f"{kid_count} 'kid' vs {gurt_count} 'gurt' loops",
            DiagnosticSeverity.Error
        ))
    if kid_count > yo_count:
        diags.append(Diagnostic(
            Range(pos_from_idx(text,0), pos_from_idx(text,1)),
            f"{kid_count} loops opened but only {yo_count} 'yo'",
            DiagnosticSeverity.Error
        ))

    return diags

def idx_from_pos(text: str, line: int, col: int) -> int:
    lines = text.splitlines(True)
    return sum(len(lines[i]) for i in range(line)) + col

# ──────────────────────────────────────────────────────────────────────────────
# 3) Register run-file command
@server.command('tspmo.runFile')
def run_file_command(ls: LanguageServer, *args):
    if not args:
        return "Error: no file URI provided"
    uri = args[0]
    parsed = urlparse(uri)
    path = unquote(parsed.path)
    code = run_file(path)
    return f"Ran {path}, exit code {code}"
# ──────────────────────────────────────────────────────────────────────────────

@server.feature(TEXT_DOCUMENT_HOVER)
def hover(ls: LanguageServer, params: HoverParams):
    uri = params.text_document.uri
    doc = ls.workspace.get_document(uri)
    pos = params.position
    line = doc.source.splitlines()[pos.line]
    for m in re.finditer(r"\b\w+\b|\b[#?]\w+\b", line):
        if m.start() <= pos.character <= m.end():
            token = m.group(0)
            if token in ls.user_docs:
                return Hover(
                    contents=MarkupContent(kind=MarkupKind.Markdown,
                                          value=ls.user_docs[token]),
                    range=Range(Position(pos.line, m.start()),
                                Position(pos.line, m.end()))
                )
            if token in KEYWORD_DOCS:
                return Hover(
                    contents=MarkupContent(kind=MarkupKind.Markdown,
                                          value=KEYWORD_DOCS[token]),
                    range=Range(Position(pos.line, m.start()),
                                Position(pos.line, m.end()))
                )
            break
    return None

@server.feature(TEXT_DOCUMENT_COMPLETION)
def completions(ls: LanguageServer, params: CompletionParams):
    doc = ls.workspace.get_document(params.text_document.uri)
    text = doc.source
    cursor = idx_from_pos(text, params.position.line, params.position.character)

    # gather function scopes
    scopes = []
    for m in re.finditer(r'\bLEBRON\s+(\w+)((?:\s+\w+)*)\s+ngl\b', text):
        start = m.end()
        name = m.group(1)
        params_list = m.group(2).strip().split() if m.group(2).strip() else []
        scopes.append({'name': name, 'start': start, 'end': None, 'params': params_list})
    goat_positions = [m.start() for m in re.finditer(r'\bGOAT\b', text)]
    for i, s in enumerate(scopes):
        s['end'] = goat_positions[i] if i < len(goat_positions) else len(text)

    # collect globals & locals
    globals_, locals_ = set(), {s['name']: set() for s in scopes}
    for m in re.finditer(r'\bts\s+rizz\s+(\w+)\b', text):
        var, idx = m.group(1), m.start()
        in_scope = False
        for s in scopes:
            if s['start'] <= idx < s['end']:
                locals_[s['name']].add(var)
                in_scope = True
                break
        if not in_scope:
            globals_.add(var)

    # current scope
    current = None
    for s in scopes:
        if s['start'] <= cursor < s['end']:
            current = s
            break

    # build items
    items = make_completions().items[:]
    for s in scopes:
        items.append(CompletionItem(label=s['name'],
                                    kind=CompletionItemKind.Function,
                                    detail="function"))
    for v in sorted(globals_):
        items.append(CompletionItem(label=v,
                                    kind=CompletionItemKind.Variable,
                                    detail="global"))
    if current:
        for p in current['params']:
            items.append(CompletionItem(label=p,
                                        kind=CompletionItemKind.Variable,
                                        detail="param"))
        for v in sorted(locals_[current['name']]):
            items.append(CompletionItem(label=v,
                                        kind=CompletionItemKind.Variable,
                                        detail="local"))

    return CompletionList(is_incomplete=False, items=items)

@server.feature(TEXT_DOCUMENT_DID_OPEN)
def did_open(ls: LanguageServer, params: DidOpenTextDocumentParams):
    uri = params.text_document.uri
    doc = ls.workspace.get_document(uri)
    ls.publish_diagnostics(uri, lint_text(doc.source))
    ls.user_docs = parse_docstrings(doc.source)

@server.feature(TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls: LanguageServer, params: DidChangeTextDocumentParams):
    uri = params.text_document.uri
    doc = ls.workspace.get_document(uri)
    ls.user_docs = parse_docstrings(doc.source)

    if uri in debouncers:
        debouncers[uri].cancel()

    def do_lint():
        d = ls.workspace.get_document(uri)
        ls.publish_diagnostics(uri, lint_text(d.source))

    t = threading.Timer(0.8, do_lint)
    debouncers[uri] = t
    t.start()

if __name__ == '__main__':
    server.start_io()
