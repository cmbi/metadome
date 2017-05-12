metadom-api is a REST wrapper around metadom.

# metadom-api
# Development

## Requirements

    Python 3.5.1

## Installation

Clone the repository and cd into the project folder:

    git clone https://github.com/cmbi/metadom-api.git
    cd metadom-api

Create a python virtual environment:

    pyvenv metadom-api

Install the dependencies:

    source metadom-api/bin/activate
    pip install -r requirements
    deactivate

Run the unit tests to check that everything works:

    UNDER CONSTRUCTION

# Implementation 
## Endpoints
| HTTP | Method URI | Action | Output type |
| :---: | :---: | :---: | :---: | 
| GET | http://[hostname]/metadom/api/chromosome/[ `locus` ] | Retrieve a list of loci that are aligned via meta-domain relation to this `locus` | `meta-domain mapping` |

### Input

A `locus` is a chromosomal position in the form of 'chr'[number]:position

### Output
A `meta-domain mapping` entry consists of:
* genes : a list of `gene` entries, which are present at this locus
* proteins : a list of `protein` entries, which are present at this locus
* domains : a list of protein `domain` entries, which are present at this locus
* meta-domain_linked_loci : a list of `locus` or loci, which are via a meta-domain relationship linked to this `locus`
* meta-domain_linked_genes : a list of `gene` entries, which are via a meta-domain relationship linked to this `locus`
* meta-domain_linked_proteins : a list of `protein` entries, which are via a meta-domain relationship linked to this `locus`

A `gene` entry consists of:
* position : the position in the gene that matches the locus
* strand
* ...


id: unique identifier for tasks. Numeric type.
title: short task description. String type.
description: long task description. Text type.
done: task completion state. Boolean type.



| Output type | Output |
| :---: | :--- |
| meta-domain mapping | <pre>{ <br>&nbsp; protein: <br>&nbsp;&nbsp;[<br>&nbsp;&nbsp;&nbsp; protein*, ... <br>&nbsp;&nbsp;], domain <br>} <pre/> |
| protein | <pre>{ <br>&nbsp; swiss-prot id:**str** <br>&nbsp;&nbsp;[<br>&nbsp;&nbsp;&nbsp; protein*, ... <br>&nbsp;&nbsp;], domain	} <pre/> |

\*: zero or many and \+: one or many

### Upcoming endpoints
| HTTP | Method URI | Action | Output type |
| :---: | :---: | :---: | :---: | 
| GET | http://[hostname]/metadom/api/gene/[gene name] | Retrieve a list of loci that are aligned via meta-domain relation to this locus |	<code>{ <br/><indent>	protein: [<protein>], domain	} <code/>|
| GET | http://[hostname]/metadom/api/gene/[gene name]/[cDNA position] | Retrieve a list of loci that are aligned via meta-domain relation to this locus |	<code>{ <br/><indent>	protein: [<protein>], domain	} <code/>|
| GET | http://[hostname]/metadom/api/protein/[swiss-prot id] | Retrieve a list of loci that are aligned via meta-domain relation to this locus |	<code>{ <br/><indent>	protein: [<protein>], domain	} <code/>|
| GET | http://[hostname]/metadom/api/protein/[swiss-prot id]/[protein position] | Retrieve a list of loci that are aligned via meta-domain relation to this locus |	<code>{ <br/><indent>	protein: [<protein>], domain	} <code/>|
| GET | http://[hostname]/metadom/api/domain/[Pfam id] | Retrieve a list of loci that are aligned via meta-domain relation to this locus |	<code>{ <br/><indent>	protein: [<protein>], domain	} <code/>|
| GET | http://[hostname]/metadom/api/domain/[Pfam id]/[domain position] | Retrieve a list of loci that are aligned via meta-domain relation to this locus |	<code>{ <br/><indent>	protein: [<protein>], domain	} <code/>|
