import pandas as pd
from sklearn.externals.joblib.parallel import Parallel, delayed
from BGVM.MetaDomains.Database.database_queries import retrieve_all_meta_domains,\
    retrieve_all_meta_domain_ids
from BGVM.MetaDomains.Construction.meta_domain_merging import EXAC_TYPE_NAME, HGMD_TYPE_NAME
from BGVM.Tools.ParallelHelper import CalculateNumberOfActiveThreads

def get_total_exac_freq_for_pos(_merged_meta_domain, consensus_pos):
    return _merged_meta_domain[(_merged_meta_domain.entry_type == EXAC_TYPE_NAME) & (_merged_meta_domain.domain_consensus_pos == consensus_pos)]['ExAC_allele_frequency'].sum()

def get_total_exac_variants_for_pos(_merged_meta_domain, consensus_pos):
    return _merged_meta_domain[(_merged_meta_domain.entry_type == EXAC_TYPE_NAME) & (_merged_meta_domain.domain_consensus_pos == consensus_pos)]['ExAC_allele_frequency'].count()

def get_column_by_domain_id(df, domain_id, column_of_interest):
    indices = df.domain_id[df.domain_id == domain_id].index.tolist()
    # check if the id is unique
    assert len(indices) == 1
    index = indices[0]
    
    return df.get_value(index, column_of_interest)

def extract_aggregated_domain_variants(characteristic_variants_in_domains_df, domain_id_of_interest):
    L_x = get_column_by_domain_id(characteristic_variants_in_domains_df, domain_id_of_interest, 'L_x')
    N_x = get_column_by_domain_id(characteristic_variants_in_domains_df, domain_id_of_interest, 'n_domain_occurrences')
    C_x_J_strict = eval(get_column_by_domain_id(characteristic_variants_in_domains_df, domain_id_of_interest, 'C_x_J_strict'))
    C_x_J_unstrict = eval(get_column_by_domain_id(characteristic_variants_in_domains_df, domain_id_of_interest, 'C_x_J_unstrict'))
    M_x_J = eval(get_column_by_domain_id(characteristic_variants_in_domains_df, domain_id_of_interest, 'M_x_J'))
    N_x_J = eval(get_column_by_domain_id(characteristic_variants_in_domains_df, domain_id_of_interest, 'N_x_J'))
    
    ## Generate a dataframe for easy plotting
    aggregated_domain = []
    for j in range(L_x):
        aggregated_domain_entry = {}
        aggregated_domain_entry['domain_consensus_pos'] = j
        aggregated_domain_entry['C_x_j_strict'] = C_x_J_strict[j]
        aggregated_domain_entry['C_x_j_unstrict'] = C_x_J_unstrict[j]
        aggregated_domain_entry['N_x'] = N_x
        aggregated_domain_entry['N_x_j'] = N_x_J[j]
        aggregated_domain_entry['M_x_j'] = M_x_J[j]
        if M_x_J[j] > 0:
            aggregated_domain_entry['CMVS_j_unstrict'] = C_x_J_unstrict[j]/M_x_J[j]
            aggregated_domain_entry['CMVS_j_strict'] = C_x_J_strict[j]/M_x_J[j]
        else:
            aggregated_domain_entry['CMVS_j_unstrict'] = 0
            aggregated_domain_entry['CMVS_j_strict'] = 0

        aggregated_domain.append(aggregated_domain_entry)

    aggregated_domain_df = pd.DataFrame(aggregated_domain)
    
    return aggregated_domain_df, L_x, N_x

def merge_dataframe_for_characteristic_variants_per_position_over_a_single_meta_domain(meta_domain, dataframe_with_significance_of_characteristic_variants_in_all_domains, entry_type):
    domain_id = meta_domain['meta_domain']['domain_id']
        
    merged_meta_domain = pd.DataFrame(meta_domain['meta_domain']['merged_meta_domain'])
    
    aggregated_variant_sets_for_domain, L_x, N_x = extract_aggregated_domain_variants(dataframe_with_significance_of_characteristic_variants_in_all_domains, domain_id)
    
    assert len(dataframe_with_significance_of_characteristic_variants_in_all_domains[(dataframe_with_significance_of_characteristic_variants_in_all_domains.domain_id == domain_id)]) == 1
    
    aggregated_variant_sets_for_domain['p_val_unstrict_corrected'] = [x for x in dataframe_with_significance_of_characteristic_variants_in_all_domains[(dataframe_with_significance_of_characteristic_variants_in_all_domains.domain_id == domain_id)]['p_val_unstrict_corrected']][0]
    aggregated_variant_sets_for_domain['significant_unstrict_corrected'] = [x for x in dataframe_with_significance_of_characteristic_variants_in_all_domains[(dataframe_with_significance_of_characteristic_variants_in_all_domains.domain_id == domain_id)]['significant_unstrict_corrected']][0]
    aggregated_variant_sets_for_domain['total_exac_frequency'] = aggregated_variant_sets_for_domain.apply(lambda data_entry : get_total_exac_freq_for_pos(merged_meta_domain, data_entry.domain_consensus_pos), axis=1)
    aggregated_variant_sets_for_domain['total_exac_variants'] = aggregated_variant_sets_for_domain.apply(lambda data_entry : get_total_exac_variants_for_pos(merged_meta_domain, data_entry.domain_consensus_pos), axis=1) 
    aggregated_variant_sets_for_domain['mean_exac_frequency'] = aggregated_variant_sets_for_domain.apply(lambda data_entry : 0.0 if data_entry.total_exac_variants == 0 else data_entry.total_exac_frequency/data_entry.total_exac_variants, axis=1)
    aggregated_variant_sets_for_domain['domain_id'] = meta_domain['meta_domain']['domain_id']
    aggregated_variant_sets_for_domain['entry_type'] = entry_type
    aggregated_variant_sets_for_domain['L_x'] = L_x
    
    return aggregated_variant_sets_for_domain

def merge_dataframe_for_characteristic_variants_per_position_over_all_meta_domains(dataframe_with_significance_of_characteristic_variants_in_all_domains, entry_type, use_parallel):
    merged_aggregated_variant_sets_for_all_domain = []
    
    if use_parallel:
        meta_domain_ids = [x for x in retrieve_all_meta_domain_ids()]
        
        merged_aggregated_variant_sets_for_all_domain = Parallel(n_jobs=CalculateNumberOfActiveThreads(len(meta_domain_ids)))(delayed(merge_dataframe_for_characteristic_variants_per_position_over_a_single_meta_domain)(meta_domain, dataframe_with_significance_of_characteristic_variants_in_all_domains, entry_type) for meta_domain in retrieve_all_meta_domains())
    else:
        merged_aggregated_variant_sets_for_all_domain = [merge_dataframe_for_characteristic_variants_per_position_over_a_single_meta_domain(meta_domain, dataframe_with_significance_of_characteristic_variants_in_all_domains, entry_type) for meta_domain in retrieve_all_meta_domains()]
        
    return pd.concat(merged_aggregated_variant_sets_for_all_domain, ignore_index=True)
     