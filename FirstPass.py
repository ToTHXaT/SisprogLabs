from typing import *

from constants import _convert
from exceptions import *
from lineparser import Command, Directive, is_reg
from lineparser import parse_line
from num import to_int
from tko import Operation, TKO


def get_lines_from_src(src: str) -> Iterator[Tuple[int, str]]:
    for i, line in enumerate(src.split('\n'), start=1):
        sc = line.rfind(';')
        l1 = line.rfind("'")
        l2 = line.rfind('"')

        l = max(l1, l2)

        if sc > l:
            line = " ".join(line.rsplit(';', 1)[0].split())

        if line:
            yield i, line


class Header(NamedTuple):
    program_name: str
    load_addr: int


class Extdef(NamedTuple):
    names: List[str]


class Extref(NamedTuple):
    names: List[str]


class End(NamedTuple):
    load_addr: int


class Cmd(NamedTuple):
    i: int
    op: Operation
    args: List[str]
    length: int
    ac: int


class Dir(NamedTuple):
    i: int
    dir: str
    args: List[str]
    length: int
    ac: int


class FPR(NamedTuple):
    header: Header
    extdef: Extdef
    extref: Extref
    tsi: Dict[str, Tuple[int, str]]
    ac: int
    op_l: List[Union[Tuple[int, Dir], Tuple[int, Cmd]]]
    res_line: str
    end: End


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


def check_extdef(lines: Iterator[Tuple[int, str]], tko: TKO, tsi: Dict[str, Tuple[int, str]]) -> Extdef:
    try:
        i, extdef = next(lines)
    except:
        raise Exception(f'[-]: External definitions line not found')

    if type(extdef_pl := parse_line(extdef, tko, i)) != Directive:
        raise Exception(f'[{i}]: There is no `extdef` directive or it is mentioned later')

    if extdef_pl.dir != 'extdef':
        raise Exception(f'[{i}]: There is no `extdef` directive or it is mentioned later than expected')

    for arg in extdef_pl.args:
        if not arg.isidentifier():
            raise Exception(f'[{i}]: `{arg}` - invalid identifier')

        if tsi.get(arg):
            raise Exception(f'[{i}]: Duplicate external definition')

        tsi[arg] = (-1, 'def')

    return Extdef(extdef_pl.args)


def check_extref(lines: Iterator[Tuple[int, str]], tko: TKO, tsi: Dict[str, Tuple[int, str]]) -> Extref:
    try:
        i, extref = next(lines)
    except:
        raise Exception(f'[-]: External names line not found')

    if type(extref_pl := parse_line(extref, tko, i)) != Directive:
        raise Exception(f'[{i}]: There is no `extref` directive or it is mentioned later')

    if extref_pl.dir != 'extref':
        raise Exception(f'[{i}]: There is no `extref` directive or it is mentioned later than expected')

    for arg in extref_pl.args:
        if not arg.isidentifier():
            raise Exception(f'[{i}]: `{arg}` - invalid identifier')

        if tsi.get(arg):
            raise Exception(f'[{i}]: Duplicate external definition')

        tsi[arg] = (-1, 'ref')

    return Extref(extref_pl.args)


def do_first_pass(src: str, tko: TKO):
    lines = get_lines_from_src(src)

    header = check_header(lines, tko)

    was_end = False
    ac = header.load_addr
    tsi: Dict[str, Tuple[int, str]] = {}
    op_l = []
    res_line = ''

    extdef = check_extdef(lines, tko, tsi)

    extref = check_extref(lines, tko, tsi)

    for i, line in lines:
        res_line += f'{hex(ac)[2:].zfill(6)}: '
        pl = parse_line(line, tko, i)

        if type(pl) is Directive and pl.dir.lower() == 'end':
            was_end = True
            ac = ac - header.load_addr

            if len(pl.args) == 1:

                try:
                    end_load_addr = to_int(pl.args[0])
                except:
                    raise Exception(f'[{i}]: `{pl.args[0]}` - invalid')

                if header.load_addr <= end_load_addr <= header.load_addr + ac:
                    end_load_addr = End(end_load_addr)
                    break
                else:
                    raise Exception(
                        f'[{i}]: boot address is bigger than  load address plus module size or lower than load addres')
            elif len(pl.args) == 0:
                end_load_addr = End(header.load_addr)

            if len(pl.args) > 1:
                raise Exception(f'[{i}]: Invalid end directive format')

            break

        if pl.label:

            if not pl.label.isidentifier():
                raise Exception(f'[{i}]: `{pl.label}` wrong format for label')

            if is_reg(pl.label):
                raise Exception(f'[{i}]: Label and register name conflict')

            if lbl := tsi.get(pl.label):
                if lbl[1] == 'def':
                    if lbl[0] == -1:
                        tsi[pl.label] = (ac, 'def')
                    else:
                        raise Exception(f'[{i}]: Duplicate symbolic name `{pl.label}`')
                elif lbl[1] == 'ref':
                    raise Exception(f'[{i}]: External reference and label name conflict')
                else:
                    raise DuplicateSymbolicNameException(i)
            else:
                tsi[pl.label] = (ac, '')

        if type(pl) is Command:

            op = tko.get(pl.cmd)

            if len(pl.args) > 2: raise Exception(f'[{i}]: No more than 2 args is possible')

            res_line += hex(op.code)[2:].zfill(2)

            if len(pl.args) == 1:
                res_line += ' ' + pl.args[0]
            elif len(pl.args) == 2:
                res_line += ' ' + pl.args[0] + ', ' + pl.args[1]

            ac += op.length

            op_l.append((ac - op.length, Cmd(i, op, pl.args, op.length, ac - op.length)))
        else:

            res_line += pl.dir + ' '
            res_line += ', '.join(pl.args)

            if len(pl.args) == 0:
                raise Exception(f'[{i}]: No arguments provided')

            length = sum(_convert(j, pl.dir, i).length for j in pl.args)

            ac += length

            op_l.append((ac - length, Dir(i, pl.dir, pl.args, length, ac - length)))

        res_line += '\n'

    if header.load_addr + ac > int('ffffff', 16):
        raise Exception(f'[-]: Not enough memory. Keep the Load address + module length below `ffffff`')

    if not was_end:
        raise Exception(f'[-]: No end statment')

    if (lond := [key for key, (addr, tp) in tsi.items() if tp == 'def' and addr == -1]):
        raise Exception(f'[-]: Following external names were not found in program: {" ".join(i for i in lond)}')

    return FPR(header, extdef, extref, tsi, ac, op_l, res_line, end_load_addr)
