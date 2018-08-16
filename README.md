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

First configure the volumes (at the \<ABSOLUTE PATH\>) to correspond with your data folders in the docker-compose.yml (lines 64, 70, 76, 82, 88, 94):

### (Optional) Credentials configuration
If you are planning to expose the MetaDome server to a public adress, please make sure you get the security in order.

	- Change the variable `POSTGRES_PASSWORD` for the postgresql database in `./metadome/postgres_credentials.py`
	- Change the variable `SECRET_KEY_CRED` in `./metadome/flask_app_credentials.py`

Otherwise you will be using default passwords and API secrets.

## First time running

@Coos: please write here the steps to first initialize the database

Note: Launching the server this way, by creating the database from scratch, will first make it generate all mappings between gencode, swissprot and Pfam. This process, depending on your configuration, may take 2 weeks. If you require a pre-build database, do not hesitate to contact us.

## Running

If you followed the above steps, you can now run the webserver via the command:

    docker-compose docker-compose.yml up -d

And tear it down via:

    docker-compose -f docker-compose.yml stop

# Citing MetaDome server

We anticipate the publication of a method paper describing this web-service in late 2018. Until that is published, please use the following citation when referencing the results in your report:
```
MetaDome web-service, Nijmegen, The Netherlands
 (URL: https://stuart.radboudumc.nl/metadome) 
 [date (month, year) accessed].
```
Together with:

```
Aggregation of population‐based genetic variation 
 over protein domain homologues and its potential 
 use in genetic diagnostics.
Laurens Wiel, Hanka Venselaar, Joris A. Veltman, 
 Gert Vriend and Christian Gilissen.
Human Mutation. (2017) 38, 1454–1463
```

# Contact

If you want to provide feedback please have a look at our
[existing issues][1] (and if necessary, create a new issue).

[1]: https://github.com/cmbi/metadome/issues
