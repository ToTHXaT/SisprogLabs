from pprint import pprint
from typing import *

from FP import FirstPassResults
from FP import Command, Directive

from parsedline import is_dir, is_cmd, is_reg
from num import to_int
from constants import convert


def make_bin(op: str, tsi: Dict[str, int], i: int = 0) -> str:
    if op is None:
        return ""

    if is_reg(op):
        return hex(int(op[1:]))[2:].zfill(8)
    elif code := tsi.get(op):
        return hex(code)[2:].zfill(8)
    else:
        try:
            return convert(op, i).code
        except Exception as e:
            print(str(e))
            print(str(e).split(':'))
            print(str(e).split(':')[0])
            raise Exception((str(e).split(":")[0]) + ': Unknown identifier')


def second_pass(fp: FirstPassResults):

    hl = fp.header_line

    H_line = f'{hl.name} {hex(hl.load_addr)[2:].zfill(12)} {hex(fp.ac)[2:].zfill(12)}\n'

    I_line = ''
    for i in fp.src:
        if type(i) == Command:
            cmd: Command = i
            code = hex(cmd.operation.code)[2:].zfill(2)
            I_line += f"{code} {make_bin(cmd.op1, fp.tsi, i.line_num)} {make_bin(cmd.op2, fp.tsi, i.line_num)}\n"
        else:
            dir: Directive = i
            I_line += f"{dir.repr.code}\n"

    E_line = f'{hex(fp.header_line.load_addr)[2:]}'


    return H_line, I_line, E_line