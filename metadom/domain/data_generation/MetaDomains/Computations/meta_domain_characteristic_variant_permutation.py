'''
Created on Aug 31, 2016

@author: laurens
'''
import pandas as pd
import numpy as np
from scipy.stats.stats import ttest_ind
from sklearn.externals.joblib.parallel import Parallel, delayed
from BGVM.MetaDomains.Database.database_queries import retrieve_single_meta_domain, retrieve_all_meta_domains, retrieve_all_meta_domain_ids
from BGVM.MetaDomains.Construction.meta_domain_merging import EXAC_TYPE_NAME,\
    HG19_REFERENCE_TYPE_NAME, HGMD_TYPE_NAME
from BGVM.Tools.ParallelHelper import CalculateNumberOfActiveThreads
from dev_settings import LOGGER_NAME,\
    GENE2PROTEIN_ANNOTATED_HOMOLOGUE_DOMAINS_DATASET
import logging
from BGVM.Domains.HomologuesDomains import load_homologue_domain_dataset,\
    annotate_homologue_domains_with_intolerance_scores
import time
from BGVM.Metrics.EvaluationMetrics import cohen_d

def generate_random_variants(X, X_prime, p_missense_x, p_missense_residue_x):
    # create the permutation
    X_prime_permutation = dict()
    
    # iterate over domain occurrences i
    for i in sorted(X.keys()):
        # add occurence i as a key to the dict
        X_prime_permutation[i] = dict()
        
        # calculate the number of (probably) non-damaging missense variants in this domain 
        M_x_i = np.sum([len(x_prime_i_j) for x_prime_i_j in X_prime[i].values()])
        # retrieve the number of matching consensus positions for this domain
        len_J_x = len(X[i].keys())
        
        # See Eq (2)
        if M_x_i == 0:
            p_high_frequency_missense_x_i = 1 / len_J_x
        else:
            p_high_frequency_missense_x_i = (1 / len_J_x) * M_x_i
        
        for j in sorted(X[i].keys()):    
            # see Eq (12)
            p_high_frequency_missense_x_i_j = p_high_frequency_missense_x_i * p_missense_x[i][j]
            
            for alt_res in sorted(p_missense_residue_x[i][j].keys()):
                # roll the dice
                random_var = np.random.rand()
                
                if p_missense_residue_x[i][j][alt_res] * p_high_frequency_missense_x_i_j >= random_var:
                    if not( j in X_prime_permutation[i].keys() ):
                        X_prime_permutation[i][j] = []
                    X_prime_permutation[i][j].append(alt_res)
                    
    return X_prime_permutation

def count_variants(X, X_prime, L_x):
    # ensure we are dealing with the same X's:
    assert X.keys() == X_prime.keys()
    for key in X.keys():
        for x_prime_key in X_prime[key].keys():
            assert x_prime_key in X[key].keys()
     
    # Let us create the counting variables
    variant_counts = dict()
    single_variant_counts = dict()
    N_x_J = dict()
    
    # iterate over the consensus domain positions
    for j in range(L_x):
        variant_counts[j] = dict()
        single_variant_counts[j] = 0
        N_x_J[j] = len(X.keys())
        
        # iterate over domain occurrences i 
        for i in X.keys():
            # no need to check domains with that are not aligned to consensus at position j
            if j not in X[i].keys():
                assert j not in X_prime[i].keys()
                N_x_J[j] -= 1
                continue
            
            # no need to check domains with no variation at position j
            if j not in X_prime[i].keys():
                continue
        
            unique_X_prime_i_j = np.unique(X_prime[i][j])
            if len(X_prime[i][j]) != len(unique_X_prime_i_j):
                logging.getLogger(LOGGER_NAME).warning("Variant list (X_prime_i_j) was not unique for "+i+"at position "+str(j))
            
            if len(unique_X_prime_i_j) > 0:
                # if at least one variant is found in this gene increment the single_variant_counts with 1
                single_variant_counts[j] += 1
            
            # be sure we are not comparing the same occurrences
            for X_prime_i_j in  unique_X_prime_i_j:
                if X[i][j] == X_prime_i_j:
                    logging.getLogger(LOGGER_NAME).warning("Variant list (X_prime_i_j) contained a synonymous variant for domain "+i+"at position "+str(j))
                    continue
                
                variant_key = X[i][j]+">"+X_prime_i_j
                
                if not variant_key in variant_counts[j]:
                    variant_counts[j][variant_key] = 0
                variant_counts[j][variant_key] += 1
            
    for j in N_x_J.keys():
        assert N_x_J[j] >= 0
        
    return variant_counts, single_variant_counts, N_x_J

