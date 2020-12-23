from constants import _convert, convert
from exceptions import *
from lineparser import Directive, parse_line
from lineparser import is_reg
from num import *
from tko import Operation
from tko import TKO


class TM(NamedTuple):
    lst: List[Tuple[str, str]]

    def __str__(self):
        return ""



def make_bin(op: str, tsi: Dict[str, Tuple[int, str, str, List[int]]], tm: TM, load_addr: int,
             frmt: str,
             ac: int,
             prg_name: str,
             i: int = 0) -> str:
    if op is None:
        return ""

    code = tsi.get(op)

    if is_reg(op):
        return hex(int(op[1:]))[2:].zfill(2)

    elif code:
        if code[0] != -1:
            if code[1] == 'ref':
                if op[0] == '~':
                    raise Exception(f'[{i}]: Relative addressing is not possible with external references')

                tm.lst.append((hex(ac - load_addr)[2:].zfill(6), op))
                return hex(0)[2:].zfill(6)

            if frmt[0] == 'D' or frmt[0] == 'M':
                tm.lst.append((hex(ac - load_addr)[2:].zfill(6), ''))
                return hex(code[0])[2:].zfill(6)
            elif frmt[0] == 'R':
                return hex(code[0] - load_addr)[2:].zfill(6)
            else:
                return ""
        else:
            if code[1] == 'ref':
                if op[0] == '~':
                    raise Exception(f'[{i}]: Relative addressing is not possible with external references')

                tm.lst.append((hex(ac)[2:].zfill(6), op))

                return hex(0)[2:].zfill(6)

            return op

    elif op.startswith('~') and (code := tsi.get(op[1:])):

        if code[1] == 'ref':
            if op[0] == '~':
                raise Exception(f'[{i}]: Relative addressing is not possible with external references')

            tm.lst.append((hex(ac - load_addr)[2:].zfill(6), op))
            return hex(0)[2:].zfill(6)

        if frmt[0] == 'D' or frmt[0] == 'R':
            raise Exception(f'[{i}]: `~` is not allowed')
        else:
            if code[0] == -1:
                return op
            else:
                return hex(code[0] - load_addr)[2:].zfill(6)

    else:
        try:
            return convert(op, i).code
        except Exception as e:
            if op.isidentifier():
                return op
            elif op[0] == '~' and op[1:].isidentifier():
                if frmt[0] in ('R', 'D'):
                    raise Exception(f'[{i}]: `~` is not allowed')
                return op
            else:
                raise Exception((str(e).split(":")[0]) + f': `{op}` Unknown identifier or invalid format')


class Header(NamedTuple):
    program_name: str
    load_addr: int
    module_len: int

    def __str__(self):
        if self.program_name is None and self.load_addr is None and self.module_len is None:
            return ''

        program_name = self.program_name or '-'
        load_addr = hex(self.load_addr)[2:].zfill(6) if not self.load_addr is None else '-'
        module_len = hex(self.module_len)[2:].zfill(6) if not self.module_len is None else '-'

        return f'H {program_name} {load_addr} {module_len}'


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
        if self.load_addr is None:
            return ''

        return f'E {hex(self.load_addr)[2:].zfill(6)}'


