The metadom-api is a REST wrapper around metadom.

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
All endpoints retrieve the information that is aligned to the position of interest via meta-domain relation, if available.

| HTTP | Method URI | Output type |
| :---: | :---: | :---: |
| GET | [hostname]/metadom/api/chr/`<str:chr>`/`<int:position>` | `meta-domain mapping` |
| GET | [hostname]/metadom/api/gene/`<str:gencode_translation_name>`/`<int:position>` | `meta-domain mapping` |
| GET | [hostname]/metadom/api/protein/`<str:uniprot_ac>`/`<int:position>` | `meta-domain mapping` |
| GET | [hostname]/metadom/api/domain/`<str:Pfam_id>`/`<int:position>` | `meta-domain mapping` |

### Input

* `<str:chr>` : ['1-23', 'X'], excluding 'Y'. String type.
* `<str:gencode_translation_name>` : the gencode translation name. String type
* `<str:uniprot_ac>` : the uniprot Accession Code. String type
* `<str:Pfam_id>` : the Pfam domain identifier. String type
* `<int:position>` : position on the chromosome, cDNA of the gene, sequence position of the protein, or pfam domain consensus position. Depending on the parent type. Numeric type.

### Output
A `meta-domain mapping` entry consists of:
* `locus` : information about the locus
* genes : a list of `gene` entries, which are present at this locus
* proteins : a list of `protein` entries, which are present at this locus
* domains : a list of protein `domain` entries, which are present at this locus
* meta-domain_linked_loci : a list of `locus` or loci, which are via a meta-domain relationship linked to this `locus`
* meta-domain_linked_genes : a list of `gene` entries, which are via a meta-domain relationship linked to this `locus`
* meta-domain_linked_proteins : a list of `protein` entries, which are via a meta-domain relationship linked to this `locus`

A `locus` entry consists of:
* chromosome : ['1-23', 'X'], excluding 'Y'. String type.
* locus : position on the chromosome. Numeric type.

A `gene` entry consists of:
* gene_position : the position in the gene that matches the locus. Numeric type
* strand : '+' or '-'. String type
* gene_name : the name of the gene wherein this domain occurs. String type
* gencode_transcription_id : gencode_transcription_id. String type
* gencode_translation_name : gencode_translation_name. String type
* gencode_gene_id : gencode_gene_id. String type
* havana_gene_id : havana_gene_id. String type
* havana_translation_id : havana_translation_id. String type
* swissprot_id : uniprot_ac. String type

A `protein` entry consists of:
* swissprot_position : the position in the gene that matches the locus
* swissprot_id : uniprot_ac. String type
* swissprot_name : uniprot_name. String type
* gencode_transcription_id : gencode_transcription_id. String type

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
