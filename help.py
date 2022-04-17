#!/usr/bin/python


import sys


def analyze_params() -> None:
    # check if there is at least one parameter
    if len(sys.argv) < 2:
        print("\033[33m\nLock file path was not specified \033[0m\n")
        print("For more info run -h or --help\n")
        exit(1)
        
    # print help    
    elif  '-h' in sys.argv or  '--help' in sys.argv:
        print("\nThis script will generate a neo4j query to create a graph of dependencies from package-lock.json")
        print("\nUsage: python main.py <path to package-lock.json> <export file>")
        print("\nExample: python main.py package-lock.json package-lock.cypher") 
        print("\nThe export file will be overwritten if it exists, defalts to output.cypher\n")
        exit(1)

