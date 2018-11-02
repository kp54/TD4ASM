import re


class Token:
    def __init__(self, pos, type_, value):
        self.pos = pos
        self.type = type_
        self.value = value

    def __str__(self):
        return f'pos={self.pos}, type={self.type}, value={self.value}'


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
        yield Token((lno, i.start()-lst), type_, value)
        if type_ == 'EOL':
            lno += 1
            lst = i.end()+1


with open('sample/blink.td4') as fp:
    code = fp.read()

print(code)
print('-'*80)

for i in tokenize(code):
    print(i)
