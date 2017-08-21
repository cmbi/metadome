import logging

from BGVM.MetaDomains.Construction.meta_domain_merging import EXAC_TYPE_NAME,\
    HG19_REFERENCE_TYPE_NAME
from BGVM.Mapping.Gene2ProteinMappingDatabase import retrieve_single_gene_entries
import numpy as np

_log = logging.getLogger(__name__)

def compute_logo_information_content_for_amino_acid_per_pos(amino_acid_entropy_per_pos, amino_acid_frequencies_per_pos, s=20):
    """ Computes the information content needed to construct a sequence logo.
    
    Information content (R_i) for a given position i is provided as:
    H_i = f_{a,i} * R_i
    R_i = log_2(s) - (H_i + e_n)
    H_i is the Shannon entropy for position i
    H_i = - \sum(f_{a,i} * log_2(f_{a,i}))
    e_n is the small-sample correction;
    e_n = \frac{1}{ln(2)}*\frac{s-1}{2n}
    s = 20 for amino acids and 4 for nucleotides
    
    Requires the aggregated amino acid frequencies. 
    Expects the input in the form of
    {position:
        {'A': freq_A, 
            ..., 
            'Y': freq_Y, 
         'count':residue_counts}
      ...}
      
    Requires the relative entropy per position. 
    Expects the input in the form of
    {position:
        {'A': relent_A, 
            ..., 
            'Y': relent_Y, 
         'count':residue_counts,
         'total_relent': total_relent}
      ...}
    """
    information_content_per_pos = {}
    for position in amino_acid_entropy_per_pos.keys():
        information_content_per_pos[position] = {}
        n_i = len(amino_acid_entropy_per_pos[position].keys())
        e_n_i = (1/np.log(2))*((s-1)/(2*n_i))
        H_i = amino_acid_entropy_per_pos[position]['total_entropy']
        R_i = np.log2(s)-(H_i+e_n_i)
        
        total_height = 0.0
        for key in amino_acid_entropy_per_pos[position].keys():
            if key == 'total_entropy': continue
            if key == 'total_relative_entropy': continue
            try:
                f_a_i = amino_acid_frequencies_per_pos[position][key]/amino_acid_frequencies_per_pos[position]['count']
            except ZeroDivisionError:
                f_a_i = 0.0
            information_content_per_pos[position][key] = f_a_i * R_i
            
            total_height += information_content_per_pos[position][key]
        information_content_per_pos[position]['total_information_content'] = total_height
            
    return information_content_per_pos


def compute_entropy_for_aggregated_amino_acid_frequences(aggregated_amino_acid_frequencies_per_pos, s=20):
    """Computes the relative entropy and relative entropy for aggregated
    amino acid frequencies per position. 
    
    H_i is the Shannon entropy for position i
    H_i = - \sum(f_{a,i} * log_2(f_{a,i}))

    
    Expects the input in the form of
     {position:
        {'A': freq_A, 
            ..., 
            'Y': freq_Y, 
         'count':residue_counts}
      ...}
    """
    entropy_amino_acid_per_pos = {}
    for position in aggregated_amino_acid_frequencies_per_pos.keys():
        entropy_amino_acid_per_pos[position] = {}
        total_entropy = 0.0
        for key in aggregated_amino_acid_frequencies_per_pos[position].keys():
            if key == 'count': continue
            try:
                f_a_i = aggregated_amino_acid_frequencies_per_pos[position][key]/aggregated_amino_acid_frequencies_per_pos[position]['count']
            except ZeroDivisionError:
                f_a_i = 0.0
                
            if f_a_i == 0.0:
                entropy_amino_acid_per_pos[position][key] = 0.0
            else:
                entropy_amino_acid_per_pos[position][key] = - (f_a_i * np.log2(f_a_i))
            total_entropy += entropy_amino_acid_per_pos[position][key]
        entropy_amino_acid_per_pos[position]['total_entropy'] = total_entropy
        entropy_amino_acid_per_pos[position]['total_relative_entropy'] = total_entropy/np.log2(s)
    
    return entropy_amino_acid_per_pos

