from Tokens import Token


class Tokenizer:
    """
    This class is for Extracting and labeling the tokens from a given file.
    This object can do scanning and screening.
    """
    def __init__(self):
        # set of states in the FA
        self.states = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22}

        # set of accepting states of FA
        self.accepting_states = {1, 2, 3, 4, 5, 8, 14, 15, 16, 17, 18, 19}

        # initial state
        self.current_state = 0

        # mapping state with respective transition functions
        self.transition_table = {0: 'transition_at_0', 1: 'transition_at_1', 2: 'transition_at_2', 3: 'transition_at_3',
                                 4: 'transition_at_4', 5: 'transition_at_5', 6: 'transition_at_6', 7: 'transition_at_7',
                                 8: 'transition_at_8', 9: 'transition_at_9', 10: 'transition_at_10',
                                 11: 'transition_at_11',
                                 12: 'transition_at_12', 13: 'transition_at_13', 14: 'transition_at_14',
                                 15: 'transition_at_15',
                                 16: 'transition_at_16', 17: 'transition_at_17', 18: 'transition_at_18',
                                 19: 'transition_at_19',
                                 20: 'transition_at_20', 21: 'transition_at_21', 22: 'transition_at_22'
                                 }

        # initial token is an empty string
        self.current_token = ''

        # keeps the picked tokens
        self.picked_tokens = []

        # position of the character being read in the current line. Used for finding position of lexical violation
        self.char_position = 0

        # the current line being read
        self.line_number = 0

        # associating states with respective labels
        self.state_labels = {1: "<IDENTIFIER>", 2: "<INTEGER>", 3: "<OPERATOR>", 4: "<OPERATOR>", 5: "<OPERATOR>",
                             8: "<DELETE>", 14: "<STRING>", 15: "<DELETE>", 16: ")", 17: "(", 18: ";", 19: ","}

        # special keywords
        self.keywords = ['let', 'in', 'fn', 'where', 'aug', 'or', 'not', 'gr', 'ge', 'ls', 'le', 'eq', 'ne', 'true',
                         'false', 'nil', 'dummy', 'within', 'and', 'rec']

        # operator symbol
        self.operator_symbols = ['+', '-', '*', '<', '>', '&', '.', '@', '/', ':', '=', '~', '|', '$', '!', '#', '%',
                                 '^', '_', '[', ']',
                                 '{', '}', '"', "`", '?']

        # digit
        self.digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

        # letter
        self.letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                        'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
                        't', 'u', 'v', 'w', 'x', 'y', 'z']

        self.white_space = chr(32)
        self.horizontal_tab = chr(9)
        self.end_of_line = chr(10)

    '''this reset() function resets the finite automaton to the initial state, 
    and collect the tokens if those tokens are acceptable'''
    def reset(self):
        """
        This function add completed tokens into the picked_tokens list and notify lexical violations if there are any
        """
        if self.current_state in self.accepting_states:
            self.picked_tokens.append(Token(self.state_labels[self.current_state], self.current_token))
            self.current_state = 0
            self.current_token = ''

        else:
            raise Exception("Lexical Rules Violated in line:%d at position:%d." % (self.line_number, self.char_position))

    '''
    ######################### Beginning of Transition Functions #########################
    '''

    def transition_at_0(self, c):
        ope_sym_4 = self.operator_symbols.copy()
        ope_sym_4.remove('/')
        if c in self.letters:
            self.current_state = 1
            self.current_token += c
            self.char_position += 1
        elif c in self.digits:
            self.current_state = 2
            self.current_token += c
            self.char_position += 1
        elif c == '/':
            self.current_state = 3
            self.current_token += c
            self.char_position += 1
        elif c in ope_sym_4:
            self.current_state = 4
            self.current_token += c
            self.char_position += 1
        # elif c == "'":
        #     self.current_state = 9
        #     self.current_token += c
        #     self.char_position += 1
        elif c == "'":
            self.current_state = 10
            self.current_token += c
            self.char_position += 1
        elif c in [self.white_space, self.horizontal_tab]:
            self.current_state = 15
            self.current_token += c
            self.char_position += 1
        elif c == ")":
            self.current_state = 16
            self.current_token += c
            self.char_position += 1
        elif c == "(":
            self.current_state = 17
            self.current_token += c
            self.char_position += 1
        elif c == ";":
            self.current_state = 18
            self.current_token += c
            self.char_position += 1
        elif c == ",":
            self.current_state = 19
            self.current_token += c
            self.char_position += 1
        elif c == "\\":
            self.current_state = 21
            self.current_token += c
            self.char_position += 1

        else:
            # set the state to 0, and collect the scanned token so far and prepare FA for scanning next token
            self.reset()

    def transition_at_1(self, c):
        if (c in self.letters) or (c in self.digits) or (c == "_"):
            self.current_state = 1
            self.current_token += c
            self.char_position += 1
        else:
            self.reset()

    def transition_at_2(self, c):
        if c in self.digits:
            self.current_state = 2
            self.current_token += c
            self.char_position += 1
        else:
            self.reset()

    def transition_at_3(self, c):
        op_sym_set_3 = self.operator_symbols.copy()
        op_sym_set_3.remove('/')  # getting set of symbols triggers a specific transition at state 3

        if c in op_sym_set_3:
            self.current_state = 4
            self.current_token += c
            self.char_position += 1
        elif c == '/':
            self.current_state = 5
            self.current_token += c
            self.char_position += 1
        else:
            self.reset()

    def transition_at_4(self, c):
        if c in self.operator_symbols:
            self.current_state = 4
            self.current_token += c
            self.char_position += 1
        else:
            self.reset()

    def transition_at_5(self, c):
        if c in self.operator_symbols:
            self.current_state = 5
            self.current_token += c
            self.char_position += 1
        elif c == "\\":
            self.current_state = 20
            self.current_token += c
            self.char_position += 1
        elif c == "'":
            self.current_state = 6
            self.current_token += c
            self.char_position += 1

        # chr(92) = \
        elif (c in self.letters) or (c in self.digits) or (
                c in [self.horizontal_tab, self.white_space, '(', ')', ';', ',', chr(92)]):
            self.current_state = 7
            self.current_token += c
            self.char_position += 1
        else:
            self.reset()

    def transition_at_6(self, c):
        if c == "'":
            self.current_state = 7
            self.current_token += c
            self.char_position += 1
        else:
            self.reset()

    def transition_at_7(self, c):
        if c == "'":
            self.current_state = 6
            self.current_token += c
            self.char_position += 1
        elif (c in self.letters) or (c in self.digits) or (c in self.operator_symbols) or (
                c in [self.horizontal_tab, self.white_space, '(', ')', ';', ',']):
            self.current_state = 7
            self.current_token += c
            self.char_position += 1
        elif c == '\\':
            self.current_state = 20
            self.current_token += c
            self.char_position += 1
        else:
            self.reset()

    def transition_at_8(self, c):
        self.reset()

    # def transition_at_9(self, c):
    #     if c == "'":
    #         self.current_state = 10
    #         self.current_token += c
    #         self.char_position += 1
    #     else:
    #         self.reset()

    def transition_at_10(self, c):
        if (c in self.letters) or (c in self.digits) or (c in self.operator_symbols) or (
                c in [self.white_space, '(', ')', ';', ',']):
            self.current_state = 10
            self.current_token += c
            self.char_position += 1
        elif c == "/":
            self.current_state = 11
            self.current_token += c
            self.char_position += 1
        # elif c == "'":
        #     self.current_state = 13
        #     self.current_token += c
        #     self.char_position += 1
        elif c == "'":
            self.current_state = 14
            self.current_token += c
            self.char_position += 1
        else:
            self.reset()

    def transition_at_11(self, c):
        if c == 't' or c == 'n' or c == '/':
            self.current_state = 10
            self.current_token += c
            self.char_position += 1
        elif c == "'":
            self.current_state = 12
            self.current_token += c
            self.char_position += 1
        else:
            self.reset()

    def transition_at_12(self, c):
        if c == "'":
            self.current_state = 10
            self.current_token += c
            self.char_position += 1
        else:
            self.reset()

    # def transition_at_13(self, c):
    #     if c == "'":
    #         self.current_state = 14
    #         self.current_token += c
    #         self.char_position += 1
    #     else:
    #         self.reset()

    def transition_at_14(self, c):
        self.reset()

    def transition_at_15(self, c):
        if c in [self.white_space, self.horizontal_tab]:
            self.current_state = 15
            self.current_token += c
            self.char_position += 1
        elif c == "\\":
            self.current_state = 22
            self.current_token += c
            self.char_position += 1
        else:
            self.reset()

    def transition_at_16(self, c):
        self.reset()

    def transition_at_17(self, c):
        self.reset()

    def transition_at_18(self, c):
        self.reset()

    def transition_at_19(self, c):
        self.reset()

    def transition_at_20(self, c):
        if c == "n":
            self.current_state = 8
            self.current_token += c
            self.char_position += 1
        elif (c in self.letters) or (c in self.digits) or (c in self.operator_symbols) or (
                c in [self.horizontal_tab, self.white_space, '(', ')', ';', ',']):
            self.current_state = 7
            self.current_token += c
            self.char_position += 1
        elif c == '\\':
            self.current_state = 20
            self.current_token += c
            self.char_position += 1
        else:
            self.reset()

    def transition_at_21(self, c):
        if c == "n" or "t":
            self.current_state = 15
            self.current_token += c
            self.char_position += 1
        else:
            self.reset()

    def transition_at_22(self, c):
        if c == "n" or "t":
            self.current_state = 15
            self.current_token += c
            self.char_position += 1
        else:
            self.reset()

    '''
    ######################### End of Transition Functions #########################
    '''

    def screen(self):
        """
        This function removes the unnecessary white spaces, tab space and EOLs.
        """

        screened_tokens = []

        for token in self.picked_tokens:
            # Separating keywords from the <IDENTIFIER> tokens.
            if token.value in self.keywords:
                token.type = '<KEYWORD>'

            # Removing tokens from <DELETE> type: white space, tabs, EOL, and comments.
            if token.type == '<DELETE>':
                continue

            screened_tokens.append(token)
        self.picked_tokens = screened_tokens

    def tokenize(self, file):
        """
        This function tokenizes the input file and output list of tokens
        """
        try:
            # open the file to tokenize it
            with open(file, 'r') as file:

                # this loop is for reading and tokenizing each line
                for line in file:

                    characters = list(repr(line)[1:-1])  # raw string representation to capture the EOL character as it is
                    self.line_number += 1
                    self.char_position = 0

                    while self.char_position < len(characters):

                        f = self.transition_table[self.current_state]
                        i = characters[self.char_position]
                        # print(f, i)
                        match f:
                            case 'transition_at_0':
                                self.transition_at_0(i)
                            case 'transition_at_1':
                                self.transition_at_1(i)
                            case 'transition_at_2':
                                self.transition_at_2(i)
                            case 'transition_at_3':
                                self.transition_at_3(i)
                            case 'transition_at_4':
                                self.transition_at_4(i)
                            case 'transition_at_5':
                                self.transition_at_5(i)
                            case 'transition_at_6':
                                self.transition_at_6(i)
                            case 'transition_at_7':
                                self.transition_at_7(i)
                            case 'transition_at_8':
                                self.transition_at_8(i)
                            # case 'transition_at_9':
                            #     self.transition_at_9(i)
                            case 'transition_at_10':
                                self.transition_at_10(i)
                            case 'transition_at_11':
                                self.transition_at_11(i)
                            case 'transition_at_12':
                                self.transition_at_12(i)
                            # case 'transition_at_13':
                            #     self.transition_at_13(i)
                            case 'transition_at_14':
                                self.transition_at_14(i)
                            case 'transition_at_15':
                                self.transition_at_15(i)
                            case 'transition_at_16':
                                self.transition_at_16(i)
                            case 'transition_at_17':
                                self.transition_at_17(i)
                            case 'transition_at_18':
                                self.transition_at_18(i)
                            case 'transition_at_19':
                                self.transition_at_19(i)
                            case 'transition_at_20':
                                self.transition_at_20(i)
                            case 'transition_at_21':
                                self.transition_at_21(i)
                            case 'transition_at_22':
                                self.transition_at_22(i)

                    # this reset invocation is for accepting states like 1,2,4,5,15 (accepting states and have
                    # transitions) when token belong to those states is collected till the end of the line,
                    # we have to break the token before moving to the next line.
                    self.reset()

            # screening the unwanted white space, tabs and end of line characters
            self.screen()
            return self.picked_tokens
        except FileNotFoundError:
            print("File doesn't exist!")
            exit()

# For debugging purpose
# tokenizer = Tokenizer()
# tokens = tokenizer.tokenize('test.txt')
#
# for token in tokens:
#     print(token.value, "------", token.type)
