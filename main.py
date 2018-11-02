import re
import collections
import enum


class Token:
    def __init__(self, pos, type_, value):
        self.pos = pos
        self.type = type_
        self.value = value

    def __str__(self):
        return f'pos={self.pos}, type={self.type}, value={self.value}'


class TokenTypeInt(enum.Enum):
    OPCODE = 0
    IMMEDIATE = 1
    IDENTIFIER = 2
    EOL = 3
    SKIP = 4
    COMMENT = 5


def tokenize(text):
    op = ('MOB', 'ADD', 'OUT', 'IN', 'JMP', 'JNC', 'NOP')

    token_spec = (
        ('OPCODE', '|'.join(map(lambda x: f'({x})', op))),
        ('IMMEDIATE', '(0[bx])?[0-9]+'),
        ('IDENTIFIER', '[a-zA-Z][0-9a-zA-Z]*'),
        ('EOL', '$'),
        ('SKIP', '\s'),
        ('COMMENT', ';.*(?=$)'),
        ('MISMATCH', ".+")
    )

    regex = '|'.join(map(lambda x: f'(?P<{x[0]}>{x[1]})', token_spec))
    proc = re.compile(regex, re.MULTILINE)

    lno = 0
    lst = 0
    for i in re.finditer(proc, text):
        type_ = i.lastgroup
        value = i.group(type_)
        if type_ == 'MISMATCH':
            raise Exception(f'E01:({lno},{i.start()-lst}):{value}')
            break
        yield Token((lno, i.start()-lst), type_, value)
        if type_ == 'EOL':
            lno += 1
            lst = i.end()+1


def verify_syntax(tokens):
    def tdict(params):
        return collections.defaultdict(
            lambda: False,
            ((TokenTypeInt[k], v) for k, v in params.items()))

    exp = (
        tdict({'OPCODE': 1, 'IDENTIFIER': 3, 'EOL': True}),
        tdict({'IMMEDIATE': 2, 'IDENTIFIER': 2, 'EOL': True}),
        tdict({'IMMEDIATE': 2, 'IDENTIFIER': 2, 'EOL': True}),
        tdict({'OPCODE': 1}),
    )

    state = 0
    line = ''
    lno = 0
    for i in tokens:
        if i.type in ('SKIP', 'COMMENT'):
            continue
        line += f'({i.type})'

        state = exp[state][TokenTypeInt[i.type]]
        if state is True:
            yield f'line {lno}: {line} OK'
            line = ''
            lno += 1
            state = 0
        if state is False:
            yield f'line {lno}: {line} ERR'
            break


with open('sample/blink.td4') as fp:
    code = fp.read()

print(code)
print('-'*80)

for i in tokenize(code):
    print(i)
print('-'*80)

for i in verify_syntax(tokenize(code)):
    print(i)
