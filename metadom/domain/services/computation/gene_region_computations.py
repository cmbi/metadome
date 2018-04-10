from metadom.domain.services.annotation.annotation import annotateSNVs
from metadom.domain.services.annotation.gene_region_annotators import annotateTranscriptWithExacData    
from metadom.domain.metrics.GeneticTolerance import background_corrected_mosy_score
from metadom.domain.services.computation.codon_computations import retrieve_variant_type_counts
from metadom.domain.services.helper_functions import create_sliding_window

def compute_tolerance_landscape(gene_region, sliding_window_size, min_frequency=0.0):
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
        
    variant_type_counts = retrieve_variant_type_counts(gene_region.retrieve_mappings_per_chromosome(), filtered_exac_annotations)
    
    # precompute the sliding window
    sliding_window = create_sliding_window(gene_region.protein_region_length, sliding_window_size)

    # Calculate the sliding window over the gene region
    region_sliding_window = []
    for i in range(len(sliding_window)):
        # correct for gene region start
        protein_pos = i + gene_region.protein_region_start
        
        total_missense_region_i = 0
        total_missense_background_region_i = 0
        total_synonymous_region_i = 0
        total_synonymous_background_region_i = 0
        for j in sliding_window[i]['sw_range']:
            # correct gene region for region start
            j += gene_region.protein_region_start
                        
            total_missense_region_i += variant_type_counts[j]['missense']
            total_missense_background_region_i += variant_type_counts[j]['background_missense']
            total_synonymous_region_i += variant_type_counts[j]['synonymous']
            total_synonymous_background_region_i += variant_type_counts[j]['background_synonymous']

        region_i_dn_ds = background_corrected_mosy_score(missense=total_missense_region_i, 
                                                         missense_background=total_missense_background_region_i,
                                                         synonymous=total_synonymous_region_i,
                                                         synonymous_background=total_synonymous_background_region_i)

        region_sliding_window.append({'pos':protein_pos, 'score':region_i_dn_ds, 'sw_coverage':sliding_window[i]['sw_coverage']})

    return region_sliding_window