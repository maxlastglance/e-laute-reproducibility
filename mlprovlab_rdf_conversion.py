import json
import re
import argparse
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS

# Define namespaces
PROV = Namespace("http://www.w3.org/ns/prov#")
EX = Namespace("http://example.org/")

# Create a new RDF graph
g = Graph()
g.bind("prov", PROV)
g.bind("ex", EX)

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Process a JSON file and output RDF in Turtle format.")
parser.add_argument("input_json", type=str, help="Path to the input JSON file")
parser.add_argument("output_ttl", type=str, help="Path to the output Turtle (.ttl) file")
args = parser.parse_args()

# Load the JSON data
with open(args.input_json, "r") as f:
    data = json.load(f)

# Helper function to create valid URIs
def create_uri(base, suffix):
    suffix = re.sub(r'\W+', '_', suffix)  # Replace non-alphanumeric characters with underscores
    return URIRef(base + suffix)

# Process each epoch in the JSON data
for epoch in data["epochs"]:
    # Create an activity for the epoch
    epoch_start_time = epoch["kernel_start_time"]
    epoch_uri = create_uri("http://example.org/epoch/", epoch_start_time)
    g.add((epoch_uri, RDF.type, PROV.Activity))
    g.add((epoch_uri, PROV.startedAtTime, Literal(epoch_start_time)))
    if "time" in epoch:
        g.add((epoch_uri, PROV.endedAtTime, Literal(epoch["time"])))
    g.add((epoch_uri, PROV.wasAssociatedWith, Literal(epoch["user_agent"])))

    # Adding used data for the epoch
    for used_data_url in data.get("used_data", []):
        used_data_entity = create_uri("http://example.org/used_data/", used_data_url)
        g.add((used_data_entity, RDF.type, PROV.Entity))
        g.add((used_data_entity, RDFS.label, Literal(f"Used Data URL: {used_data_url}")))
        g.add((epoch_uri, PROV.used, used_data_entity))

    # Add attributes to the activity (not used by PROV directly, but can be helpful)
    g.add((epoch_uri, RDFS.label, Literal(f"Epoch starting at {epoch_start_time}")))

    # Adding language and version as entities
    language_entity = create_uri("http://example.org/language/", epoch["language"])
    g.add((language_entity, RDF.type, PROV.Entity))
    g.add((language_entity, RDFS.label, Literal(f"Language: {epoch['language']}")))
    g.add((epoch_uri, PROV.used, language_entity))

    language_version_entity = create_uri("http://example.org/language_version/", epoch["language_version"])
    g.add((language_version_entity, RDF.type, PROV.Entity))
    g.add((language_version_entity, RDFS.label, Literal(f"Language Version: {epoch['language_version']}")))
    g.add((epoch_uri, PROV.used, language_version_entity))

    # Adding kernel and version as entities
    kernel_entity = create_uri("http://example.org/kernel/", epoch["kernel"])
    g.add((kernel_entity, RDF.type, PROV.Entity))
    g.add((kernel_entity, RDFS.label, Literal(f"Kernel: {epoch['kernel']}")))
    g.add((epoch_uri, PROV.used, kernel_entity))

    kernel_version_entity = create_uri("http://example.org/kernel_version/", epoch["kernel_version"])
    g.add((kernel_version_entity, RDF.type, PROV.Entity))
    g.add((kernel_version_entity, RDFS.label, Literal(f"Kernel Version: {epoch['kernel_version']}")))
    g.add((epoch_uri, PROV.used, kernel_version_entity))

    # Add modules used as entities
    for module, details in epoch["modules"].items():
        module_uri = create_uri("http://example.org/module/", module)
        g.add((module_uri, RDF.type, PROV.Entity))
        g.add((module_uri, RDFS.label, Literal(f"Module: {module}")))
        if details["version"]:
            module_version_entity = create_uri("http://example.org/module_version/", details["version"])
            g.add((module_version_entity, RDF.type, PROV.Entity))
            g.add((module_version_entity, RDFS.label, Literal(f"Module Version: {details['version']}")))
            g.add((module_uri, PROV.hadPrimarySource, module_version_entity))
        g.add((epoch_uri, PROV.used, module_uri))

    # Process each execution_data entry
    for exec_data in epoch["execution_data"]:
        exec_uri = create_uri("http://example.org/execution/", str(exec_data["execution_count"]))
        g.add((exec_uri, RDF.type, PROV.Activity))
        g.add((exec_uri, PROV.used, epoch_uri))

        # Add code as an entity
        code_entity = create_uri("http://example.org/code/", str(exec_data["execution_count"]))
        code_literal = Literal(exec_data["code"])
        g.add((code_entity, RDF.type, PROV.Entity))
        g.add((code_entity, PROV.value, code_literal))
        g.add((exec_uri, PROV.generated, code_entity))

        # Adding used data in execution data
        for used_data_url in exec_data.get("used_data", []):
            used_data_entity = create_uri("http://example.org/used_data/", used_data_url)
            g.add((used_data_entity, RDF.type, PROV.Entity))
            g.add((used_data_entity, RDFS.label, Literal(f"Used Data URL: {used_data_url}")))
            g.add((exec_uri, PROV.used, used_data_entity))

        # Add imports as entities
        for imp in exec_data.get("imports", []):
            import_uri = create_uri("http://example.org/import/", imp)
            g.add((import_uri, RDF.type, PROV.Entity))
            g.add((import_uri, RDFS.label, Literal(f"Import: {imp}")))
            g.add((exec_uri, PROV.used, import_uri))

        # Add dependencies as entities
        for dep in exec_data.get("dependencies", []):
            dep_uri = create_uri("http://example.org/dependency/", dep)
            g.add((dep_uri, RDF.type, PROV.Entity))
            g.add((dep_uri, RDFS.label, Literal(f"Dependency: {dep}")))
            g.add((exec_uri, PROV.used, dep_uri))

# Serialize the graph to RDF format (Turtle in this case) and save to a file
rdf_data = g.serialize(format="turtle")
with open(args.output_ttl, "w") as f:
    f.write(rdf_data)
