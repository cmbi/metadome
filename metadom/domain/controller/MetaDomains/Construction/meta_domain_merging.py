'''
Created on Aug 9, 2016

@author: laurens
'''

import pandas as pd
import numpy as np
from BGVM.Statistics.codon_statistics import calculate_codon_report

HG19_REFERENCE_TYPE_NAME = "HG19_ref"
HG_HSSP_TYPE_NAME = "HG_HSSP"
HGMD_TYPE_NAME = "HGMD"
EXAC_TYPE_NAME = "ExAC"

def annotate_alt_residues_per_domain_consensus_pos(position, data, entry_type):
    return str([x for x in data[(data.domain_consensus_pos == position) & (data.entry_type == entry_type)]['alt_residue']])

def annotate_variants_per_domain_consensus_pos(position, data, entry_type):
    return str([x[0]+">"+x[1] for x in data[(data.domain_consensus_pos == position)  & (data.entry_type == entry_type)][['ref_residue','alt_residue']].values])

def retrieve_field_of_interest_for_entry_per_domain_consensus_pos(position, data, entry_type, field_of_interest):
    for index, item in data[(data.domain_consensus_pos == position) & (data.entry_type == entry_type)].iterrows():
        return item[field_of_interest] 
    return []


def alt_residue_occurs_in_both_HGMD_and_ExAC_as_alt_meta_domain(entry):
    if entry.entry_type == HG19_REFERENCE_TYPE_NAME or entry.entry_type == HG_HSSP_TYPE_NAME:
        return False
    
    exac_list = entry.ExAC_alt_residues
    hgmd_list = entry.HGMD_alt_residues
    
    return ((entry.alt_residue in exac_list) and (entry.alt_residue in hgmd_list))

def variant_occurs_in_both_HGMD_and_ExAC_as_variant_meta_domain(entry):
    if entry.entry_type == HG19_REFERENCE_TYPE_NAME or entry.entry_type == HG_HSSP_TYPE_NAME:
        return False
    
    exac_list = entry.ExAC_variants
    hgmd_list = entry.HGMD_variants
    
    variant = entry.ref_residue+">"+entry.alt_residue
    
    return ((variant in exac_list) and (variant in hgmd_list))

