import logging
from metadom.database import db
from metadom.domain.data_generation.mapping.mapping_generator import generate_gene_mapping

_log = logging.getLogger(__name__)

def list_tables():
    return db.Model.metadata.tables.keys()
  
def test_connection():
    try:
        db.session.commit()
        return True
    except db.OperationalError as e:
        _log.error(e)
    return False

def create_db():
    # initialize custom logging framework
    _log.info("Starting analysis")
#     # lists used for the analyses
#     lists_of_genes = LoadDataFromJsonFile(GENE2PROTEIN_LOCATION_OF_GENE_LISTS)
#     list_of_failing_genes = LoadDataFromJsonFile(GENE2PROTEIN_LOCATION_OF_FAILING_GENE_LISTS)
           
    # the genes that are to be checked
    genes_of_interest = ['USH2A', 'PACS1', 'PACS2']
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
        for gene_translation in generate_gene_mapping(gene_name):
            pass