def count_characteristic_variants(variant_counts):
    # Let us create the counting variables
    unstrict_characteristic_variants_count = 0 
    strict_characteristic_variants_count = 0
    unstrict_characteristic_variants = dict()
    strict_characteristic_variants = dict()
    
    # iterate over the consensus domain positions
    for j in sorted(variant_counts.keys()):
        processed_variants = []
        unstrict_characteristic_variants[j] = dict()
        strict_characteristic_variants[j] = dict()
        
        for variant_key in sorted(variant_counts[j].keys()):
            if variant_key in processed_variants:
                continue
            variant_key_splitted = variant_key.split(">")
            inverted_variant_key = variant_key_splitted[1]+">"+variant_key_splitted[0]
            
            processed_variants.append(variant_key)
            processed_variants.append(inverted_variant_key)
            
            unstrict_variant_key = variant_key_splitted[0]+"<->"+variant_key_splitted[1]
    
            if inverted_variant_key in variant_counts[j].keys():
                if variant_counts[j][inverted_variant_key] > 1:
                    # strict variant
                    strict_characteristic_variants_count += variant_counts[j][inverted_variant_key]
                    strict_characteristic_variants[j][inverted_variant_key] = variant_counts[j][inverted_variant_key]
                    
                if variant_counts[j][variant_key]+variant_counts[j][inverted_variant_key] > 1:
                    # unstrict variant
                    unstrict_characteristic_variants_count += variant_counts[j][variant_key]+variant_counts[j][inverted_variant_key]
                    unstrict_characteristic_variants[j][unstrict_variant_key] = variant_counts[j][variant_key]+variant_counts[j][inverted_variant_key]
            
            if variant_counts[j][variant_key] > 1:
                # strict variant
                strict_characteristic_variants_count += variant_counts[j][variant_key]
                strict_characteristic_variants[j][variant_key] = variant_counts[j][variant_key]
                
                if not unstrict_variant_key in unstrict_characteristic_variants[j].keys():
                    unstrict_characteristic_variants_count += variant_counts[j][variant_key]
                    unstrict_characteristic_variants[j][unstrict_variant_key] = variant_counts[j][variant_key]
            
    return strict_characteristic_variants_count, unstrict_characteristic_variants_count, strict_characteristic_variants, unstrict_characteristic_variants
    
def count_total_variants(x_prime):
    return np.sum([np.sum([len(x_prime_i_j) for x_prime_i_j in x_prime[i].values()]) for i in x_prime.keys()])

def compute_characteristic_missense_variant_score(variant_counts, characteristic_variant_counts, L_x):
    """ Calculates the characteristic missense variant score for the number of
    characteristic missense variants, based on the number of total missense variants.
    A normalized score is also computed, based on the total length of the meta domain.
    
    Input:
    variant_counts - dictionary of variant counts for a meta domain (expected format: {pos:{'variant':count})
    characteristic_variant_counts - dictionary of characteristic variant counts for the same meta domain (expected format: {pos:{'variant':count})
    L_x - Integer representing the total domain length
    
    Returns:
    characteristic_missense_variant_score, 
    normalized_characteristic_missense_variant_score
    """
    C_x_J = dict()
    M_x_J = dict()
    characteristic_missense_variant_score = 0.0
    M_x = 0 # total missense variants
    C_x = 0 # total characteristic variants
    for j in variant_counts.keys():
        # count total missense variants across meta domain position j
        M_x_J[j] = int(np.sum(list(variant_counts[j].values())))
        # count total characteristic missense variants across meta domain position j
        C_x_J[j] = int(np.sum(list(characteristic_variant_counts[j].values())))
        
        # increment overall totals
        M_x += M_x_J[j]
        C_x += C_x_J[j]
        
        # characteristic variants cannot be  larger than the number of missense variants at the same position
        assert C_x_J[j] <= M_x_J[j]
        
        if M_x_J[j] == 0:
            # skip this entry to prevent a divide by zero exception
            continue
        
        # compute the score
        characteristic_missense_variant_score += (C_x_J[j]/M_x_J[j])
        
    # Normalize the score by the total length of the domain
    normalized_characteristic_missense_variant_score = characteristic_missense_variant_score / L_x

    return characteristic_missense_variant_score, normalized_characteristic_missense_variant_score, C_x_J, M_x_J

