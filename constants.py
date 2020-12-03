from typing import *

from bitstring import Bits

from parsedline import ParsedLine
from num import to_int_safe
from dataclasses import dataclass


def twos(num: int, bt: int) -> str:
    return Bits(int=num, length=bt).bin


class ConstantRepr(NamedTuple):
    code: str
    length: int


def reverse_bits(s: str) -> str:
    return ''.join(reversed([s[i:i+2] for i in range(0, len(s), 2)]))


def convert(cs: str, i: Optional[int] = 0) -> ConstantRepr:
    if int_repr := to_int_safe(cs):

        if int_repr >= 2 ** 64:
            raise Exception(f"[{i}]: {cs} is too big")

        if int_repr > 0:

            if int_repr >= 2 ** 32:
                length = 64
            elif int_repr >= 2 ** 16:
                length = 32
            elif int_repr >= 2 ** 8:
                length = 16
            else:
                length = 8

            code = hex(int_repr)[2:].zfill(length // 4)

        else:

            if int_repr <= - (2 ** 64):
                raise Exception(f"[{i}]: {cs} is too big")

            if int_repr >= - (2 ** 7):
                code = twos(int_repr, 8)
                length = 8
            elif int_repr >= - (2 ** 15):
                code = twos(int_repr, 16)
                length = 16
            elif int_repr >= - (2 ** 31):
                code = twos(int_repr, 32)
                length = 32
            else:
                code = twos(int_repr, 64)
                length = 64

    elif (cs.startswith('"') and cs.endswith('"')) or (cs.startswith("'") and cs.endswith("'")):
        s = cs[1:-1]
        length = s.__len__() * 8
        code = "".join((hex(ord(i))[2:].zfill(2) for i in s))
    elif cs.startswith("'") and cs.endswith("'") and cs.__len__() == 3:
        s = cs[1:-1]
        length = 8
        code = hex(ord(s))[2:].zfill(2)
    else:
        raise Exception(f'[{i}]: `{cs}` - Invalid constant')

    return ConstantRepr(code, length // 8)


def _convert(cs: str, typ: str, i: Optional[int] = 0) -> ConstantRepr:

    if int_repr := to_int_safe(cs):

        if typ == 'byte':
            if abs(int_repr) > 2 ** 8: raise Exception(f'[{i}]: `{cs}` is too big for byte')
            length = 8
        elif typ == 'word':
            if abs(int_repr) > 2 ** 16: raise Exception(f'[{i}]: `{cs}` is too big for word')
            length = 16
        else:
            raise Exception(' Unimplemented `constants._convert` ')

        if int_repr >= 0:
            code = hex(int_repr)[2:].zfill(length // 4)
        else:
            code = twos(int_repr, length)

        if typ == 'word':
            code = reverse_bits(code)

    elif cs.startswith("'") and cs.endswith("'") and cs.__len__() == 3:
        s = cs[1:-1]

        if typ == 'byte':
            length = 8
        elif typ == 'word':
            length = 16
        else:
            raise Exception(' Unimplemented `constants._convert` ')

        code = hex(ord(s))[2:].zfill(length // 4)
        code = reverse_bits(code)

    elif (cs.startswith('"') and cs.endswith('"')) or (cs.startswith("'") and cs.endswith("'")):
        s = cs[1:-1]
        length = s.__len__() * 8
        code = "".join((hex(ord(i))[2:].zfill(2) for i in s))
    else:
        raise Exception(f'[{i}]: `{cs}` - Invalid constant')

    return ConstantRepr(code, length // 8)
