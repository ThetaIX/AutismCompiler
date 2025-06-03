from symmantic import Parser
from interpretator import interpret_rpn
from lexer import Lexer
import argparse
import sys

def read_source_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Set up command line argument parser
    parser = argparse.ArgumentParser(description='Autism programming language compiler')
    parser.add_argument('source_file', nargs='?', help='Path to the source code file')

    args = parser.parse_args()

    # Default example code if no file is provided
    sample = '''int wiseTree;
    wiseTree = 65;
    int joker;
    joker = 4;
    output wiseTree + joker;
    '''

    # If a source file is provided, read from it instead of using the sample code
    if args.source_file:
        if args.source_file.endswith('.aul'):
            source_code = read_source_file(args.source_file)
        else:
            print("Error: File must have .aul extension")
            sys.exit(1)
    else:
        source_code = sample
        print("No source file provided. Running with example code...")
    #print(source_code)
    # Parse and interpret the code
    parser = Parser(Lexer())
    rpn = parser.parse(source_code)
    # parser.lexer.run(source_code)
    # print(rpn)
    interpret_rpn(rpn, parser.symtable)