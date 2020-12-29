from checks import *
from constants import _convert
from lineparser import yield_lines, Command

tko: TKO = None


def do_one_pass(src: str, _tko: TKO, frmt: str):
    global tko
    tko = _tko

    header: Header = Header(None, None, None)
    extref: Extref = Extref([])
    extdef: Extdef = Extdef([])
    end: End = End(None)
    tsi: Dict[str, Tuple[int, str, str, List[int]]] = {}
    op_l: List[Union[Dir, Cmd]] = []
    tm: TM = TM([])
    ac = 0

    module = Module(header, extref, extdef, op_l, end, tsi, tm)
    module_l: List[Module] = []

    state = {
        'was_refs' : False,
        'was_defs' : False,
        'was_norm' : False,
        'was_end'  : False,
        'was_start': False
    }

    lines = yield_lines(src)

    header = check_header(lines, tko)
    ac = header.load_addr

    yield [*module_l, Module(header, extref, extdef, op_l, end, tsi, tm)]

    for i, line in lines:
        pl = parse_line(line, tko, i)
        print(pl)

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

                yield [*module_l, Module(header, extref, extdef, op_l, end, tsi, tm)]
                continue

            if pl.dir == 'extdef':
                if state.get('was_normal'):
                    raise Exception(f'[{i}]: Extdef should be on the top')
                if state.get('was_extdef'):
                    raise Exception(f'[{i}]: Duplicate extdef')

                extdef = check_extdef(pl, tsi, header.program_name, i)
                state['was_extdef'] = True

                yield [*module_l, Module(header, extref, extdef, op_l, end, tsi, tm)]
                continue

            state['was_norm'] = True

            if pl.dir == 'csect':
                end = End(0)

                if lond := [key for key, (addr, tp, prg, _lst) in tsi.items() if tp == 'def' and addr == -1]:
                    raise Exception(
                        f'[-]: Following external names were not found in program: {" ".join(i for i in lond)}')

                header = Header(header.program_name, header.load_addr, ac - header.load_addr)

                module_l.append(Module(header, extref, extdef, op_l, end, tsi, tm))

                header: Header = Header(None, None, None)
                extref: Extref = Extref([])
                extdef: Extdef = Extdef([])
                end: End = End(None)
                tsi: Dict[str, Tuple[int, str, str, List[int]]] = {}
                op_l: List[Union[Dir, Cmd]] = []
                tm: TM = TM([])
                ac = 0

                module = Module(header, extref, extdef, op_l, end, tsi, tm)

                state = {
                    'was_refs' : False,
                    'was_defs' : False,
                    'was_norm' : False,
                    'was_end'  : False,
                    'was_start': False
                }

                header = Header(pl.label, 0, None)

                ac = 0

                yield [*module_l, Module(header, extref, extdef, op_l, end, tsi, tm)]
                continue

            if pl.dir == 'end':
                state['was_end'] = True
                if pl.args and (end_addr := to_int_safe(pl.args[0])):
                    end = End(end_addr)
                else:
                    end = End(header.load_addr)

                if lond := [key for key, (addr, tp, prg, _lst) in tsi.items() if tp == 'def' and addr == -1]:
                    raise Exception(
                        f'[-]: Following external names were not found in program: {" ".join(i for i in lond)}')

                header = Header(header.program_name, header.load_addr, ac - header.load_addr)

                module_l.append(Module(header, extref, extdef, op_l, end, tsi, tm))

                yield module_l
                break

        state['was_norm'] = True

        if pl.label:
            if l := tsi.get(pl.label):
                addr, tp, sect, ref_l = l

                if tp == 'ref':
                    raise Exception(f'[{i}]: Duplicate symbolic name `{pl.label}`')
                else:
                    if addr != -1:
                        raise Exception(f'[{i}]: Duplicate symbolic name `{pl.label}`')
                    else:
                        tsi.update({pl.label: (ac, tp, sect, [])})
                        for ref in ref_l:
                            try:
                                ln = next(op for op in op_l if op.ac == ref)

                                if ln.args.__len__() == 2:
                                    if ln.args[1] == pl.label:
                                        ln.args[1] = make_bin(ln.args[1], tsi, tm, header.load_addr, frmt, ref,
                                                              header.program_name, i, ac)
                                    elif ln.args[1][0] == '~' and ln.args[1][1:] == pl.label:
                                        ln.args[1] = make_bin(ln.args[1], tsi, tm, header.load_addr, frmt, ref,
                                                              header.program_name, i)

                                    if ln.args[0] == pl.label:
                                        ln.args[0] = make_bin(ln.args[0], tsi, tm, header.load_addr, frmt, ref,
                                                              header.program_name, i, ac)
                                    elif ln.args[0][0] == '~' and ln.args[0][1:] == pl.label:
                                        ln.args[0] = make_bin(ln.args[0], tsi, tm, header.load_addr, frmt, ref,
                                                              header.program_name, i, ac)

                                elif ln.args.__len__() == 1:
                                    if ln.args[0] == pl.label:
                                        ln.args[0] = make_bin(ln.args[0], tsi, tm, header.load_addr, frmt, ref,
                                                              header.program_name, i, ac)
                                    elif ln.args[0][0] == '~' and ln.args[0][1:] == pl.label:
                                        ln.args[0] = make_bin(ln.args[0], tsi, tm, header.load_addr, frmt, ref,
                                                              header.program_name, i, ac)

                            except StopIteration:
                                raise Exception(f'[{i}]: Hz')
            else:
                tsi[pl.label] = (ac, '', header.program_name, [])

        if type(pl) is Directive:
            if pl.dir == 'byte' or pl.dir == 'word':

                if len(pl.args) == 0:
                    raise Exception(f'[{i}]: No arguments provided')

                length = sum(_convert(j, pl.dir, i).length for j in pl.args)

                ac += length

                op_l.append(Dir(i, pl.dir, pl.args, length, ac - length))

        if type(pl) is Command:
            op = tko.get(pl.cmd)

            if len(pl.args) > 2: raise Exception(f'[{i}]: No more than 2 args is possible')

            ac += op.length

            cmd = Cmd(i, op, pl.args, '', ac - op.length)

            cmd = cmd.validate(tsi, tm, header.load_addr, frmt, header.program_name)

            op_l.append(cmd)

        yield [*module_l, Module(header, extref, extdef, op_l, end, tsi, tm)]

    if not state['was_end']:
        raise Exception(f'[-]: End directive not found')
