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
            self.build_tree('tau', n)  # building 'tau' node

    def procedureTa(self):
        pass

    def procedureTc(self):
        pass

    def procedureD(self):
        pass

    def procedureDr(self):
        pass

    def procedureVb(self):
        pass
