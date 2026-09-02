import sys
from textwrap import TextWrapper
import os

def markdown_to_plain(md: str) -> str:
    return _wrap(md.replace('<', '&lt;').replace('>', '&gt;'))

def _wrap(text: str, width: int = 72) -> str:
    wrapper = TextWrapper(width=width)
    lines = text.split('\n')
    for i in range(len(lines)):
        if not lines[i].startswith('* '):
            if not lines[i].startswith('#'):
                if not lines[i].startswith('> ') and (i == 0 or lines[i-1] != ''):
                    wrapper.initial_indent = ''
                    wrapper.subsequent_indent = ''
            else:
                wrapper.initial_indent = ''
                wrapper.subsequent_indent = ''
        if lines[i].startswith('
