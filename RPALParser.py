from LexicalAnalyzer import Tokenizer
from TreeNodes import TreeNode
from Tokens import Token


class RPALParser:
    def __init__(self):
        self.tokenizer = Tokenizer()
        self.tokens = []
        self.current_token_idx = 0
        self.current_token = None
        self.stack = []  # contains tree nodes


    def extract_tokens(self, file):
        self.tokens = self.tokenizer.tokenize(file)
        self.current_token = self.tokens[self.current_token_idx]

    def read_token(self, value):
        # for i in self.stack:
        #     print(i.value, end=', ')
        # print()

        if self.current_token.value == value:
            self.current_token_idx += 1
            # moving to next token
            if self.current_token_idx < len(self.tokens):
                self.current_token = self.tokens[self.current_token_idx]
            else:
                self.current_token = Token("<END>", 'END')
        else:
            for t in self.tokens[:self.current_token_idx]:
                print(t.value, end = ', ')
            raise Exception("Syntax Error: %s is expected near %s." % (value, self.tokens[self.current_token_idx-1].value))

    def read_token_by_type(self, type):
        # for i in self.stack:
        #     print(i.value, end=', ')
        if self.current_token.type == type:
            self.current_token_idx += 1

            if self.current_token.type in ["<IDENTIFIER>", "<INTEGER>", "<STRING>"]:
                self.stack.append(TreeNode("<%s:%s>" % (self.current_token.type, self.tokens[self.current_token_idx-1].value)))

            # moving to next token
            if self.current_token_idx < len(self.tokens):
                self.current_token = self.tokens[self.current_token_idx]
            else:
                self.current_token = Token("<END>", 'END')


        else:
            raise Exception("Syntax Error: %s type is expected near %s." % (type, self.current_token.value))

    def build_tree(self, value, n):
        parent = TreeNode(value)
        for i in range(n):
            parent.add_child(self.stack.pop())
        self.stack.append(parent)
        return

    def procedureE(self):

        match self.current_token.value:
            case 'let':
                self.read_token('let')
                self.procedureD()
                self.read_token('in')
                self.procedureE()


                print('E -> ’let’ D ’in’ E')

                self.build_tree('let', 2)  # building 'let' node
            case 'fn':
                self.read_token('fn')

                self.procedureVb()
                n = 1

                while self.current_token.value == "(" or self.current_token.type == "<IDENTIFIER>":
                    self.procedureVb()
                    n += 1
                self.read_token('.')
                self.procedureE()
                print('E -> ’fn’ Vb+ ’.’ E')
                self.build_tree('lambda', n + 1)  # building 'lambda' node
            case _:
                self.procedureEw()
                print('E -> Ew')

    def procedureEw(self):
        self.procedureT()

        if self.current_token.value == 'where':
            self.read_token('where')
            self.procedureDr()
            print('Ew -> T ’where’ Dr')
            self.build_tree('where', 2)  # building 'where' node

            return
        print('Ew -> T')

    def procedureT(self):
        self.procedureTa()

        if self.current_token.value == ',':
            self.read_token(',')
            self.procedureTa()
            n = 1
            while self.current_token.value == ',':
                self.read_token(',')
                self.procedureTa()
                n += 1
            print('T -> Ta ( ’,’ Ta )+')
            self.build_tree('tau', n + 1)  # building 'tau' node
            return
        print('T -> Ta ')
        return

    def procedureTa(self):
        self.procedureTc()
        print('Ta -> Tc')
        while self.current_token.value == 'aug':
            self.read_token('aug')
            self.procedureTc()
            print('Ta -> Ta ’aug’ Tc')
            self.build_tree('aug', 2)


    def procedureTc(self):
        self.procedureB()

        if self.current_token.value == '->':
            self.read_token('->')
            self.procedureTc()
            self.read_token('|')
            self.procedureTc()
            print('Tc -> B ’->’ Tc ’|’ Tc')
            self.build_tree('->', 3)
            return
        print('Tc -> B')
        return

    def procedureB(self):
        self.procedureBt()
        print('B -> Bt')

        while self.current_token.value == 'or':
            self.read_token('or')
            self.procedureBt()
            print('B ->B’or’ Bt')
            self.build_tree('or', 2)


    def procedureBt(self):
        self.procedureBs()
        print('Bt -> Bs')
        while self.current_token.value == '&':
            self.read_token('&')
            self.procedureBs()
            print('Bt -> Bt ’&’ Bs')
            self.build_tree('&', 2)

    def procedureBs(self):
        if self.current_token.value == 'not':
            self.read_token('not')
            self.procedureBp()
            print('Bs -> ’not’ Bp')
            self.build_tree('not', 1)
        else:
            self.procedureBp()
            print('Bs -> Bp')

    def procedureBp(self):
        self.procedureA()

        match self.current_token.value:
            case 'gr':
                self.read_token('gr')
                self.procedureA()
                print('Bp -> A ’gr’ A')
                self.build_tree('gr', 2)
            case '>':
                self.read_token('>')
                self.procedureA()
                print('Bp -> A ’>’ A')
                self.build_tree('gr', 2)
            case 'ge':
                self.read_token('ge')
                self.procedureA()
                print('Bp -> A ’ge’ A')
                self.build_tree('ge', 2)
            case '>=':
                self.read_token('>=')
                self.procedureA()
                print('Bp -> A ’>=’ A')
                self.build_tree('ge', 2)
            case 'ls':
                self.read_token('ls')
                self.procedureA()
                print('Bp -> A ’ls’ A')
                self.build_tree('ls', 2)
            case '<':
                self.read_token('<')
                self.procedureA()
                print('Bp -> A ’<’ A')
                self.build_tree('ls', 2)
            case 'le':
                self.read_token('le')
                self.procedureA()
                print('Bp -> A ’le’ A')
                self.build_tree('le', 2)
            case '<=':
                self.read_token('<=')
                self.procedureA()
                print('Bp -> A ’<=’ A')
                self.build_tree('le', 2)
            case 'eq':
                self.read_token('eq')
                self.procedureA()
                print('Bp -> A ’eq’ A')
                self.build_tree('eq', 2)
            case 'ne':
                self.read_token('ne')
                self.procedureA()
                print('Bp -> A ’ne’ A')
                self.build_tree('ne', 2)
            case _ :
                print('Bp -> A')
                return

    ##### check #####
    def procedureA(self):

        if self.current_token.value == '+':
            self.read_token('+')
            self.procedureAt()
            print('A ->’+’ At')

        elif self.current_token.value == '-':
            self.read_token('-')
            self.procedureAt()
            print('A ->’-’ At')
            self.build_tree('neg', 1)

        else:
            self.procedureAt()
            print('A -> At')

        while self.current_token.value == '+' or self.current_token.value == '-':
            if self.current_token.value == '+':
                self.read_token('+')
                self.procedureAt()
                print('A ->A’+’ At')
                self.build_tree('+', 2)
            elif self.current_token.value == '-':
                self.read_token('-')
                self.procedureAt()
                print('A ->A’-’ At')
                self.build_tree('-', 2)

    def procedureAt(self):
        self.procedureAf()
        print('At -> Af')

        while self.current_token.value == '*' or self.current_token.value == '/':
            if self.current_token.value == '*':
                self.read_token('*')
                self.procedureAf()
                print('At -> At ’*’ Af')
                self.build_tree('*', 2)
            elif self.current_token.value == '/':
                self.read_token('/')
                self.procedureAf()
                print('At -> At ’/’ Af')
                self.build_tree('/', 2)

    def procedureAf(self):
        self.procedureAp()

        if self.current_token.value == '**':
            self.read_token('**')
            self.procedureAf()
            print('Af -> Ap ’**’ Af')
            self.build_tree('**', 2)
            return
        print('Af -> Ap')

    ##### Check #####
    def procedureAp(self):
        self.procedureR()
        print('Ap -> R')

        while self.current_token.value == '@':
            self.read_token('@')
            self.read_token_by_type('<IDENTIFIER>')
            self.procedureR()
            print('Ap -> Ap ’@’ ’<IDENTIFIER>’ R')
            self.build_tree('@', 3)  ##### Check #####

    ##### Check #####
    def procedureR(self):
        self.procedureRn()
        print('R -> Rn')

        while (self.current_token.type in ["<IDENTIFIER>", "<INTEGER>", "<STRING>"] or
               self.current_token.value in ['true', 'false', 'nil', '(', 'dummy']):
            self.procedureRn()
            print('R ->R Rn')

            self.build_tree('gamma', 2)

    ##### Check #####
    def procedureRn(self):

        if self.current_token.type in ["<IDENTIFIER>", "<INTEGER>", "<STRING>"]:

            match self.current_token.type:
                case "<IDENTIFIER>":
                    self.read_token_by_type("<IDENTIFIER>")
                    print('Rn -> ’<IDENTIFIER>’')
                case "<INTEGER>":
                    self.read_token_by_type("<INTEGER>")
                    print('Rn -> ’<INTEGER>’')
                case "<STRING>":
                    self.read_token_by_type("<STRING>")
                    print('Rn -> ’<STRING>’')

        elif self.current_token.value in ['true', 'false', 'nil', '(', 'dummy']:

            match self.current_token.value:
                case 'true':
                    self.read_token('true')
                    print('Rn -> ’true’')
                    self.build_tree('true', 0)
                case 'false':
                    self.read_token('false')
                    print('Rn -> ’false’')
                    self.build_tree('false', 0)
                case 'nil':
                    self.read_token('nil')
                    print('Rn -> ’nil’')
                    self.build_tree('nil', 0)
                case 'dummy':
                    self.read_token('dummy')
                    print('Rn -> ’dummy’')
                    self.build_tree('dummy', 0)
                case '(':
                    self.read_token('(')
                    self.procedureE()
                    self.read_token(')')
                    print('Rn -> ’( E )’')

    def procedureD(self):
        self.procedureDa()

        if self.current_token.value == 'within':
            self.read_token('within')
            self.procedureD()
            print('D -> Da ’within’ D')
            self.build_tree('within', 2)
            return
        print('D -> Da')
        return

    def procedureDa(self):

        self.procedureDr()

        if self.current_token.value == 'and':
            self.read_token('and')
            self.procedureDr()
            n = 1
            while self.current_token == 'and':
                self.read_token('and')
                self.procedureDr()
                n += 1
            print('Da -> Dr ( ’and’ Dr )+')
            self.build_tree('and', n+1)
        print('Da -> Dr')

    def procedureDr(self):
        if self.current_token.value == 'rec':

            self.read_token('rec')
            self.procedureDb()
            print('Dr -> ’rec’ Db')
            self.build_tree('rec', 1)
        else:
            self.procedureDb()
            print('Dr -> Db')

    ##### Check #####
    def procedureDb(self):
        if self.current_token.value == '(':
            self.read_token('(')
            self.procedureD()
            self.read_token(')')
            print('Db -> ’(’ D ’)’ ')
        elif self.current_token.type == '<IDENTIFIER>':
            look_ahead_token = self.tokens[self.current_token_idx+1]
            if look_ahead_token.type == '<IDENTIFIER>' or look_ahead_token.value == '(':
                self.read_token_by_type('<IDENTIFIER>')

                if self.current_token.value == '(' or self.current_token.type == '<IDENTIFIER>':
                    self.procedureVb()
                    n = 1

                    while self.current_token.value == '(' or self.current_token.type == '<IDENTIFIER>':
                        self.procedureVb()
                        n += 1

                    self.read_token('=')

                    self.procedureE()
                    print('Db -> ’<IDENTIFIER>’ Vb+ ’=’ E')
                    self.build_tree('fcn_form', n+2)  ##### Check n+2 #####
            else:
                self.procedureVl()
                self.read_token('=')
                self.procedureE()

                print('Db -> Vl ’=’ E')
                self.build_tree('=', 2)



    def procedureVb(self):
        if self.current_token.value == '(':
            self.read_token('(')
            if self.current_token.value == ')':
                self.read_token(')')
                print('Vb -> ’(’ ’)’')
                self.build_tree('()', 0)
            else:
                self.procedureVl()
                self.read_token(')')
                print('Vb -> ’(’ Vl ’)’')
        else:
            self.read_token_by_type('<IDENTIFIER>')
            print('Vb -> ’<IDENTIFIER>’')
        return

    def procedureVl(self):

        self.read_token_by_type('<IDENTIFIER>')

        n = 0
        while self.current_token.value == ',':
            self.read_token(',')
            self.read_token_by_type('<IDENTIFIER>')
            n += 1

        if n > 0:
            print('Vl -> ’<IDENTIFIER>’ list ’,’')
            self.build_tree(',', n+1)

    def parse_file(self, file):
        self.extract_tokens(file)
        self.procedureE()
        return self.stack

# Testing
parser = RPALParser()
s = parser.parse_file('test.txt')
print(len(s))

def print_tree(node, level):
    print('.'*level, node.value)
    if len(node.children) == 0:
        return
    level += 1
    for child in node.children[-1::-1]:
        print_tree(child, level)
print_tree(s[0], 0)






