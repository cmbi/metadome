# Flask settings
DEBUG = True
SECRET_KEY = 'asfdcq93n4c981q34hfn39890'

# FLask-SQLAchemy settings
SQLALCHEMY_RECORD_QUERIES = True # TODO: should be false when not debug
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = "postgresql://metadom_user:example@metadom_db_1/"
SQLALCHEMY_ECHO = True
SQLALCHEMY_POOL_TIMEOUT = 10

# Debug toolbar
DEBUG_TB_ENABLED = DEBUG

# local data directory
DATA_DIR = "/usr/data/"
GENE_NAMES_FILE = DATA_DIR+'gene_names.txt'

# local executables
BLASTP_EXECUTABLE = "/usr/externals/blast/bin/blastp"
CLUSTALW_EXECUTABLE = "/usr/externals/clustalw/clustalw2"
HMMFETCH_EXECUTABLE = "/usr/externals/hmmer/binaries/hmmfetch"
HMMLOGO_EXECUTABLE = "/usr/externals/hmmer/binaries/hmmlogo"
HMMALIGN_EXECUTABLE = "/usr/externals/hmmer/binaries/hmmalign"
HMMEMIT_EXECUTABLE = "/usr/externals/hmmer/binaries/hmmemit"
HMMSTAT_EXECUTABLE = "/usr/externals/hmmer/binaries/hmmstat"

# Genome specific files
GENCODE_HG_ANNOTATION_FILE_GTF = DATA_DIR+"Gencode/gencode.v19.annotation.gtf"
GENCODE_HG_ANNOTATION_FILE_GFF3 = DATA_DIR+"Gencode/gencode.v19.annotation.gff3"
GENCODE_HG_TRANSCRIPTION_FILE = DATA_DIR+"Gencode/gencode.v19.pc_transcripts.fa"
GENCODE_HG_TRANSLATION_FILE = DATA_DIR+"Gencode/gencode.v19.pc_translations.fa"
GENCODE_SWISSPROT_FILE = DATA_DIR+"Gencode/gencode.v19.metadata.SwissProt"
GENCODE_BASIC_FILE = DATA_DIR+"Gencode/ucsc.gencode.v19.wgEncodeGencodeBasic.txt"

# InterPro Files
INTERPROSCAN_DOCKER_IMAGE = "blaxterlab/interproscan:5.22-61.0"
INTERPROSCAN_DOCKER_VOLUME = 'metadom_interpro_temp'
INTERPROSCAN_EXECUTABLE = "interproscan.sh"
INTERPROSCAN_TEMP_DIR = '/usr/interpro_temp'
INTERPROSCAN_DOMAIN_DATABASES = 'Pfam'

# UNIPROT
UNIPROT_MAX_BLAST_RESULTS = 10
UNIPROT_DIR = DATA_DIR+"UniProt/"
UNIPROT_SPROT_CANONICAL_AND_ISOFORM = UNIPROT_DIR+"uniprot_sprot_canonical_and_varsplic.fasta"
UNIPROT_SPROT_ISOFORM = UNIPROT_DIR+"uniprot_sprot_varsplic.fasta"
UNIPROT_SPROT_CANONICAL = UNIPROT_DIR+"uniprot_sprot.fasta"
UNIPROT_SPROT_SPECIES_FILTER = "HUMAN"
UNIPROT_TREMBL = UNIPROT_DIR+"uniprot_trembl.fasta"

# PFAM specific files
PFAM_DIR = DATA_DIR+"PFAM/Pfam30.0"
PFAM_ALIGNMENT_DIR = PFAM_DIR+"/alignment/"
PFAM_HMM_DAT = PFAM_DIR+"/Pfam-A.hmm.dat.gz"
PFAM_HMM = PFAM_DIR+"/Pfam-A.hmm"

# Exac specific files
EXAC_DIR = DATA_DIR + "ExAC/release1.0/"
EXAC_VCF_FILE = EXAC_DIR + "ExAC.r1.sites.vep.vcf.gz"
EXAC_ACCEPTED_FILTERS = ['PASS']

## TODO: create filter based on ExAC r1.0
# ClinVar specific files
CLINVAR_DIR = DATA_DIR + 'ClinVar/GRCh37/20170615_vcf_2.0/'
CLINVAR_ORIGINAL_VCF_FILE = CLINVAR_DIR + 'clinvar.vcf.gz'
CLINVAR_FILTERED_VCF_FILE = CLINVAR_DIR + 'clinvar.snv.filtered_ExAC.r0.3.1.pass.0.001AF.vcf.gz'
CLINVAR_VCF_FILE = CLINVAR_FILTERED_VCF_FILE
CLINVAR_CONSIDERED_CLINSIG = ['Pathogenic']

# # Configuration
# MINIMAL_BLASTPE_VALUE = 0.01
# MINIMAL_TRANSLATION_TO_STRUCTURE_PIDENT_VALUE = 95.0
# MINIMAL_XRAY_STRUCTURE_RESOLUTION = 4.0
# 
# 
# # PDB specific files
# PDB_DIR = DATA_DIR+"PDB"
# PDB_STRUCTURE_DIR = PDB_DIR+'/Structures/pdb/'
# PDB_SEQRES_FASTA = PDB_DIR+"/pdb_seqres_prot.txt"
