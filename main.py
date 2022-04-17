#!/usr/bin/python


import sys
import json 
from help import analyze_params
from operator import itemgetter 
from generate import create_nodes_query, optimize_cypher_variables, create_relations_query

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
all_relations: list = []  # all relations between dependencies in format of [{"from": "integrity", "to": "integrity"}]
all_dependencies: list = [] # add all dependencies from lock file to this list
    
    
def iterate_dependencies(dependencies: dict) -> None:
    for key, value in dependencies.items(): 
        global all_dependencies
        name, [version, integrity] = key, itemgetter('version', 'integrity')(value)  # destruct
        
        # if dependency is not in the all_dependencies list, add it
        if [i for i in all_dependencies if i['integrity'] == integrity] == []:
            all_dependencies.append({"name": name, "version": version, "integrity": integrity})
        
        # if dependency has dependencies, add them to the list recursively
        if 'dependencies' in value:
            iterate_dependencies(value['dependencies'])  # recursive call    


# create a node for each dependency
iterate_dependencies(lockfile_content['dependencies'])

 
     

# todo: create relations

def iterate_relations(dependencies: dict) -> None:
    for _, value in dependencies.items(): 
        global all_relations 
        
        # if value isn't in all_relations list, add it to the list
        def append_value(value: dict) -> None:
            if [i for i in all_relations if i == value] == []:
                    all_relations.append(value)      
        
        if "requires" in value and "dependencies" in value:
            for name in value["requires"]:
                if name in value["dependencies"]:
                    append_value({"from": value["integrity"], "to": value["dependencies"][name]["integrity"]})
                else:
                    append_value({"from": value["integrity"], "to": lockfile_content["dependencies"][name]["integrity"]})
        elif "requires" in value:
            for name in value["requires"]: 
                if name in lockfile_content["dependencies"]:
                    append_value({"from": value["integrity"], "to": lockfile_content["dependencies"][name]["integrity"]})       
            
        # if dependency has dependencies, add them to the list recursively
        if 'dependencies' in value:
            iterate_relations(value['dependencies'])  # recursive call    


# create a node for each dependency
iterate_relations(lockfile_content['dependencies'])
output: str = ""
relations_output: str = create_relations_query(all_relations)
tmp_output, all_used_variables = create_nodes_query(all_dependencies, all_relations)
output += tmp_output
output += relations_output

output = optimize_cypher_variables(output, all_used_variables)
    
     
# write output to the file
output_path: str = sys.argv[2] if len(sys.argv) > 2 else "output.cypher"
output_file = open(output_path, "w")
output_file.write(output)
output_file.close()

print("\n\033[32m\nOutput file created at %s\n\033[0m\n" % output_path)
