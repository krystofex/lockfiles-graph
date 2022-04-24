#!/usr/bin/python


import sys


def get_path_to_directory() -> str:
    return sys.argv[1][:-1] if sys.argv[1].endswith("/") else sys.argv[1]
