from metadom.domain.services.annotation.annotation import annotateSNVs
from metadom.domain.services.annotation.gene_region_annotators import annotateTranscriptWithExacData    
from metadom.domain.metrics.GeneticTolerance import background_corrected_mosy_score
from metadom.domain.metrics.codon_statistics import codon_background_rates
from Bio.Seq import translate

class ExternalREFAlleleNotEqualsTranscriptionException(Exception):
    pass

def retrieve_background_variant_counts(gene_region):
    # the value that is to be returned
    variant_type_counts = dict()
    
    # retrieve the mappings per chromosome position
    _mappings_per_chromosome = gene_region.retrieve_mappings_per_chromosome()
    
    for chrom_pos in _mappings_per_chromosome.keys():
        codon = _mappings_per_chromosome[chrom_pos].codon
        residue_position = _mappings_per_chromosome[chrom_pos].amino_acid_position
    
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
            
def retrieve_variant_type_counts(gene_region, annotated_region):
    """Given an annotated region, returns a per position count"""
    # First retrieve the background for the region
    variant_type_counts = retrieve_background_variant_counts(gene_region)
    
    # retrieve the mappings per chromosome position
    _mappings_per_chromosome = gene_region.retrieve_mappings_per_chromosome()
    
    for chrom_pos in annotated_region.keys():
        codon = _mappings_per_chromosome[chrom_pos].codon
        codon_pos = _mappings_per_chromosome[chrom_pos].codon_base_pair_position
        residue = _mappings_per_chromosome[chrom_pos].amino_acid_residue
        residue_position = _mappings_per_chromosome[chrom_pos].amino_acid_position
                 
        for annotation_entry in annotated_region[chrom_pos]:
            if _mappings_per_chromosome[chrom_pos].base_pair != annotation_entry['REF']:
                raise ExternalREFAlleleNotEqualsTranscriptionException("For transcript '"+str(gene_region.gencode_transcription_id)+
                                                   "', at chrom_pos '"+str(chrom_pos)+"' : analysis of protein region could"+
                                                   " not be made due to: gene_region.retrieve_mappings_per_chromosome()[chrom_pos].base_pair"+
                                                   " != annotation_entry['REF']")
        
            alt = annotation_entry['ALT']
            alt_codon =""
            for i in range(len(codon)):
                if i == codon_pos:
                    alt_codon+= alt
                else:
                    alt_codon+= codon[i]
            
            alt_residue = translate(alt_codon)
            if alt_residue == '*':
                variant_type_counts[residue_position]['nonsense']+=1
            elif alt_residue != residue:
                variant_type_counts[residue_position]['missense']+=1
            else:
                variant_type_counts[residue_position]['synonymous']+=1
                
    return variant_type_counts

def compute_tolerance_landscape(gene_region, slidingWindow, min_frequency=0.0):
    # Annotate exac information
    full_exac_annotations = annotateSNVs(annotateTranscriptWithExacData, 
                                         mappings_per_chr_pos=gene_region.retrieve_mappings_per_chromosome(),
                                         strand=gene_region.strand, 
                                         chromosome=gene_region.chr,
                                         regions=gene_region.regions)
    filtered_exac_annotations = dict()
    # filter on the minimal frequency
    for chrom_pos in full_exac_annotations.keys():
        for exac_variant in full_exac_annotations[chrom_pos]:
            if exac_variant['AF'] >= min_frequency:
                if not chrom_pos in filtered_exac_annotations.keys():
                    filtered_exac_annotations[chrom_pos] = []
                filtered_exac_annotations[chrom_pos].append(exac_variant)
        
    variant_type_counts = retrieve_variant_type_counts(gene_region, filtered_exac_annotations)

    # compute the sliding window size
    sliding_window_size = float(gene_region.protein_region_length)*slidingWindow

    # Calculate the sliding window over the gene region
    region_sliding_window = []
    for i in range(gene_region.protein_region_length):
        if sliding_window_size == 0:
            region_i_start=i
            region_i_stop=i
        else:
            region_i_start = i-(sliding_window_size/2)
            region_i_stop = i+(sliding_window_size/2)-1
        
        if region_i_start <= gene_region.protein_region_start or region_i_stop >= gene_region.protein_region_stop:
            region_sliding_window.append({'pos':i, 'score':0})
            continue
        else:
            total_missense_region_i = 0
            total_missense_background_region_i = 0
            total_synonymous_region_i = 0
            total_synonymous_background_region_i = 0
            
            for j in range(int(region_i_start), int(region_i_stop)):
                total_missense_region_i += variant_type_counts[j]['missense']
                total_missense_background_region_i += variant_type_counts[j]['background_missense']
                total_synonymous_region_i += variant_type_counts[j]['synonymous']
                total_synonymous_background_region_i += variant_type_counts[j]['background_synonymous']

            region_i_dn_ds = background_corrected_mosy_score(missense=total_missense_region_i, 
                                                             missense_background=total_missense_background_region_i,
                                                             synonymous=total_synonymous_region_i,
                                                             synonymous_background=total_synonymous_background_region_i)

            region_sliding_window.append({'pos':i, 'score':region_i_dn_ds})

    return region_sliding_window