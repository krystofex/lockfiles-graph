#!/usr/bin/python

import sys
import json

if len(sys.argv) < 2:
    print("\033[33m path was not specified\033[0m")
    exit(1)

path: str = sys.argv[1]  # path to the file
lockfile = open(path, 'r')
lockfile_content = json.loads(lockfile.read())
dependecies = lockfile_content['dependencies']

#  create all dependencies
output: str = "CALL {\n"
for dependency in dependecies:
    version: str = dependecies[dependency]['version']
    integrity: str = dependecies[dependency]['integrity']
    resolved: str = dependecies[dependency]['resolved']
    output += "\tCREATE (:Dependency {name: \"%s\", version: \"%s\", integrity: \"%s\", resolved: \"%s\"})\n" % (
        dependency, version, integrity, resolved)
output += "}\n"

# create relations
for dependency in dependecies:
    # if there is a requires key
    if "requires" in dependecies[dependency]:
        for dep_dependency in dependecies[dependency]['requires']:
            dep_dependency_version: str = dependecies[dependency]['requires'][dep_dependency]

            output += "CALL {\n"
            output += "\tMATCH (d1:Dependency {integrity: \"%s\"}), (d2:Dependency {name: \"%s\"})\n\t" % (
                dependecies[dependency]["integrity"], dep_dependency)

            # ^
            if dep_dependency_version[0] == "^":
                dep_dependency_version = dep_dependency_version[1:].split(".")[
                    0]
                output += "WHERE d2.version STARTS WITH \"%s\"" % (
                    dep_dependency_version)
            # ~
            elif dep_dependency_version[0] == "~":
                dep_dependency_version = dep_dependency_version[1:].split(".")[
                    0:2]
                output += "WHERE d2.version STARTS WITH \"%s\"" % (
                    dep_dependency_version)
            # exact version
            else:
                output += "WHERE d2.version = \"%s\"" % (
                    dep_dependency_version)
            output += "\n\tCREATE (d1)-[:REQUIRES]->(d2)\n}\n"


output_file = open("output.cypher", "w")
output_file.write(output)
output_file.close()
