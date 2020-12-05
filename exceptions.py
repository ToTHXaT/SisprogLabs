class TKOError(Exception):
    pass


class ParseError(Exception):
    pass


class LenghtIsNotIntException(TKOError):
    def __str__(self):
        return f'TKO: Operation length is not int at row {self.args[0]}'


class CodeIsNotBinaryException(TKOError):
    def __str__(self):
        return f'TKO: Code is not int value at row {self.args[0]}'


class LengthIsBelowOrEqualZeroException(TKOError):
    def __str__(self):
        return f'TKO: Length is below or equal 0 at row {self.args[0]}'


class NameNotMentionedInTheTKOException(TKOError):
    def __str__(self):
        return f'TKO: Name is not mentioned at row {self.args[0]}'


class CodeNotMentionedInTheTKOException(TKOError):
    def __str__(self):
        return f'TKO: Code is not mentioned in the TKO at row {self.args[0]}'


class LengthNotMentionedInTheTKOException(TKOError):
    def __str__(self):
        return f'TKO: Length is not mentioned in the TKO at row {self.args[0]}'


class OpeartionNameDoubleDefinitionException(TKOError):
    def __str__(self):
        return f'TKO: Operation was defined twice at rows {self.args[0]} and {self.args[1]}'


class OpeartionCodeDoubleDefinitionException(TKOError):
    def __str__(self):
        return f'TKO: Operation code is equal at rows {self.args[0]} and {self.args[1]}'


class CodeIsTooLargeException(TKOError):
    def __str__(self):
        return f'TKO: Code is too large at row {self.args[0]}. Max 63'


class HeaderNotFoundException(ParseError):
    def __str__(self):
        return f'[-]: There is no Start directive in source code.'


class HeaderNotFirstException(ParseError):
    def __str__(self):
        return f'[{self.args[0]}]: Start directive must be first entry in source code.'


class OperationNotFoundException(ParseError):
    def __str__(self):
        return f'[{self.args[0]}]: Operation with name {self.args[1]} not found'


class WrongHeaderFormatException(ParseError):
    def __str__(self):
        return f'[{self.args[0]}]: Wrong Start directive format'


class DuplicateSymbolicNameException(ParseError):
    def __str__(self):
        return f'[{self.args[0]}]: Duplicate symbolic name'


class UnknownIdentifierException(ParseError):
    def __str__(self):
        return f"[{self.args[0]}]: Unknown identifier '{self.args[1]}'"


class EndNotFoundException(ParseError):
    def __str__(self):
        return f"[-]: End directive not found."


class LineWrongFormatException(ParseError):
    def __str__(self):
        return f"[{self.args[0]}]: Wrong format"