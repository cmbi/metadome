'''
Created on Aug 17, 2016

@author: laurens
'''
import pandas as pd
import numpy as np
from BGVM.MetaDomains.Database.database_queries import retrieve_all_meta_domains,\
    retrieve_all_meta_domain_ids
from BGVM.MetaDomains.Construction.meta_domain_merging import EXAC_TYPE_NAME, HGMD_TYPE_NAME,\
    HG19_REFERENCE_TYPE_NAME
from sklearn.externals.joblib.parallel import Parallel, delayed
from BGVM.Tools.ParallelHelper import CalculateNumberOfActiveThreads
from BGVM.Tools.CustomLogger import initLogging
import logging
from dev_settings import LOGGER_NAME
import time

def analyse_all_merged_meta_domains(meta_domain_analysis_filename):
    meta_domain_analysis_df = pd.DataFrame.from_csv(meta_domain_analysis_filename, sep='\t')
    
    n_characteristic_snps = 0
    n_unique_characteristic_snps = 0
    n_characteristic_muts = 0
    n_unique_characteristic_muts = 0
    n_no_variants_perseverance = 0
    total_positions = 0
    total_occurrences = 0
    total_snps = 0
    total_muts = 0
    total_meta_domains = 0
    domains_without_any_variation = 0
    domains_without_any_snps = 0
    domains_without_any_muts = 0
    domain_occurrences_without_any_muts = 0
    domain_occurrences_without_any_snps = 0
    domain_occurrences_without_any_variation = 0
    n_pure_characteristic_snps = 0
    n_unique_pure_characteristic_snps = 0
    n_pure_characteristic_muts = 0
    n_unique_pure_characteristic_muts = 0
    n_overlapping_characteristic_muts_snps = 0
    n_unique_overlapping_characteristic_muts_snps = 0
    n_overlapping_single_muts_snps = 0
    n_unique_overlapping_single_muts_snps = 0
    
    # lists of domain ids that contain specific variations
    domains_with_snps = []
    domains_with_only_snps = []
    domains_with_characteristic_snps = []
    domains_with_muts = []
    domains_with_only_muts = []
    domains_with_characteristic_muts = []
    
    meta_domains = retrieve_all_meta_domains()
    for meta_domain_entry in meta_domains:
        domain_id = meta_domain_entry["domain_id"]
        meta_domain = meta_domain_entry['meta_domain']
        ExAC_HGMD_merge = pd.DataFrame(meta_domain['merged_meta_domain'])        
        total_meta_domains += 1
        total_positions += len(meta_domain['consensus_sequence'])
        total_occurrences += len(pd.unique(ExAC_HGMD_merge.domain_identifier))
        n_snps = len(ExAC_HGMD_merge[(ExAC_HGMD_merge.entry_type == EXAC_TYPE_NAME)])
        n_muts = len(ExAC_HGMD_merge[(ExAC_HGMD_merge.entry_type == HGMD_TYPE_NAME)])
        total_snps += n_snps
        total_muts += n_muts
        
        # check if there is no mutation in this domain
        if n_muts == 0 and n_snps == 0:
            domains_without_any_variation += 1
        
        # check if there are any mutations in this domain
        if n_muts > 0:
            domains_with_muts.append(domain_id)
        elif n_muts == 0:
            domains_without_any_muts += 1
            # if there are snps in this domain, then there are only snps
            if n_snps > 0:
                domains_with_only_snps.append(domain_id)
        
        # check if there are any snp variations in this domain
        if n_snps > 0:
            domains_with_snps.append(domain_id)
        elif n_snps == 0:
            domains_without_any_snps += 1
            # if there are muts in this domain, then there are only snps
            if n_muts > 0:
                domains_with_only_muts.append(domain_id)
        
              
        occurrence_grouping = ExAC_HGMD_merge.groupby('domain_identifier')
        for identifier, group in occurrence_grouping:
            n_occurence_snps = len(group[(group.entry_type == EXAC_TYPE_NAME)])
            n_occurence_muts = len(group[(group.entry_type == HGMD_TYPE_NAME)])
              
            if n_occurence_muts == 0:
                domain_occurrences_without_any_muts += 1
            if n_occurence_snps == 0:
                domain_occurrences_without_any_snps += 1
            if n_occurence_snps == 0 and n_occurence_muts == 0:
                domain_occurrences_without_any_variation += 1
        
        # group this domain based on the consensus positions
        meta_domain_analysis_group = meta_domain_analysis_df[meta_domain_analysis_df.domain_id == domain_id].groupby(['domain_consensus_pos'])
        
        # iterate over each position and analyse the variants there
        domain_contains_characteristic_snp = False
        domain_contains_characteristic_mut = False
        for domain_consensus_pos, group in meta_domain_analysis_group:
            entry_types = group['entry_type'].tolist()
            if HG19_REFERENCE_TYPE_NAME in entry_types:
                n_no_variants_perseverance += 1
                assert len(entry_types) == 1
            else:
                # retrieve the variants and occurrences across meta domain (for both muts and snps) for the current position
                variants = group['variant'].tolist()
                variant_counts = group['variant_count'].tolist()
                
                variants_count = dict()
                assert len(variants) == len(entry_types)
                for index, variant in enumerate(variants):
                    if not variant in variants_count.keys():
                        variants_count[variant] = {EXAC_TYPE_NAME:0, HGMD_TYPE_NAME:0}
                    
                    variants_count[variant][entry_types[index]] += variant_counts[index]
                
                for variant in variants_count.keys():
                    # Variants that are SNPs and occur on the same consensus position across multiple domain occurrences of the same domain within HG19
                    if variants_count[variant][EXAC_TYPE_NAME] > 1:
                        n_unique_characteristic_snps += 1
                        n_characteristic_snps += variants_count[variant][EXAC_TYPE_NAME]
                        domain_contains_characteristic_snp = True
                    
                    # Variants that are MUTs and occur on the same consensus position across multiple domain occurrences of the same domain within HG19
                    if variants_count[variant][HGMD_TYPE_NAME] > 1:
                        n_unique_characteristic_muts += 1
                        n_characteristic_muts += variants_count[variant][HGMD_TYPE_NAME]
                        domain_contains_characteristic_mut = True
                        
                    # Variants that only occur as SNPs and the same consensus position across multiple domain occurrences of the same domain within HG19
                    if variants_count[variant][EXAC_TYPE_NAME] > 1 and variants_count[variant][HGMD_TYPE_NAME] == 0:
                        n_pure_characteristic_snps += variants_count[variant][EXAC_TYPE_NAME]
                        n_unique_pure_characteristic_snps += 1
                    
                    # Variants that only occur as MUTs and the same consensus position across multiple domain occurrences of the same domain within HG19
                    if variants_count[variant][EXAC_TYPE_NAME] == 0 and variants_count[variant][HGMD_TYPE_NAME] > 1:
                        n_pure_characteristic_muts += variants_count[variant][HGMD_TYPE_NAME]
                        n_unique_pure_characteristic_muts += 1
                    
                    # Variants that are both MUTs and SNPs and occur on the same consensus position across multiple domain occurrences of the same domain within HG19
                    if (variants_count[variant][EXAC_TYPE_NAME] > 1 and variants_count[variant][HGMD_TYPE_NAME] >= 1) or (variants_count[variant][EXAC_TYPE_NAME] >= 1 and variants_count[variant][HGMD_TYPE_NAME] > 1):
                        n_overlapping_characteristic_muts_snps += variants_count[variant][HGMD_TYPE_NAME] + variants_count[variant][EXAC_TYPE_NAME]
                        n_unique_overlapping_characteristic_muts_snps += 1
                    
                    # Variants that are a single MUT and a single SNPs on the same consensus position across multiple domain occurrences of the same domain within HG19
                    if variants_count[variant][EXAC_TYPE_NAME] == 1 and variants_count[variant][HGMD_TYPE_NAME] == 1:
                        n_overlapping_single_muts_snps += variants_count[variant][HGMD_TYPE_NAME] + variants_count[variant][EXAC_TYPE_NAME]
                        n_unique_overlapping_single_muts_snps += 1
                
        # Check if the domain contains a characteristic mut 
        if domain_contains_characteristic_mut:
            domains_with_characteristic_muts.append(domain_id)
            
        # Check if the domain contains a characteristic snp
        if domain_contains_characteristic_snp:
            domains_with_characteristic_snps.append(domain_id)
                    
    print_str ="===== STATISTICS OVER ALL META DOMAINS =====\n"
    print_str +="===== GENERAL STATISTICS =====\n"
    print_str +="Homologue domains: "+str(total_meta_domains)+"\n"
    print_str +="Homologue domain occurrences: "+str(total_occurrences)+"\n"
    print_str +="Total meta domain size (aggregation of all domain sizes): "+str(total_positions)+"\n"
    print_str +="Number of domains with snps: "+str(len(domains_with_snps))+"\n"
    print_str +="Number of domains with only snps: "+str(len(domains_with_only_snps))+"\n"
    print_str +="Number of domains with characteristic snps: "+str(len(domains_with_characteristic_snps))+"\n"
    print_str +="Number of domains with muts: "+str(len(domains_with_muts))+"\n"
    print_str +="Number of domains with only muts: "+str(len(domains_with_only_muts))+"\n"
    print_str +="Number of domains with characteristic muts: "+str(len(domains_with_characteristic_muts))+"\n"
    print_str +="\n"
    assert (len(domains_with_snps)-(len(domains_with_muts)-len(domains_with_only_muts))) == len(domains_with_only_snps)
    print_str +="===== ARE SNPs CHARACTERISTIC FOR A POSITION ? =====\n"
    print_str +="Total number of snps in all domains: "+str(total_snps)+"\n"
    print_str +="Average number of snps in all domains: "+str(total_snps/total_occurrences)+"\n"
    print_str +="Average number of snps per position (in domains): "+str(total_snps/total_positions)+"\n"
    print_str +="Count of characteristic variants that occur multiply as the same SNP on the same domain consensus: "+str(n_characteristic_snps)+", unique: "+str(n_unique_characteristic_snps)+"\n"
    print_str +="Count of PURE characteristic variants that occur only as a multiply of the same SNP on the same domain consensus (no MUTs known): "+str(n_pure_characteristic_snps)+", unique: "+str(n_unique_pure_characteristic_snps)+"\n"
    print_str +="\n"
    print_str +="===== ARE MUTs CHARACTERISTIC FOR A POSITION ? =====\n"
    print_str +="Total number of muts in all domains: "+str(total_muts)+"\n"
    print_str +="Average number of muts in all domains: "+str(total_muts/total_occurrences)+"\n"
    print_str +="Average number of muts per position (in domains): "+str(total_muts/total_positions)+"\n"
    print_str +="Count of characteristic variants that occur multiply as the same MUT on the same domain consensus: "+str(n_characteristic_muts)+", unique: "+str(n_unique_characteristic_muts)+"\n"
    print_str +="Count of PURE characteristic variants that occur only as a multiply of the same MUT on the same domain consensus (no SNPs known): "+str(n_pure_characteristic_muts)+", unique: "+str(n_unique_pure_characteristic_muts)+"\n"
    print_str +="\n"
    print_str +="===== OVERLAP =====\n"
    print_str +="A 'characteristic' variant that occurs multiple times as both a MUT and a SNPs on the same consensus position: "+str(n_overlapping_characteristic_muts_snps)+", unique: "+str(n_unique_overlapping_characteristic_muts_snps)+"\n"
    print_str +="A variant that occurs as a single MUT and a single SNPs on the same consensus position: "+str(n_overlapping_single_muts_snps)+", unique: "+str(n_unique_overlapping_single_muts_snps)+"\n"
    print_str +="\n"
    print_str +="===== ABSENCE OF VARIATION =====\n"
    print_str +="domains without any variation: "+str(domains_without_any_variation)+"\n"
    print_str +="domain occurrences without any variation: "+str(domain_occurrences_without_any_variation)+"\n"
    print_str +="domains without any snps: "+str(domains_without_any_snps)+"\n"
    print_str +="domain occurrences without any snps: "+str(domain_occurrences_without_any_snps)+"\n"
    print_str +="domains without any muts: "+str(domains_without_any_muts)+"\n"
    print_str +="domain occurrences without any muts: "+str(domain_occurrences_without_any_muts)+"\n"
    print_str +="positions without any variation: "+str(n_no_variants_perseverance)+"\n"
    print_str +="Percentage of positions without any variation: "+str(n_no_variants_perseverance/total_positions)
       
    print(print_str)