def permute_domain_variation(x, x_prime, p_missense_x, p_missense_residue_x, L_x):
    X_prime_random = generate_random_variants(x, x_prime, p_missense_x, p_missense_residue_x)
    permuted_variant_counts, permuted_single_variant_counts, _ = count_variants(x, X_prime_random, L_x)
    permuted_n_strict_characteristic_variants, permuted_n_unstrict_characteristic_variants, permuted_strict_characteristic_variants, permuted_unstrict_characteristic_variants = count_characteristic_variants(permuted_variant_counts)
    
    return permuted_variant_counts, permuted_n_strict_characteristic_variants, permuted_n_unstrict_characteristic_variants, permuted_strict_characteristic_variants, permuted_unstrict_characteristic_variants


def extract_x_and_x_prime(merged_meta_domain, group_of_interest, adjusted_observed_variant_percentage=None):
    # construct variant and missense probability sets
    x = dict()
    x_prime = dict() 
    p_missense_x = dict()
    p_missense_residue_x = dict()
    for i, single_domain in merged_meta_domain.groupby('domain_identifier'):
        # create x_i
        x[i] = dict() 
        x_prime[i] = dict() 
        p_missense_x[i] = dict()
        p_missense_residue_x[i] = dict()
        
        single_domain = single_domain.sort_values('domain_consensus_pos')
        cur_cons_sequence = ''
        domain_sequence = ''
        for domain_position in single_domain.index:
            j = single_domain.domain_consensus_pos[domain_position]
            # append x_{i,j}
            x[i][j] = single_domain.ref_residue[domain_position]
            p_missense_x[i][j] = single_domain.missense_probability[domain_position]
            p_missense_residue_x[i][j] = single_domain.possible_missense_alt_residues[domain_position]
            
            if single_domain.entry_type[domain_position] == group_of_interest:
                # check if we are using the full observed data or only a percentage
                if not adjusted_observed_variant_percentage is None:
                    use_in_analysis = np.random.rand() < adjusted_observed_variant_percentage
                else:
                    use_in_analysis = True
                    
                if use_in_analysis:
                    if not( j in x_prime[i].keys() ):
                        x_prime[i][j] = []
                    x_prime[i][j].append(single_domain.alt_residue[domain_position])
            cur_cons_sequence += single_domain.consensus_domain_residue[domain_position]
            domain_sequence += single_domain.ref_residue[domain_position]
    
    return x, x_prime, p_missense_x, p_missense_residue_x

def analyse_meta_domain_variants(x, x_prime, L_x):
    meta_domain_variant_analysis = {}
    meta_domain_variant_analysis["M_x"] = count_total_variants(x_prime)
    meta_domain_variant_analysis["L_x"] = L_x
    meta_domain_variant_analysis["variant_counts"], meta_domain_variant_analysis["M_unique_x_j"], meta_domain_variant_analysis["N_x_J"] = count_variants(x, x_prime, L_x)
    meta_domain_variant_analysis["n_strict_characteristic_variants"], meta_domain_variant_analysis["n_unstrict_characteristic_variants"], meta_domain_variant_analysis["strict_characteristic_variants"], meta_domain_variant_analysis["unstrict_characteristic_variants"] = count_characteristic_variants(meta_domain_variant_analysis["variant_counts"])
    meta_domain_variant_analysis["strict_characteristic_missense_variant_score"], meta_domain_variant_analysis["strict_normalized_characteristic_missense_variant_score"], meta_domain_variant_analysis["strict_C_x_J"], meta_domain_variant_analysis["M_x_J"] = compute_characteristic_missense_variant_score(meta_domain_variant_analysis["variant_counts"], meta_domain_variant_analysis["strict_characteristic_variants"], L_x)
    meta_domain_variant_analysis["unstrict_characteristic_missense_variant_score"], meta_domain_variant_analysis["unstrict_normalized_characteristic_missense_variant_score"], meta_domain_variant_analysis["unstrict_C_x_J"], M_x_j = compute_characteristic_missense_variant_score(meta_domain_variant_analysis["variant_counts"], meta_domain_variant_analysis["unstrict_characteristic_variants"], L_x)
    
    # count the percentage of positions in a column wher a variant occurs versus the number of columns
    assert sorted(meta_domain_variant_analysis["M_unique_x_j"].keys()) == sorted(meta_domain_variant_analysis["N_x_J"].keys())
    meta_domain_variant_analysis["ratio_M_unique_x_j"] = {}
    for j in meta_domain_variant_analysis["M_unique_x_j"].keys():
        if meta_domain_variant_analysis["N_x_J"][j] == 0:
            meta_domain_variant_analysis["ratio_M_unique_x_j"][j]  = 0
            continue
        
        meta_domain_variant_analysis["ratio_M_unique_x_j"][j] = meta_domain_variant_analysis["M_unique_x_j"][j]/meta_domain_variant_analysis["N_x_J"][j]
    
    assert M_x_j == meta_domain_variant_analysis["M_x_J"] 
    
    return meta_domain_variant_analysis
    
