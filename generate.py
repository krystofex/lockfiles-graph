#!/usr/bin/python


from operator import itemgetter
from typing import Union 


def format_integrity(integrity: str) -> str:
    return integrity.replace("//", "__")

def create_nodes_query(all_dependencies: list, all_relations: dict) -> Union[str, list]:
    output: str = ""
    all_used_variables: list = []
    
    # create nodes
    for dependency in all_dependencies:
        name, version, integrity = itemgetter('name', 'version', 'integrity')(dependency) 
            
        # if the dependency has a relation, set its integrity as a cypher variable
        node_var_name: str = ""
        if [i for i in all_relations if i['from'] == integrity or i['to'] == integrity] != []:
            node_var_name = integrity
            all_used_variables.append(node_var_name)
        
        # create node cypher query
        output  += "CREATE (%s:Dependency {name: \"%s\", version: \"%s\", integrity: \"%s\"})\n" % (node_var_name,  name, version,integrity)
    return output, all_used_variables


def create_relations_query(all_relations: dict) -> str:
    output: str = ""
    for relation in all_relations:
        output += "CREATE (%s)-[:DEPENDS_ON]->(%s)\n" % (relation['from'], relation['to'])
    return output


def optimize_cypher_variables(query: str, all_used_variables: list) -> str:
    # replace integrity variables with numbers - shorter cypher query
    output: str = query
    for index, value in enumerate(all_used_variables):
        output = output.replace(value, "var" + str(index))
    return output