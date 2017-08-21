'''
Created on Oct 24, 2016

@author: laurens
'''
from BGVM.Tools.CustomLogger import initLogging
from BGVM.Tools.DataIO import LoadDataFromJsonFile, SaveDataToJsonFile
from dev_settings import GENE2PROTEIN_HOMOLOGUE_DOMAINS, LOGGER_NAME,\
    GENE2PROTEIN_ANNOTATED_HOMOLOGUE_DOMAINS_DATASET,\
    GENE2PROTEIN_ANNOTATED_HOMOLOGUE_DOMAINS_DATASET_FAILURES,\
    GENE2PROTEIN_DOMAINS
from BGVM.Mapping.Gene2ProteinMappingDatabase import retrieve_single_gene_entries
import logging
from BGVM.Mapping.Regions.region_annotation import analyse_dn_ds_over_protein_region
from BGVM.BGVMExceptions import RegionIsNotEncodedBycDNAException,\
    RegioncDNALengthDoesNotEqualProteinLengthException,\
    ExternalREFAlleleNotEqualsTranscriptionException
import pandas as pd
import numpy as np
import time
from BGVM.Metrics.GeneticTolerance import mosy_score,\
    background_corrected_mosy_score
from BGVM.Metrics.EvaluationMetrics import MedianAbsoluteDeviation
from sklearn.metrics.regression import mean_squared_error
from BGVM.Annotation.CreateAnnotatedGenesDataset import retrieve_all_annotated_gene_entries,\
    retrieve_single_annotated_gene

def create_homologues_domains_dataset():
    """Creates 2 datasets that consist of domains that occur throughout H19,
    The first dataset is stored in dev_settings.GENE2PROTEIN_DOMAINS consists
        of all domains within HG19
    The second dataset is stored in dev_settings.GENE2PROTEIN_HOMOLOGUE_DOMAINS
        consists of all domains that occur as homologues troughout HG19"""
    # retrieve and save all homologue domains
    logging.getLogger(LOGGER_NAME).info("Starting analysing homologues domains for all genes in the mapping database")
    start_time = time.clock()
    domains, domains_in_homologues, genes_with_interpro_ids, genes_without_interpro_ids = extract_domains_and_homologue_domains()
    SaveDataToJsonFile(GENE2PROTEIN_DOMAINS, domains)
    SaveDataToJsonFile(GENE2PROTEIN_HOMOLOGUE_DOMAINS, domains_in_homologues)
    time_step = time.clock()
    logging.getLogger(LOGGER_NAME).info("Finished analysing homologues domains for "+str(len(genes_with_interpro_ids)+len(genes_without_interpro_ids))+" genes and found '"+str(len(genes_without_interpro_ids))+"' genes without any interpro domains linked and "+str(len(domains_in_homologues))+" homologues domains in "+str(time_step-start_time)+" seconds")

def load_homologue_domain_dataset(filename):
    """Loads the homologues domain dataset contained within filename
    into a pandas dataframe object and annotates tolerance metrics"""
    return load_domain_dataset(filename, require_strictly_homologue=True)

def load_domain_dataset(filename, require_strictly_homologue=False):
    """Loads the domain dataset contained within filename
    into a pandas dataframe object and annotates tolerance metrics"""
    # load the data
    domain_tolerance_dataset = pd.DataFrame().from_csv(filename, sep=';')
     
    # check which domains are homologue across multiple genes
    domain_genes_mapping = create_dictionary_of_domains_to_gene_names(domain_tolerance_dataset)
    
    if require_strictly_homologue: 
        domains_with_homologues_across_genes = [domain_id for domain_id in domain_genes_mapping.keys() if len(domain_genes_mapping[domain_id]) > 1]
        domain_tolerance_dataset = domain_tolerance_dataset[domain_tolerance_dataset['external_database_id'].isin(domains_with_homologues_across_genes)]
                              
    # recompute the myssense over synonymous scores:
    domain_tolerance_dataset['background_corrected_missense_synonymous_ratio'] = domain_tolerance_dataset.apply(lambda domain_entry: background_corrected_mosy_score(domain_entry['exac_missense_in_domain'],
                                                                                                        domain_entry['background_missense_in_domain'],
                                                                                                        domain_entry['exac_synonymous_in_domain'],
                                                                                                        domain_entry['background_synonymous_in_domain']), axis=1)
 
    domain_tolerance_dataset['missense_synonymous_ratio'] = domain_tolerance_dataset.apply(lambda domain_entry: mosy_score(domain_entry['exac_missense_in_domain'],
                                                                                                                           domain_entry['exac_synonymous_in_domain']), axis=1)             
     
    # Calculate and add rank percentiles
    domain_tolerance_dataset['background_corrected_missense_synonymous_percentile_rank'] = (domain_tolerance_dataset['background_corrected_missense_synonymous_ratio'].rank()/len(domain_tolerance_dataset))
    domain_tolerance_dataset['missense_synonymous_percentile_rank'] = (domain_tolerance_dataset['missense_synonymous_ratio'].rank()/len(domain_tolerance_dataset))
     
    return domain_tolerance_dataset