def annotate_variant(entry):
    if entry.entry_type == HG19_REFERENCE_TYPE_NAME:
        return ''
    return entry.ref_residue+">"+entry.alt_residue

def construct_single_meta_domain_analysis_dataset_entry(meta_domain_entry, domain_dataset):
    meta_domain_analysis = []

    # load the data for this domain
    meta_domain = meta_domain_entry['meta_domain']
    ExAC_HGMD_merge = pd.DataFrame(meta_domain['merged_meta_domain'])
 
    # add the variant as an annotation
    ExAC_HGMD_merge['variant'] = ExAC_HGMD_merge.apply(lambda data_entry: annotate_variant(data_entry), axis=1)
         
    # how many pos
    meta_domain_size = len(meta_domain['consensus_sequence'])
    domain_of_interest_domain_data = domain_dataset[(domain_dataset.external_database_id == meta_domain['domain_id'])]
    n_domain_occurrences = len(domain_of_interest_domain_data)
    n_domain_in_gene_occurrences = len(pd.unique(domain_of_interest_domain_data.gene_name))
    n_domain_in_meta_domain_occurrences = len(pd.unique(ExAC_HGMD_merge.domain_identifier))
     
    exac_group = ExAC_HGMD_merge[(ExAC_HGMD_merge.entry_type == EXAC_TYPE_NAME)].groupby('domain_consensus_pos')
    hgmd_group = ExAC_HGMD_merge[(ExAC_HGMD_merge.entry_type == HGMD_TYPE_NAME)].groupby('domain_consensus_pos')
 
    all_group = ExAC_HGMD_merge.groupby('domain_consensus_pos')
    for domain_consensus_pos, group in all_group:
        entry_types = group['entry_type'].tolist()
  
        if HG19_REFERENCE_TYPE_NAME in np.unique(entry_types) and len(np.unique(entry_types)) == 1:
            entry = {'domain_consensus_pos':int(domain_consensus_pos),
                     'entry_type':HG19_REFERENCE_TYPE_NAME, 
                     'domain_id':meta_domain['domain_id'],
                     'variant':'no_variant', 
                     'variant_count':0, 
                     'meta_domain_size':meta_domain_size,
                     'n_domain_occurrences_in_meta_domain':n_domain_in_meta_domain_occurrences,
                     'n_domain_occurrences':n_domain_occurrences,
                     'n_domain_in_gene_occurrences':n_domain_in_gene_occurrences,}
            meta_domain_analysis.append(entry)
  
    for domain_consensus_pos, group in exac_group:
        ExAC_variants = group['variant'].tolist()
        for i in np.unique(ExAC_variants):
            entry = {'domain_consensus_pos':int(domain_consensus_pos), 
                     'entry_type':EXAC_TYPE_NAME, 
                     'domain_id':meta_domain['domain_id'],
                     'variant':i, 
                     'variant_count':ExAC_variants.count(i), 
                     'meta_domain_size':meta_domain_size,
                     'n_domain_occurrences_in_meta_domain':n_domain_in_meta_domain_occurrences,
                     'n_domain_occurrences':n_domain_occurrences,
                     'n_domain_in_gene_occurrences':n_domain_in_gene_occurrences,}
            meta_domain_analysis.append(entry)
  
    for domain_consensus_pos, group in hgmd_group:
        HGMD_variants = group['variant'].tolist()
        for i in np.unique(HGMD_variants):
            entry = {'domain_consensus_pos':int(domain_consensus_pos), 
                     'entry_type':HGMD_TYPE_NAME, 
                     'domain_id':meta_domain['domain_id'],
                     'variant':i, 
                     'variant_count':HGMD_variants.count(i), 
                     'meta_domain_size':meta_domain_size,
                     'n_domain_occurrences_in_meta_domain':n_domain_in_meta_domain_occurrences,
                     'n_domain_occurrences':n_domain_occurrences,
                     'n_domain_in_gene_occurrences':n_domain_in_gene_occurrences,}
            meta_domain_analysis.append(entry)
    
    return meta_domain_analysis        
    
