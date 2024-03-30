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

    def get_next_token(self):
        pass

    def read_token(self, value):
        current_token: Token = self.tokens[self.current_token_idx]
        if current_token.value == value:
            self.current_token_idx += 1  # moving to next token

            if current_token.type in ["<IDENTIFIER>", "<INTEGER>"]:
                self.stack.append(TreeNode("<%s:%s>" % (current_token.type, current_token.value)))
        else:
            raise Exception("Syntax Error: %s is expected." % value)

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

                self.build_tree('lambda', n+1)  # building 'lambda' node
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
            self.build_tree('tau', n+1)  # building 'tau' node

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


    def procedureA(self):
        pass

    def procedureD(self):
        pass

    def procedureDr(self):
        pass

    def procedureVb(self):
        pass
