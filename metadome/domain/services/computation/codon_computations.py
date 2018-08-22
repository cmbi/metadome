from metadome.domain.metrics.codon_statistics import codon_background_rates
from Bio.Seq import translate

class ExternalREFAlleleNotEqualsTranscriptionException(Exception):
    pass

def interpret_alt_codon(ref_codon, codon_pos, alt):
    alt_codon =""
    for i in range(len(ref_codon)):
        if i == codon_pos:
            alt_codon+= alt
        else:
            alt_codon+= ref_codon[i]
    
    return alt_codon

def residue_variant_type(ref_residue, alt_residue):
    if alt_residue == '*':
        return 'nonsense'
    elif alt_residue != ref_residue:
        return 'missense'
    else:
        return 'synonymous'
    
def interpret_SNV_variant_type(ref_codon, codon_pos, alt):
    # interpret alt codon
    alt_codon = interpret_alt_codon(ref_codon=ref_codon, codon_pos=codon_pos, alt=alt)
    # translate the residues
    ref_residue = translate(ref_codon)
    alt_residue = translate(alt_codon)
    # interpret the variant type
    return residue_variant_type(ref_residue, alt_residue)

def retrieve_background_variant_counts(mappings_per_chromosome):
    # the value that is to be returned
    variant_type_counts = dict()
    
    for chrom_pos in mappings_per_chromosome.keys():
        codon = mappings_per_chromosome[chrom_pos]['base_pair_representation']
        residue_position = mappings_per_chromosome[chrom_pos]['amino_acid_position']
    
        if not residue_position in variant_type_counts.keys():
            variant_type_counts[residue_position] = dict()
            
            # Add the background mutation type rates for this codon        
            variant_type_counts[residue_position]['background_missense'] = codon_background_rates[codon]['missense']
            variant_type_counts[residue_position]['background_nonsense'] = codon_background_rates[codon]['nonsense']
            variant_type_counts[residue_position]['background_synonymous'] = codon_background_rates[codon]['synonymous']
            
            # Add the background mutation type rates for this codon        
            variant_type_counts[residue_position]['missense'] = 0
            variant_type_counts[residue_position]['nonsense'] = 0
            variant_type_counts[residue_position]['synonymous'] = 0
    
    # return the variant type counts
    return variant_type_counts
            
def retrieve_variant_type_counts(mappings_per_chromosome, annotated_region):
    """Given an annotated region, returns a per position count"""
    # First retrieve the background for the region
    variant_type_counts = retrieve_background_variant_counts(mappings_per_chromosome)
    
    for chrom_pos in annotated_region.keys():
        codon = mappings_per_chromosome[chrom_pos]['base_pair_representation']
        codon_pos = mappings_per_chromosome[chrom_pos]['codon_base_pair_position']
        residue_position = mappings_per_chromosome[chrom_pos]['amino_acid_position']
        
        for annotation_entry in annotated_region[chrom_pos]:
            if mappings_per_chromosome[chrom_pos]['base_pair'] != annotation_entry['REF']:
                raise ExternalREFAlleleNotEqualsTranscriptionException("For gene id '"+str(mappings_per_chromosome[chrom_pos]['gencode_transcription_id'])+
                                                   "', at chrom_pos '"+str(chrom_pos)+"' : analysis of protein region could"+
                                                   " not be made due to: gene_region.retrieve_mappings_per_chromosome()[chrom_pos].base_pair"+
                                                   " != annotation_entry['REF']")
            
            # interpret the variant type
            variant_type = interpret_SNV_variant_type(ref_codon=codon, codon_pos=codon_pos, alt=annotation_entry['ALT'])
            
            # add variant_type to variant_type counts
            variant_type_counts[residue_position][variant_type] += 1
                
    return variant_type_counts