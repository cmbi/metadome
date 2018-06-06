from metadom.domain.services.annotation.annotation import annotateSNVs
from metadom.domain.services.annotation.gene_region_annotators import annotateTranscriptWithGnomADData    
from metadom.domain.metrics.GeneticTolerance import background_corrected_mosy_score
from metadom.domain.services.computation.codon_computations import retrieve_variant_type_counts
from metadom.domain.services.helper_functions import create_sliding_window

def compute_tolerance_landscape(gene_region, sliding_window_size, min_frequency=0.0):
    # Annotate gnomad information
    full_gnomad_annotations = annotateSNVs(annotateTranscriptWithGnomADData, 
                                         mappings_per_chr_pos=gene_region.retrieve_mappings_per_chromosome(),
                                         strand=gene_region.strand, 
                                         chromosome=gene_region.chr,
                                         regions=gene_region.regions)
    filtered_gnomad_annotations = dict()
    # filter on the minimal frequency
    for chrom_pos in full_gnomad_annotations.keys():
        for gnomad_variant in full_gnomad_annotations[chrom_pos]:
            if gnomad_variant['AF'] >= min_frequency:
                if not chrom_pos in filtered_gnomad_annotations.keys():
                    filtered_gnomad_annotations[chrom_pos] = []
                filtered_gnomad_annotations[chrom_pos].append(gnomad_variant)
        
    variant_type_counts = retrieve_variant_type_counts(gene_region.retrieve_mappings_per_chromosome(), filtered_gnomad_annotations)
    
    # precompute the sliding window
    sliding_window = create_sliding_window(gene_region.protein_region_length, sliding_window_size)

    # Calculate the sliding window over the gene region
    tolerance_landscape = []
    for i in range(len(sliding_window)):
        tolerance_landscape_entry = {}
                
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

        # Add tolerance data
        tolerance_landscape_entry['sw_dn_ds'] = region_i_dn_ds
        tolerance_landscape_entry['sw_coverage']  = sliding_window[i]['sw_coverage']
        tolerance_landscape_entry['sw_size']  = sliding_window_size
        
        # retrieve codon
        protein_pos = i + gene_region.protein_region_start # correct for gene region start
        current_codon = gene_region.retrieve_codon_for_protein_position(protein_pos)
        
        # Add positional information
        tolerance_landscape_entry['strand'] = current_codon.strand.value
        tolerance_landscape_entry['protein_pos'] = current_codon.amino_acid_position
        tolerance_landscape_entry['cdna_pos'] = current_codon.pretty_print_cDNA_region()
        tolerance_landscape_entry['chr'] = current_codon.chr
        tolerance_landscape_entry['chr_positions'] = current_codon.pretty_print_chr_region()
        
        # Add residue and nucleotide information
        tolerance_landscape_entry['ref_aa'] = current_codon.amino_acid_residue
        tolerance_landscape_entry['ref_aa_triplet'] = current_codon.three_letter_amino_acid_residue()
        tolerance_landscape_entry['ref_codon'] = current_codon.base_pair_representation

        # Add information to landscape
        tolerance_landscape.append(tolerance_landscape_entry)

    return tolerance_landscape