def create_dictionary_of_domains_to_gene_names(domains_of_interest):
    domain_gene = {domain:[] for domain in domains_of_interest['external_database_id']}
     
    group_of_domain_ids = domains_of_interest.groupby(['external_database_id'])
    for domain_name, domain_group in group_of_domain_ids:
        for gene_name in domain_group['gene_name']:
            if gene_name in domain_gene[domain_name]: continue
            domain_gene[domain_name].append(gene_name)
     
    return domain_gene

def extract_domains_and_homologue_domains():
    """Analyses the domains contained within gene_reports and combines any homologues"""
    # homologue domain
    domains = {}
    genes_without_interpro_ids = []
    genes_with_interpro_ids = []
    for gene_mapping in retrieve_all_annotated_gene_entries():
        gene_report = gene_mapping['gene_mapping']
        
        #Gen naam |  Domein naam (external database) | InterproID | start/end_pos | heeft pdb | intolerantie in domein
        if len(gene_report['interpro']) > 0:
            genes_with_interpro_ids.append(gene_report['gene_name'])
            for interpro_entry in gene_report['interpro']:
                domain_key = str(gene_report['gene_name'])+"_"+str(interpro_entry['uniprot_ac'])+"_"+str(interpro_entry['start_pos'])+"-"+str(interpro_entry['end_pos'])
                if interpro_entry['ext_db_id'] in domains.keys():
                    if not(domain_key in domains[interpro_entry['ext_db_id']]["entries"]):
                        domains[interpro_entry['ext_db_id']]["entries"].append(domain_key)
                else:
                    domains[interpro_entry['ext_db_id']] = {
                        "interpro_id":interpro_entry['interpro_id'],
                        "region_name":interpro_entry['region_name'],
                        "entries":[domain_key]}
        else:
            genes_without_interpro_ids.append(gene_report['gene_name'])
     
    domains_in_homologues = {}
    for domain in domains.keys():
        if len(domains.get(domain)['entries']) > 1:
            domains_in_homologues[domain] = domains[domain]
            
    return domains, domains_in_homologues, genes_with_interpro_ids, genes_without_interpro_ids


def annotate_homologue_domains_with_intolerance_scores(domain_data, score_of_interest):
    # Group the data by the domain identifiers
    group_of_domain_ids = domain_data.groupby(['external_database_id'])
    group_of_domain_ids.filter(lambda x: len(x) > 1)
 
    # Create a list of summaries per domain based on the score of interest
    domain_summaries = []
    for domain_name, domain_group in group_of_domain_ids:
        domain_mean = np.mean(domain_group[score_of_interest])
        domain_median = np.mean(domain_group[score_of_interest])
        domain_entries = []
        for score in domain_group[score_of_interest]:
            domain_entries.append(score)
 
        y_i = np.ones_like(domain_entries)
        y_i = y_i * domain_mean
 
        domain_MAD = MedianAbsoluteDeviation(domain_entries)
        domain_MSE = mean_squared_error(y_i, domain_entries)
         
        domain_summary = {'external_database_id': domain_name,'MAD':domain_MAD , 'MSE': domain_MSE, 'mean': domain_mean, 'median':domain_median, 'n_domains':len(domain_entries), 'domain_entries':domain_entries}
        domain_summaries.append(domain_summary)
    return domain_summaries


