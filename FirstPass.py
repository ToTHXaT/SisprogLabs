from typing import *

from PyQt5.QtWidgets import QPlainTextEdit, QTableWidget, QTableWidgetItem
from exceptions import *
from num import to_int, to_int_safe
from lineparser import parse_line
from lineparser import Command, Directive

from constants import convert, ConstantRepr, _convert
from tko import Operation, TKO


def get_lines_from_src(src: str) -> Iterator[Tuple[int, str]]:
    for i, line in enumerate(src.split('\n'), start=1):

        line = " ".join(line.split(';', 1)[0].split())
        if line:
            yield i, line


class Header(NamedTuple):
    program_name: str
    load_addr: int


class Cmd(NamedTuple):
    i: int
    op: Operation
    args: List[str]


class Dir(NamedTuple):
    i: int
    dir: str
    args: List[str]


class FPR(NamedTuple):
    header: Header
    tsi: Dict[str, int]
    ac: int
    op_l: List[Union[Dir, Cmd]]
    res_line: str



def check_header(lines: Iterator[Tuple[int, str]], tko: TKO) -> Header:
    try:
        i, header = next(lines)
    except StopIteration:
        raise HeaderNotFoundException()

    if type(header_parsed_line := parse_line(header, tko, i)) != Directive:
        raise Exception(f'[{i}]: There is no `start` directive')

    if header_parsed_line.dir.lower() != 'start':
        raise HeaderNotFirstException(i)

    if header_parsed_line.args.__len__() < 1:
        raise Exception(f'[{i}]: No load address')

    if not header_parsed_line.label:
        raise Exception(f'[{i}]: Program does not have a name')

    try:
        load_addr = to_int(header_parsed_line.args[0])
    except Exception:
        raise Exception(f'[{i}]: Invalid load address')

    return Header(header_parsed_line.label, load_addr)


def do_first_pass(src: str, tko: TKO):

    lines = get_lines_from_src(src)

    header = check_header(lines, tko)

    was_end = False
    ac = header.load_addr
    tsi: Dict[str, int] = {}
    op_l = []
    res_line = ''

    for i, line in lines:
        res_line += f'{hex(ac)[2:].zfill(8)}: '
        pl = parse_line(line, tko, i)

        if type(pl) is Directive and pl.dir.lower() == 'end':
            was_end = True
            ac = ac - header.load_addr
            break

        if pl.label:
            if tsi.get(pl.label):
                raise DuplicateSymbolicNameException(i)
            else:
                tsi[pl.label] = ac

        if type(pl) is Command:

            op = tko.get(pl.cmd)

            if len(pl.args) > 2: raise Exception(f'[{i}]: No more than 2 args is possible')

            res_line += hex(op.code)[2:].zfill(2)

            if len(pl.args) == 1:
                res_line += ' ' + pl.args[0]
            elif len(pl.args) == 2:
                res_line += ' ' + pl.args[0] + ', ' + pl.args[1]

            ac += op.length

            op_l.append(Cmd(i, op, pl.args))
        else:

            res_line += pl.dir + ' '
            res_line += ', '.join(pl.args)

            length = sum(_convert(i, pl.dir).length for i in pl.args)

            ac += length

            op_l.append(Dir(i, pl.dir, pl.args))

        res_line += '\n'

    return FPR(header, tsi, ac, op_l, res_line)


