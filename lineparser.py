from shlex import shlex
from typing import *

from tko import TKO

directives = [
    'byte',
    'word',
    'start',
    'end'
]

registers = [f"r{i}" for i in range(16)]


def is_cmd(name: str, tko: TKO) -> bool:
    return bool(tko.get(name))


def is_dir(name: str) -> bool:
    return name.lower() in directives


def is_opr(name: str, tko: TKO) -> bool:
    return is_cmd(name) or is_dir(name)


def is_reg(name: str) -> bool:
    return name.lower() in registers


class Command(NamedTuple):
    label: str
    cmd: str
    args: List[str]


class Directive(NamedTuple):
    label: str
    dir: str
    args: List[str]


def parse_line(line: str, tko: TKO, i: int) -> Union[Command, Directive]:

    try:
        shl = shlex(line, posix=False)
        shl.whitespace += ','
        sp = list(shl)
    except Exception as e:
        raise Exception(f'[{i}]: ' + str(e))

    length = len(sp)

    if length == 0:
        pass
    elif length == 1:
        cmd = sp[0]
        if not is_cmd(cmd, tko):
            raise Exception(f'[{i}]: {cmd} is not an operation')
    else:
        label, cmd, *args = sp

        if is_cmd(cmd, tko):
            return Command(label, cmd, args)
        elif is_dir(cmd):
            return Directive(label, cmd, args)

        cmd, *args = sp

        if is_cmd(cmd, tko):
            return Command(None, cmd, args)
        elif is_dir(cmd):
            return Directive(None, cmd, args)

        raise Exception(f'[{i}]: No operation found')
