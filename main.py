import re


class Token:
    def __init__(self, pos, type_, value):
        self.pos = pos
        self.type = type_
        self.value = value

    def __str__(self):
        return f'pos={self.pos}, type={self.type}, value={self.value}'


def fdict(dict_):
    import collections
    return collections.defaultdict(lambda: False, dict_)


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
        col = i.start()-lst
        type_ = i.lastgroup
        value = '' if type_ in ('EOL', 'SKIP') else i.group(type_)
        if type_ == 'MISMATCH':
            raise Exception(f'E01:({lno},{col}):{value}')
            break
        yield Token((lno, col), type_, value)
        if type_ == 'EOL':
            lno += 1
            lst = i.end()+1


def verify_syntax(tokens):
    exp = (
        fdict({'OPCODE': 1, 'IDENTIFIER': 3, 'EOL': True}),
        fdict({'IMMEDIATE': 2, 'IDENTIFIER': 2, 'EOL': True}),
        fdict({'IMMEDIATE': 2, 'IDENTIFIER': 2, 'EOL': True}),
        fdict({'OPCODE': 1}),
    )

    state = 0
    line = ''
    lno = 0
    for i in tokens:
        if i.type == 'SKIP':
            continue
        line += f'({i.type})'
        if i.type == 'COMMENT':
            continue

        state = exp[state][i.type]
        if state is True:
            yield f'line {lno}: {line} OK'
            line = ''
            lno += 1
            state = 0
        if state is False:
            raise Exception(f'line {lno}: {line} ERR')
            break


def verify_arguments(tokens):
    tokens_ = [
        Token(
            i.pos,
            i.value if i.type == 'OPCODE' else i.type,
            '' if i.type == 'OPCODE' else i.value,
        ) for i in tokens]

    for i in tokens_:
        yield i


def line():
    import shutil
    print('-'*shutil.get_terminal_size()[0])


with open('sample/blink.td4') as fp:
    code = fp.read()

print(code)
line()

for i in tokenize(code):
    print(i)
line()

for i in verify_syntax(tokenize(code)):
    print(i)
line()

for i in verify_arguments(tokenize(code)):
    print(i)
line()
