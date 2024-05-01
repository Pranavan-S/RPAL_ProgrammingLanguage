# from myrpal import RPALParser

from LexicalAnalyzer import Tokenizer
from TreeNodes import TreeNode
from Tokens import Token
import sys



def pre_order(root):
    if not root.children:
        print(root.value)
        return
    print(root.value)
    pre_order(root.children[0])
    pre_order(root.children[1])

class Standardizer:
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

        curr_node.add_child(node.children[-1])

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




