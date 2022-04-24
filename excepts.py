#!/usr/bin/python


import os
from functions import get_path_to_directory


def read_package_lock_error():
    files: list = os.listdir(get_path_to_directory() + "/")

    print("\033[33m")
    if not "package-lock.json" in files:
        if "yarn.lock" in files:
            print("convert yarn.lock to package-lock.json first")
            print("\033[0mrun: npx synp --source-file <path to yarn.lock>")
        else:
            print("package-lock.json not found")
    elif not os.access(get_path_to_directory() + "/package-lock.json", os.R_OK):
        print("package-lock.json is not readable")
    else:
        print("Failed to load package-lock.json file")
    print("\033[0m\n")
    exit(1)