def aggregate_amino_acid_ExAC_frequences_in_merged_meta_domain(merged_meta_domain):
    """Extracts the ExAC frequencies for merged homologues
     domains across genes"""
    fields_of_interest = merged_meta_domain[['domain_identifier', 'consensus_domain_residue', 'domain_consensus_pos', 'ref_residue', 'alt_residue', 'ExAC_allele_frequency', 'entry_type', 'gene_name']][(merged_meta_domain.entry_type == EXAC_TYPE_NAME) | (merged_meta_domain.entry_type  == HG19_REFERENCE_TYPE_NAME)].sort_values('domain_consensus_pos')

    # pos: residue: count: freq
    list_of_domain_distributions_per_pos = []
    for domain_consensus_pos, merged_domain_group in fields_of_interest.groupby('domain_consensus_pos'):
        for domain_identifier, single_domain in merged_domain_group.groupby('domain_identifier'):
            # create the null distribution, will be filled in based
            # on this position in this domain's occurrence
            single_domain_distribution_pos = {
                 'A': 0.0, 'C': 0.0, 'D': 0.0, 'E': 0.0,
                 'F': 0.0, 'G': 0.0, 'H': 0.0, 'I': 0.0,
                 'K': 0.0, 'L': 0.0, 'M': 0.0, 'N': 0.0,
                 'P': 0.0, 'Q': 0.0, 'R': 0.0, 'S': 0.0, 
                 'T': 0.0, 'V': 0.0, 'W': 0.0, 'Y': 0.0, 
                 'pos': domain_consensus_pos, 'id':domain_identifier}
            if len(single_domain.domain_identifier) > 1:
                ref_residue = None
                total_not_ref_AF = 0.0

                for row_index, row in single_domain.iterrows():
                    if row.entry_type == HG19_REFERENCE_TYPE_NAME:
                        ref_residue = row.ref_residue
                    else:
                        if not row.entry_type == EXAC_TYPE_NAME:
                            raise Exception('Found other entry type besides ExAC and HG19 reference')
                        single_domain_distribution_pos[row.alt_residue] += row.ExAC_allele_frequency
                        total_not_ref_AF += row.ExAC_allele_frequency

                # set ref residue AF to 1 - all other AF for this position
                if ref_residue is None:
                    raise Exception('Found multiple entries for position: '+str(domain_consensus_pos)+' id: '+str(domain_identifier)+', but no REFERENCE')

                single_domain_distribution_pos[ref_residue] = 1.0 - total_not_ref_AF
                
                if total_not_ref_AF > 1.0:
                    # in case the distribution is no longer correct, fix it
                    single_domain_distribution_pos[ref_residue] = single_domain_distribution_pos[ref_residue] * -1
                    total_not_ref_AF += single_domain_distribution_pos[ref_residue]
                    
                    for residue in single_domain_distribution_pos.keys():
                        if residue not in ['id', 'pos']:
                            single_domain_distribution_pos[residue] /= total_not_ref_AF
                            
            elif len(single_domain.domain_identifier) == 1:
                if single_domain.entry_type.item() == EXAC_TYPE_NAME:
                    # There may have been a mismatch between the translation used and swissprot
                    # first we check if this is the case, and f so use the ExAC reference
                    # otherwse we throw an error
                    print('For '+str(domain_identifier)+', at domain_consensus_pos '+str(domain_consensus_pos)+' expected HG19, but found '+str(single_domain.entry_type.item()))
                    # retrieve the gene mapping
                    gene_mapping = retrieve_single_gene_entries(single_domain.gene_name.item())['gene_mapping']
                    if not gene_mapping['translation_used']['sequence'] == gene_mapping['uniprot']['sequence']:
                        # there is a mismatch between the gene translation and the swissprot used,
                        # so we can use the ExAC reference
                        print('For '+str(domain_identifier)+', at domain_consensus_pos '+str(domain_consensus_pos)+' the gene_translation did not match the swissprot translation, therefore we use the exac reference as the hg19 genome reference')
                        single_domain_distribution_pos[single_domain.alt_residue.item()] = single_domain.ExAC_allele_frequency.item()
                        single_domain_distribution_pos[single_domain.ref_residue.item()] = 1.0 - single_domain_distribution_pos[single_domain.alt_residue.item()]
                    else:
                        # the gene translation and swissprot used do match, there must be 
                        # something else that is wrong. 
                        raise Exception('For '+str(domain_identifier)+', at domain_consensus_pos '+str(domain_consensus_pos)+' expected HG19, but found '+str(single_domain.entry_type.item())+", but the swissprot and gene translation do match")
                elif single_domain.entry_type.item() == HG19_REFERENCE_TYPE_NAME:
                    # no ExAC information, set ref residue to probability 1.0
                    single_domain_distribution_pos[single_domain.ref_residue.item()] = 1.0
                else:
                    raise Exception('For '+str(domain_identifier)+', at domain_consensus_pos '+str(domain_consensus_pos)+' expected HG19, but found '+str(single_domain.entry_type.item()))
            else:
                raise Exception('Found other entry type besides ExAC and HG19 reference')
            # append the distributions for this position to the main list
            list_of_domain_distributions_per_pos.append(single_domain_distribution_pos)

    # aggregate the distributions found for this position
    aggregated_distributions_per_pos = {}
    for single_domain_distribution_pos in list_of_domain_distributions_per_pos:
        domain_consensus_pos = single_domain_distribution_pos['pos']
        if not domain_consensus_pos in aggregated_distributions_per_pos.keys():
            aggregated_distributions_per_pos[single_domain_distribution_pos['pos']] = {
                 'A': 0.0, 'C': 0.0, 'D': 0.0, 'E': 0.0,
                 'F': 0.0, 'G': 0.0, 'H': 0.0, 'I': 0.0,
                 'K': 0.0, 'L': 0.0, 'M': 0.0, 'N': 0.0,
                 'P': 0.0, 'Q': 0.0, 'R': 0.0, 'S': 0.0, 
                 'T': 0.0, 'V': 0.0, 'W': 0.0, 'Y': 0.0, 
                 'count':0}

        for key in single_domain_distribution_pos.keys():
            if key in aggregated_distributions_per_pos[domain_consensus_pos].keys():
                aggregated_distributions_per_pos[domain_consensus_pos][key] += single_domain_distribution_pos[key]

        aggregated_distributions_per_pos[domain_consensus_pos]['count'] += 1

    # check if the counts equal the cumalitive probability
    for position in aggregated_distributions_per_pos.keys():
        count = aggregated_distributions_per_pos[position]['count']
        total_count = 0.0
        total_prob = 0.0
        
        if count > 0:
            for key in aggregated_distributions_per_pos[position].keys():
                if key != 'count':
                    total_count += aggregated_distributions_per_pos[position][key]
                    prob = aggregated_distributions_per_pos[position][key] / count

                    total_prob += prob
            
        assert np.round(total_prob,1) == 1.0
        assert int(np.round(total_count)) == count

    return aggregated_distributions_per_pos