def construct_meta_domain_statistics_dataset(domain_dataset, filename, use_parallel):
    logging.getLogger(LOGGER_NAME).info("Started creating the merged domain data statistics dataset")
    start_time = time.clock()
    
    # perform the analysis (e.g. aggregation)
    meta_domain_ids = [domain_id for domain_id in retrieve_all_meta_domain_ids()]
    
    if use_parallel:
        meta_domain_analysis = Parallel(n_jobs=CalculateNumberOfActiveThreads(len(meta_domain_ids)))(delayed(construct_single_meta_domain_analysis_dataset_entry)(meta_domain_entry, domain_dataset) for meta_domain_entry in retrieve_all_meta_domains())        
    else:
        meta_domain_analysis = [construct_single_meta_domain_analysis_dataset_entry(meta_domain_entry, domain_dataset) for meta_domain_entry in retrieve_all_meta_domains()]
    
    time_step = time.clock()
    logging.getLogger(LOGGER_NAME).info("Finished creating the merged domain data statistics dataset in "+str(time_step-start_time)+" seconds")
    
    # flatten the list
    meta_domain_analysis =  [val for sublist in meta_domain_analysis for val in sublist]
    
    # Set the results in a dataframe
    meta_domain_analysis_df = pd.DataFrame(meta_domain_analysis)
 
    # Safe the dataframe
    meta_domain_analysis_df.to_csv(filename, sep='\t')
