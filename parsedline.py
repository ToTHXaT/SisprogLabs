import shlex
from tko import TKO

from exceptions import *

from dataclasses import dataclass


directives = [
    'byte',
    'word',
    'start',
    'end'
]

registers = [f"r{i}" for i in range(15)]


@dataclass
class ParsedLine:
    __slots__ = ('label', 'cmd', 'op1', 'op2')
    label: str
    cmd: str
    op1: str
    op2: str


def is_cmd(tko: TKO, name: str) -> bool:
    return bool(tko.get(name))


def is_dir(name: str) -> bool:
    return name.lower() in directives


def is_reg(name: str) -> bool:
    return name.lower() in registers


def parse_line(line: str, tko: TKO, i: int) -> ParsedLine:

    label = None
    cmd = None
    op1 = None
    op2 = None

    try:
        sp = shlex.split(line, posix=False)
    except Exception as e:
        raise Exception(f'[{i}]: ' + str(e))
    length = sp.__len__()

    if length == 1:
        cmd = sp[0]
    elif length == 2:

        if is_cmd(tko, sp[0]) or is_dir(sp[0]):
            cmd = sp[0]
            op1 = sp[1]
        else:
            label = sp[0]
            cmd = sp[1]

    elif length == 3:

        if is_cmd(tko, sp[0]) or is_dir(sp[0]):
            cmd = sp[0]
            op1 = sp[1] if sp[1][-1] != ',' else sp[1][:-1]
            op2 = sp[2]
        else:
            label = sp[0]
            cmd = sp[1]
            op1 = sp[2]

    elif length == 4:

        if is_cmd(tko, sp[0]) or is_dir(sp[0]): raise Exception(f'[{i}]: Wrong line format')

        if not (is_cmd(tko, sp[1]) or is_dir(sp[1])): raise Exception(f'[{i}]: Wrong format')

        label = sp[0]
        cmd = sp[1]
        op1 = sp[2] if sp[2][-1] != ',' else sp[2][:-1]
        op2 = sp[3]
    else:
        raise LineWrongFormatException(i)

    return ParsedLine(label=label, cmd=cmd, op1=op1, op2=op2)
