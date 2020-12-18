from typing import *

from FirstPass import FPR, Cmd, Dir
from constants import _convert
from constants import convert
from lineparser import is_reg
from num import to_int_safe


def is_label(name: str, tsi: Dict[str, Tuple[int, str]]):
    if name[0] == '~':
        return bool(tsi.get(name[1:]))
    return bool(tsi.get(name))


def make_bin(op: str, tsi: Dict[str, Tuple[int, str]], tm: List[Tuple[str, str]], load_addr: int, frmt: str, ac: int,
             i: int = 0) -> str:
    if op is None:
        return ""

    if is_reg(op):
        return hex(int(op[1:]))[2:].zfill(2)

    elif code := tsi.get(op):

        if code[1] == 'ref':
            if op[0] == '~':
                raise Exception(f'[{i}]: Relative addressing is not possible with external references')

            tm.append((hex(ac - load_addr)[2:].zfill(6), op))
            return hex(0)[2:].zfill(6)

        if frmt[0] == 'D' or frmt[0] == 'M':
            tm.append((hex(ac - load_addr)[2:].zfill(6), ''))
            return hex(code[0])[2:].zfill(6)
        elif frmt[0] == 'R':
            return hex(code[0] - load_addr)[2:].zfill(6)
        else:
            return ""
    elif op.startswith('~') and (code := tsi.get(op[1:])):

        if code[1] == 'ref':
            if op[0] == '~':
                raise Exception(f'[{i}]: Relative addressing is not possible with external references')

            tm.append((hex(ac - load_addr)[2:].zfill(6), op))
            return hex(0)[2:].zfill(6)

        if frmt[0] == 'D' or frmt[0] == 'R':
            raise Exception(f'[{i}]: `~` is only allowed in mixed mode')
        else:
            return hex(code[0] - load_addr)[2:].zfill(6)

    else:
        try:
            return convert(op, i).code
        except Exception as e:
            print(str(e))
            print(str(e).split(':'))
            print(str(e).split(':')[0])
            raise Exception((str(e).split(":")[0]) + f': `{op}` Unknown identifier')


def do_second_pass(fpr: FPR, frmt: str):
    tm: List[Tuple[str, str]] = []

    hl = fpr.header

    H_line = f'H {hl.program_name} {hex(hl.load_addr)[2:].zfill(12)} {hex(fpr.ac)[2:].zfill(12)}\n'

    I_line = ''

    for ac, i in fpr.op_l:
        if type(i) is Cmd:
            cmd: Cmd = i

            if len(cmd.args) == 0 and cmd.op.length > 1:
                raise Exception(f'[{i.i}]: Invalid params for `{cmd.op.name}`')

            if len(cmd.args) == 1:
                if is_label(cmd.args[0], fpr.tsi):
                    if cmd.op.length != 4:
                        raise Exception(f"[{i.i}]: Invalid param type for `{cmd.op.name}` operation")
                    code = cmd.op.code * 4 + 1
                elif is_reg(cmd.args[0]):
                    if cmd.op.length != 2:
                        raise Exception(f"[{i.i}]: Invalid param type for `{cmd.op.name}` operation")
                    code = cmd.op.code * 4
                else:
                    code = cmd.op.code * 4
            else:
                if is_label(cmd.args[0], fpr.tsi) and is_label(cmd.args[1], fpr.tsi):
                    if cmd.op.length != 6:
                        raise Exception(f"[{i.i}]: Invalid param type for `{cmd.op.name}` operation")
                elif is_reg(cmd.args[0]) and is_reg(cmd.args[1]):
                    if cmd.op.length != 3:
                        raise Exception(f"[{i.i}]: Invalid param type for `{cmd.op.name}` operation")
                    code = cmd.op.code * 4
                elif to_int_safe(cmd.args[1]) and is_reg(cmd.args[0]):
                    if cmd.op.length != 3:
                        raise Exception(f"[{i.i}]: Invalid param type for `{cmd.op.name}` operation")
                    code = cmd.op.code * 4
                elif is_reg(cmd.args[0]) and is_label(cmd.args[1], fpr.tsi):
                    if cmd.op.length != 5:
                        raise Exception(f"[{i.i}]: Invalid param type for `{cmd.op.name}` operation")
                    code = cmd.op.code * 4 + 1
                elif is_reg(cmd.args[1]) and is_label(cmd.args[0], fpr.tsi):
                    if cmd.op.length != 5:
                        raise Exception(f"[{i.i}]: Invalid param type for `{cmd.op.name}` operation")
                    code = cmd.op.code * 4 + 1

                else:
                    raise Exception(f"[{i.i}]: Invalid params type for `{cmd.op.name}` operation")

            code = hex(code)[2:].zfill(2)
            I_line += f"T {hex(i.ac)[2:].zfill(6)} {hex(cmd.op.length)[2:].zfill(2)} {code} "
            I_line += " ".join((make_bin(j, fpr.tsi, tm, hl.load_addr, frmt, ac, i.i) for j in cmd.args)) + '\n'

        else:
            dir: Dir = i
            I_line += f"T {hex(i.ac)[2:].zfill(6)} {hex(dir.length)[2:].zfill(2)} " + ' '.join(
                (_convert(j, dir.dir, dir.i).code for j in dir.args)) + '\n'
    E_line = f'E {hex(fpr.end.load_addr)[2:].zfill(12)}'

    return H_line, I_line, E_line, tm
