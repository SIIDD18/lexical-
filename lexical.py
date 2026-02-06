#!/usr/bin/env python3
"""
Simple regex-based lexical analyzer (lexer/tokenizer).

Produces Token(type, value, line, column) tuples.
Skips whitespace and comments. Recognizes keywords, identifiers,
numbers, string literals, operators and punctuation.

Usage: import tokenize from this file or run as a script to see an example.
"""

import re
from dataclasses import dataclass
from typing import List, Iterator, Optional

@dataclass
class Token:
    type: str
    value: str
    line: int
    column: int

# Example set of keywords for a C/Java-like language
KEYWORDS = {
    "if", "else", "while", "for", "return", "int", "float", "void", "break", "continue", "true", "false"
}

# Token specification as (NAME, pattern)
TOKEN_SPECIFICATION = [
    ("NUMBER",   r'\d+(?:\.\d+)?'),                   # Integer or decimal number
    ("ID",       r'[A-Za-z_]\w*'),                    # Identifiers
    ("STRING",   r'"(?:\\.|[^"\\])*"'),               # Double-quoted string with escapes
    ("COMMENT",  r'//[^\n]*|/\*[\s\S]*?\*/'),         # Single-line or multi-line comments
    ("NEWLINE",  r'\n'),                              # Line endings
    ("SKIP",     r'[ \t\r]+'),                        # Skip spaces, tabs, carriage returns
    ("OP",       r'==|!=|<=|>=|\+\+|--|->|[+\-*/%=<>!]'), # Operators (including multi-char)
    ("PUNCT",    r'[()[\]{},;.]'),                    # Punctuation
    ("MISMATCH", r'.'),                               # Any other character
]

MASTER_PATTERN = re.compile(
    "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPECIFICATION),
    re.MULTILINE
)

def tokenize(code: str) -> Iterator[Token]:
    """
    Yield Tokens found in code string.
    Raises SyntaxError on unexpected character.
    """
    line = 1
    line_start = 0
    pos = 0
    mo = MASTER_PATTERN.match(code, pos)
    while mo is not None:
        kind = mo.lastgroup
        value = mo.group(kind)
        if kind == "NEWLINE":
            line += 1
            line_start = mo.end()
        elif kind == "SKIP" or kind == "COMMENT":
            pass
        elif kind == "ID":
            tok_type = "KEYWORD" if value in KEYWORDS else "IDENT"
            yield Token(tok_type, value, line, mo.start() - line_start + 1)
        elif kind == "NUMBER":
            yield Token("NUMBER", value, line, mo.start() - line_start + 1)
        elif kind == "STRING":
            # Optionally validate/interpret escapes here
            yield Token("STRING", value, line, mo.start() - line_start + 1)
        elif kind == "OP":
            yield Token("OP", value, line, mo.start() - line_start + 1)
        elif kind == "PUNCT":
            yield Token("PUNCT", value, line, mo.start() - line_start + 1)
        elif kind == "MISMATCH":
            raise SyntaxError(f"Unexpected character {value!r} at line {line} col {mo.start() - line_start + 1}")
        pos = mo.end()
        mo = MASTER_PATTERN.match(code, pos)

    # End of input sentinel (optional)
    yield Token("EOF", "", line, pos - line_start + 1)

if __name__ == "__main__":
    sample = r'''
    // Sample program
    int main() {
        int x = 42;
        float y = 3.14;
        string s = "hello\n\"world\"";
        if (x > 0) {
            x = x - 1;
        }
        /* multi-line
           comment */
        return 0;
    }
    '''
    for t in tokenize(sample):
        print(f"{t.line:3}:{t.column:3}  {t.type:8} {t.value!r}")
