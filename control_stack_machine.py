from environment import Environment
import re


class CSE_machine:
    def __init__(self):
        self.control_structure = {}
        self.stack = []
        self.control_stack = []
        # self.environment_tree = Environment(0)
        self.env_idx = 0
        self.idx = 0  # to discriminate new control structure
        self.curr_env = None

    def label_lambda(self, root):
        """
        This function is for labeling lambda nodes and for casting int, strings before generating control structure
        :param root:
        :return:
        """

        # each time encountering lambda node idx is incremented by 1 and lambda--> lambda(idx)
        if root.value == "lambda":
            self.idx += 1
            root.value = (root.value, self.idx)
            self.label_lambda(root.children[1])

        if len(root.children) == 0:
            return

        for child in root.children:
            self.label_lambda(child)

    def generate_control_structure(self, root, idx):
        """
        This function traverses the ST and generates respective control structures
        :param root:
        :param idx:
        :return:
        """
        # create a list for the new control structure
        if idx not in self.control_structure:
            self.control_structure[idx] = []

        # add the node in ST to control structure
        self.control_structure[idx].append(root.value)

        # encountering lambda indicates new control stack
        if root.value[0] == "lambda":
            if root.children[0].value == ',':
                comma_children = root.children[0].children  # children of comma
                comma_child_values = []
                for child in comma_children:
                    child_val = child.value
                    colon_idx = child_val.find(":")
                    child_val = child_val[colon_idx + 1:-1]
                    comma_child_values.append(child_val)
                comma_child_values = tuple(comma_child_values)

                self.control_structure[idx][-1] = ("lambda", root.value[-1], comma_child_values)

            else:
                # add the additional info of the variable related to that node and
                # environment where the expression in lambda is going to be evaluated.
                self.control_structure[idx][-1] = ("lambda", root.value[-1], root.children[0].value)

            # create another tree for the expression in lambda node.
            self.generate_control_structure(root.children[1], root.value[-1])

            # remove the children of lambda inorder to traverse further.
            root.children = []

        # control structure for conditional operators
        elif root.value == '->':
            # make new expression for then clause in control structure
            self.idx += 1
            then_expr = ('then', self.idx)  # has the key for then expression in control structure
            self.generate_control_structure(root.children[1], self.idx)

            # make new expression for else clause in control structure
            self.idx += 1
            else_expr = ('else', self.idx)  # has the key for else expression in control structure
            self.generate_control_structure(root.children[2], self.idx)

            self.control_structure[idx].pop()  # remove '->' from respective control stack
            self.control_structure[idx].append(then_expr)  # pushing expression for then clause
            self.control_structure[idx].append(else_expr)  # pushing expression for else clause
            self.control_structure[idx].append('->')  # pushing '->' to activate branching in control stack.

            # remove the last 2 children of '->' node as they are generated above.
            root.children.pop()
            root.children.pop()

        elif root.value == 'tau':
            child_count = len(root.children)
            self.control_structure[idx][-1] = ("tau", child_count)

        # base case for recursion: if the node has no children simply return
        if len(root.children) == 0:
            return

        # preorder traversal
        for child in root.children:
            self.generate_control_structure(child, idx)

    def apply(self):
        # '<ID: Conc>'
        rator = self.control_stack.pop()
        if rator in ['+', '-', '*', '/', '**']:
            op1 = self.stack.pop()
            op2 = self.stack.pop()
            expression = str(op1) + rator + str(op2)
            return eval(expression)

        # this operator is for finding the length of a tuple
        elif rator == 'gamma':

            operator = self.stack.pop()  # popping respective operator from stack
            if operator == '<ID:Order>':
                op_tuple = self.stack.pop()
                if isinstance(op_tuple, tuple):
                    return len(op_tuple)
                else:
                    exit('Tuple expected for Order')

            # returns first character in a String
            elif operator == '<ID:Stem>':
                op_string = self.stack.pop()
                if isinstance(op_string, str):
                    # removing the apostrophe at the beginning and the end.
                    op_string = op_string[1:-1]

                    try:
                        return op_string[0]
                    # empty string case
                    except IndexError:
                        return ''
                else:
                    exit('String expected for Stem')

            # returns the string except first character
            elif operator == '<ID:Stern>':
                op_string = self.stack.pop()
                if isinstance(op_string, str):
                    # removing the apostrophe at the beginning and the end.
                    op_string = op_string[1:-1]

                    try:
                        return op_string[1:]
                    # empty string case
                    except IndexError:
                        return ''
                else:
                    exit('String expected for Stern')

            # returns concatenate two strings
            elif operator == '<ID:Conc>':

                # pop another gamma from control stack
                self.control_stack.pop()

                op_string_1 = self.stack.pop()
                op_string_2 = self.stack.pop()

                # both operands should be string
                if isinstance(op_string_1, str) and isinstance(op_string_2, str):
                    # removing the apostrophe at the beginning and the end.
                    op_string_1 = op_string_1[1:-1]
                    op_string_2 = op_string_2[1:-1]

                    return op_string_1 + op_string_2  # concatenated string

                else:
                    exit('Strings expected for Conc')

        elif rator == 'aug':
            op1 = self.stack.pop()
            op2 = self.stack.pop()

            # creating a new tuple
            if op1 == 'nil':
                t = (op2,)

            # add elements to existing tuple
            elif isinstance(op1, tuple):
                t = list(op1)
                t.append(op2)
                t = tuple(t)
            return t

        elif rator in ['gr', 'ge', 'ls', 'le', 'eq', 'ne', 'or', '&', '>', '>=', '<', '<=']:
            op1 = self.stack.pop()
            op2 = self.stack.pop()

            match rator:
                case 'gr':
                    return 'true' if op1 > op2 else 'false'
                case 'ge':
                    return 'true' if op1 >= op2 else 'false'
                case 'ls':
                    return 'true' if op1 < op2 else 'false'
                case 'le':
                    return 'true' if op1 <= op2 else 'false'
                case 'eq':
                    return 'true' if op1 == op2 else 'false'
                case 'ne':
                    return 'true' if op1 != op2 else 'false'
                case '>':
                    return 'true' if op1 > op2 else 'false'
                case '>=':
                    return 'true' if op1 >= op2 else 'false'
                case '<':
                    return 'true' if op1 < op2 else 'false'
                case '<=':
                    return 'true' if op1 <= op2 else 'false'
                case 'or':
                    return 'true' if op1 or op2 else 'false'
                case '&':
                    return 'true' if op1 and op2 else 'false'

        elif rator in ['not', 'neg']:
            op = self.stack.pop()
            match rator:
                case 'not':
                    return 'true' if not op else 'false'
                case 'neg':
                    return -op

    def run_program(self):
        ############################ Initialization ############################
        # initializing environment
        global content
        env_0 = Environment(self.env_idx)

        self.env_idx += 1  # increment env_idx after creation of each environment

        self.curr_env = env_0

        # initializing stack
        self.stack.append(env_0)

        # initializing control_stack
        self.control_stack.append(env_0)
        self.control_stack.extend(self.control_structure[self.curr_env.name])

        content = ''

        while self.control_stack:
        # for i in range(20):
        #     for debugging - print control stack and stack
            sline = ''
            cline = ''
            for i in self.control_stack:
                if isinstance(i, Environment):
                    cline += f"e{i.name} "
                elif isinstance(i, tuple) and i[0] == 'lambda':
                    cline += f"<lambda delta({i[1]}) var:{i[2][4:-1]}> "
                elif str(i)[0]=='<' and str(i)[-1]=='>':
                    col_idx = str(i).find(":")
                    cline += str(i)[col_idx+1:-1]+ ' '
                else:
                    cline = cline+str(i)+' '

        # (parent_env, lambda, expression_num, variable)
            for i in self.stack[::-1]:
                if isinstance(i, Environment):
                    sline += f"e{i.name} "
                elif isinstance(i, tuple) and len(i) == 4:
                    if i[1] == 'lambda' or i[1] == 'eta':
                        sline += f"<{i[1]} e{i[0].name},delta({i[2]}) var:{i[3]}> "
                else:
                    sline = sline+str(i)+' '
            content += f"{cline:<120}{sline:>100}"
            content += '\n'

            stack_top = self.stack[-1]
            control_top = self.control_stack[-1]

            ############################ Rule 1 ############################
            if isinstance(control_top, str):
                #  to print the output
                if control_top == '<ID:Print>' or control_top == '<ID:print>':
                    self.control_stack.pop()  #  to pop Print from control stack
                    self.control_stack.pop()  # to pop gamma from control stack

                    print(self.stack[-1])  # print the output without disturbing the stack.

                # treat '<ID:Order>','<ID: Conc>' , '<ID:Stem>', '<ID:Stern>' as operators.
                elif control_top in ['<ID:Order>','<ID:Conc>', '<ID:Stem>', '<ID:Stern>']:
                    self.stack.append(self.control_stack.pop())  # pop from control stack push into stack

                # identifier on the top of control stack
                elif control_top[0] == "<" and control_top[-1] == ">" and 'ID' in control_top:
                    colon_idx = control_top.find(':')
                    name = control_top[colon_idx + 1:-1]  # extracting identifier from <ID:name>
                    value = self.curr_env.lookup(name)

                    self.control_stack.pop()
                    self.stack.append(value)

                # string at the top of the control stack
                elif control_top[0] == "<" and control_top[-1] == ">" and 'STR' in control_top:
                    colon_idx = control_top.find(':')
                    str_literal = control_top[colon_idx + 1:-1]  # extracting string from <STR:str_literal>

                    self.control_stack.pop()
                    self.stack.append(str(str_literal))

                # integer at the top of control stack
                elif control_top[0] == "<" and control_top[-1] == ">" and 'INT' in control_top:
                    colon_idx = control_top.find(':')
                    number = control_top[colon_idx + 1:-1]  # extracting integer from <INT:number>

                    self.control_stack.pop()
                    self.stack.append(int(number))

                elif control_top in ['true', 'false', 'nil', 'Y*']:
                    self.stack.append(self.control_stack.pop())

                ############################ Rule 3 ############################
                elif control_top == 'gamma':
                    if isinstance(stack_top, tuple):
                        if stack_top[1] == 'lambda':
                            # unpack the lambda node from stack and remove top of stack
                            (parent_env, _, expr_key, variables) = self.stack.pop()

                            # pop the value for binding from stack
                            values = self.stack.pop()

                            # remove top of control stack to remove gamma
                            self.control_stack.pop()

                            # create new environment
                            new_env = Environment(self.env_idx)
                            self.env_idx += 1  # increment env_idx

                            # when the variables given inside a tuple
                            if isinstance(stack_top[-1], tuple):
                                if len(values) == len(variables):
                                    for i in range(len(variables)):
                                        new_env.add_binding(variables[i], values[i])
                                else:
                                    exit('Variable count doesn\'t match')
                            else:
                                # add binding
                                new_env.add_binding(variables, values)

                            # # for debugging
                            # print("---"*20)
                            # print('curr_env:', self.curr_env.name)
                            # print('new Env:', new_env.name)
                            # print('New env bind:', new_env.binding)

                            # make new env as the child
                            parent_env.add_child(new_env)

                            # add new environment to both stack and control stack
                            self.control_stack.append(new_env)
                            self.stack.append(new_env)

                            # add the new control structure for lambda.
                            self.control_stack.extend(self.control_structure[expr_key])

                            # make new env as the current env
                            self.curr_env = new_env

                        ############################ Rule 12 ############################
                        # case when gamma and eta are on the top of each stack
                        elif stack_top[1] == 'eta':
                            # prepare a lambda node using eta node.
                            lambda_node = list(stack_top)
                            lambda_node[1] = 'lambda'
                            lambda_node = tuple(lambda_node)

                            self.control_stack.append('gamma')
                            self.stack.append(lambda_node)

                        # tuple selection
                        elif isinstance(self.stack[-2], int):
                            t = self.stack.pop()
                            i = self.stack.pop()

                            try:
                                elem = t[i - 1]  # 1st element's idx = 1
                                self.stack.append(elem)
                                self.control_stack.pop()
                            except IndexError:
                                exit("Index out of range")

                    ############################ Rule 12 ############################
                    #  encountering gamma and Y* at the top of each stack
                    elif stack_top == 'Y*':
                        #  verify the next element of Y* is a lambda
                        if isinstance(self.stack[-2], tuple) and self.stack[-2][1] == 'lambda':
                            self.control_stack.pop()  # removing gamma from control stack

                            # removing Y* from stack
                            self.stack.pop()

                            # for eta node
                            eta_node = list(self.stack.pop())
                            eta_node[1] = 'eta'
                            eta_node = tuple(eta_node)

                            # push eta node back to stack
                            self.stack.append(eta_node)

                    # execute following operators as soon as encounter gamma on control stack top.
                    elif stack_top in ['<ID:Order>', '<ID:Conc>', '<ID:Stem>', '<ID:Stern>']:
                        self.stack.append(self.apply())

                ############################ Rule 6,7 ############################
                elif control_top in ['aug', '+', '-', '*', '/', '**', 'gr', 'ge', 'ls', 'le', 'eq', 'ne', 'or', '&', '>',
                                     '>=', '<', '<=', 'not', 'neg']:
                    self.stack.append(self.apply())

                elif control_top == '->':
                    self.control_stack.pop()  # removing '->' from ctrl stack
                    if self.stack[-1] == 'true':
                        self.stack.pop()  # remove true from stack
                        self.control_stack.pop()
                        then_part = self.control_stack.pop()
                        then_expr = self.control_structure[then_part[-1]]
                        self.control_stack.extend(then_expr)

                    else:
                        self.stack.pop()  # remove true from stack
                        else_part = self.control_stack.pop()
                        self.control_stack.pop()
                        else_expr = self.control_structure[else_part[-1]]
                        self.control_stack.extend(else_expr)



            ############################ Rule 2 ############################
            elif isinstance(control_top, tuple):
                # lambda node
                if control_top[0] == "lambda":
                    if isinstance(control_top[-1], tuple):
                        name = control_top[-1]  # tuple of variables
                    else:
                        colon_idx = control_top[2].find(':')
                        name = control_top[2][colon_idx + 1:-1]  # extracting identifier from <ID:name>
                    stack_element = (self.curr_env, control_top[0], control_top[1],
                                     name)  # (parent_env, lambda, expression_num, variable)

                    self.control_stack.pop()
                    self.stack.append(stack_element)

                elif control_top[0] == 'tau':
                    tau_child = []
                    child_count = control_top[-1]
                    for i in range(child_count):
                        tau_child.append(self.stack.pop())

                    self.control_stack.pop()  # remove tau from control stack
                    self.stack.append(tuple(tau_child))  # push the formed tuple into stack

            ############################ Rule 2 ############################
            elif isinstance(control_top, Environment):
                # retrieving final result from an environment
                if control_top is self.stack[-2]:
                    # remove the environment object on top of the control stack.
                    self.control_stack.pop()

                    # get the value from the stack
                    result = self.stack.pop()

                    # remove the environment object on top of the stack.
                    self.stack.pop()

                    # when removing the environment from the stack, we have to make next closest environment as the current one.
                    for elem in self.stack[::-1]:
                        if isinstance(elem, Environment):
                            self.curr_env = elem
                            break

                    # put the result back to the stack.
                    self.stack.append(result)
        else:
            with open('CSE evaluation.txt', 'w') as f:
                f.write(content)

    def execute(self, root):
        """
        This function executes the program by calling necessary functions on the given root node.
        :param root:
        :return:
        """
        self.label_lambda(root)
        self.generate_control_structure(root, 0)
        self.run_program()