def aggregate_amino_acid_frequences_in_pfam_alignment(pfam_alignment):
    """Aggregates amino acid frequencies in a multiple sequence alignment
    resulting from a pfam domain
    
    Ignore residues of the following type
    Pyl    O    Pyrrolysine
    Sec    U    Selenocysteine
    Asx    B    Aspartic acid or Asparagine
    Glx    Z    Glutamic acid or Glutamine
    Xaa    X    Any amino acid
    Xle    J    Leucine or Isoleucine
    """
    ignore_list = ['-', 'O', 'U', 'B', 'Z', 'X', 'J']
    
    amino_acid_distribution = {}
    for al in pfam_alignment['alignments']:
        for position, aa in enumerate(al['alignment_consensus']):
            if position not in amino_acid_distribution.keys():
                # create the null distribution, will be filled in based
                # on the position of the alignment_consensus
                amino_acid_distribution[position] = {
                     'A': 0.0, 'C': 0.0, 'D': 0.0, 'E': 0.0,
                     'F': 0.0, 'G': 0.0, 'H': 0.0, 'I': 0.0,
                     'K': 0.0, 'L': 0.0, 'M': 0.0, 'N': 0.0,
                     'P': 0.0, 'Q': 0.0, 'R': 0.0, 'S': 0.0, 
                     'T': 0.0, 'V': 0.0, 'W': 0.0, 'Y': 0.0, 
                     'count':0}
                
            if aa in amino_acid_distribution[position].keys():
                amino_acid_distribution[position][aa] += 1.0
                amino_acid_distribution[position]['count'] += 1
            elif aa not in ignore_list:                
                _log.warning("For "+pfam_alignment['AC']+" at consensus position '"+str(position)+"' ignoring residue '"+aa+"' for amino acid distribution")
    
    return amino_acid_distribution