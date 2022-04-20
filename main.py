#!/usr/bin/python


import sys
from help import analyze_params
from generator import Generator

# analyze parameters with which the script was called (--help, package-lock path, output path)
analyze_params()

generator = Generator()

generator.get_all_relations(None)
generator.get_all_nodes(None)
generator.create_nodes_query()
generator.create_relations_query()
generator.optimize_query()


# write output to the file
output_path: str = sys.argv[2] if len(sys.argv) > 2 else "output.cypher"
output_file = open(output_path, "w")
output_file.write(generator.generated_string)
output_file.close()

print("\n\033[32m\nOutput file created at %s\n\033[0m\n" % output_path)
