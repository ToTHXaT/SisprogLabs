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


def check_strings(f: Callable[[str, TKO, int], Union[Command, Directive]]) -> Callable[
    [str, TKO, int], Union[Command, Directive]]:
    def inner(line: str, tko: TKO, i: int):
        dir_or_cmd = f(line, tko, i)

        if type(dir_or_cmd) is Directive:
            dirc = cast(Directive, dir_or_cmd)

            # print(dirc.label, dirc.dir, dirc.args)

            return dirc
        else:
            return dir_or_cmd

    return inner


def handle_string(line: str, tko: TKO, i: int):
    i_of_1 = line.find('"')
    i_of_2 = line.find("'")

    if i_of_1 >= 0 and i_of_2 >= 0:
        lind = min(i_of_1, i_of_2)

    elif i_of_1 >= 0 > i_of_2:
        lind = i_of_1

    elif i_of_1 < 0 <= i_of_2:
        lind = i_of_2

    else:
        raise Exception("lineparser.check_string")

    ch = line[lind]

    rind = line.rfind(ch)

    if rind == -1 or rind == lind: raise Exception(f"[{i}]: No closing quotation")

    if line[rind + 1:] != "":
        raise Exception(f'[{i}]: Invalid string format')

    prm = line[lind:rind + 1]
    line = line[:lind] + line[rind + 1:]

    if ',' in line:
        raise Exception(f'[{i}]: Multiple arguments prohibited when defining strings')

    pl = parse_line(line, tko, i)

    #print(pl, prm, ch, lind, rind, line)

    return Directive(pl.label, pl.dir, [prm])


@check_strings
def parse_line(line: str, tko: TKO, i: int) -> Union[Command, Directive]:
    if "'" in line or '"' in line:
        return handle_string(line, tko, i)

    try:
        shl = shlex(line, posix=False)
        shl.whitespace += ','
        shl.wordchars += '-+?~!@#$%^&*'
        sp = list(shl)
    except Exception as e:
        raise Exception(e)

    length = len(sp)

    if length == 0:
        pass
    elif length == 1:
        cmd = sp[0]

        if is_cmd(cmd, tko):
            return Command(None, cmd, [])
        elif is_dir(cmd):
            return Directive(None, cmd, [])
        else:
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

        raise Exception(f'[{i}]: Invalid line. `{args[0]}` is neither operation nor directive.')
