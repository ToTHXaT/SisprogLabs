from dataclasses import dataclass
from typing import List, Union, Optional

from PyQt5 import QtWidgets

from exceptions import *
from num import to_int


@dataclass
class Operation:
    __slots__ = ('name', 'code', 'length')
    name: str
    code: int
    length: int


class TKO:
    __slots__ = ('tb',)
    tb: List[Operation]

    def __init__(self, tb: QtWidgets.QTableWidget):

        mentioned_names = {}
        mentioned_codes = {}
        res = []
        for i in range(tb.rowCount()):
            inner = []
            for j in range(tb.columnCount()):
                try:
                    inner.append(tb.item(i, j).text())
                except AttributeError:
                    inner.append('')

            inner = self._check_row(inner[0], inner[1], inner[2], i)
            if inner:
                res.append(inner)
                n = mentioned_names.get(inner.name, None)
                if n:
                    raise OpeartionNameDoubleDefinitionException(n[1] + 1, i + 1)

                n = mentioned_codes.get(inner.code)
                if n:
                    raise OpeartionCodeDoubleDefinitionException(n[1] + 1, i + 1)

                mentioned_names[inner.name] = (True, i)
                mentioned_codes[inner.code] = (True, i)

        self.tb = res

    def _check_row(self, name: str, code: str, length: str, row_num: int) -> Optional[Operation]:
        if name == '' and code == '' and length == '':
            return

        if name == '':
            raise NameNotMentionedInTheTKOException(row_num + 1)
        if code == '':
            raise CodeNotMentionedInTheTKOException(row_num + 1)
        if length == '':
            raise LengthNotMentionedInTheTKOException(row_num + 1)

        try:
            length = to_int(length)
        except ValueError:
            raise LenghtIsNotIntException(row_num + 1)

        try:
            int_code = to_int(code)
        except ValueError:
            raise CodeIsNotBinaryException(row_num + 1)

        if int_code > 63:
            raise CodeIsTooLargeException(row_num + 1)

        if length < 1:
            raise LengthIsBelowOrEqualZeroException(row_num + 1)

        return Operation(name=name, code=int_code, length=length)

    def get(self, name: str) -> Union[Operation, bool]:
        try:
            return next(i for i in self.tb if i.name.lower() == name.lower())
        except StopIteration:
            return False


class MockTKO(TKO):
    def __init__(self):
        self.tb = [
            Operation(name='add', code=1, length=2),
            Operation(name='jmp', code=2, length=4)
        ]
