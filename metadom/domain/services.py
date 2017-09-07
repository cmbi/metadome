import logging
from metadom.database import db
from metadom.domain.data_generation.mapping.mapping_generator import generate_gene_to_swissprot_mapping,\
    annotate_interpro_domains_to_proteins, generate_pfam_alignment_mappings
from metadom.domain.models.protein import Protein
from metadom.domain.models.interpro import Interpro, get_all_Pfam_identifiers
from sqlalchemy_schemadisplay import create_schema_graph

_log = logging.getLogger(__name__)

## Save the schema of the database
def write_db_schema_graph(schema_filename):
    # create the pydot graph object by autoloading all tables via a bound metadata object
    graph = create_schema_graph(metadata=db.Model.metadata,
       show_datatypes=True, # The image would get nasty big if we'd show the datatypes
       show_indexes=True, # ditto for indexes
       rankdir='LR', # From left to right (instead of top to bottom)
       concentrate=False # Don't try to join the relation lines together
    )
    graph.write_png(schema_filename) # write out the file

def create_db():
    # initialize custom logging framework
    _log.info("Starting creation of new database")
#     # lists used for the analyses
#     lists_of_genes = LoadDataFromJsonFile(GENE2PROTEIN_LOCATION_OF_GENE_LISTS)
#     list_of_failing_genes = LoadDataFromJsonFile(GENE2PROTEIN_LOCATION_OF_FAILING_GENE_LISTS)
           
    # the genes that are to be checked
    genes_of_interest = ['LMX1A','LMX1B', 'ZBTB18'] # 'LRTOMT', 'USH2A', 'PACS1', 'PACS2']
#     genes_of_interest = lists_of_genes['all_gencode_genes']
#     genes_of_interest = lists_of_genes['all_known_genes']
#     genes_of_interest = lists_of_genes['longlist_of_well_structured_genes_that_have_swissprot']
#     genes_of_interest = lists_of_genes["genes_of_phd_aanvraag"] 
#     genes_of_interest = lists_of_genes["shortlist_of_well_structured_genes"]
#     genes_of_interest = lists_of_genes["pseudoautosomal_genes"]
#     genes_of_interest = lists_of_genes["genes_for_lucca"]    
#     genes_of_interest = lists_of_genes["shortlist_of_well_structured_genes"] + list_of_failing_genes["failing_genes"] # Fast test
#     genes_of_interest = ["GENE_NAME"]
#     ignore_genes = ['TTN']
#     genes_of_interest = [x for x in genes_of_interest if x not in ignore_genes]
 
    # (re-) construct the mapping database  => GENE2PROTEIN_MAPPING_DB
    for gene_name in genes_of_interest:
        # generate all gene to swissprot mappings
        generate_gene_to_swissprot_mapping(gene_name)
    
    for protein in Protein.query.all():
        # generate all pfam domain to swissprot mappings
        annotate_interpro_domains_to_proteins(protein)
    
    for pfam_domain_id in get_all_Pfam_identifiers():
        # generate alignments and mappings based on protein domains
        generate_pfam_alignment_mappings(pfam_domain_id)
        