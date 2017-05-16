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
| :---: | :-- | :-- |
| GET | [hostname]/metadom/api/chr/`<str:chr>`/`<int:position>` | `locus` |

 \*: zero or many

### Input

* `<str:chr>` : ['1-23', 'X'], excluding 'Y'. String type.
* `<int:position>` : position on the chromosome, cDNA of the gene, sequence position of the protein, or pfam domain consensus position. Depending on the parent type. Numeric type.

### Output
A `locus` entry consists of:
```
{
    "locus":{
        "chromosome":<str>,
        "position":<int>,
    },
    "locus_information": 
        [
            {
                "information":information,
                "meta_information":
                    [
                        information*,
                        ...
                    ],
            }*, ... 
        ],
}
```

An `information` entry consists of:
* chromosome : ['1-23', 'X'], excluding 'Y'. String type.
* chromosome_position : position on the chromosome. Numeric type.
* cDNA_position : the position in the cDNA of the gene that matches the locus. Numeric type
* uniprot_position : the sequence position of the protein that matched the locus. Numeric type
* strand : '+' or '-'. String type
* allele : one of the four nucleotide 'A', 'T', 'C', 'G'. String type.
* codon : 'ATG',
* codon_allele_position : position of the alle in the codon [0-2]. Numeric type.
* amino_acid_residue : one of the twenty amino acids in single character respresentation, including '\*' for stop codon. String type
* gene_name : the name of the gene wherein this domain occurs. String type
* gencode_transcription_id : the transcription id from GENCODE. String type
* gencode_translation_name : the translation name from GENCODE. String type
* gencode_gene_id : the gene id from GENCODE. String type
* havana_gene_id : the gene id from HAVANA. String type
* havana_translation_id : the translation id from HAVANA. String type
* uniprot_ac : the uniprot Accession Code. String type
* uniprot_name : the name of the uniprot entry. String type
* pfam_domain_consensus_position : the consensus position of the Pfam domain where this position is aligned to. Numeric type  or None
* pfam_domain_name : the name of the Pfam domain. String type or None
* pfam_domain_id : the Pfam domain identifier. String type  or None
* interpro_id : the interpro identifier. String type  or None
* uniprot_domain_start_pos : the position in the uniprot sequence where this domain starts. Numeric type or None
* uniprot_domain_end_pos : the position in the uniprot sequence where this domain starts. Numeric type or None

A `meta_information` entry consists of zero or more `information` entries, which are via a meta-domain relationship linked to this `information`

### Future endpoints
| HTTP | Method URI | Output type |
| :---: | :-- | :-- |
| GET | [hostname]/metadom/api/gene/`<str:gencode_translation_name>`/`<int:position>` | `locus` |
| GET | [hostname]/metadom/api/protein/`<str:uniprot_ac>`/`<int:position>` | `locus` |
| GET | [hostname]/metadom/api/domain/`<str:Pfam_id>`/`<int:position>` | `locus` |

#### Future Input

* `<str:gencode_translation_name>` : the gencode translation name. String type
* `<str:uniprot_ac>` : the uniprot Accession Code. String type
* `<str:Pfam_id>` : the Pfam domain identifier. String type
