# Lockfiles graph generator

This script generates Cypher query from `package-lock.json` file. Generated query could then be pasted in Neo4j Cypher shell and executed.

## Usage
`python main.py <path to package-lock.json> <export file>`

## Example
`python main.py ../test/package-lock.json generated.cypher`

## Generated file 
Generated file will look something like this
```cypher
CREATE (:Dependency {name: "argparse", version: "2.0.1", integrity: "sha512-8+9WqebbFzpX9OR+Wa6O29asIogeRMzcGtAINdpMHHyAg10f05aSFVBbcEqGf/PXw1EjAZ+q2/bEBg3DvurK3Q=="})
CREATE (:Dependency {name: "invariant", version: "2.2.4", integrity: "sha512-phJfQVBuaJM5raOpJjSfkiD6BpbCE4Ns//LaXl6wGYtUBY83nWS6Rf9tXm2e8VaK60JEjYldbPif/A2B1C2gNA=="})
CREATE (:Dependency {name: "js-tokens", version: "4.0.0", integrity: "sha512-RdJUflcE3cUzKiMqQgsCu06FPu9UdIJO0beYbPhHN4k6apgJtifcoCtT9bcxOpYBtpD2kCM6Sbzg4CausW/PKQ=="})
```
