from typing import Dict, Any

from TreeNodes import TreeNode


class Standardizer:

    def __init__(self):
        self.std_tree = None
        self.output_ST = ''  # standardized tree

    def std_let(self, node):

        # renaming node's name
        node.value = "gamma"
        node.children[0].value = "lambda"

        # swapping P and E
        node.children[0].children[1], node.children[1] = node.children[1], node.children[0].children[1]

    def std_where(self, node):

        # renaming node's name from where to gamma
        node.value = "gamma"

        # swap '=' node with 'P' node
        node.children[0], node.children[1] = node.children[1], node.children[0]

        # rename '=' node with lambda
        node.children[0].value = "lambda"

        # swapping P and E
        node.children[0].children[1], node.children[1] = node.children[1], node.children[0].children[1]

    def std_fcn_form(self, node):
        # create "=" node
        eq_node = TreeNode("=")

        # add node P to eq_node
        eq_node.add_child(node.children[0])

        # make eq_node as the current node for iteratively add lambda node.
        curr_node = eq_node

        for variable in node.children[1:-1]:
            # new lambda node
            lambda_node = TreeNode("lambda")

            # add a variable as the left child of lambda node.
            lambda_node.add_child(variable)

            # add the newly created lambda node to the current node
            curr_node.add_child(lambda_node)

            # make the newly created lambda node as the current node.
            # Inorder to add new lambda nodes.
            curr_node = lambda_node

        # add the node E to the last lambda node.
        curr_node.add_child(node.children[-1])

        node.value = eq_node.value
        node.children = eq_node.children

    def std_multi_param_fn(self, node):

        top_lambda = TreeNode(node.value)

        # make current node for iteratively add lambda nodes.
        curr_node = top_lambda

        for param in node.children[:-1]:

            # add the param node as the child of the lamda node.
            curr_node.add_child(param)

            # make a new lambda node
            lambda_node = TreeNode("lambda")

            # add the newly created lambda node as the child to current node.
            curr_node.add_child(lambda_node)

            # make the newly created lambda node as the current node.
            curr_node = lambda_node

        curr_node.value = node.children[-1].value
        curr_node.children = node.children[-1].children

        node.value = top_lambda.value
        node.children = top_lambda.children

    def std_within(self, node):
        # left "=" of within node
        left_eq_node = node.children[0]

        # right "=" of within node
        right_eq_node = node.children[1]

        # new "=" node
        top_eq_node = TreeNode("=")

        # add X2 node to top_eq_node.
        top_eq_node.add_child(right_eq_node.children[0])

        # new gamma node
        gamma_node = TreeNode("gamma")

        # add gamma node to top_eq_node as a right child.
        top_eq_node.add_child(gamma_node)

        # new lambda node
        lambda_node = TreeNode("lambda")

        # add lambda node to gamma node as a left child.
        gamma_node.add_child(lambda_node)

        # add E1 to gamma node as the  left child.
        gamma_node.add_child(left_eq_node.children[1])

        # add X1 to lambda node as left child
        lambda_node.add_child(left_eq_node.children[0])

        # add E2 to lambda node as right child
        lambda_node.add_child(right_eq_node.children[1])

        # update the node
        node.value = top_eq_node.value
        node.children = top_eq_node.children

    def std_at_sign(self, node):
        # top gamma
        top_gamma = TreeNode("gamma")

        # second gamma
        low_gamma = TreeNode("gamma")

        # adding top gamma's child
        top_gamma.add_child(low_gamma)
        top_gamma.add_child(node.children[2])

        # adding low gamma's child
        low_gamma.add_child(node.children[1])
        low_gamma.add_child(node.children[0])

        # update the @ node with standardized value, children.
        node.value = top_gamma.value
        node.children = top_gamma.children

    def std_and(self, node):
        # new '=' node
        eq_node = TreeNode("=")

        # comma node and tau node
        comma = TreeNode(",")
        tau = TreeNode("tau")

        # add variables and values into respective lists in order.
        for child in node.children:
            comma.add_child(child.children[0])
            tau.add_child(child.children[1])

        # adding children to "=" node.
        eq_node.add_child(comma)
        eq_node.add_child(tau)

        # update the standardized node.
        node.value = eq_node.value
        node.children = eq_node.children

    def std_rec(self, node):
        # extracting X from rec tree
        x_node = node.children[0].children[0]

        # extracting E from rec tree
        e_node = node.children[0].children[1]

        # creating necessary nodes
        eq_node = TreeNode("=")
        gamma_node = TreeNode("gamma")
        lambda_node = TreeNode("lambda")
        ystar_node = TreeNode("Y*")

        # adding children to lambda node
        lambda_node.add_child(x_node)
        lambda_node.add_child(e_node)

        # adding children to gamma node.
        gamma_node.add_child(ystar_node)
        gamma_node.add_child(lambda_node)

        # adding children to "=" node
        eq_node.add_child(x_node)
        eq_node.add_child(gamma_node)

        # updated rec node.
        node.value = eq_node.value
        node.children = eq_node.children

    def standardize_nodes(self, root):
        """
        This function standardize each node.
        :param root:
        :return:
        """
        for child in root.children:
            self.standardize_nodes(child)
        # standardize "let" node
        if root.value == "let" and root.children[0].value == "=":
            self.std_let(root)

        # standardize "where" node
        elif root.value == "where" and root.children[1].value == "=":
            self.std_where(root)

        # standardize "fcn_form" node
        elif root.value == "function_form":
            self.std_fcn_form(root)

        # standardize "multi parameter function node" node
        elif root.value == "lambda" and len(root.children) > 2:
            self.std_multi_param_fn(root)

        # standardize "within" node
        elif root.value == "within" and root.children[0].value == "=" and root.children[1].value == "=":
            self.std_within(root)

        # standardize "@" node
        elif root.value == "@":
            self.std_at_sign(root)

        # standardize simultaneous definitions
        elif root.value == "and" and len(root.children) >= 2 and root.children[0].value == "=" and root.children[1].value == "=":
            self.std_and(root)

        # standardize "rec" node
        elif root.value == "rec" and root.children[0].value == "=":
            self.std_rec(root)

    def build_ST(self, node, level=0):
        """
        This function prints the built ST tree from the stack.
        :param node:
        :param level:
        :return:
        """
        # level parameter is used for discriminate the levels of nodes in the AST
        self.output_ST += '.' * level + node.value + "\n"
        if len(node.children) == 0:
            return

        level += 1

        for child in node.children:
            self.build_ST(child, level)

    def standardize(self, stack):
        """
        This function take care of all the standardization tasks by invoking necessary functions.
        :param stack:
        :return:
        """
        self.std_tree = stack
        self.standardize_nodes(self.std_tree[0])
        self.build_ST(self.std_tree[0])



