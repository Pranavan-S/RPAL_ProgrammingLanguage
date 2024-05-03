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

if len(arguments) >= 2:
    # input file from the command line argument
    input_file = arguments[1]
    if len(arguments) == 3:
        if arguments[2] == '-ast':
            parser.parse_file(input_file)
            print(parser.output_AST)
        elif arguments[2] == "-st":
            parser.parse_file(input_file)
            standardizer.standardize(parser.stack)
            print(standardizer.output_ST)
        else:
            print("Invalid Command!")
    else:
        parser.parse_file(input_file)
        standardizer.standardize(parser.stack)
        cse.label_lambda(standardizer.std_tree[0])
        cse.generate_control_structure(standardizer.std_tree[0], 0)
        cse.run_program()
        # cse.run_program()
        # # cse.run_program()
        print(cse.control_structure)
else:
    print("Invalid Command!")
