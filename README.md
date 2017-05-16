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
| GET | http://[hostname]/metadom/api/chr/[ `locus` ] | Retrieve a list of loci that are aligned via meta-domain relation to this `locus` | `meta-domain mapping` |

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
* position : the position in the gene that matches the locus. Numeric type
* strand : '+' or '-'. String type
* gene_name : the name of the gene wherein this domain occurs. String type
* gencode_transcription_id : gencode_transcription_id. String type
* gencode_translation_name : gencode_translation_name. String type
* gencode_gene_id : gencode_gene_id. String type
* havana_gene_id : havana_gene_id. String type
* havana_translation_id : havana_translation_id. String type

A `protein` entry consists of:
* swissprot_position : the position in the gene that matches the locus
* swissprot_id : uniprot_ac. String type
* swissprot_name : uniprot_name. String type

A `domain` entry consists of:
* pfam_domain_consensus_position : the consensus position of the Pfam domain where this position is aligned to. Numeric type
* pfam_domain_name : the name of the domain. String type
* pfam_domain_id : the domain identifier. String type
* interpro_id : the interpro identifier. String type
* gene_name : the name of the gene wherein this domain occurs. String type
* swissprot_id : uniprot_ac. String type
* swissprot_start_pos : domain_uniprot_start_pos. Numeric type
* swissprot_end_pos : domain_uniprot_end_pos. Numeric type
* swissprot_length : domain_result["region_length"]. Numeric type
* chromosome : domain_result["chromosome"]. String type
* chr_region : domain_result["chromosome_positions"]. List of binary tuples of numeric types

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
