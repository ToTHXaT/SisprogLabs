from checks import *
from lineparser import yield_lines, Command

tko: TKO = None


def do_one_pass(src: str, _tko: TKO):
    global tko
    tko = _tko

    header: Header = Header(None, None, None)
    extref: Extref = Extref([])
    extdef: Extdef = Extdef([])
    end: End = End(None)
    tsi: Dict[str, Tuple[int, str, str]] = {}
    op_l: List[Union[Tuple[int, Directive], Tuple[int, Command]]] = []

    module = Module(header, extref, extdef, op_l, end, tsi)

    output: Module

    state = {
        'was_refs' : False,
        'was_defs' : False,
        'was_norm' : False,
        'was_end'  : False,
        'was_start': False
    }

    lines = yield_lines(src)

    header = check_header(lines, tko)

    yield Module(header, extref, extdef, op_l, end, tsi)

    for i, line in lines:
        pl = parse_line(line, tko, i)

        if type(pl) is Directive:
            if pl.dir == 'start':
                raise Exception(f'[{i}]: Duplicate start directive')
            if pl.dir == 'extref':
                if state.get('was_normal'):
                    raise Exception(f'[{i}]: Extref should be on the top')
                if state.get('was_extref'):
                    raise Exception(f'[{i}]: Duplicate extref')

                extref = check_extref(pl, tsi, header.program_name, i)
                state['was_extref'] = True
                continue

            if pl.dir == 'extdef':
                if state.get('was_normal'):
                    raise Exception(f'[{i}]: Extdef should be on the top')
                if state.get('was_extdef'):
                    raise Exception(f'[{i}]: Duplicate extdef')

                extdef = check_extdef(pl, tsi, header.program_name, i)
                state['was_extdef'] = True
                continue

            state['was_norm'] = True

            if pl.dir == 'csect':
                pass
            if pl.dir == 'byte':
                pass
            if pl.dir == 'word':
                pass
            if pl.dir == 'end':
                state['was_end'] = True

        state['was_norm'] = True

        if type(pl) is Command:
            pass
