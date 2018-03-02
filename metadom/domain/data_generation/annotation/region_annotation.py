import logging

from metadom.domain.data_generation.annotation.GenomeTranscriptionAnnotation import annotateTranscriptWithExacData,\
    annotateTranscriptWithHGMDData, annotateSNVs,\
    annotateTranscriptWithClinvarData
from metadom.domain.metrics.codon_statistics import calculate_CDS_background_rate
from metadom.domain.data_generation.mapping.Gene2ProteinMapping import extract_gene_region
from Bio.Seq import translate

_log = logging.getLogger(__name__)

class RegionIsNotEncodedBycDNAException(Exception):
    pass

class ExternalREFAlleleNotEqualsTranscriptionException(Exception):
    pass

def extract_cdna_and_protein_sequence_from_region(gene_mapping, region_of_interest):
    region_cdna = ""
    region_proteinseq = ""
    for cdna_pos in region_of_interest['cdna_positions']:
        region_cdna += gene_mapping['GenomeMapping']['cDNA'][cdna_pos]['allele']
        if (int(cdna_pos)-1)%3 == 0:
            region_proteinseq += gene_mapping['GenomeMapping']['cDNA'][cdna_pos]['uniprot_residue']
    
    if translate(region_cdna) != region_proteinseq:
        raise RegionIsNotEncodedBycDNAException("analysis of protein region may contain gaps: translate(region_cdna) != region_proteinseq")
    
    return region_cdna, region_proteinseq    

def analyse_dn_ds_over_protein_region(gene_mapping, region_start, region_stop):
    # retrieve cDNA position region
    region_of_interest = extract_gene_region(gene_mapping, region_start, region_stop)
    
    # extract cdna and protein sequence from region
    region_cdna, region_proteinseq = extract_cdna_and_protein_sequence_from_region(gene_mapping, region_of_interest)
    
    # Calculate the background mutation rates
    background_missense_in_domain, background_nonsense_in_domain, background_synonymous_in_domain = calculate_CDS_background_rate(region_cdna)
    
    # Annotate exac information
    exac_annotations = annotateSNVs(annotateTranscriptWithExacData, gene_mapping, region_of_interest)
    exac_missense_in_region, exac_synonymous_in_region, exac_nonsense_in_region, exac_region_information = annotate_gene_variant_dataset_information(gene_mapping, exac_annotations)
    
    # Annotate hgmd information
    hgmd_annotations = annotateSNVs(annotateTranscriptWithHGMDData, gene_mapping, region_of_interest)
    hgmd_missense_in_region, hgmd_synonymous_in_region, hgmd_nonsense_in_region, hgmd_region_information = annotate_gene_variant_dataset_information(gene_mapping, hgmd_annotations)

    # Annotate clinvar information
    clinvar_annotations = annotateSNVs(annotateTranscriptWithClinvarData, gene_mapping, region_of_interest)
    clinvar_missense_in_region, clinvar_synonymous_in_region, clinvar_nonsense_in_region, clinvar_region_information = annotate_gene_variant_dataset_information(gene_mapping, clinvar_annotations)

    # put all the results in a dictionary
    region_result = {"exac_missense":exac_missense_in_region,
                     "exac_nonsense":exac_nonsense_in_region,
                     "exac_synonymous":exac_synonymous_in_region,
                     "exac_information":exac_region_information, 
                     "clinvar_missense":clinvar_missense_in_region,
                     "clinvar_nonsense":clinvar_nonsense_in_region,
                     "clinvar_synonymous":clinvar_synonymous_in_region,
                     "clinvar_information":clinvar_region_information,
                     "hgmd_missense":hgmd_missense_in_region, 
                     "hgmd_synonymous":hgmd_synonymous_in_region,
                     "hgmd_nonsense":hgmd_nonsense_in_region,
                     "hgmd_information":hgmd_region_information,
                     "background_missense":background_missense_in_domain, 
                     "background_nonsense":background_nonsense_in_domain, 
                     "background_synonymous":background_synonymous_in_domain, 
                     "region_length":region_of_interest['protein_region_length'], 
                     "chromosome":region_of_interest['chr'], 
                     "chromosome_positions":region_of_interest['regions'], 
                     "cDNA":region_cdna,
                     "protein":region_proteinseq} 
    
    return region_result

def annotate_gene_variant_dataset_information(gene_mapping, annotated_region):
    missense_in_region = 0
    synonymous_in_region = 0
    nonsense_in_region = 0
    region_information = []
    for chrom_pos in annotated_region.keys():
        codon = gene_mapping['GenomeMapping']['Genome'][chrom_pos]['translation_codon']
        codon_pos = gene_mapping['GenomeMapping']['Genome'][chrom_pos]['translation_codon_allele_pos']
        residue = gene_mapping['GenomeMapping']['Genome'][chrom_pos]['translation_residue']
        
        for annotation_entry in annotated_region[chrom_pos]:
            if gene_mapping['GenomeMapping']['Genome'][chrom_pos]['allele'] != annotation_entry['REF']:
                raise ExternalREFAlleleNotEqualsTranscriptionException("analysis of protein region could not be made due to: gene_mapping['GenomeMapping']['Genome'][chrom_pos]['allele'] !=hgmd_annotations[chrom_pos]['REF']")
        
            alt = annotation_entry['ALT']
            alt_codon =""
            for i in range(len(codon)):
                if i == codon_pos:
                    alt_codon+= alt
                else:
                    alt_codon+= codon[i]
            
            alt_residue = translate(alt_codon)
            if alt_residue == '*':
                nonsense_in_region+=1
            elif alt_residue != residue:
                missense_in_region+=1
            else:
                synonymous_in_region+=1
            
            region_information_entry = {'ref_codon':codon, 'alt_codon':alt_codon, 'ref_residue':residue, 'alt_residue':translate(alt_codon), 'uniprot_pos':gene_mapping['GenomeMapping']['Genome'][chrom_pos]['uniprot']}
            for annotation_key in annotation_entry.keys():
                if annotation_key not in ['ALT', 'REF']:
                    region_information_entry[annotation_key] = annotation_entry[annotation_key]
            
            region_information.append(region_information_entry)
    return missense_in_region, synonymous_in_region, nonsense_in_region, region_information
