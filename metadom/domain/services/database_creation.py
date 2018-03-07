from metadom.domain.data_generation.mapping.mapping_generator import generate_gene_to_swissprot_mapping,\
    annotate_interpro_domains_to_proteins, generate_pfam_alignment_mappings
from metadom.domain.infrastructure import add_gene_mapping_to_database,\
    filter_gene_names_present_in_database
from metadom.domain.models.protein import Protein
from metadom.domain.models.interpro import get_all_Pfam_identifiers
from metadom.domain.wrappers.gencode import retrieve_all_protein_coding_gene_names
from sklearn.externals.joblib.parallel import Parallel, cpu_count, delayed
import logging

_log = logging.getLogger(__name__)

def CalculateNumberOfActiveThreads(numberOfTasks):
    if(cpu_count() == 2):
        return cpu_count()
    elif numberOfTasks < cpu_count():
        return numberOfTasks
    else:
        return cpu_count()

def create_db():
    # initialize custom logging framework
    _log.info("Starting creation of new database")

    # the genes that are to be checked
    genes_of_interest = retrieve_all_protein_coding_gene_names()
 
    # (re-) construct the mapping database  => GENE2PROTEIN_MAPPING_DB
    generate_mappings_for_genes(genes_of_interest, batch_size=10, use_parallel=True)
            
    for protein in Protein.query.all():
        # generate all pfam domain to swissprot mappings
        annotate_interpro_domains_to_proteins(protein)
       
    for pfam_domain_id in get_all_Pfam_identifiers():
        # generate alignments and mappings based on protein domains
        generate_pfam_alignment_mappings(pfam_domain_id)

def generate_mappings_for_genes(genes_of_interest, batch_size, use_parallel):
    # filter gene names alreay present in the database
    genes_of_interest = filter_gene_names_present_in_database(genes_of_interest)
    
    # Create batches
    genes_of_interest_batches = [genes_of_interest[i:i+batch_size] for i in range(0, len(genes_of_interest), batch_size)]
    n_batches = len(genes_of_interest_batches)
    n_genes = len(genes_of_interest)
     
    # Annotate the genes in batches
    _log.info("Starting the mapping of batched analysis of '"+str(n_genes)+"' over '"+str(n_batches)+"' batches")
    succeeded_genes = 0
    for batch_counter, gene_batch in enumerate(genes_of_interest_batches):
        _log.info("Starting batch '"+str(batch_counter+1)+"' out of '"+str(n_batches)+"', with '"+str(len(gene_batch))+"' genes")
     
        gene_mappings = []
        if use_parallel:
            gene_mappings = Parallel(n_jobs=CalculateNumberOfActiveThreads(batch_size))(delayed(generate_gene_to_swissprot_mapping)(gene) for gene in gene_batch)            
        else:
            gene_mappings = [generate_gene_to_swissprot_mapping(gene) for gene in gene_batch]

        # add the batches to the database
        for gene_mapping in gene_mappings:
            add_gene_mapping_to_database(gene_mapping)
         
        _log.info("Finished batch '"+str(batch_counter+1)+"' out of '"+str(n_batches)+"'")
    _log.info("Finished the mapping of batched analysis of '"+str(n_genes)+"' over '"+str(n_batches)+"' batches, resulting in '"+str(succeeded_genes)+"' successful gene mappings")

