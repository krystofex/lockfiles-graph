#!/usr/bin/python


from re import I
import sys
import json
from operator import itemgetter
import os


def format_integrity(integrity: str) -> str:
    return "`" + integrity.replace("//", "__") + "`"


class Generator:
    def __init__(self) -> None:
        self.generated_string: str = ""
        self.all_relations: list[dict] = []
        self.all_nodes: list[dict] = []

        path_to_directory = sys.argv[1][:-1] if sys.argv[1].endswith(
            "/") else sys.argv[1]

        try:
            files: list = os.listdir(path_to_directory + "/")
        except:
            print("\033[33m\nFailed to open directory\033[0m\n")
            exit(1)

        # read package-lock file
        try:
            package_lock_file = open(
                path_to_directory + "/package-lock.json", 'r')
        except:
            print("\033[33m")
            if not "package-lock.json" in files and "yarn.lock" in files:
                print("convert yarn.lock to package-lock.json first")
                print("\033[0mrun: npx synp --source-file <path to yarn.lock>")
            elif not "package-lock.json" in files:
                print("package-lock.json not found")
            elif not os.access(path_to_directory + "/package-lock.json", os.R_OK):
                print("package-lock.json is not readable")
            else:
                print("Failed to load package-lock.json file")
            print("\033[0m\n")
            exit(1)

        # read package.json file
        try:
            package_json_file = open(path_to_directory + "/package.json", 'r')
        except:
            print("\033[33m\nFailed to load package.json file\033[0m\n")
            exit(1)

        # parse package-lock.json file
        try:
            self.package_lock_content = json.loads(package_lock_file.read())
        except:
            print("\033[33m\nError while parsing package-lock.json\033[0m\n")
            exit(1)

        # parse package.json file
        try:
            self.package_json_content = json.loads(package_json_file.read())
        except:
            print("\033[33m\nError while parsing package.json\033[0m\n")
            exit(1)

    def get_all_nodes(self, dependencies) -> None:
        if dependencies is None:
            dependencies = self.package_lock_content['dependencies']

        for key, value in dependencies.items():
            name, [version, integrity] = key, itemgetter(
                'version', 'integrity')(value)  # destruct
            is_dev_dependency: bool = name in self.package_json_content["devDependencies"]
            is_main_dependency: bool = name in self.package_json_content["dependencies"]

            # if dependency is not in the all_dependencies list, add it
            if [i for i in self.all_nodes if i['integrity'] == integrity] == []:
                self.all_nodes.append(
                    {"name": name, "version": version, "integrity": integrity,
                     "is_dev_dependency": is_dev_dependency,
                     "is_main_dependency": is_main_dependency or is_dev_dependency
                     })

            # if dependency has dependencies, add them to the list recursively
            if 'dependencies' in value:
                self.get_all_nodes(value['dependencies'])  # recursive call

    def get_all_relations(self, dependencies) -> None:
        if dependencies is None:
            dependencies = self.package_lock_content['dependencies']

        for _, value in dependencies.items():
            # if value isn't in all_relations list, add it to the list
            def append_value(value: dict) -> None:
                if [i for i in self.all_relations if i == value] == []:
                    self.all_relations.append(value)

            if "requires" in value and "dependencies" in value:
                for name in value["requires"]:
                    if name in value["dependencies"]:
                        append_value({"from": value["integrity"], "to": (
                            value if name in value["dependencies"] else self.package_lock_content)["dependencies"][name]["integrity"]})
                    else:
                        append_value(
                            {"from": value["integrity"], "to": self.package_lock_content["dependencies"][name]["integrity"]})
            elif "requires" in value:
                for name in value["requires"]:
                    if name in self.package_lock_content["dependencies"]:
                        append_value(
                            {"from": value["integrity"], "to": self.package_lock_content["dependencies"][name]["integrity"]})

            # if dependency has dependencies, add them to the list recursively
            if 'dependencies' in value:
                self.get_all_relations(value['dependencies'])  # recursive call

    def create_nodes_query(self) -> None:
        # create nodes
        for dependency in self.all_nodes:
            name, version, integrity, is_main_dependency, is_dev_dependency = itemgetter(
                'name', 'version', 'integrity', 'is_main_dependency', 'is_dev_dependency')(dependency)
            # create node cypher query
            self.generated_string += "CREATE (%s:Dependency%s%s {name: \"%s\", version: \"%s\", integrity: \"%s\"})\n" % (
                format_integrity(integrity),
                ":MainDependency" if is_main_dependency else "", ":DevDependency" if is_dev_dependency else "", name, version, integrity)

    def create_relations_query(self) -> None:
        for relation in self.all_relations:
            self.generated_string += "CREATE (%s)-[:DEPENDS_ON]->(%s)\n" % (
                format_integrity(relation['from']), format_integrity(relation['to']))

    def optimize_query(self) -> None:
        # replace integrity variables with numbers -> shorter cypher query
        for index, value in enumerate(self.all_nodes):
            self.generated_string = self.generated_string.replace(
                format_integrity(value["integrity"]), "var" + str(index))
