from metadom.domain.services.annotation.annotation import annotateSNVs
from metadom.domain.services.annotation.gene_region_annotators import annotateTranscriptWithExacData    
from metadom.domain.metrics.GeneticTolerance import background_corrected_mosy_score

def compute_tolerance_landscape(gene_region, slidingWindow, min_frequency=0.0):
    # Annotate exac information
    full_exac_annotations = annotateSNVs(annotateTranscriptWithExacData, gene_region)
    filtered_exac_annotations = dict()
    # filter on the minimal frequency
    for chrom_pos in full_exac_annotations.keys():
        for exac_variant in full_exac_annotations[chrom_pos]:
            if exac_variant['AF'] >= min_frequency:
                if not chrom_pos in filtered_exac_annotations.keys():
                    filtered_exac_annotations[chrom_pos] = []
                filtered_exac_annotations[chrom_pos].append(exac_variant)
        
    variant_type_counts = gene_region.retrieve_variant_type_counts(filtered_exac_annotations)

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
            
            for j in range(int(region_i_start)-1, int(region_i_stop)):
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