from collections import namedtuple


ANY = lambda v: True  # noqa
NUMBER = lambda v: v.isdigit and int(v) >= 0  # noqa
NONZORE_NUMBER = lambda v: v.isdigit and int(v) > 0  # noqa
N_NOT_ZORE = object()
N_IS_ZORE = object()


_STATES = ('S', 'A', 'B', 'C', 'D', 'E', 'END')
STATES = namedtuple('STATES', _STATES)(*_STATES)
_STATE_MAP = {
    # (FROM_STATE, inputs): TO_STATE
    (STATES.S, ('+', '-', ':')): STATES.A,
    (STATES.S, ('$',)): STATES.B,
    (STATES.S, ('*',)): STATES.D,
    (STATES.A, (ANY,)): STATES.END,
    (STATES.B, ('-1',)): STATES.END,
    (STATES.B, (NUMBER,)): STATES.C,
    (STATES.C, (ANY,)): STATES.END,
    (STATES.D, ('0', '-1')): STATES.END,
    (STATES.D, (NONZORE_NUMBER,)): STATES.E,
    (STATES.E, (N_NOT_ZORE,)): STATES.E,    # n != 0, n--
    (STATES.E, (N_IS_ZORE,)): STATES.END,  # n == 0
}
STATE_MAP = {}
for k, v in _STATE_MAP.items():
    from_state, inputs = k
    to_state = v
    for i in inputs:
        STATE_MAP.setdefault(from_state, {}).update({i: to_state})


class RESPState:

    def __init__(self):
        self.lines = []
        self._state = STATES.S

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, v):
        if v not in STATE_MAP[self._state].values():
            raise ValueError('cannot change state from {} to {}'.format(
                self._state, v))
        self._state = v

    @property
    def is_stoped(self):
        return self.state == STATES.END

    def add(self, line):
        self.lines.append(line.decode() if isinstance(line, bytes) else line)
        self._handle_state()

    def _handle_state(self):
        if self.state == STATES.S:
            self._handle_state_s()
            return
        if self.state == STATES.E:
            self._handle_state_e()
            return
        last_input = self.lines[-1]
        state_map = STATE_MAP[self.state]
        for except_input in state_map.keys():
            if except_input == last_input or (callable(except_input) and
                                              except_input(last_input)):
                self.state = state_map[except_input]
                return
        raise ValueError('state {} not excpet input {}'.format(self.state,
                                                               last_input))

    def _handle_state_s(self):
        last_input = self.lines.pop()
        symbol, last_input = last_input[0], last_input[1:]
        self.lines.extend([symbol, last_input])
        state_map = STATE_MAP[STATES.S]
        self.state = state_map[symbol]
        self._handle_state()

    def _handle_state_e(self):
        if not hasattr(self, 'resp_state') or self.resp_state.is_stoped:
            self.resp_state = self.__class__()
            # if no n, -2nd input is n
            self.n = getattr(self, 'n', None) or int(self.lines[-2])
        self.resp_state.add(self.lines[-1])
        if self.resp_state.state == STATES.END:
            self.n -= 1
            if self.n == 0:
                self.state = STATES.END
            elif self.n < 0:
                raise ValueError


def handle_line(line, resp=None):
    if not resp or resp.is_stoped:
        resp = RESPState()
    resp.add(line)
    return resp