class Cmd(NamedTuple):
    i: int
    op: Operation
    args: List[str]
    code: str
    ac: int

    def validate(self, tsi: Dict[str, Tuple[int, str, str, List[int]]], tm: TM, load_addr: int,
                 frmt: str,
                 prg_name: str):
        if len(self.args) == 0 and self.op.length > 1:
            raise Exception(f'[{self.i}]: Invalid params for `{self.op.name}`')

        if len(self.args) == 1:
            if can_be_label(self.args[0]):
                if self.op.length != 4:
                    raise Exception(f"[{self.i}]: Invalid param type for `{self.op.name}` operation")
                code = self.op.code * 4 + 1
            elif is_reg(self.args[0]):
                if self.op.length != 2:
                    raise Exception(f"[{self.i}]: Invalid param type for `{self.op.name}` operation")
                code = self.op.code * 4
            else:
                code = self.op.code * 4
        else:

            if is_reg(self.args[0]) and is_reg(self.args[1]):
                if self.op.length != 3:
                    raise Exception(f"[{self.i}]: Invalid param type for `{self.op.name}` operation")
                code = self.op.code * 4
            elif to_int_safe(self.args[1]) and is_reg(self.args[0]):
                if self.op.length != 3:
                    raise Exception(f"[{self.i}]: Invalid param type for `{self.op.name}` operation")
                code = self.op.code * 4
            elif to_int_safe(self.args[1]) and can_be_label(self.args[0]):
                if self.op.length != 5:
                    raise Exception(f"[{self.i}]: Invalid param type for `{self.op.name}` operation")
                code = self.op.code * 4 + 1
            elif is_reg(self.args[0]) and can_be_label(self.args[1]):
                if self.op.length != 5:
                    raise Exception(f"[{self.i}]: Invalid param type for `{self.op.name}` operation")
                code = self.op.code * 4 + 1
            elif is_reg(self.args[1]) and can_be_label(self.args[0]):
                if self.op.length != 5:
                    raise Exception(f"[{self.i}]: Invalid param type for `{self.op.name}` operation")
                code = self.op.code * 4 + 1
            elif can_be_label(self.args[0]) and can_be_label(self.args[1]):
                if self.op.length != 6:
                    raise Exception(f"[{self.i}]: Invalid param type for `{self.op.name}` operation")

            else:
                raise Exception(f"[{self.i}]: Invalid params type for `{self.op.name}` operation")

        code = hex(code)[2:].zfill(2)

        if self.args.__len__() == 0:
            args = []
        elif self.args.__len__() == 1:
            args = [make_bin(self.args[0], tsi, tm, load_addr, frmt, self.ac, prg_name, self.i)]
        elif self.args.__len__() == 2:
            args = [
                make_bin(self.args[0], tsi, tm, load_addr, frmt, self.ac, prg_name, self.i),
                make_bin(self.args[1], tsi, tm, load_addr, frmt, self.ac, prg_name, self.i),
            ]
        else:
            raise Exception(f'[{self.i}]: No more than 2 args is possible')
        for arg in args:
            if can_be_label(arg):
                if frmt[0] in ('R', 'D') and arg[0] == '~':
                    raise Exception(f'[{self.i}]: `~` is not allowed')

                if arg[0] == '~':
                    ag = arg[1:]
                else:
                    ag = arg

                if ts := tsi.get(ag):
                    if ts[1] == 'ref':
                        pass
                        # tm.lst.append((hex(self.ac)[2:].zfill(6), ag))
                        # tsi.update({
                        #     ag: (0, ts[1], ts[2], ts[3])
                        # })
                    else:
                        if ts[0] == -1:
                            tsi.update({
                                ag: (ts[0], ts[1], ts[2], [*ts[3], self.ac])
                            })
                        else:
                            pass
                else:
                    tsi[ag] = (-1, '', prg_name, [self.ac])

        return Cmd(self.i, self.op, args, code, self.ac)

    def __str__(self):
        I_line = ''
        I_line += f"T {hex(self.ac)[2:].zfill(6)} {hex(self.op.length)[2:].zfill(2)} " \
                  f"{self.code} {' '.join(self.args)}"

        return I_line


class Dir(NamedTuple):
    i: int
    dir: str
    args: List[str]
    length: int
    ac: int

    def __str__(self):
        return f"T {hex(self.ac)[2:].zfill(6)} {hex(self.length)[2:].zfill(2)} " + ' '.join(
            (_convert(j, self.dir, self.i).code for j in self.args))


class Module(NamedTuple):
    header: Header
    extdef: Extref
    extref: Extdef
    op_l: List[Union[Cmd, Dir]]
    end: End
    tsi: Dict[str, Tuple[int, str, str, List[int]]]
    tm: TM

    def __str__(self):
        if str(self.end):
            for k, (ac, tp, prg_name, ref_l) in self.tsi.items():
                if ref_l.__len__() > 0:
                    raise Exception(
                        f'[-]: `{k}` - symbol not found. Used in {str(" ").join(hex(i)[2:].zfill(6) for i in ref_l)}')

                if ac == -1 and tp != 'ref':
                    raise Exception(f'[-]: `{k}` - symbol not found')

        body = '\n'.join(str(i) for i in self.op_l)

        return f'{self.header}\n{body}\n{self.tm if str(self.end) else str()}\n{self.end}'


def can_be_label(name: str):
    if name[0] == '~':
        return name[1:].isidentifier()
    return name.isidentifier()


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

    if load_addr == 0:
        raise Exception(f'[{i}]: load addr cant be 0')

    return Header(header_parsed_line.label, load_addr, None)


def check_extdef(pl: Directive, tsi: Dict[str, Tuple[int, str, str, List[int]]], csect_name: str, i: int) -> Extdef:
    for arg in pl.args:
        if not arg.isidentifier():
            raise Exception(f'[{i}]: `{arg}` - invalid identifier')

        if tsi.get(arg):
            raise Exception(f'[{i}]: Duplicate external definition')

        tsi[arg] = (-1, 'def', csect_name, [])

    return Extdef(pl.args)


def check_extref(pl: Directive, tsi: Dict[str, Tuple[int, str, str, List[int]]], csect_name: str, i: int) -> Extref:
    for arg in pl.args:
        if not arg.isidentifier():
            raise Exception(f'[{i}]: `{arg}` - invalid identifier')

        if tsi.get(arg):
            raise Exception(f'[{i}]: Duplicate external definition')

        tsi[arg] = (-1, 'ref', csect_name, [])

    return Extref(pl.args)
