from LexicalAnalyzer import Tokenizer
from TreeNodes import TreeNode
from Tokens import Token


class RPALParser:
    def __init__(self):
        self.tokenizer = Tokenizer()
        self.tokens = []
        self.current_token_idx = 0
        self.stack = []  # contains tree nodes

    def extract_tokens(self, file):
        self.tokens = self.tokenizer.tokenize(file)

    def read_token(self, value):
        current_token: Token = self.tokens[self.current_token_idx]
        if current_token.value == value:
            self.current_token_idx += 1  # moving to next token
        else:
            raise Exception("Syntax Error: %s is expected." % value)

    def read_token_by_type(self, type):
        current_token: Token = self.tokens[self.current_token_idx]
        if current_token.type == type:
            self.current_token_idx += 1  # moving to next token

            if current_token.type in ["<IDENTIFIER>", "<INTEGER>", "<STRING>"]:
                self.stack.append(TreeNode("<%s:%s>" % (current_token.type, current_token.value)))
        else:
            raise Exception("Syntax Error: %s type is expected." % type)

    def build_tree(self, value, n):
        parent = TreeNode(value)
        for i in range(n):
            parent.add_child(self.stack.pop())
        self.stack.append(parent)

    def procedureE(self):
        current_token = self.tokens[self.current_token_idx]
        match current_token.value:
            case 'let':
                self.read_token('let')
                self.procedureD()
                self.read_token('in')
                self.procedureE()

                self.build_tree('let', 2)  # building 'let' node
            case 'fn':
                self.read_token('fn')

                self.procedureVb()
                n = 1
                while current_token.value == "(" or current_token.type == "<IDENTIFIER>":
                    self.procedureVb()
                    n += 1

                self.read_token('.')
                self.procedureE()

                self.build_tree('lambda', n + 1)  # building 'lambda' node
            case _:
                self.procedureEw()

    def procedureEw(self):
        self.procedureT()

        if self.tokens[self.current_token_idx].value == 'where':
            self.read_token('where')
            self.procedureDr()
            self.build_tree('where', 2)  # building 'where' node

    def procedureT(self):
        self.procedureTa()

        if self.tokens[self.current_token_idx].value == ',':
            self.read_token(',')
            self.procedureTa()
            n = 1
            while self.tokens[self.current_token_idx].value == ',':
                self.read_token(',')
                self.procedureTa()
                n += 1
            self.build_tree('tau', n + 1)  # building 'tau' node

    def procedureTa(self):
        self.procedureTc()

        while self.tokens[self.current_token_idx].value == 'aug':
            self.read_token('aug')
            self.procedureTc()
            self.build_tree('aug', 2)

    def procedureTc(self):
        self.procedureB()

        if self.tokens[self.current_token_idx].value == '->':
            self.read_token('->')
            self.procedureTc()
            self.read_token('|')
            self.procedureTc()

            self.build_tree('->', 2)

    def procedureB(self):
        self.procedureBt()

        while self.tokens[self.current_token_idx].value == 'or':
            self.read_token('or')
            self.procedureBt()
            self.build_tree('or', 2)

    def procedureBt(self):
        self.procedureBs()

        while self.tokens[self.current_token_idx].value == '&':
            self.read_token('&')
            self.procedureBs()
            self.build_tree('&', 2)

    def procedureBs(self):
        if self.tokens[self.current_token_idx].value == 'not':
            self.read_token('not')
            self.procedureBp()
            self.build_tree('not', 1)
        else:
            self.procedureBp()

    def procedureBp(self):
        self.procedureA()

        match self.tokens[self.current_token_idx].value:
            case 'gr':
                self.read_token('gr')
                self.procedureA()
                self.build_tree('gr', 2)
            case '>':
                self.read_token('>')
                self.procedureA()
                self.build_tree('gr', 2)
            case 'ge':
                self.read_token('ge')
                self.procedureA()
                self.build_tree('ge', 2)
            case '>=':
                self.read_token('>=')
                self.procedureA()
                self.build_tree('ge', 2)
            case 'ls':
                self.read_token('ls')
                self.procedureA()
                self.build_tree('ls', 2)
            case '<':
                self.read_token('<')
                self.procedureA()
                self.build_tree('ls', 2)
            case 'le':
                self.read_token('le')
                self.procedureA()
                self.build_tree('le', 2)
            case '<=':
                self.read_token('<=')
                self.procedureA()
                self.build_tree('le', 2)
            case 'eq':
                self.read_token('eq')
                self.procedureA()
                self.build_tree('eq', 2)
            case 'ne':
                self.read_token('ne')
                self.procedureA()
                self.build_tree('ne', 2)

    ##### check #####
    def procedureA(self):

        if self.tokens[self.current_token_idx].value == '+':
            self.read_token('+')
            self.procedureAt()

        elif self.tokens[self.current_token_idx].value == '-':
            self.read_token('-')
            self.procedureAt()
            self.build_tree('neg', 1)

        else:
            self.procedureAt()

        while self.tokens[self.current_token_idx].value == '+' or self.tokens[self.current_token_idx].value == '-':
            if self.tokens[self.current_token_idx].value == '+':
                self.read_token('+')
                self.procedureAt()
                self.build_tree('+', 2)
            elif self.tokens[self.current_token_idx].value == '-':
                self.read_token('-')
                self.procedureAt()
                self.build_tree('-', 2)

    def procedureAt(self):
        self.procedureAf()

        while self.tokens[self.current_token_idx].value == '*' or self.tokens[self.current_token_idx].value == '/':
            if self.tokens[self.current_token_idx].value == '*':
                self.read_token('*')
                self.procedureAf()
                self.build_tree('*', 2)
            elif self.tokens[self.current_token_idx].value == '/':
                self.read_token('/')
                self.procedureAf()
                self.build_tree('/', 2)


    def procedureAf(self):
        self.procedureAp()

        if self.tokens[self.current_token_idx].value == '**':
            self.read_token('**')
            self.procedureAf()
            self.build_tree('**', 2)

    ##### Check #####
    def procedureAp(self):
        self.procedureR()

        if self.tokens[self.current_token_idx].value == '@':
            self.read_token('@')
            self.read_token_by_type('<IDENTIFIER>')
            self.procedureR()
            self.build_tree('@', 3)


    def procedureR(self):
        self.procedureRn()
        c_token = self.tokens[self.current_token_idx]
        while (c_token.type in ["<IDENTIFIER>", "<INTEGER>", "<STRING>"] or
               c_token.value in ['true', 'false', 'nil', '(', 'dummy']):

            self.procedureRn()
            self.build_tree('gamma', 2)



    def procedureRn(self):
        c_token = self.tokens[self.current_token_idx]

        if c_token.type in ["<IDENTIFIER>", "<INTEGER>", "<STRING>"]:
            match c_token.type:
                case "<IDENTIFIER>":
                    self.read_token_by_type("<IDENTIFIER>")
                case "<INTEGER>":
                    self.read_token_by_type("<INTEGER>")
                case "<STRING>":
                    self.read_token_by_type("<STRING>")

        elif c_token.value in ['true', 'false', 'nil', '(', 'dummy']:
            match c_token.value:
                case 'true':
                    self.read_token('true')
                    self.build_tree('true', 0)
                case 'false':
                    self.read_token('false')
                    self.build_tree('false', 0)
                case 'nil':
                    self.read_token('nil')
                    self.build_tree('nil', 0)
                case '(':
                    self.read_token('(')
                    self.procedureE()
                    self.read_token(')')
                case 'dummy':
                    self.read_token('dummy')
                    self.build_tree('dummy', 0)

    def procedureD(self):
        self.procedureDa()

        if self.tokens[self.current_token_idx].value == 'within':
            self.read_token('within')
            self.procedureD()
            self.build_tree('within', 2)

    def procedureDa(self):
        self.procedureDr()

        if self.tokens[self.current_token_idx].value == 'and':
            self.read_token('and')
            self.procedureDr()
            n = 1
            while self.tokens[self.current_token_idx].value == 'and':
                self.read_token('and')
                self.procedureDr()
                n += 1
            self.build_tree('and', n+1)


    def procedureDr(self):
        if self.tokens[self.current_token_idx].value == 'rec':
            self.read_token('rec')
            self.procedureDb()
            self.build_tree('rec', 1)
        else:
            self.procedureDb()

    ##### Check #####
    def procedureDb(self):
        if self.tokens[self.current_token_idx].value == '(':
            self.read_token('(')
            self.procedureD()
            self.read_token(')')
        elif self.tokens[self.current_token_idx].type == '<IDENTIFIER>':
            self.read_token_by_type('<IDENTIFIER>')

            self.procedureVb()
            n = 1
            current_token = self.tokens[self.current_token_idx].value
            while current_token.value == '(' or current_token.type == '<IDENTIFIER>':
                self.procedureVb()
                n += 1

                self.read_token('=')
                self.procedureE()
            self.build_tree('fcn_form', n+2) ##### Check n+2 #####
        else:
            self.procedureVl()
            self.read_token('=')
            self.procedureE()
            self.build_tree('=', 2)


    def procedureVb(self):
        if self.tokens[self.current_token_idx].value == '(':
            self.read_token('(')
            if self.tokens[self.current_token_idx].value == ')':
                self.read_token(')')
                self.build_tree('()', 0)
            else:
                self.procedureVl()
                self.read_token(')')
        else:
            self.read_token_by_type('<IDENTIFIER>')


    def procedureVl(self):
        self.read_token_by_type('<IDENTIFIER>')

        n = 0
        while self.tokens[self.current_token_idx].value == ',':
            self.read_token(',')
            self.read_token_by_type('<IDENTIFIER>')
            n += 1

        if n > 0:
            self.build_tree(',', n+1)