def generate_report_meta_domain_variant_analysis(set_name, meta_domain_variant_analysis):
    report_string = set_name+": "+str(meta_domain_variant_analysis["M_x"])+\
                ", C_x[strict]="+str(meta_domain_variant_analysis["n_strict_characteristic_variants"])+\
                ", CMVS[strict]="+str(meta_domain_variant_analysis["strict_characteristic_missense_variant_score"])+\
                ", NCMVS[strict]="+str(meta_domain_variant_analysis["strict_normalized_characteristic_missense_variant_score"])+\
                ", C_x[unstrict]="+str(meta_domain_variant_analysis["n_unstrict_characteristic_variants"])+\
                ", CMVS[unstrict]="+str(meta_domain_variant_analysis["unstrict_characteristic_missense_variant_score"])+\
                ", NCMVS[unstrict]="+str(meta_domain_variant_analysis["unstrict_normalized_characteristic_missense_variant_score"])
                
    return report_string

def generate_permutations_characteristic_meta_domain_variations(domain_id, merged_meta_domain, L_x, n_permutations=50, random_seed_value=1, group_of_interest=EXAC_TYPE_NAME, adjusted_observed_variant_percentage=None):
    # first set the seed for repeatable results
    np.random.seed(random_seed_value)
    
    # Extract necessary domain information
    x, x_prime, p_missense_x, p_missense_residue_x = extract_x_and_x_prime(merged_meta_domain, group_of_interest, adjusted_observed_variant_percentage)
    meta_domain_variant_analysis = analyse_meta_domain_variants(x, x_prime, L_x)
    
    # report on domain analysis information
    if adjusted_observed_variant_percentage is None:
        logging.getLogger(LOGGER_NAME).info(generate_report_meta_domain_variant_analysis("Original domain of: "+domain_id, meta_domain_variant_analysis))
    else:
        logging.getLogger(LOGGER_NAME).info(generate_report_meta_domain_variant_analysis("Original ("+str(adjusted_observed_variant_percentage)+" percentage) domain of: "+domain_id, meta_domain_variant_analysis))
    
    
    # generate variation permutations for this meta domain
    permutations_meta_domain_variant_analysis = []
    for E in range(n_permutations):
        # generate random variants in this meta domain
        X_prime_random = generate_random_variants(x, x_prime, p_missense_x, p_missense_residue_x)
        permuted_meta_domain_variant_analysis = analyse_meta_domain_variants(x, X_prime_random, L_x)
        # report on domain analysis information
        logging.getLogger(LOGGER_NAME).info(generate_report_meta_domain_variant_analysis("Permutation ("+str(E+1)+"/"+str(n_permutations)+") of "+domain_id, permuted_meta_domain_variant_analysis))
        
        # add the results to the set
        permutations_meta_domain_variant_analysis.append(permuted_meta_domain_variant_analysis)
        
    return meta_domain_variant_analysis, permutations_meta_domain_variant_analysis

