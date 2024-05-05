from parser import RPALParser
from Standardizer import Standardizer
from control_stack_machine import CSE_machine
import sys

# reading inputs from command line
arguments = sys.argv

# instantiate parser
parser = RPALParser()

# instantiate standardizer
standardizer = Standardizer()

# instantiate CSE machine
cse = CSE_machine()
if len(arguments) <= 3:
    if len(arguments) == 2:
        # input file from the command line argument
        input_file = arguments[1]

        parser.parse_file(input_file)
        standardizer.standardize(parser.stack)
        cse.execute(standardizer.std_tree[0])
        # print(cse.control_structure)  # for debugging

    elif len(arguments) == 3:
        # input file from the command line argument
        input_file = arguments[2]

        if arguments[1] == '-ast':
            parser.parse_file(input_file)
            print(parser.output_AST)
        elif arguments[1] == "-st":
            parser.parse_file(input_file)
            standardizer.standardize(parser.stack)
            print(standardizer.output_ST)
        else:
            print('Invalid Command: try <file_name> [<-ast>/<-st>] <RPAL source file>')
    else:
        print('Invalid Command: try <file_name> [<-ast>/<-st>] <RPAL source file>')
else:
    print('Invalid Command: try <file_name> [<-ast>/<-st>] <RPAL source file>')
