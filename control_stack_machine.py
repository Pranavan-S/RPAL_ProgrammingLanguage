from environment import Environment
import re

class CSE_machine:
    def __init__(self):
        self.control_structure = {}
        self.stack = []
        self.control_stack = []
        self.environment_tree = Environment(0)
        self.idx = 0
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
            # add the additional info of the variable related to that node and
            # environment where the expression in lambda is going to be evaluated.
            self.control_structure[idx][-1] = ("lambda", root.value[-1], root.children[0].value)

            # create another tree for the expression in lambda node.
            self.generate_control_structure(root.children[1], root.value[-1])

            # remove the children of lambda inorder to traverse further.
            root.children = []

        # control structure for conditional operators
        if root.value == '->':
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



        # base case for recursion: if the node has no children simply return
        if len(root.children) == 0:
            return

        # preorder traversal
        for child in root.children:
            self.generate_control_structure(child, idx)

    def apply(self):
        rator = self.control_stack.pop()
        if rator in ['+', '-', '*', '/', '**']:
            op1 = self.stack.pop()
            op2 = self.stack.pop()
            expression = str(op1)+rator+str(op2)
            return eval(expression)

        elif rator == 'aug':
            op1 = self.stack.pop()
            op2 = self.stack.pop()

            if op1 == 'nil':
                t = (op2,)

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
                case'not':
                    return 'true' if not op else 'false'
                case 'neg':
                    return -op

    def run_program(self):
        ############################ Initialization ############################
        # initializing environment
        env_0 = Environment(0)
        self.curr_env = env_0

        # initializing stack
        self.stack.append(env_0)

        # initializing control_stack
        self.control_stack.append(env_0)
        self.control_stack.extend(self.control_structure[self.curr_env.name])


        while self.control_stack:
        # for i in range(20):
    #--------------------------------------loooooooooooooooppppp----------------------------------------------#

            stack_top = self.stack[-1]
            control_top = self.control_stack[-1]

            ############################ Rule 1 ############################
            if isinstance(control_top, str):
                # identifier on the top of control stack
                if control_top[0] == "<" and control_top[-1] == ">" and 'ID' in control_top:
                    colon_idx = control_top.find(':')
                    name = control_top[colon_idx+1:-1]  # extracting identifier from <ID:name>
                    value = self.curr_env.lookup(name)

                    self.control_stack.pop()
                    self.stack.append(value)

                # string at the top of the control stack
                elif control_top[0] == "<" and control_top[-1] == ">" and 'STR' in control_top:
                    colon_idx = control_top.find(':')
                    str_literal = control_top[colon_idx+1:-1]  # extracting string from <STR:str_literal>

                    self.control_stack.pop()
                    self.stack.append(str(str_literal))

                # integer at the top of control stack
                elif control_top[0] == "<" and control_top[-1] == ">" and 'INT' in control_top:
                    colon_idx = control_top.find(':')
                    number = control_top[colon_idx + 1:-1]  # extracting integer from <INT:number>

                    self.control_stack.pop()
                    self.stack.append(int(number))

                elif control_top in ['true', 'false', 'nil']:
                    self.stack.append(self.control_stack.pop())

                ############################ Rule 3 ############################
                elif control_top == 'gamma':
                   if isinstance(stack_top, tuple):
                        if stack_top[1] == 'lambda':
                            # unpack the lambda node from stack and remove top of stack
                            (parent_env, _, expr_key, variable) = self.stack.pop()

                            # pop the value for binding from stack
                            value = self.stack.pop()

                            # remove top of control stack
                            self.control_stack.pop()

                            # create new environment
                            new_env = Environment(expr_key)

                            # add binding
                            new_env.add_binding(variable, value)

                            # make new env as the child
                            parent_env.add_child(new_env)

                            # add new environment to both stack and control stack
                            self.control_stack.append(new_env)
                            self.stack.append(new_env)

                            # add the new control structure for lambda.
                            self.control_stack.extend(self.control_structure[expr_key])

                            # make new env as the current env
                            self.curr_env = new_env

                        # tuple selection
                        elif self.stack[-2]:
                            t = self.stack.pop()
                            i = self.stack.pop()

                            try:
                                elem = t[i-1]  # 1st element's idx = 1
                                self.stack.append(elem)
                                self.control_stack.pop()
                            except IndexError:
                                exit("Index out of range")

                ############################ Rule 6,7 ############################
                if control_top in ['aug', '+', '-', '*', '/', '**', 'gr', 'ge', 'ls', 'le', 'eq', 'ne', 'or', '&', '>', '>=', '<', '<=', 'not', 'neg']:
                    self.stack.append(self.apply())

                if control_top == '->':
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
            if isinstance(control_top, tuple):
                # lambda node
                if control_top[0] == "lambda":
                    colon_idx = control_top[2].find(':')
                    name = control_top[2][colon_idx + 1:-1]  # extracting identifier from <ID:name>
                    stack_element = (self.curr_env, control_top[0], control_top[1], name)  # (parent_env, lambda, expression_num, variable)

                    self.control_stack.pop()
                    self.stack.append(stack_element)

            ############################ Rule 2 ############################
            if isinstance(control_top, Environment):
                # retrieving final result from an environment
                if control_top is self.stack[-2]:
                    # remove the environment object on top of the control stack.
                    self.control_stack.pop()

                    # get the value from the stack
                    result = self.stack.pop()

                    # remove the environment object on top of the stack.
                    self.stack.pop()

                    # put the result back to the stack.
                    self.stack.append(result)

            print("\ncs:", self.control_stack)
            print("\ns:", self.stack)

