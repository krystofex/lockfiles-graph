#!/usr/bin/python


import sys
import json 
from operator import itemgetter
from typing import Union

 
def format_integrity(integrity: str) -> str:
    return "`" + integrity.replace("//", "__") + "`"
 

class Generator:
    def __init__(self) -> None:
        self.generated_string: str = ""
        self.all_used_variables: list[dict] = []
        self.all_relations: list[dict] = []
        self.all_nodes: list[dict] = []
        
        # read lock file
        try:
            lockfile = open(sys.argv[1], 'r')
        except:
            print("\033[33m\nWrong path \033[0m\n")
            exit(1)
            
        # parse file to json
        try:
            self.lockfile_content = json.loads(lockfile.read())
        except:
            print("\033[33m\Error while parsing the file \033[0m\n")
            exit(1)
    
    def get_all_nodes(self) -> None:
        def iterate_dependencies(dependencies: dict) -> None:
            for key, value in dependencies.items(): 
                name, [version, integrity] = key, itemgetter('version', 'integrity')(value)  # destruct
                
                # if dependency is not in the all_dependencies list, add it
                if [i for i in self.all_nodes if i['integrity'] == integrity] == []:
                    self.all_nodes.append({"name": name, "version": version, "integrity": integrity})
                
                # if dependency has dependencies, add them to the list recursively
                if 'dependencies' in value:
                    iterate_dependencies(value['dependencies'])  # recursive call    


        # create a node for each dependency
        iterate_dependencies(self.lockfile_content['dependencies'])
    
    
    def get_all_relations(self) -> None:
        def iterate_relations(dependencies: dict) -> None:
            for _, value in dependencies.items():             
                # if value isn't in all_relations list, add it to the list
                def append_value(value: dict) -> None:
                    if [i for i in self.all_relations if i == value] == []:
                        self.all_relations.append(value)      
                
                if "requires" in value and "dependencies" in value:
                    for name in value["requires"]:
                        if name in value["dependencies"]: 
                            append_value({"from": value["integrity"], "to": value["dependencies"][name]["integrity"]})
                        else:
                            append_value({"from": value["integrity"], "to": self.lockfile_content["dependencies"][name]["integrity"]})
                elif "requires" in value:
                    for name in value["requires"]: 
                        if name in self.lockfile_content["dependencies"]:
                            append_value({"from": value["integrity"], "to": self.lockfile_content["dependencies"][name]["integrity"]})       
                    
                # if dependency has dependencies, add them to the list recursively
                if 'dependencies' in value:
                    iterate_relations(value['dependencies'])  # recursive call    

        # create a node for each dependency
        iterate_relations(self.lockfile_content['dependencies'])
     

    
    def create_nodes_query(self) -> None:
        # create nodes
        for dependency in self.all_nodes:
            name, version, integrity = itemgetter('name', 'version', 'integrity')(dependency) 
                
            # if the dependency has a relation, set its integrity as a cypher variable
            node_var_name: str = ""
            if [i for i in self.all_relations if i['from'] == integrity or i['to'] == integrity] != []:
                node_var_name = format_integrity(integrity)
                self.all_used_variables.append(node_var_name)
            
            # create node cypher query
            self.generated_string  += "CREATE (%s:Dependency {name: \"%s\", version: \"%s\", integrity: \"%s\"})\n" % (node_var_name,  name, version,integrity)


    
    def create_relations_query(self) -> None: 
        for relation in self.all_relations:
            self.generated_string += "CREATE (%s)-[:DEPENDS_ON]->(%s)\n" % (format_integrity(relation['from']) ,format_integrity(relation['to']))

    
    def optimize_query(self) -> None:
        # replace integrity variables with numbers -> shorter cypher query
        for index, value in enumerate(self.all_used_variables):
            self.generated_string = self.generated_string.replace(value, "var" + str(index))
        