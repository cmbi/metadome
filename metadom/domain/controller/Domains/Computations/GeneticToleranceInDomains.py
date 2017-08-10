'''
Created on Oct 24, 2016

@author: laurens
'''
import numpy as np
from BGVM.Domains.HomologuesDomains import annotate_homologue_domains_with_intolerance_scores
from BGVM.Metrics.EvaluationMetrics import MedianAbsoluteDeviation_permutation
from sklearn.metrics.regression import mean_squared_error

def domain_intolerance_signal_analysis(domain_data,  domain_selection_name, score_of_interest, n_permutations, random_seed, original_y=None):
    """Computes metrics (e.g. MAD, MSE, MAE) across a given 
    domain data set based on a specific score of interest.
     
    This analysis tests the assumption that the mean/median 
    (in)tolerance over an aggregation of homologue 
    domains, should be similar to the intolerance
    score for each of those domain entries"""
    # Ensure we keep the randomness under control and maintain reproducable results
    np.random.seed(random_seed)
     
    # Create the result and add info
    result = {"score_of_interest":score_of_interest, "domain_selection_name":domain_selection_name, "domain_occurences":len(domain_data), "n_permutations":n_permutations, "random_seed":random_seed}
     
    # Group the data by the domain identifiers and add info to results
    group_of_domain_ids = domain_data.groupby(['external_database_id'])
    result['unique_domains'] = len(group_of_domain_ids)
    result['unique_homologue_domains'] = len(group_of_domain_ids)
 
    # add the doain summaries to the result
    result['domain_summaries'] = annotate_homologue_domains_with_intolerance_scores(domain_data, score_of_interest)
     
    # Check if a original y is provided, if not, use the y of current dataset
    if original_y is None:
        original_y = result['domain_summaries']
     
    # Permute the y labels and see how strong the signal in this dataset is
    for i in range(n_permutations):
        # create a permutation
        random_domain_summaries = np.random.permutation(original_y)
         
        # save the mean score per permutation
        random_permutation_mean = []
        random_permutation_median = []
        for index, domain_summary in enumerate(result['domain_summaries']):            
            if not 'random_MAD' in domain_summary.keys():
                domain_summary['random_MAD'] = []
            if not 'random_MSE' in domain_summary.keys():
                domain_summary['random_MSE'] = []
             
            y_i = np.ones_like(domain_summary['domain_entries'])
            y_i = y_i * random_domain_summaries[index]['mean']
             
            # Add the MAD and MSE to the set
            domain_summary['random_MAD'].append(MedianAbsoluteDeviation_permutation(data=domain_summary['domain_entries'], permuted_data=random_domain_summaries[index]['domain_entries']))
            domain_summary['random_MSE'].append(mean_squared_error(y_i, domain_summary['domain_entries']))
             
            # add the current mean and median score to the set
            random_permutation_mean.append(random_domain_summaries[index]['mean'])
            random_permutation_median.append(random_domain_summaries[index]['median'])
         
        if not 'average_random_permutation_mean' in result.keys():
            result['average_random_permutation_mean'] = []
             
        if not 'average_random_permutation_median' in result.keys():
            result['average_random_permutation_median'] = []
             
        # add the random permutation means and medians to the results
        result['average_random_permutation_mean'].append(random_permutation_mean)
        result['average_random_permutation_median'].append(random_permutation_median)
         
    return result