def create_annotated_domains_dataset(input_domains, output_domains, output_failures):
    domains_in_homologues = LoadDataFromJsonFile(input_domains)
    pfam_domain_ids = [d for d in domains_in_homologues.keys() if d.startswith('PF')]
     
    pfam_domains_in_homologues = {pfam_key:domains_in_homologues[pfam_key] for pfam_key in pfam_domain_ids}
     
    pfam_gene_names = []
    pfam_gene_regions = {}
    for pfam_key in pfam_domain_ids:
        for pfam_entry in pfam_domains_in_homologues[pfam_key]['entries']:
            pfam_entry_tokens = pfam_entry.split('_')
            pfam_gene_name = pfam_entry_tokens[0]
            pfam_uniprot_ac = pfam_entry_tokens[1]
            pfam_uniprot_region = pfam_entry_tokens[2]
             
            pfam_gene_names.append(pfam_gene_name)
             
            pfam_gene_region_entry = {'external_db_id':pfam_key,\
                                      'uniprot_ac':pfam_uniprot_ac,\
                                      'uniprot_domain_region':pfam_uniprot_region,\
                                      'interpro_id':pfam_domains_in_homologues[pfam_key]['interpro_id'],\
                                      'region_name':pfam_domains_in_homologues[pfam_key]['region_name']}
             
             
            if pfam_gene_name in pfam_gene_regions.keys():
                pfam_gene_regions[pfam_gene_name].append(pfam_gene_region_entry)
     
            else:
                pfam_gene_regions[pfam_gene_name] = [pfam_gene_region_entry]
             
    pfam_gene_names = set(pfam_gene_names)
     
    # Domein naam | external database | InterproID | Gen naam | swissprot_id | swissprot start/end_pos | chr start/end | pdb_id | intolerantie in domein
    final_dataset = []
    failed_genes = []
    failed = []
    for gene_name in pfam_gene_names:
        gene_mapping = retrieve_single_gene_entries(gene_name)['gene_mapping']
        pfam_gene_mapping = retrieve_single_annotated_gene(gene_name)['gene_mapping']
        
        # retrieve some stats needed towards the end
        gencode_transcription_id = pfam_gene_mapping["gencode_transcription_id"]
        gencode_translation_name = pfam_gene_mapping["gencode_translation_name"]
        gencode_gene_id = pfam_gene_mapping["gencode_gene_id"]
        havana_gene_id = pfam_gene_mapping["havana_gene_id"]
        havana_translation_id = pfam_gene_mapping["havana_translation_id"]
        
        if 'pdb_seqres_used' in pfam_gene_mapping.keys() and not(pfam_gene_mapping['pdb_seqres_used'] is None):
            pdb_id = pfam_gene_mapping['pdb_seqres_used']['sseqid']
        else:
            pdb_id = "-"
         
        for pfam_gene_region_entry in pfam_gene_regions[gene_name]:
             
            # retrieve uniprot position region
            domain_uniprot_start_pos = int(pfam_gene_region_entry['uniprot_domain_region'].split('-')[0])
            domain_uniprot_end_pos = int(pfam_gene_region_entry['uniprot_domain_region'].split('-')[1])
  
            # retrieve the missense, synonymous and background rates for a given protein region
            try:
                domain_result = analyse_dn_ds_over_protein_region(gene_mapping, domain_uniprot_start_pos-1, domain_uniprot_end_pos)
            except (RegionIsNotEncodedBycDNAException, RegioncDNALengthDoesNotEqualProteinLengthException, ExternalREFAlleleNotEqualsTranscriptionException) as e:
                logging.getLogger(LOGGER_NAME).error(e)
                failed_genes.append(gene_name)
                failed.append({'gene_name':gene_name,'error':e})
            
            if not(gene_name in failed_genes):
                dataset_entry = {\
                    "region_name":pfam_gene_region_entry['region_name'], \
                    "external_database_id":pfam_gene_region_entry['external_db_id'], \
                    "interpro_id":pfam_gene_region_entry['interpro_id'], \
                    "gene_name":gene_name, \
                    "gencode_transcription_id":gencode_transcription_id, \
                    "gencode_translation_name":gencode_translation_name, \
                    "gencode_gene_id":gencode_gene_id, \
                    "havana_gene_id":havana_gene_id, \
                    "havana_translation_id":havana_translation_id, \
                    "pdb_id":pdb_id, \
                    "swissprot_id":pfam_gene_region_entry['uniprot_ac'], \
                    "swissprot_start_pos":domain_uniprot_start_pos, \
                    "swissprot_end_pos":domain_uniprot_end_pos, \
                    "swissprot_length":domain_result["region_length"], \
                    "chromosome":domain_result["chromosome"], \
                    "chr_region":domain_result["chromosome_positions"], \
                    "domain_cdna_length":len(domain_result["cDNA"]), \
                    "background_missense_in_domain":domain_result["background_missense"], \
                    "background_synonymous_in_domain":domain_result["background_synonymous"], \
                    "background_nonsense_in_domain":domain_result["background_nonsense"], \
                    "exac_missense_in_domain":domain_result["exac_missense"], \
                    "exac_synonymous_in_domain":domain_result["exac_synonymous"], \
                    "exac_nonsense_in_domain":domain_result["exac_nonsense"], \
                    "clinvar_missense_in_domain":domain_result["clinvar_missense"],\
                    "clinvar_nonsense_in_domain":domain_result["clinvar_nonsense"],\
                    "clinvar_synonymous_in_domain":domain_result["clinvar_synonymous"],\
                    "hgmd_missense_in_domain":domain_result["hgmd_missense"], \
                    "hgmd_synonymous_in_domain":domain_result["hgmd_synonymous"], \
                    "hgmd_nonsense_in_domain":domain_result["hgmd_nonsense"], \
                    "exac_information_in_domain":domain_result["exac_information"], \
                    "hgmd_information_in_domain":domain_result["hgmd_information"], \
                    "clinvar_information_in_domain":domain_result["clinvar_information"],\
                    }
                    
                final_dataset.append(dataset_entry)
    try:
        logging.getLogger(LOGGER_NAME).info("Writing to data to file ...")
        final_dataset_df = pd.DataFrame(final_dataset)
        final_dataset_df.to_csv(output_domains, sep=";")
        logging.getLogger(LOGGER_NAME).info("Writing to data to file completed")
        
        logging.getLogger(LOGGER_NAME).info("Writing "+str(len(failed))+" failed genes to text file ...")
        failed_df = pd.DataFrame(failed)
        failed_df.to_csv(output_failures, sep=';')
        logging.getLogger(LOGGER_NAME).info("Writing failed genes to text file completed")
    except Exception as e:
        logging.getLogger(LOGGER_NAME).critical("Writing to text file failed due to: %s" % str(e))