def check_significance_of_characteristic_variants(meta_domain_variant_analysis, permutations_meta_domain_variant_analysis, key_to_check, assume_equal_variance):
    # construct the sets that are going to be used in stat significance checks
    original_characteristic_variant_significance_check_input = []
    permuted_characteristic_variant_significance_check_input = []
    
    original_characteristic_variant_significance_check_input_value = meta_domain_variant_analysis[key_to_check]
    
    for x in permutations_meta_domain_variant_analysis:
        original_characteristic_variant_significance_check_input.append(original_characteristic_variant_significance_check_input_value)
        permuted_characteristic_variant_significance_check_input.append(x[key_to_check])
        
    result = ttest_ind(original_characteristic_variant_significance_check_input, permuted_characteristic_variant_significance_check_input, equal_var=assume_equal_variance)
    cohens_d_value = cohen_d(original_characteristic_variant_significance_check_input, permuted_characteristic_variant_significance_check_input) 
    
    return result.statistic, result.pvalue, cohens_d_value, original_characteristic_variant_significance_check_input_value, permuted_characteristic_variant_significance_check_input

def check_significance_of_variants_ratios(meta_domain_variant_analysis, permutations_meta_domain_variant_analysis, assume_equal_variance):
    ratio_M_unique_x_j_t_stat,  ratio_M_unique_x_j_p_value, ratio_M_unique_x_j_cohens_d = {}, {}, {}
    original_variant_ratio_significance_check_input_value_x_j = {}
    permuted_variant_ratio_significance_check_input_x_j = {}
    percentage_of_significant_variant_ratios = 0
    
    for j in meta_domain_variant_analysis["ratio_M_unique_x_j"].keys():
        # construct the sets that are going to be used in stat significance checks
        original_variant_ratio_significance_check_input = []
        permuted_variant_ratio_significance_check_input = []
        
        for x in permutations_meta_domain_variant_analysis:
            original_variant_ratio_significance_check_input.append(meta_domain_variant_analysis["ratio_M_unique_x_j"][j])
            permuted_variant_ratio_significance_check_input.append(x["ratio_M_unique_x_j"][j])
        
        result = ttest_ind(original_variant_ratio_significance_check_input, permuted_variant_ratio_significance_check_input, equal_var=assume_equal_variance)
        cohens_d_value = cohen_d(original_variant_ratio_significance_check_input, permuted_variant_ratio_significance_check_input) 
        
        # test statistical significance while correcting for the number of tests
        ratio_M_unique_x_j_t_stat[j] = result.statistic
        ratio_M_unique_x_j_p_value[j] = result.pvalue * meta_domain_variant_analysis["L_x"]
        ratio_M_unique_x_j_cohens_d[j] = cohens_d_value
        permuted_variant_ratio_significance_check_input_x_j[j] = permuted_variant_ratio_significance_check_input
        original_variant_ratio_significance_check_input_value_x_j[j] = meta_domain_variant_analysis["ratio_M_unique_x_j"][j]
        
        if ratio_M_unique_x_j_p_value[j] < 0.05:
            percentage_of_significant_variant_ratios += 1
    
    percentage_of_significant_variant_ratios /= meta_domain_variant_analysis["L_x"]
    
    return ratio_M_unique_x_j_t_stat, ratio_M_unique_x_j_p_value, ratio_M_unique_x_j_cohens_d, original_variant_ratio_significance_check_input_value_x_j, permuted_variant_ratio_significance_check_input_x_j, percentage_of_significant_variant_ratios


