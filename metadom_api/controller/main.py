'''
Benign Genomic Variation Mapper (BGVM)


@author: laurensvdwiel
'''
# import logging
# from BGVM.Tools.CustomLogger import initLogging
# from BGVM.Annotation.GenerateReport import annotate_genes_of_interest
# from dev_settings import LOGGER_NAME, GENE2PROTEIN_LOCATION_OF_GENE_LISTS,\
#  GENE2PROTEIN_LOCATION_OF_FAILING_GENE_LISTS,\
#     GENE2PROTEIN_META_DOMAIN_STATISTICS,\
#     GENE2PROTEIN_ANNOTATED_HOMOLOGUE_DOMAINS_DATASET,\
#     GENE2PROTEIN_META_DOMAIN_CHARACTERISTIC_VARIANTS_HGMD,\
#     GENE2PROTEIN_META_DOMAIN_CHARACTERISTIC_VARIANTS_EXAC,\
#     GENE2PROTEIN_HOMOLOGUE_DOMAINS, GENE2PROTEIN_DOMAINS,\
#     GENE2PROTEIN_ANNOTATED_HOMOLOGUE_DOMAINS_DATASET_FAILURES,\
#     GENE2PROTEIN_ANNOTATED_DOMAINS_DATASET_FAILURES,\
#     GENE2PROTEIN_ANNOTATED_DOMAINS_DATASET,\
#     GENE2PROTEIN_META_DOMAIN_CHARACTERISTIC_VARIANTS_EXAC_SMALL,\
#     GENE2PROTEIN_META_DOMAIN_CHARACTERISTIC_VARIANTS_HGMD_SMALL,\
#     GENE2PROTEIN_META_DOMAIN_CHARACTERISTIC_VARIANTS_EXAC_MEDIUM,\
#     GENE2PROTEIN_META_DOMAIN_CHARACTERISTIC_VARIANTS_HGMD_MEDIUM
# from BGVM.Tools.DataIO import LoadDataFromJsonFile
# import time
# from BGVM.Domains.HomologuesDomains import create_homologues_domains_dataset,\
#     create_annotated_domains_dataset, load_homologue_domain_dataset
# from BGVM.MetaDomains.Database.database_creation import create_meta_domain_database
# from BGVM.Annotation.CreateAnnotatedGenesDataset import add_all_genes_to_the_annoted_gene_database
# from BGVM.MetaDomains.Computations.meta_domain_statistics import construct_meta_domain_statistics_dataset
# from BGVM.MetaDomains.Construction.meta_domain_merging import EXAC_TYPE_NAME,\
#     HGMD_TYPE_NAME
# from BGVM.MetaDomains.Computations.meta_domain_characteristic_variant_permutation import create_characteristic_variants_dataset
import logging
from metadom_api.controller.mapping.mapping_generator import generate_gene_mapping

_log = logging.getLogger(__name__)

