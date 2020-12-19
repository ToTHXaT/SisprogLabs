from exceptions import *
from lineparser import Directive, parse_line
from num import *
from tko import Operation
from tko import TKO


class Header(NamedTuple):
    program_name: str
    load_addr: int
    module_len: Union[int, str]

    def __str__(self):
        if self.program_name is None and self.load_addr is None and self.module_len is None:
            return ''

        return f'H {self.program_name or "-"} {hex(self.load_addr or 0)[2:].zfill(6)} {hex(self.module_len or 0)[2:].zfill(6)}\n'


class Extdef(NamedTuple):
    names: List[str]

    def __bool__(self):
        return bool(self.names)


class Extref(NamedTuple):
    names: List[str]

    def __bool__(self):
        return bool(self.names)


class End(NamedTuple):
    load_addr: int

    def __str__(self):
        return f'E {self.load_addr}'


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


class Module(NamedTuple):
    header: Header
    extdef: Extdef
    extref: Extref
    op_l: List[Union[Tuple[int, Dir], Tuple[int, Cmd]]]
    end: End
    tsi: Dict[str, Tuple[int, str, str]]

    def __str__(self):
        return f'{self.header}\n{self.extdef}\n{self.extref}\n{self.op_l}\n{self.end}'


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

    return Header(header_parsed_line.label, load_addr, '')


def check_extdef(pl: Directive, tsi: Dict[str, Tuple[int, str, str]], csect_name: str, i: int) -> Extdef:
    for arg in pl.args:
        if not arg.isidentifier():
            raise Exception(f'[{i}]: `{arg}` - invalid identifier')

        if tsi.get(arg):
            raise Exception(f'[{i}]: Duplicate external definition')

        tsi[arg] = (-1, 'def', csect_name)

    return Extdef(pl.args)


def check_extref(pl: Directive, tsi: Dict[str, Tuple[int, str, str]], csect_name: str, i: int) -> Extref:
    for arg in pl.args:
        if not arg.isidentifier():
            raise Exception(f'[{i}]: `{arg}` - invalid identifier')

        if tsi.get(arg):
            raise Exception(f'[{i}]: Duplicate external definition')

        tsi[arg] = (-1, 'ref', csect_name)

    return Extref(pl.args)