def analyse_significance_of_characteristic_variants_in_a_single_domains(domain_intolerance_signals, tolerance_score_name, meta_domain, n_permutations, random_seed_value, group_of_interest, adjusted_observed_variant_percentage):
    domain_id = meta_domain['domain_id']
    domain_intolerance_signal = [x for x in domain_intolerance_signals if x['external_database_id'] == domain_id]
    assert len(domain_intolerance_signal) == 1
    domain_median_intolerance = domain_intolerance_signal[0]['median']
    domain_MAD_intolerance = domain_intolerance_signal[0]['MAD']
    
    # retrieve the domain of interest
    merged_meta_domain = pd.DataFrame(meta_domain['meta_domain']['merged_meta_domain'])
    
    # count the number of domain occurences for this meta domain 
    n_domain_occurrences = len(pd.unique(merged_meta_domain.domain_identifier))
    
    # permute the domain and analyse it
    meta_domain_variant_analysis, permutations_meta_domain_variant_analysis = generate_permutations_characteristic_meta_domain_variations(domain_id, merged_meta_domain, len(meta_domain['meta_domain']['consensus_sequence']), n_permutations, random_seed_value, group_of_interest, adjusted_observed_variant_percentage)
    
    # check for statistical significance
    ratio_M_unique_x_j_t_stat, ratio_M_unique_x_j_p_value, ratio_M_unique_x_j_cohens_d, original_variant_ratio_significance_check_input_value_x_j, permuted_variant_ratio_significance_check_input_x_j, percentage_of_significant_variant_ratios = check_significance_of_variants_ratios(meta_domain_variant_analysis, permutations_meta_domain_variant_analysis, assume_equal_variance=True)
    t_stat_strict, p_val_strict, cohens_d_value_strict, original_strict_characteristic_variant_significance_check_input_value, permuted_strict_characteristic_variant_significance_check_input = check_significance_of_characteristic_variants(meta_domain_variant_analysis, permutations_meta_domain_variant_analysis, key_to_check="strict_normalized_characteristic_missense_variant_score",  assume_equal_variance=True)
    t_stat_unstrict, p_val_unstrict, cohens_d_value_unstrict, original_unstrict_characteristic_variant_significance_check_input_value, permuted_unstrict_characteristic_variant_significance_check_input = check_significance_of_characteristic_variants(meta_domain_variant_analysis, permutations_meta_domain_variant_analysis, key_to_check="unstrict_normalized_characteristic_missense_variant_score",  assume_equal_variance=True)
    
    logging.getLogger(LOGGER_NAME).info(domain_id+" NCMVS[strict] vs permuted("+str(n_permutations)+"x) NCMVS[strict] t-statistic: "+str(t_stat_strict)+", p-value: "+str(p_val_strict))
    logging.getLogger(LOGGER_NAME).info(domain_id+" NCMVS[unstrict] vs permuted("+str(n_permutations)+"x) NCMVS[unstrict] t-statistic: "+str(t_stat_unstrict)+", p-value: "+str(p_val_unstrict))
    
    meta_domain_analysis_result = {"domain_id":domain_id,\
                                   "tolerance_score":tolerance_score_name,\
                                   "median_tolerance_score":domain_median_intolerance,\
                                   "MAD_tolerance_score":domain_MAD_intolerance,\
                                   "n_domain_occurrences":n_domain_occurrences,\
                                   "L_x": meta_domain_variant_analysis["L_x"],\
                                   "M_x":meta_domain_variant_analysis["M_x"],\
                                   "M_x_J":meta_domain_variant_analysis["M_x_J"],\
                                   "N_x_J":meta_domain_variant_analysis["N_x_J"],\
                                   "ratio_M_unique_x_j":meta_domain_variant_analysis["ratio_M_unique_x_j"],\
                                   "M_unique_x_j":meta_domain_variant_analysis["M_unique_x_j"],\
                                   "C_x_J_strict":meta_domain_variant_analysis["strict_C_x_J"],\
                                   "C_x_strict":meta_domain_variant_analysis["n_strict_characteristic_variants"],\
                                   "C_x_J_unstrict":meta_domain_variant_analysis["unstrict_C_x_J"],\
                                   "C_x_unstrict":meta_domain_variant_analysis["n_unstrict_characteristic_variants"],\
                                   "CMVS_strict":meta_domain_variant_analysis["strict_characteristic_missense_variant_score"],\
                                   "NCMVS_strict":meta_domain_variant_analysis["strict_normalized_characteristic_missense_variant_score"],\
                                   "CMVS_unstrict":meta_domain_variant_analysis["unstrict_characteristic_missense_variant_score"],\
                                   "NCMVS_unstrict":meta_domain_variant_analysis["unstrict_normalized_characteristic_missense_variant_score"],\
                                   "t_stat_strict":t_stat_strict,\
                                   "p_val_strict":p_val_strict,\
                                   "cohens_d_val_strict":cohens_d_value_strict,\
                                   "t_stat_unstrict":t_stat_unstrict,\
                                   "p_val_unstrict":p_val_unstrict,\
                                   "cohens_d_val_unstrict":cohens_d_value_unstrict,\
                                   "original_unstrict_characteristic_variant_significance_check_input_value":original_unstrict_characteristic_variant_significance_check_input_value, \
                                   "permuted_unstrict_characteristic_variant_significance_check_input":permuted_unstrict_characteristic_variant_significance_check_input,\
                                   "original_strict_characteristic_variant_significance_check_input_value":original_strict_characteristic_variant_significance_check_input_value, \
                                   "permuted_strict_characteristic_variant_significance_check_input":permuted_strict_characteristic_variant_significance_check_input,\
                                   "ratio_M_unique_x_j_p_value":ratio_M_unique_x_j_p_value,\
                                   "ratio_M_unique_x_j_t_stat":ratio_M_unique_x_j_t_stat,\
                                   "ratio_M_unique_x_j_cohens_d":ratio_M_unique_x_j_cohens_d,\
                                   "original_variant_ratio_significance_check_input_value_x_j":original_variant_ratio_significance_check_input_value_x_j,\
                                   "permuted_variant_ratio_significance_check_input_x_j":permuted_variant_ratio_significance_check_input_x_j,\
                                   "percentage_of_significant_variant_ratios":percentage_of_significant_variant_ratios,\
                                   }
   
    return  meta_domain_analysis_result


