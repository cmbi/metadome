'''
Created on Dec 28, 2016

@author: laurens
'''
import pandas as pd
from BGVM.MetaDomains.Computations.meta_domain_characteristic_variant_analysis import merge_dataframe_for_characteristic_variants_per_position_over_all_meta_domains
from BGVM.MetaDomains.Construction.meta_domain_merging import EXAC_TYPE_NAME,\
    HGMD_TYPE_NAME
import logging
import time
from BGVM.Tools.CustomLogger import initLogging
from dev_settings import LOGGER_NAME, GENE2PROTEIN_META_DOMAIN_STATISTICS,\
    GENE2PROTEIN_ANNOTATED_HOMOLOGUE_DOMAINS_DATASET
from BGVM.MetaDomains.Computations.meta_domain_characteristic_variant_permutation import analyse_significance_of_characteristic_variants_in_all_domains
from BGVM.Domains.HomologuesDomains import annotate_homologue_domains_with_intolerance_scores,\
    load_homologue_domain_dataset

    
# # from BGVM.MetaDomains.Computations.meta_domain_characteristic_variant_analysis
# def analyse_permuted_variants():
#     print("This should only be used for debugging purposes"); exit(0)    
#     initLogging(print_to_console=True, logging_level=logging.DEBUG)
#         
#     ___significance_of_characteristic_ExAC_variants_in_all_domains_filename = '/media/laurens/LVDW_DATA/Gen_Prot_Mapping/results_16-aug-2016/significance_of_characteristic_ExAC_variants_in_all_domains'
#     ___significance_of_characteristic_HGMD_variants_in_all_domains_filename = '/media/laurens/LVDW_DATA/Gen_Prot_Mapping/results_16-aug-2016/significance_of_characteristic_HGMD_variants_in_all_domains'
# #     ___ExAC_merged_aggregated_variant_sets_for_all_domain_filename = '/media/laurens/LVDW_DATA/Gen_Prot_Mapping/results_16-aug-2016/ExAC_merged_aggregated_variant_sets_for_all_domain'
# #     ___HGMD_merged_aggregated_variant_sets_for_all_domain_filename = '/media/laurens/LVDW_DATA/Gen_Prot_Mapping/results_16-aug-2016/HGMD_merged_aggregated_variant_sets_for_all_domain'
#         
#     # Load dataset for significance_of_characteristic_ExAC_variants_in_all_domains
#     ___significance_of_characteristic_ExAC_variants_in_all_domains = pd.DataFrame.from_csv(___significance_of_characteristic_ExAC_variants_in_all_domains_filename, sep='\t')
#     ___significance_of_characteristic_HGMD_variants_in_all_domains = pd.DataFrame.from_csv(___significance_of_characteristic_HGMD_variants_in_all_domains_filename, sep='\t')
#         
#     # apply multiple correction
#     ___N_correction = len(___significance_of_characteristic_ExAC_variants_in_all_domains)
#     assert ___N_correction == len(___significance_of_characteristic_HGMD_variants_in_all_domains)
#     p_value_threshold = 0.05
#     # ExAC
#     ___significance_of_characteristic_ExAC_variants_in_all_domains['p_val_strict_corrected'] = ___significance_of_characteristic_ExAC_variants_in_all_domains.apply(lambda data_entry : data_entry.p_val_strict * ___N_correction, axis=1)
#     ___significance_of_characteristic_ExAC_variants_in_all_domains['significant_strict_corrected'] = ___significance_of_characteristic_ExAC_variants_in_all_domains.apply(lambda data_entry : data_entry.p_val_strict_corrected < p_value_threshold, axis=1)
#     ___significance_of_characteristic_ExAC_variants_in_all_domains['p_val_unstrict_corrected'] = ___significance_of_characteristic_ExAC_variants_in_all_domains.apply(lambda data_entry : data_entry.p_val_unstrict * ___N_correction, axis=1)
#     ___significance_of_characteristic_ExAC_variants_in_all_domains['significant_unstrict_corrected'] = ___significance_of_characteristic_ExAC_variants_in_all_domains.apply(lambda data_entry : data_entry.p_val_unstrict_corrected < p_value_threshold, axis=1)
#     # HGMD
#     ___significance_of_characteristic_HGMD_variants_in_all_domains['p_val_strict_corrected'] = ___significance_of_characteristic_HGMD_variants_in_all_domains.apply(lambda data_entry : data_entry.p_val_strict * ___N_correction, axis=1)
#     ___significance_of_characteristic_HGMD_variants_in_all_domains['significant_strict_corrected'] = ___significance_of_characteristic_HGMD_variants_in_all_domains.apply(lambda data_entry : data_entry.p_val_strict_corrected < p_value_threshold, axis=1)
#     ___significance_of_characteristic_HGMD_variants_in_all_domains['p_val_unstrict_corrected'] = ___significance_of_characteristic_HGMD_variants_in_all_domains.apply(lambda data_entry : data_entry.p_val_unstrict * ___N_correction, axis=1)
#     ___significance_of_characteristic_HGMD_variants_in_all_domains['significant_unstrict_corrected'] = ___significance_of_characteristic_HGMD_variants_in_all_domains.apply(lambda data_entry : data_entry.p_val_unstrict_corrected < p_value_threshold, axis=1)
#         
#     ___use_parallel = True
#         
# #     ___start_time = time.perf_counter()
# #     ___ExAC_merged_aggregated_variant_sets_for_all_domain = merge_dataframe_for_characteristic_variants_per_position_over_all_meta_domains(___significance_of_characteristic_ExAC_variants_in_all_domains, EXAC_TYPE_NAME, use_parallel=___use_parallel)
# #     ___time_step = time.perf_counter()
# #     logging.getLogger(LOGGER_NAME).info("Finished merging for ExAC in "+str(___time_step-___start_time)+" seconds")
# #         
# #     ___start_time = time.perf_counter()
# #     ___HGMD_merged_aggregated_variant_sets_for_all_domain = merge_dataframe_for_characteristic_variants_per_position_over_all_meta_domains(___significance_of_characteristic_HGMD_variants_in_all_domains, HGMD_TYPE_NAME, use_parallel=___use_parallel)
# #     ___time_step = time.perf_counter()
# #     logging.getLogger(LOGGER_NAME).info("Finished merging for HGMD in "+str(___time_step-___start_time)+" seconds")
#         
#     # write to disk
# #     ___ExAC_merged_aggregated_variant_sets_for_all_domain.to_csv(___ExAC_merged_aggregated_variant_sets_for_all_domain_filename, sep='\t')
# #     ___HGMD_merged_aggregated_variant_sets_for_all_domain.to_csv(___HGMD_merged_aggregated_variant_sets_for_all_domain_filename, sep='\t')