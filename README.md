# Metadome Web server

Here you may find all details on how to set up the MetaDome web server in your own environment.

## Software Requirements

The MetaDome webserver has only been tested for running in a Linux-based OS (tested on Ubuntu 16.04, Ubuntu 18.04 and Centos 7), but as it is fully containerized in docker it should in theory be possible to run it on any other OS.
Please ensure you have the following software installed on your machine:

	docker
    docker-compose

You can install docker from [here](https://www.docker.com/get-docker) and docker-compose from [here](https://docs.docker.com/compose/install/#install-compose)

## Data Requirements

The MetaDome webserver makes use of the following data resources

### Gencode

MetaDome uses version v19 of Gencode for GRCH37.
From [here](https://www.gencodegenes.org/releases/19.html), please download the following files:
    
    gencode.v19.annotation.gtf
    gencode.v19.annotation.gff3
    gencode.v19.pc_transcripts.fa
    gencode.v19.pc_translations.fa
    gencode.v19.metadata.SwissProt
    ucsc.gencode.v19.wgEncodeGencodeBasic.txt

And put this in your preferred data storage folder under '/Gencode/'

### UniProt

MetaDome was tested with UniProt version 2016_09.
From [here](ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/), please download the following files:

    uniprot_sprot.dat.gz
    uniprot_sprot_varsplic.fasta.gz
    uniprot_sprot.fasta.gz

Unzip 'uniprot_sprot_varsplic.fasta.gz' and 'uniprot_sprot.fasta.gz' and combine them to a new file: uniprot_sprot_canonical_and_varsplic.fasta

Next you should build a blast database from this new file 'uniprot_sprot_canonical_and_varsplic.fasta'. See [here](https://www.ncbi.nlm.nih.gov/books/NBK279688/) for a further explanation on how to do this if you are unfamiliar with that.

Next, put all this in your preferred data storage folder under '/UniProt/'

### ClinVar

MetaDome was tested with version 20180603 for GRCh37, but later versions may work as well as long as the GRCh37 remains unchanged.
From [here](ftp://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh37/), please download the following files:
    clinvar.vcf.gz
    clinvar.vcf.gz.tbi

And put this in your preferred data storage folder under '/ClinVar/GRCh37/'

### gnomAD

MetaDome was tested with version r2.0.2 for GRCh37, but later versions may work as well as long as the GRCh37 remains unchanged.
From [here](https://console.cloud.google.com/storage/browser/gnomad-public/release/2.0.2/vcf/exomes/?pli=1), please download the following files:

    gnomad.exomes.r2.0.2.sites.vcf.bgz
    gnomad.exomes.r2.0.2.sites.vcf.bgz.tbi

And put this in your preferred data storage folder under '/gnomAD/'

### PFAM

MetaDome was tested with PFAM version 30.0.
From [here](ftp://ftp.ebi.ac.uk/pub/databases/Pfam/releases/Pfam30.0/), please download the following files:

    Pfam-A.hmm.dat.gz
    Pfam-A.hmm.gz

Unzip 'Pfam-A.hmm.gz' to Pfam-A.hmm.
We used a Python script (available upon request) to seperate each of the PFAM alignments contained within 'Pfam-A.hmm.dat.gz' to a folder : 'alignment/PFXXXXX/full' where XXXXX corresponds to the PFAM identifier for faster querying and the alignment is contained in the file 'full'. MetaDome webserver expects the files to be organised as such.

Put all this in your preferred data storage folder under '/PFAM/'

## Installation

Clone the repository and cd into the project folder:

    git clone https://github.com/cmbi/metadome.git
    cd metadome

    TODO: docker-compose with volumes attached
    
    TODO: alter credentials for flask app and postgesql



Run the unit tests to check that everything works:

    TODO

## Running

    TODO: docker-compose up command