def analyse_significance_of_characteristic_variants_in_all_domains(_domain_intolerance_signals, _tolerance_score_of_interest, n_permutations=100, random_seed_value=1, group_of_interest=EXAC_TYPE_NAME, use_parallel=False, adjusted_observed_variant_percentage = None):
    results = []
    if use_parallel:
        meta_domain_ids = [x for x in retrieve_all_meta_domain_ids()]
        
        results = Parallel(n_jobs=CalculateNumberOfActiveThreads(len(meta_domain_ids)))(delayed(analyse_significance_of_characteristic_variants_in_a_single_domains)(_domain_intolerance_signals, _tolerance_score_of_interest, meta_domain, n_permutations, random_seed_value, group_of_interest, adjusted_observed_variant_percentage) for meta_domain in retrieve_all_meta_domains())
    else:
        results = [analyse_significance_of_characteristic_variants_in_a_single_domains(_domain_intolerance_signals, _tolerance_score_of_interest, meta_domain, n_permutations, random_seed_value, group_of_interest, adjusted_observed_variant_percentage) for meta_domain in retrieve_all_meta_domains()]
        
    return results

def create_characteristic_variants_dataset(filename, group_of_interest, n_permutations=100, random_seed_value=1, use_parallel=True, tolerance_score_of_interest="background_corrected_missense_synonymous_ratio", adjusted_observed_variant_percentage=None):
    # Dataset containing the tolerance scores per domain
    homologue_domains = load_homologue_domain_dataset(GENE2PROTEIN_ANNOTATED_HOMOLOGUE_DOMAINS_DATASET)
    # retrieve intolerance sigma for this domain
    domain_intolerance_signals = annotate_homologue_domains_with_intolerance_scores(homologue_domains, tolerance_score_of_interest)

    # Save the results
    start_time = time.perf_counter()
    results = pd.DataFrame(analyse_significance_of_characteristic_variants_in_all_domains(domain_intolerance_signals, tolerance_score_of_interest, n_permutations, random_seed_value, group_of_interest, use_parallel, adjusted_observed_variant_percentage))
    # apply multiple correction
    N_correction = len(results)
    p_value_threshold = 0.05
    results['p_val_strict_corrected'] = results.apply(lambda data_entry : data_entry.p_val_strict * N_correction, axis=1)
    results['significant_strict_corrected'] = results.apply(lambda data_entry : data_entry.p_val_strict_corrected < p_value_threshold, axis=1)
    results['p_val_unstrict_corrected'] = results.apply(lambda data_entry : data_entry.p_val_unstrict * N_correction, axis=1)
    results['significant_unstrict_corrected'] = results.apply(lambda data_entry : data_entry.p_val_unstrict_corrected < p_value_threshold, axis=1)
    results['n_gene_occurences'] = results.apply(lambda data_entry : len(pd.unique(homologue_domains[homologue_domains.external_database_id == data_entry.domain_id].gene_name)), axis=1)
    
    # add the adjusted_observed_variant_percentage to the results
    if adjusted_observed_variant_percentage is None:
        adjusted_observed_variant_percentage = 1.0
    results['adjusted_observed_variant_percentage'] = adjusted_observed_variant_percentage
    
    pd.DataFrame(results).to_csv(filename, sep='\t')
    time_step = time.perf_counter()
    logging.getLogger(LOGGER_NAME).info("Finished permuting domains with '"+group_of_interest+"' variants in "+str(time_step-start_time)+" seconds")