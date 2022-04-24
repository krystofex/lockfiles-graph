
#!/usr/bin/python


import json
from operator import itemgetter
from excepts import read_package_lock_error
from functions import get_path_to_directory


class Generator:

    def __init__(self) -> None:
        self.generated_string: str = ""
        self.all_relations: list[dict] = []
        self.all_nodes: list[dict] = []
        self.integrities: list = []

        # read package-lock file
        try:
            package_lock_file = open(
                get_path_to_directory() + "/package-lock.json", 'r')
        except:
            read_package_lock_error()

        # read package.json file
        try:
            package_json_file = open(
                get_path_to_directory() + "/package.json", 'r')
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
            is_main_dependency: bool = name in self.package_json_content[
                "dependencies"] or is_dev_dependency

            # if dependency is not in the all_dependencies list, add it
            if [i for i in self.all_nodes if i['integrity'] == integrity] == []:
                self.all_nodes.append(
                    {"name": name, "version": version, "integrity": integrity,
                     "is_dev_dependency": is_dev_dependency,
                     "is_main_dependency": is_main_dependency
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
        for index, dependency in enumerate(self.all_nodes):
            self.integrities.append(dependency["integrity"])

            name, version, integrity, is_main_dependency, is_dev_dependency = itemgetter(
                'name', 'version', 'integrity', 'is_main_dependency', 'is_dev_dependency')(dependency)
            # create node cypher query
            self.generated_string += "CREATE (%s:Dependency%s%s {name: \"%s\", version: \"%s\", integrity: \"%s\"})\n" % (
                "var" + str(index),
                ":MainDependency" if is_main_dependency else "", ":DevDependency" if is_dev_dependency else "", name, version, integrity)

    def create_relations_query(self) -> None:
        for relation in self.all_relations:
            self.generated_string += "CREATE (%s)-[:DEPENDS_ON]->(%s)\n" % (
                "var" + str(self.integrities.index(relation['from'])), "var"+str(self.integrities.index(relation['to'])))
