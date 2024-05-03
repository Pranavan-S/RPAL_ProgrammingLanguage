from LexicalAnalyzer import Tokenizer
from TreeNodes import TreeNode
from Tokens import Token


class RPALParser:
    def __init__(self):
        # tokenizer for extracting tokens
        self.tokenizer = Tokenizer()

        # keeps the tokens in the input file
        self.tokens = []

        # tracks the current token index
        self.current_token_idx = 0

        # current token that has been parsed
        self.current_token = None

        # stack for AST node building
        self.stack = []

        # AST output of parser
        self.output_AST = ''

    def extract_tokens(self, file):
        """
        This function uses the Tokenizer to extract token from the given file.
        :param file:
        :return:
        """
        self.tokens = self.tokenizer.tokenize(file)
        self.current_token = self.tokens[self.current_token_idx]
        return

    def read_token(self, value):
        """
        This function consumes the current token if it matches the required token's value.
        Otherwise, throws Exception saying syntax error occurred.
        :param value:
        :return:
        """
        # # For debugging.
        # for i in self.stack:
        #     print(i.value, end=', ')
        # print()

        # Check for value
        if self.current_token.value == value:
            self.current_token_idx += 1
            # moving to next token
            if self.current_token_idx < len(self.tokens):
                self.current_token = self.tokens[self.current_token_idx]
            else:
                self.current_token = Token("<END>", 'END')
        else:
            # For tracking the parsed token when there is syntax error is encountered.
            for t in self.tokens[:self.current_token_idx]:
                print(t.value, end=', ')

            # Raising exception during syntax rules violation
            raise Exception("Syntax Error: %s is expected near %s."
                            % (value, self.tokens[self.current_token_idx - 1].value))
        return

    def read_token_by_type(self, type):
        """
        This function consumes the current token if it matches the required token's type.
        Otherwise, throws Exception saying syntax error occurred.
        :param type:
        :return:
        """
        # # For debugging
        # for i in self.stack:
        #     print(i.value, end=', ')

        # Check for type
        if self.current_token.type == type:
            self.current_token_idx += 1  # increment current token index

            match self.current_token.type:
                case "<IDENTIFIER>":
                    self.stack.append(TreeNode("<%s:%s>" % ("ID", self.tokens[self.current_token_idx - 1].value)))
                case "<INTEGER>":
                    self.stack.append(TreeNode("<%s:%s>" % ("INT", self.tokens[self.current_token_idx - 1].value)))
                case "<STRING>":
                    self.stack.append(TreeNode("<%s:%s>" % ("STR", self.tokens[self.current_token_idx - 1].value)))

            # if self.current_token.type in ["<IDENTIFIER>", "<INTEGER>", "<STRING>"]:
            #     self.stack.append(TreeNode("<%s:%s>"
            #                           % (self.current_token.type[1:-1], self.tokens[self.current_token_idx-1].value)))

            # moving to next token
            if self.current_token_idx < len(self.tokens):
                self.current_token = self.tokens[self.current_token_idx]
            else:
                self.current_token = Token("<END>", 'END')
        else:
            # Raising exception during syntax rules violation
            raise Exception("Syntax Error: %s type is expected near %s." % (type, self.current_token.value))
        return

    def build_tree(self, value, n):
        """
        This function build pops the nodes from the stack, makes them the child of the parent
        , and pushes the parent back to stack.
        :param value:
        :param n:
        :return:
        """
        parent = TreeNode(value)
        for i in range(n):
            parent.add_child(self.stack.pop())
        self.stack.append(parent)
        return

    '''
    ######################### Procedures for each Non-Terminals Below #########################
    '''

    def procedureE(self):

        match self.current_token.value:
            case 'let':
                self.read_token('let')
                self.procedureD()
                self.read_token('in')
                self.procedureE()

                # print('E -> ’let’ D ’in’ E')

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
                # print('E -> ’fn’ Vb+ ’.’ E')
                self.build_tree('lambda', n + 1)  # building 'lambda' node
            case _:
                self.procedureEw()
                # print('E -> Ew')
        return

    def procedureEw(self):
        self.procedureT()

        if self.current_token.value == 'where':
            self.read_token('where')
            self.procedureDr()
            # print('Ew -> T ’where’ Dr')
            self.build_tree('where', 2)  # building 'where' node
            return
        # print('Ew -> T')
        return

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
            # print('T -> Ta ( ’,’ Ta )+')
            self.build_tree('tau', n + 1)  # building 'tau' node
            return
        # print('T -> Ta ')
        return

    def procedureTa(self):

        self.procedureTc()
        # print('Ta -> Tc')

        while self.current_token.value == 'aug':
            self.read_token('aug')
            self.procedureTc()
            # print('Ta -> Ta ’aug’ Tc')
            self.build_tree('aug', 2)
        return

    def procedureTc(self):

        self.procedureB()

        if self.current_token.value == '->':
            self.read_token('->')
            self.procedureTc()
            self.read_token('|')
            self.procedureTc()
            # print('Tc -> B ’->’ Tc ’|’ Tc')
            self.build_tree('->', 3)
            return
        # print('Tc -> B')
        return

    def procedureB(self):

        self.procedureBt()
        # print('B -> Bt')

        while self.current_token.value == 'or':
            self.read_token('or')
            self.procedureBt()
            # print('B ->B’or’ Bt')
            self.build_tree('or', 2)
        return

    def procedureBt(self):

        self.procedureBs()
        # print('Bt -> Bs')
        while self.current_token.value == '&':
            self.read_token('&')
            self.procedureBs()
            # print('Bt -> Bt ’&’ Bs')
            self.build_tree('&', 2)
        return

    def procedureBs(self):

        if self.current_token.value == 'not':
            self.read_token('not')
            self.procedureBp()
            # print('Bs -> ’not’ Bp')
            self.build_tree('not', 1)
        else:
            self.procedureBp()
            # print('Bs -> Bp')
        return

    def procedureBp(self):
        self.procedureA()

        match self.current_token.value:
            case 'gr':
                self.read_token('gr')
                self.procedureA()
                # print('Bp -> A ’gr’ A')
                self.build_tree('gr', 2)
            case '>':
                self.read_token('>')
                self.procedureA()
                # print('Bp -> A ’>’ A')
                self.build_tree('gr', 2)
            case 'ge':
                self.read_token('ge')
                self.procedureA()
                # print('Bp -> A ’ge’ A')
                self.build_tree('ge', 2)
            case '>=':
                self.read_token('>=')
                self.procedureA()
                # print('Bp -> A ’>=’ A')
                self.build_tree('ge', 2)
            case 'ls':
                self.read_token('ls')
                self.procedureA()
                # print('Bp -> A ’ls’ A')
                self.build_tree('ls', 2)
            case '<':
                self.read_token('<')
                self.procedureA()
                # print('Bp -> A ’<’ A')
                self.build_tree('ls', 2)
            case 'le':
                self.read_token('le')
                self.procedureA()
                # print('Bp -> A ’le’ A')
                self.build_tree('le', 2)
            case '<=':
                self.read_token('<=')
                self.procedureA()
                # print('Bp -> A ’<=’ A')
                self.build_tree('le', 2)
            case 'eq':
                self.read_token('eq')
                self.procedureA()
                # print('Bp -> A ’eq’ A')
                self.build_tree('eq', 2)
            case 'ne':
                self.read_token('ne')
                self.procedureA()
                # print('Bp -> A ’ne’ A')
                self.build_tree('ne', 2)
            case _:
                # print('Bp -> A')
                pass
        return

    # Checked & Fixed
    def procedureA(self):

        if self.current_token.value == '+':
            self.read_token('+')
            self.procedureAt()
            # print('A ->’+’ At')

        elif self.current_token.value == '-':
            self.read_token('-')
            self.procedureAt()
            # print('A ->’-’ At')
            self.build_tree('neg', 1)

        else:
            self.procedureAt()
            # print('A -> At')

        while self.current_token.value == '+' or self.current_token.value == '-':
            if self.current_token.value == '+':
                self.read_token('+')
                self.procedureAt()
                # print('A ->A’+’ At')
                self.build_tree('+', 2)
            elif self.current_token.value == '-':
                self.read_token('-')
                self.procedureAt()
                # print('A ->A’-’ At')
                self.build_tree('-', 2)
        return

    def procedureAt(self):

        self.procedureAf()
        # print('At -> Af')

        while self.current_token.value == '*' or self.current_token.value == '/':
            if self.current_token.value == '*':
                self.read_token('*')
                self.procedureAf()
                # print('At -> At ’*’ Af')
                self.build_tree('*', 2)
            elif self.current_token.value == '/':
                self.read_token('/')
                self.procedureAf()
                # print('At -> At ’/’ Af')
                self.build_tree('/', 2)
        return

    def procedureAf(self):

        self.procedureAp()

        if self.current_token.value == '**':
            self.read_token('**')
            self.procedureAf()
            # print('Af -> Ap ’**’ Af')
            self.build_tree('**', 2)
            return
        # print('Af -> Ap')
        return

    # Checked & Fixed
    def procedureAp(self):

        self.procedureR()
        # print('Ap -> R')

        while self.current_token.value == '@':
            self.read_token('@')
            self.read_token_by_type('<IDENTIFIER>')
            self.procedureR()
            # print('Ap -> Ap ’@’ ’<IDENTIFIER>’ R')
            self.build_tree('@', 3)  # Checked & Fixed
        return

    # Checked and Fixed
    def procedureR(self):

        self.procedureRn()
        # print('R -> Rn')

        while (self.current_token.type in ["<IDENTIFIER>", "<INTEGER>", "<STRING>"] or
               self.current_token.value in ['true', 'false', 'nil', '(', 'dummy']):
            self.procedureRn()
            # print('R ->R Rn')
            self.build_tree('gamma', 2)
        return

    # Checked & Fixed
    def procedureRn(self):

        if self.current_token.type in ["<IDENTIFIER>", "<INTEGER>", "<STRING>"]:

            match self.current_token.type:
                case "<IDENTIFIER>":
                    self.read_token_by_type("<IDENTIFIER>")
                    # print('Rn -> ’<IDENTIFIER>’')
                case "<INTEGER>":
                    self.read_token_by_type("<INTEGER>")
                    # print('Rn -> ’<INTEGER>’')
                case "<STRING>":
                    self.read_token_by_type("<STRING>")
                    # print('Rn -> ’<STRING>’')

        elif self.current_token.value in ['true', 'false', 'nil', '(', 'dummy']:

            match self.current_token.value:
                case 'true':
                    self.read_token('true')
                    # print('Rn -> ’true’')
                    self.build_tree('true', 0)
                case 'false':
                    self.read_token('false')
                    # print('Rn -> ’false’')
                    self.build_tree('false', 0)
                case 'nil':
                    self.read_token('nil')
                    # print('Rn -> ’nil’')
                    self.build_tree('nil', 0)
                case 'dummy':
                    self.read_token('dummy')
                    # print('Rn -> ’dummy’')
                    self.build_tree('dummy', 0)
                case '(':
                    self.read_token('(')
                    self.procedureE()
                    self.read_token(')')
                    # print('Rn -> ’( E )’')
        return

    def procedureD(self):

        self.procedureDa()

        if self.current_token.value == 'within':
            self.read_token('within')
            self.procedureD()
            # print('D -> Da ’within’ D')
            self.build_tree('within', 2)
            return
        # print('D -> Da')
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
            # print('Da -> Dr ( ’and’ Dr )+')
            self.build_tree('and', n + 1)
        # print('Da -> Dr')
        return

    def procedureDr(self):
        if self.current_token.value == 'rec':

            self.read_token('rec')
            self.procedureDb()
            # print('Dr -> ’rec’ Db')
            self.build_tree('rec', 1)
        else:
            self.procedureDb()
            # print('Dr -> Db')
        return

    # Checked & Fixed
    def procedureDb(self):

        if self.current_token.value == '(':
            self.read_token('(')
            self.procedureD()
            self.read_token(')')
            # print('Db -> ’(’ D ’)’ ')
        elif self.current_token.type == '<IDENTIFIER>':
            '''
            We happened to check two consecutive tokens as 
                Db -> Vl ’=’ E => ’=’
                   -> ’<IDENTIFIER>’ Vb+ ’=’ E
                both have the same first set <IDENTIFIER>
            '''
            # up-coming token is looked ahead to resolve the issued mentioned above.
            look_ahead_token = self.tokens[self.current_token_idx + 1]

            if look_ahead_token.type == '<IDENTIFIER>' or look_ahead_token.value == '(':
                # 'Db -> ’<IDENTIFIER>’ Vb+ ’=’ E' is chosen
                self.read_token_by_type('<IDENTIFIER>')

                if self.current_token.value == '(' or self.current_token.type == '<IDENTIFIER>':
                    self.procedureVb()
                    n = 1

                    while self.current_token.value == '(' or self.current_token.type == '<IDENTIFIER>':
                        self.procedureVb()
                        n += 1

                    self.read_token('=')

                    self.procedureE()
                    # print('Db -> ’<IDENTIFIER>’ Vb+ ’=’ E')
                    self.build_tree('function_form', n + 2)  # Checked & Fixed
            else:
                self.procedureVl()
                self.read_token('=')
                self.procedureE()

                # print('Db -> Vl ’=’ E')
                self.build_tree('=', 2)
        return

    def procedureVb(self):

        if self.current_token.value == '(':
            self.read_token('(')
            if self.current_token.value == ')':
                self.read_token(')')
                # print('Vb -> ’(’ ’)’')
                self.build_tree('()', 0)
            else:
                self.procedureVl()
                self.read_token(')')
                # print('Vb -> ’(’ Vl ’)’')
        else:
            self.read_token_by_type('<IDENTIFIER>')
            # print('Vb -> ’<IDENTIFIER>’')
        return

    def procedureVl(self):

        self.read_token_by_type('<IDENTIFIER>')

        n = 0
        while self.current_token.value == ',':
            self.read_token(',')
            self.read_token_by_type('<IDENTIFIER>')
            n += 1

        if n > 0:
            # print('Vl -> ’<IDENTIFIER>’ list ’,’')
            self.build_tree(',', n + 1)
        return

    '''
    ######################### Procedures for each Non-Terminals Ends #########################
    '''

    # def parse_file(self, in_file, out_file):
    #     """
    #     This function first extracts the tokens,  parses by invoking respective functions.
    #     :param in_file: contains source RPAL program
    #     :param out_file: output file contains AST
    #     :return:
    #     """
    #     self.extract_tokens(in_file)
    #     self.procedureE()
    #     self.print_tree(self.stack[0])
    #      with open(out_file, 'w') as output:
    #          output.write(self.output_AST)
    #     return

    def parse_file(self, in_file):
        """
        This function first extracts the tokens,  parses by invoking respective functions.
        :param in_file: contains source RPAL program
        :return:
        """
        self.extract_tokens(in_file)
        self.procedureE()
        self.build_AST(self.stack[0])
        return

    def build_AST(self, node, level=0):
        """
        This function prints the built AST tree.
        :param node:
        :param level:
        :return:
        """
        # level parameter is used for discriminate the levels of nodes in the AST
        self.output_AST += '.' * level + node.value + "\n"
        if len(node.children) == 0:
            return

        # when building AST children of each node is reversed.
        # To reciprocate that we have to again reverse the stack in each node level.
        node.children.reverse()

        level += 1

        for child in node.children:
            self.build_AST(child, level)