def merge_meta_domain(meta_domain, filter_ExAC_AF=None, filter_missense_only=False):
    # Load the meta domain annotation for ExAC and HGMD
    ExAC_meta_domain = pd.DataFrame(meta_domain['ExAC'])
    HGMD_meta_domain = pd.DataFrame(meta_domain['HGMD'])
    Reference_meta_domain = pd.DataFrame(meta_domain['reference'])

    ExAC_meta_domain_columns = ['ExAC_alt_residues', 'entry_type', 'domain_identifier', 'domain_consensus_pos', 'consensus_domain_residue', 'ref_residue', 'alt_residue', 'ref_codon', 'alt_codon', 'ExAC_allele_frequency', 'uniprot_ac', 'uniprot_name', 'swissprot_pos', 'gene_name', 'gencode_gene_id', 'gencode_transcription_id', 'gencode_translation_name']
    HGMD_meta_domain_columns = ['HGMD_alt_residues', 'entry_type', 'domain_identifier', 'domain_consensus_pos', 'consensus_domain_residue', 'ref_residue', 'alt_residue', 'ref_codon', 'alt_codon', 'HGMD_Phenotype', 'HGMD_Prot', 'HGMD_MUT', 'HGMD_Dna', 'HGMD_STRAND', 'uniprot_ac', 'uniprot_name', 'swissprot_pos', 'gene_name', 'gencode_gene_id', 'gencode_transcription_id', 'gencode_translation_name']
    
    if len(ExAC_meta_domain) == 0:
        for column in ExAC_meta_domain_columns:
            ExAC_meta_domain[column] = np.nan
    if len(HGMD_meta_domain) == 0:
        for column in HGMD_meta_domain_columns:
            HGMD_meta_domain[column] = np.nan                            

    # add the entry types to each set, so we can find each set again after merge
    Reference_meta_domain['entry_type'] = HG19_REFERENCE_TYPE_NAME
    HGMD_meta_domain['entry_type'] = HGMD_TYPE_NAME
    ExAC_meta_domain['entry_type'] = EXAC_TYPE_NAME
    
    # Filter ExAC on population frequence
    if not(filter_ExAC_AF is None) and type(filter_ExAC_AF) == float:
        ExAC_meta_domain = ExAC_meta_domain[(ExAC_meta_domain.ExAC_allele_frequency > filter_ExAC_AF)]
    
    # Annotate the merged set with any ExAC and HGMD alt-residues that may occur at that point
    if len(ExAC_meta_domain) != 0:
        if filter_missense_only:
            # Filter ExAC on missense only
            ExAC_meta_domain = ExAC_meta_domain[(ExAC_meta_domain.alt_residue != ExAC_meta_domain.ref_residue) & (ExAC_meta_domain.alt_residue != '*')]
        # check if after filtering there is anything left
        if len(ExAC_meta_domain) != 0:
            ExAC_meta_domain['ExAC_alt_residues'] = ExAC_meta_domain.apply(lambda data_entry: annotate_alt_residues_per_domain_consensus_pos(data_entry['domain_consensus_pos'], ExAC_meta_domain, entry_type=EXAC_TYPE_NAME), axis=1)
            ExAC_meta_domain['ExAC_variants'] = ExAC_meta_domain.apply(lambda data_entry: annotate_variants_per_domain_consensus_pos(data_entry['domain_consensus_pos'], ExAC_meta_domain, entry_type=EXAC_TYPE_NAME), axis=1)
    
    # Annotate the merged set with any ExAC and HGMD variants that may occur at that point
    if len(HGMD_meta_domain) != 0:
        if filter_missense_only:
            # Filter HGMD on missense only
            HGMD_meta_domain = HGMD_meta_domain[(HGMD_meta_domain.alt_residue != HGMD_meta_domain.ref_residue) & (HGMD_meta_domain.alt_residue != '*')]
        # check if after filtering there is anything left
        if len(HGMD_meta_domain) != 0:
            HGMD_meta_domain['HGMD_variants'] = HGMD_meta_domain.apply(lambda data_entry: annotate_variants_per_domain_consensus_pos(data_entry['domain_consensus_pos'], HGMD_meta_domain, entry_type=HGMD_TYPE_NAME), axis=1)
            HGMD_meta_domain['HGMD_alt_residues'] = HGMD_meta_domain.apply(lambda data_entry: annotate_alt_residues_per_domain_consensus_pos(data_entry['domain_consensus_pos'], HGMD_meta_domain, entry_type=HGMD_TYPE_NAME), axis=1)
    
    # Merge HGMD and ExAC
    merged_meta_domain = pd.concat([ExAC_meta_domain, HGMD_meta_domain, Reference_meta_domain,])

    # Annotate the merged set with any ExAC and HGMD alt-residues that may occur at that point
    merged_meta_domain['ExAC_alt_residues'] = merged_meta_domain.apply(lambda data_entry: retrieve_field_of_interest_for_entry_per_domain_consensus_pos(data_entry['domain_consensus_pos'], merged_meta_domain, entry_type=EXAC_TYPE_NAME, field_of_interest='ExAC_alt_residues'), axis=1)
    merged_meta_domain['HGMD_alt_residues'] = merged_meta_domain.apply(lambda data_entry: retrieve_field_of_interest_for_entry_per_domain_consensus_pos(data_entry['domain_consensus_pos'], merged_meta_domain, entry_type=HGMD_TYPE_NAME, field_of_interest='HGMD_alt_residues'), axis=1)
    
    # Annotate the merged set with any ExAC and HGMD variants that may occur at that point
    merged_meta_domain['ExAC_variants'] = merged_meta_domain.apply(lambda data_entry: retrieve_field_of_interest_for_entry_per_domain_consensus_pos(data_entry['domain_consensus_pos'], merged_meta_domain, entry_type=EXAC_TYPE_NAME, field_of_interest='ExAC_variants'), axis=1)
    merged_meta_domain['HGMD_variants'] = merged_meta_domain.apply(lambda data_entry: retrieve_field_of_interest_for_entry_per_domain_consensus_pos(data_entry['domain_consensus_pos'], merged_meta_domain, entry_type=HGMD_TYPE_NAME, field_of_interest='HGMD_variants'), axis=1)

    # Annotate alt residues and variants that occur in both ExAC and HGMD at that 'meta' position
    merged_meta_domain['identical_ExAC_HGMD_alt_residue'] =  merged_meta_domain.apply(lambda data_entry: alt_residue_occurs_in_both_HGMD_and_ExAC_as_alt_meta_domain(data_entry), axis=1)
    merged_meta_domain['identical_ExAC_HGMD_variant'] =  merged_meta_domain.apply(lambda data_entry: variant_occurs_in_both_HGMD_and_ExAC_as_variant_meta_domain(data_entry), axis=1)

    # Append the possible residues to the set
    merged_meta_domain['possible_missense_alt_residues'] = merged_meta_domain.apply(lambda data_entry: calculate_codon_report(data_entry['ref_codon'])['missense_alt_residues'], axis=1)
    merged_meta_domain['missense_probability'] = merged_meta_domain.apply(lambda data_entry: calculate_codon_report(data_entry['ref_codon'])['missense_probability'], axis=1)
    merged_meta_domain['synonymous_probability'] = merged_meta_domain.apply(lambda data_entry: calculate_codon_report(data_entry['ref_codon'])['synonymous_probability'], axis=1)
    merged_meta_domain['nonsense_probability'] = merged_meta_domain.apply(lambda data_entry: calculate_codon_report(data_entry['ref_codon'])['nonsense_probability'], axis=1)
    merged_meta_domain['nonsynonymous_probability'] = merged_meta_domain.apply(lambda data_entry: calculate_codon_report(data_entry['ref_codon'])['nonsynonymous_probability'], axis=1)
     
    # Specify how we want the column order and sort 
    merged_meta_domain_column_sort = ['domain_identifier', 'domain_consensus_pos', 'consensus_domain_residue', 'ref_residue', 'alt_residue', 'ExAC_allele_frequency', 'HGMD_Phenotype', 'possible_missense_alt_residues', 'missense_probability', 'ref_codon', 'alt_codon', 'ExAC_alt_residues', 'ExAC_variants', 'HGMD_alt_residues', 'HGMD_variants', 'identical_ExAC_HGMD_alt_residue', 'identical_ExAC_HGMD_variant', 'synonymous_probability', 'nonsense_probability', 'nonsynonymous_probability', 'HGMD_Prot', 'HGMD_MUT', 'HGMD_Dna', 'HGMD_STRAND', 'uniprot_ac', 'uniprot_name', 'swissprot_pos', 'gene_name', 'gencode_gene_id', 'gencode_transcription_id', 'gencode_translation_name','entry_type',]
    merged_meta_domain=merged_meta_domain[merged_meta_domain_column_sort]
    
    return merged_meta_domain