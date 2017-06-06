# local data directory
DATA_DIR = ""

# local executables
BLASTP_EXECUTABLE = "/usr/bin/blastp"
CLUSTALW_EXECUTABLE = "/usr/bin/clustalw"
HMMFETCH_EXECUTABLE = "/usr/bin/hmmfetch"
HMMLOGO_EXECUTABLE = "/usr/bin/hmmlogo"
HMMALIGN_EXECUTABLE = "/usr/bin/hmmalign"
HMMEMIT_EXECUTABLE = "/usr/bin/hmmemit"
HMMSTAT_EXECUTABLE = "/usr/bin/hmmstat"

# Gene 2 Protein mapping database

# Meta domain databases and datasets

# location of gene lists

# Configuration
MINIMAL_BLASTPE_VALUE = 0.01

# Exac specific files
EXAC_DIR = DATA_DIR + "Exac/release0.3.1/"
EXAC_VCF_FILE = EXAC_DIR + "ExAC.r0.3.1.sites.vep.vcf.gz"
EXAC_TBI_FILE = EXAC_VCF_FILE + ".tbi"
EXAC_ACCEPTED_FILTERS = ['PASS']

#HGMD specific files
HGMD_DIR = DATA_DIR + 'HGMD/HGMD_PRO_2016.2/2016.2/'
HGMD_VCF_FILE = HGMD_DIR + "HGMD_PRO_2016.2_hg19.vcf.gz"
HGMD_TBI_FILE = HGMD_VCF_FILE + ".tbi"
HGMD_CONSIDERED_CLASSES = ['DM']


# Genome specific files
GENCODE_HG_ANNOTATION_FILE_GTF = DATA_DIR+"Gencode/gencode.v19.annotation.gtf"
GENCODE_HG_ANNOTATION_FILE_GFF3 = DATA_DIR+"Gencode/gencode.v19.annotation.gff3"
GENCODE_HG_TRANSCRIPTION_FILE = DATA_DIR+"Gencode/gencode.v19.pc_transcripts.fa"
GENCODE_HG_TRANSLATION_FILE = DATA_DIR+"Gencode/gencode.v19.pc_translations.fa"
GENCODE_SWISSPROT_FILE = DATA_DIR+"Gencode/gencode.v19.metadata.SwissProt"
GENCODE_BASIC_FILE = DATA_DIR+"Gencode/ucsc.gencode.v19.wgEncodeGencodeBasic.txt"

# InterPro Files
INTERPRO_DIR = DATA_DIR+"InterPro/59.0/"
INTERPROSCAN_EXECUTABLE = INTERPRO_DIR+"interproscan-5.20-59.0/interproscan.sh"
INTERPRO_PRO2IPR_DB = INTERPRO_DIR+"protein2ipr.db"
INTERPRO_PRO2IPR = INTERPRO_DIR+"protein2ipr.dat.gz"

# UNIPROT
UNIPROT_MAX_BLAST_RESULTS = 10
UNIPROT_DIR = DATA_DIR+"UniProt/"
UNIPROT_SPROT_CANONICAL_AND_ISOFORM = UNIPROT_DIR+"uniprot_sprot_canonical_and_varsplic.fasta"
UNIPROT_SPROT_ISOFORM = UNIPROT_DIR+"uniprot_sprot_varsplic.fasta"
UNIPROT_SPROT_CANONICAL = UNIPROT_DIR+"uniprot_sprot.fasta"
UNIPROT_SPROT_SPECIES_FILTER = "HUMAN"
UNIPROT_TREMBL = UNIPROT_DIR+"uniprot_trembl.fasta"

# PDB specific files
PDB_DIR = DATA_DIR+"PDB"
PDB_STRUCTURE_DIR = PDB_DIR+'/Structures/pdb/'
PDB_SEQRES_FASTA = PDB_DIR+"/pdb_seqres_prot.txt"

# PFAM specific files
PFAM_DIR = DATA_DIR+"PFAM/Pfam30.0"
PFAM_ALIGNMENT_DIR = PFAM_DIR+"/alignment/"
PFAM_HMM_DAT = PFAM_DIR+"/Pfam-A.hmm.dat.gz"
PFAM_HMM = PFAM_DIR+"/Pfam-A.hmm"

# MRS client
MRS_CLIENT = 'http://mrs.cmbi.ru.nl/mrsws/search/wsdl'

# development logging
LOGGER_NAME = 'logger_dev'