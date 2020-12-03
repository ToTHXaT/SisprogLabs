from typing import *

from FirstPass import FPR, Cmd, Dir
from constants import _convert
from constants import convert
from lineparser import is_reg


def make_bin(op: str, tsi: Dict[str, int], tm: List[str], load_addr: int, frmt: str, ac: int, i: int = 0) -> str:
    if op is None:
        return ""

    if is_reg(op):
        return hex(int(op[1:]))[2:].zfill(2)
    elif code := tsi.get(op):

        print(hex(code)[2:].zfill(8), frmt, hex(ac), hex(load_addr))
        if frmt[0] == 'D':
            tm.append(hex(ac - load_addr)[2:].zfill(8))
            return hex(code)[2:].zfill(8)
        elif frmt[0] == 'R' or frmt[0] == 'M':
            return hex(code - load_addr)[2:].zfill(8)
        else:
            return ""
    elif op.startswith('~') and (code := tsi.get(op[1:])):

        print('$', hex(code)[2:].zfill(8), frmt)

        if frmt[0] == 'D' or frmt[0] == 'R':
            raise Exception(f'[{i}]: `~` is only allowed in mixed mode')
        else:
            tm.append(hex(ac - load_addr)[2:].zfill(8))
            return hex(code)[2:].zfill(8)

    else:
        try:
            return convert(op, i).code
        except Exception as e:
            print(str(e))
            print(str(e).split(':'))
            print(str(e).split(':')[0])
            raise Exception((str(e).split(":")[0]) + f': `{op}` Unknown identifier')


def do_second_pass(fpr: FPR, frmt: str):
    tm: List[str] = []

    hl = fpr.header

    H_line = f'{hl.program_name} {hex(hl.load_addr)[2:].zfill(12)} {hex(fpr.ac)[2:].zfill(12)}\n'

    I_line = ''
    for ac, i in fpr.op_l:
        if type(i) is Cmd:
            cmd: Cmd = i
            code = hex(cmd.op.code)[2:].zfill(2)
            I_line += f"{code} "
            I_line += " ".join((make_bin(j, fpr.tsi, tm, hl.load_addr, frmt, ac, i.i) for j in cmd.args)) + '\n'
        else:
            dir: Dir = i
            I_line += ' '.join((_convert(j, dir.dir, dir.i).code for j in dir.args)) + '\n'

    E_line = f'{hex(fpr.header.load_addr)[2:]}'

    return H_line, I_line, E_line, tm