def main():
    logging_level = logging.INFO
    _log.setLevel(logging_level)
    console = logging.StreamHandler()
            
    # set the logging level
    console.setLevel(logging_level)
            
    # set a format which is simpler to interpret for console use
    formatter = logging.Formatter('%(asctime)s %(levelname)-2s %(module)s.%(funcName)s: %(message)s (%(processName)s (Thread-ID: %(thread)d))')
             
    # tell the handler to use this format
    console.setFormatter(formatter)
            
    # ensure we push all custom log messages to the console
    _log.addHandler(console)
    
    # ensure we push all warning to the console
    logging.getLogger('py.warnings').addHandler(console)
    
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
#         
#     create_mapping_database(genes_of_interest=genes_of_interest, reconstruct_database=True, reevaluate_genes_present_in_db=False, require_structure=False, use_parallel=True)
#   
#     # Create a database with full annotation, based on the current mapped genes database
#     add_all_genes_to_the_annoted_gene_database(reconstruct_database=True, use_parallel=True, batch_size=50)
#   
#     # create a dataset that consists of homologue domains => GENE2PROTEIN_DOMAINS, GENE2PROTEIN_HOMOLOGUE_DOMAINS
#     create_homologues_domains_dataset() 
#         
#     # annotate the homologues domains => GENE2PROTEIN_ANNOTATED_HOMOLOGUE_DOMAINS_DATASET
#     create_annotated_domains_dataset(GENE2PROTEIN_HOMOLOGUE_DOMAINS, GENE2PROTEIN_ANNOTATED_HOMOLOGUE_DOMAINS_DATASET, GENE2PROTEIN_ANNOTATED_HOMOLOGUE_DOMAINS_DATASET_FAILURES)
#     
#     # annotate all domains => GENE2PROTEIN_ANNOTATED_DOMAINS_DATASET
#     create_annotated_domains_dataset(GENE2PROTEIN_DOMAINS, GENE2PROTEIN_ANNOTATED_DOMAINS_DATASET, GENE2PROTEIN_ANNOTATED_DOMAINS_DATASET_FAILURES)
#         
#     # Create the meta domain dataset => GENE2PROTEIN_META_DOMAIN_DB    
#     create_meta_domain_database(load_homologue_domain_dataset(GENE2PROTEIN_ANNOTATED_HOMOLOGUE_DOMAINS_DATASET), reconstruct_database=True, use_parallel=True, batch_size=2)
#      
#     # Create the meta domain statistics dataset => GENE2PROTEIN_META_DOMAIN_STATISTICS
#     construct_meta_domain_statistics_dataset(load_homologue_domain_dataset(GENE2PROTEIN_ANNOTATED_HOMOLOGUE_DOMAINS_DATASET), GENE2PROTEIN_META_DOMAIN_STATISTICS, use_parallel=True)
#     
#     # Permute in order to retrieve the characteristic variant dataset => GENE2PROTEIN_META_DOMAIN_CHARACTERISTIC_VARIANTS_EXAC, GENE2PROTEIN_META_DOMAIN_CHARACTERISTIC_VARIANTS_HGMD
#     n_permutations = 1000
#     tolerance_score_of_interest="background_corrected_missense_synonymous_ratio"
#     random_seed_value = 1
#     create_characteristic_variants_dataset(GENE2PROTEIN_META_DOMAIN_CHARACTERISTIC_VARIANTS_EXAC, EXAC_TYPE_NAME, n_permutations=n_permutations, random_seed_value=random_seed_value, use_parallel=True, tolerance_score_of_interest=tolerance_score_of_interest, adjusted_observed_variant_percentage=None)
#     create_characteristic_variants_dataset(GENE2PROTEIN_META_DOMAIN_CHARACTERISTIC_VARIANTS_HGMD, HGMD_TYPE_NAME, n_permutations=n_permutations, random_seed_value=random_seed_value, use_parallel=True, tolerance_score_of_interest=tolerance_score_of_interest, adjusted_observed_variant_percentage=None)
#     
#     adjusted_observed_variant_percentage_small = 1/3
#     create_characteristic_variants_dataset(GENE2PROTEIN_META_DOMAIN_CHARACTERISTIC_VARIANTS_EXAC_SMALL, EXAC_TYPE_NAME, n_permutations=n_permutations, random_seed_value=random_seed_value, use_parallel=True, tolerance_score_of_interest=tolerance_score_of_interest, adjusted_observed_variant_percentage=adjusted_observed_variant_percentage_small)
#     create_characteristic_variants_dataset(GENE2PROTEIN_META_DOMAIN_CHARACTERISTIC_VARIANTS_HGMD_SMALL, HGMD_TYPE_NAME, n_permutations=n_permutations, random_seed_value=random_seed_value, use_parallel=True, tolerance_score_of_interest=tolerance_score_of_interest, adjusted_observed_variant_percentage=adjusted_observed_variant_percentage_small)
#     
#     adjusted_observed_variant_percentage_medium = 2/3
#     create_characteristic_variants_dataset(GENE2PROTEIN_META_DOMAIN_CHARACTERISTIC_VARIANTS_EXAC_MEDIUM, EXAC_TYPE_NAME, n_permutations=n_permutations, random_seed_value=random_seed_value, use_parallel=True, tolerance_score_of_interest=tolerance_score_of_interest, adjusted_observed_variant_percentage=adjusted_observed_variant_percentage_medium)
#     create_characteristic_variants_dataset(GENE2PROTEIN_META_DOMAIN_CHARACTERISTIC_VARIANTS_HGMD_MEDIUM, HGMD_TYPE_NAME, n_permutations=n_permutations, random_seed_value=random_seed_value, use_parallel=True, tolerance_score_of_interest=tolerance_score_of_interest, adjusted_observed_variant_percentage=adjusted_observed_variant_percentage_medium)
    
# def create_mapping_database(genes_of_interest, reconstruct_database=False, reevaluate_genes_present_in_db=False, require_structure=False, use_parallel=True):
#     # Perform the mappings
#     _log.info("Starting mapping for "+str(len(genes_of_interest))+" genes")
#     start_time = time.clock()
#     annotate_genes_of_interest(genes_of_interest=genes_of_interest, reconstruct_database=reconstruct_database, reevaluate_genes_present_in_db=reevaluate_genes_present_in_db, require_structure=require_structure, use_parallel=use_parallel)
#     time_step = time.clock()
#     _log.info("Finished mapping for "+str(len(genes_of_interest))+" genes in "+str(time_step-start_time)+" seconds")
# 
# def create_annotated_genes_database():
#     initLogging(print_to_console=True, logging_level=logging.INFO)  
#     
#     _log.info("Starting annotation of genes and storing the results in a database")
#     start_time = time.clock()
#       
#     add_all_genes_to_the_annoted_gene_database(reconstruct_database=True, use_parallel=True, batch_size=50)
#      
#     time_step = time.clock()
#     _log.info("Finished annotation of genes and storing the results in a database in "+str(time_step-start_time)+" seconds")
     

if __name__ == "__main__":
    main()
