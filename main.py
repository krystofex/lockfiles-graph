#!/usr/bin/python


import sys
import json 
from help import *
from operator import itemgetter

# analyze parameters with which the script was called (--help, package-lock path, output path)
analyze_params()

# read lock file
try:
    lockfile = open(sys.argv[1], 'r')
except:
    print("\033[33m\nWrong path \033[0m\n")
    exit(1)
    
# parse lock file
lockfile_content = json.loads(lockfile.read())
all_dependencies: list = [] # add all dependencies from lock file to this list
all_relations: list = []  # all relations between dependencies in format of [{"from": "integrity", "to": "integrity"}]
      
    

def iterate_dependencies(dependencies: dict) -> None:
    for key, value in dependencies.items(): 
        name, [version, integrity] = key, itemgetter('version', 'integrity')(value)  # destruct
        
        # if dependency is not in the all_dependencies list, add it
        if [i for i in all_dependencies if i['integrity'] == integrity] == []:
            all_dependencies.append({"name": name, "version": version, "integrity": integrity})
        
        # if dependency has dependencies, add them to the list recursively
        if 'dependencies' in value:
            iterate_dependencies(value['dependencies'])  # recursive call

     
# create a node for each dependency
iterate_dependencies(lockfile_content['dependencies'])


# final output to the file
output: str = ""
   
all_used_variables: list = []
   
# create nodes
for dependency in all_dependencies:
    name, version, integrity = itemgetter('name', 'version', 'integrity')(dependency) 
        
    # if the dependency has a relation, set its integrity as a cypher variable
    node_var_name: str = ""
    if [i for i in all_relations if i['from'] == integrity or i['to'] == integrity] != []:
        node_var_name = "`" + integrity.replace("//", "__") + "`"
        all_used_variables.append(node_var_name)
     
    # create node cypher query
    output  += "CREATE (%s:Dependency {name: \"%s\", version: \"%s\", integrity: \"%s\"})\n" % (node_var_name,  name, version,integrity)
     

# todo: create relations   

# replace integrity variables with numbers - shorter cypher query
for index, value in enumerate(all_used_variables):
    output = output.replace(value, "var" + str(index))
    
    
# write output to the file
output_path: str = sys.argv[2] if len(sys.argv) > 2 else "output.cypher"
output_file = open(output_path, "w")
output_file.write(output)
output_file.close()

print("\n\033[32m\nOutput file created at %s\n\033[0m\n" % output_path)
