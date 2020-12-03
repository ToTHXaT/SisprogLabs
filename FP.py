from typing import *

from PyQt5.QtWidgets import QPlainTextEdit, QTableWidget, QTableWidgetItem
from exceptions import *
from num import to_int
from parsedline import *

from constants import convert, ConstantRepr
from tko import Operation


def get_lines_from_src(src: str) -> Iterator[Tuple[int, str]]:
    for i, line in enumerate(src.split('\n'), start=1):

        line = " ".join(line.split(';', 1)[0].split())
        if line:
            yield i, line


@dataclass
class Directive:
    __slots__ = ('type', 'repr')
    type: str
    repr: ConstantRepr


@dataclass
class Command:
    __slots__ = ('operation', 'op1', 'op2', 'line_num')
    operation: Operation
    op1: str
    op2: str
    line_num: int


@dataclass
class HeaderLine:
    __slots__ = ('name', 'load_addr')
    name: str
    load_addr: int


@dataclass
class FirstPassResults:
    __slots__ = ('tsi', 'src', 'ac', 'pass1_str', 'header_line')
    tsi: Dict[str, int]
    src: List[Union[Command, Directive]]
    ac: int
    pass1_str: str
    header_line: HeaderLine


def first_pass(src: str, tko: TKO):

    lines = get_lines_from_src(src)

    try:
        i, header = next(lines)
    except StopIteration:
        raise HeaderNotFoundException()

    header_parsed_line = parse_line(header, tko, i)

    if header_parsed_line.cmd.lower() != 'start':
        raise HeaderNotFirstException(i)
    if not header_parsed_line .label:
        raise Exception(f'[{i}]: Program doesnt have a name')

    try:
        load_addr = to_int(header_parsed_line.op1)
    except Exception:
        raise WrongHeaderFormatException(i)

    header_line = HeaderLine(name=header_parsed_line.label, load_addr=load_addr)

    was_end = False

    ac = load_addr
    tsi = {}
    op_l = []
    res_line = ''

    for i, line in lines:
        res_line += f'{hex(ac)[2:].zfill(8)}: '
        pl = parse_line(line, tko, i)

        if pl.cmd and pl.cmd.lower() == 'end':
            ac = ac - load_addr
            was_end = True
            break

        if pl.label:
            if tsi.get(pl.label):
                raise DuplicateSymbolicNameException(i)
            else:
                tsi[pl.label] = ac

        if is_cmd(tko, pl.cmd):
            op = tko.get(pl.cmd)
            res_line += hex(op.code)[2:].zfill(2)
            res_line += ' ' + (pl.op1 or '')
            res_line += ' ' + (pl.op2 or '')
            ac += op.length

            op_l.append(Command(operation=op, op1=pl.op1, op2=pl.op2, line_num=i))

        elif is_dir(pl.cmd):

            if pl.cmd == 'byte':
                res_line += 'byte'
                res_line += ' ' + (pl.op1 or '')
                res_line += ' ' + (pl.op2 or '')

                if pl.op2:
                    raise Exception(f"[{i}]: Second argument is not necessary")

                repr = convert(pl.op1, i)

                ac += repr.length

                op_l.append(Directive(type='byte', repr=repr))
            elif pl.cmd == 'word':
                res_line += 'word'
                res_line += ' ' + (pl.op1 or '')
                res_line += ' ' + (pl.op2 or '')

            else:
                raise UnknownIdentifierException(i, pl.cmd)
        else:
            raise UnknownIdentifierException(i, pl.cmd)

        res_line += '\n'

    if not was_end:
        raise EndNotFoundException()

    return FirstPassResults(tsi=tsi, src=op_l, ac=ac, pass1_str=res_line, header_line=header_line)
