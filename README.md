# E-Laute Reproducibility

## Project Goal

In the E-Laute project, we focus on the analysis of medieval lute tablatures by applying various models to extract information from these musical pieces. At this early stage of the project, our primary aim is to develop a robust pipeline for integrating data from different sources, facilitating the execution of reproducible experiments.

This document addresses the reproducibility aspect of our work. After a thorough review of existing provenance tracking libraries, we chose to use MLProvLab, developed by Sheeba Samuel. MLProvLab is a Jupyter Lab extension designed to track all processes within notebooks. Upon completing a process, the extension allows for the export of data in JSON format. This exported JSON data can be processed using our custom script, `mlprovlab_rdf_conversion.py`, which converts the JSON into a Turtle file in the PROV-O format. This format is suitable for use in graph databases such as GraphDB. Below are some sample SPARQL queries that can be executed on the provenance data:

### Query: All Activities with Corresponding Code

```
PREFIX prov: <http://www.w3.org/ns/prov#>

SELECT ?activity ?code
WHERE {
  ?activity a prov:Activity ;
            prov:generated ?codeEntity .
  ?codeEntity prov:value ?code .
}
```

### Query: Involved Agents

```
PREFIX prov: <http://www.w3.org/ns/prov#>

SELECT ?activity ?agent
WHERE {
  ?activity a prov:Activity ;
            prov:wasAssociatedWith ?agent .
}
```

### Query: Used Entities

```
PREFIX prov: <http://www.w3.org/ns/prov#>

SELECT ?activity ?usedEntity
WHERE {
  ?activity a prov:Activity ;
            prov:used ?usedEntity .
}
```

### Query: Used Entities Sorted by Activity ID

```
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?activity ?usedEntity
WHERE {
  ?activity a prov:Activity ;
            prov:used ?usedEntity .
  BIND(xsd:integer(REPLACE(STR(?activity), "http://example.org/execution/", "")) AS ?activityID)
}
ORDER BY ?activityID
```

## Provenance Documentation

Each Jupyter notebook cell corresponds to an individual `prov:Activity`, and each dependency used within the cells is represented as an `prov:Entity`. These entities are linked through the `prov:used` attribute. The `prov:wasAssociatedWith` attribute captures the agent responsible for executing these Jupyter notebooks, typically the computational engine or the user.

For comprehensive provenance documentation, ensure that the experiment is running when you activate MLProvLab. This allows for the complete documentation of the process in one instance. The generated provenance data can then be transformed using the provided conversion script.

## Guide to Use

1. Complete your experiments within Jupyter Lab.
2. Install MLProvLab:

   ```bash
   pip install mlprovlab
   ```

3. Launch Jupyter Lab:

   ```bash
   python3 jupyter lab
   ```

4. Execute the cells in your notebook.
5. Click "Export" in the MLProvLab tab and download the JSON file containing the provenance data.
6. Convert the JSON to Turtle format using the provided script:

   ```bash
   python3 mlprovlab_rdf_conversion.py path/to/input.json path/to/output.ttl
   ```

This documentation will help ensure that all experimental processes are tracked and reproducible, aiding in the validation and verification of results.
