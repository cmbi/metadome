from metadome.domain.models.entities.gene_region import GeneRegion
from metadome.domain.services.computation.gene_region_computations import compute_tolerance_landscape
from metadome.domain.services.annotation.annotation import annotateSNVs
from metadome.domain.services.annotation.gene_region_annotators import annotateTranscriptWithClinvarData,\
    annotateTranscriptWithGnomADData
from metadome.domain.models.entities.meta_domain import MetaDomain
from metadome.domain.repositories import GeneRepository
from flask import Blueprint, jsonify, render_template
from flask.globals import request
from builtins import Exception
import traceback

import logging

_log = logging.getLogger(__name__)

bp = Blueprint('api', __name__)

##########################################
#########    Route end points    #########
##########################################

@bp.route('/gene/geneToTranscript', methods=['GET'])
def get_default_transcript_ids():
    """This endpoint is a stub, to ensure deeper endpoints may be used"""
    pass

@bp.route('/gene/geneToTranscript/<string:gene_name>', methods=['GET'])
def get_transcript_ids_for_gene(gene_name):  
    # retrieve the transcript ids for this gene
    trancripts = GeneRepository.retrieve_all_transcript_ids(gene_name)
    
    # check if there was any return value
    if len(trancripts) > 0:
        message = "Retrieved transcripts for gene '"+trancripts[0].gene_name+"'"
    else:
        message = "No transcripts available in database for gene '"+gene_name+"'"
    
    transcripts_with_data = [t.gencode_transcription_id for t in trancripts if not t.protein_id is None]
    transcripts_with_no_data = [t.gencode_transcription_id for t in trancripts if t.protein_id is None]
    
    return jsonify(trancript_ids=transcripts_with_data, no_protein_data=transcripts_with_no_data, message=message)

@bp.route('/gene/getToleranceLandscape', methods=['GET'])
def get_tolerance_landscape():
    """This endpoint is a stub, to ensure deeper endpoints may be used"""
    pass

@bp.route('/gene/getToleranceLandscape/<transcript_id>/', methods=['GET'])
def get_tolerance_landscape_for_transcript(transcript_id):
    sliding_window = request.args.get('slidingwindow')
    if sliding_window is None:
        sliding_window = 10
    else:
        sliding_window = int(sliding_window)
    
    frequency = request.args.get('frequency')
    if frequency is None:
        frequency = 0.0
    else:
        frequency = float(frequency)
    
    # Retrieve the gene from the database
    gene = GeneRepository.retrieve_gene(transcript_id)
    # build the gene region
    gene_region = GeneRegion(gene)
    
    if not gene_region is None:
        # generate the positional annotation for this gene by first computing the tolerance landscape
        region_positional_annotation = compute_tolerance_landscape(gene_region, sliding_window, frequency)
        
        # Annotate Pfam domains
        Pfam_domains = []
        meta_domains = {}
        for domain in gene_region.interpro_domains:
            if domain.ext_db_id.startswith('PF'):
                # we have a Pfam domain
                pfam_domain = {}
                pfam_domain["ID"] = domain.ext_db_id
                pfam_domain["Name"] = domain.region_name
                pfam_domain["start"] = domain.uniprot_start
                pfam_domain["stop"] = domain.uniprot_stop
                 
                try:
                    if not pfam_domain['ID'] in meta_domains.keys():
                        # construct a meta-domain if possible
                        meta_domains[pfam_domain['ID']] = MetaDomain(domain.ext_db_id)
                        pfam_domain["metadomain"] = True
                    else:
                        pfam_domain["metadomain"] = not(meta_domains[pfam_domain['ID']] is None)
                except:
                    # meta domain is not possible
                    meta_domains[pfam_domain['ID']] = None
                    
                # Add the domain to the domain list
                Pfam_domains.append(pfam_domain)
                
        # Annotate the clinvar variants for the current gene
        ClinVar_annotation = annotateSNVs(annotateTranscriptWithClinvarData,
                                         mappings_per_chr_pos=gene_region.retrieve_mappings_per_chromosome(),
                                         strand=gene_region.strand, 
                                         chromosome=gene_region.chr,
                                         regions=gene_region.regions)
        
        # retrieve the mappings per chromosome position
        _mappings_per_chromosome = gene_region.retrieve_mappings_per_chromosome()
        
        for chrom_pos in ClinVar_annotation.keys():
            for variant in ClinVar_annotation[chrom_pos]:
                protein_pos = _mappings_per_chromosome[chrom_pos].uniprot_position
                
                if not 'ClinVar' in region_positional_annotation[protein_pos].keys():
                    region_positional_annotation[protein_pos]['ClinVar'] = []
                
                codon = gene_region.retrieve_codon_for_protein_position(protein_pos)
                
                # create new entry for this variant
                variant_entry = {}
                # append variant information
                variant_entry['alt_codon'], variant_entry['alt_aa'], variant_entry['alt_aa_triplet'], variant_entry['type']  = codon.interpret_SNV_type(position=chrom_pos, var_nucleotide= variant['ALT'])
                variant_entry['pos'] = variant['POS']
                variant_entry['ref'] = variant['REF']
                variant_entry['alt'] = variant['ALT']

                # append ClinVar specific information
                variant_entry['clinvar_ID'] = variant['ID']
                
                region_positional_annotation[protein_pos]['ClinVar'].append(variant_entry)
        
        # annotate the positions further
        for d in region_positional_annotation:
            # retrieve the position as is in the database
            db_position = d['protein_pos']
            
            # update the positions to abide the users' expectation (start at 1, not zero)
            d.update((k, v+1) for k, v in d.items() if k == "protein_pos")
            
            # add domain and meta domain information per position
            d['domains'] = {}
            for domain in Pfam_domains:
                if d['protein_pos'] >= domain["start"] and d['protein_pos'] <= domain["stop"]:
                    # add the domain id for this position
                    d['domains'][domain['ID']] = None 
                    # retrieve the context for this protein
                    protein_to_consensus_positions = meta_domains[domain['ID']].consensus_pos_per_protein[gene_region.uniprot_ac]
                    if domain["metadomain"] and db_position in protein_to_consensus_positions.keys():
                        # add the MetaDomain information if there is any
                        d['domains'][domain['ID']] = create_meta_domain_entry(gene_region, meta_domains[pfam_domain['ID']], protein_to_consensus_positions, db_position)
                                
        return jsonify({"transcript_id":transcript_id, "protein_ac":gene_region.uniprot_ac, "gene_name":gene_region.gene_name, "positional_annotation":region_positional_annotation, "domains":Pfam_domains})
    else:
        return jsonify({'error': 'No gene region could be build for transcript '+str(transcript_id)}), 500

def create_meta_domain_entry(gene_region, metadomain, protein_to_consensus_positions, protein_pos):
    metadom_entry = {}
    metadom_entry['consensus_pos'] = protein_to_consensus_positions[protein_pos]
    metadom_entry['normal_missense_variant_count'] = 0
    metadom_entry['normal_synonymous_variant_count'] = 0
    metadom_entry['normal_nonsense_variant_count'] = 0
    metadom_entry['normal_variant_count'] = 0
    metadom_entry['pathogenic_missense_variant_count'] = 0
    metadom_entry['pathogenic_synonymous_variant_count'] = 0
    metadom_entry['pathogenic_nonsense_variant_count'] = 0    
    metadom_entry['pathogenic_variant_count'] = 0
    metadom_entry['other_codons'] = []
    
    # Retrieve the meta codons for this position
    meta_codons = metadomain.get_codons_aligned_to_consensus_position(metadom_entry['consensus_pos'])
    
    # iterate over meta_codons and add to metadom_entry
    for meta_codon in meta_codons:
        # Check if we are dealing with the gene and protein_pos of interest
        if not (gene_region.gene_id in meta_codon.codon_aggregate.keys() \
            and protein_pos == meta_codon.codon_aggregate[gene_region.gene_id].amino_acid_position):
            # first append the general information for this codon
            position_entry = {}
            position_entry['chr'] = meta_codon.chr
            position_entry['chr_positions'] = meta_codon.pretty_print_chr_region()
            position_entry['strand'] = meta_codon.strand.value
            position_entry['ref_aa'] = meta_codon.amino_acid_residue
            position_entry['ref_aa_triplet'] = meta_codon.three_letter_amino_acid_residue()
            position_entry['ref_codon'] = meta_codon.base_pair_representation

            # annotate missense from gnomad
            position_entry['normal_variants'] = []
            normal_variant_annotation = annotateSNVs(annotateTranscriptWithGnomADData,
                                     mappings_per_chr_pos=meta_codon.retrieve_mappings_per_chromosome(),
                                     strand=meta_codon.strand, 
                                     chromosome=meta_codon.chr,
                                     regions=meta_codon.regions)
            
            # process the annotation
            for chrom_pos in normal_variant_annotation.keys():
                for variant in normal_variant_annotation[chrom_pos]:
                    # create new entry for this variant
                    variant_entry = {}
                    # append variant information
                    variant_entry['alt_codon'], variant_entry['alt_aa'], variant_entry['alt_aa_triplet'], variant_entry['type']  = meta_codon.interpret_SNV_type(position=chrom_pos, var_nucleotide= variant['ALT'])
                    variant_entry['pos'] = variant['POS']
                    variant_entry['ref'] = variant['REF']
                    variant_entry['alt'] = variant['ALT']

                    # append gnomAD specific information
                    variant_entry['allele_number'] = variant['AN']
                    variant_entry['allele_count'] = variant['AC']
                    
                    # add to the position entry
                    position_entry['normal_variants'].append(variant_entry)
                    
                    # count the variants
                    if variant_entry['type'] == 'missense': metadom_entry['normal_missense_variant_count'] += 1
                    if variant_entry['type'] == 'synonymous': metadom_entry['normal_synonymous_variant_count'] += 1
                    if variant_entry['type'] == 'nonsense': metadom_entry['normal_nonsense_variant_count'] += 1
            
            # annotate pathogenic missense from clinvar
            position_entry['pathogenic_variants'] = []
            pathogenic_variant_annotation = annotateSNVs(annotateTranscriptWithClinvarData,
                                     mappings_per_chr_pos=meta_codon.retrieve_mappings_per_chromosome(),
                                     strand=meta_codon.strand, 
                                     chromosome=meta_codon.chr,
                                     regions=meta_codon.regions)
            
            # process the annotation
            for chrom_pos in pathogenic_variant_annotation.keys():
                for variant in pathogenic_variant_annotation[chrom_pos]:
                    
                    # create new entry for this variant
                    variant_entry = {}
                    # append variant information
                    variant_entry['alt_codon'], variant_entry['alt_aa'], variant_entry['alt_aa_triplet'], variant_entry['type']  = meta_codon.interpret_SNV_type(position=chrom_pos, var_nucleotide= variant['ALT'])
                    variant_entry['pos'] = variant['POS']
                    variant_entry['ref'] = variant['REF']
                    variant_entry['alt'] = variant['ALT']

                    # append ClinVar specific information
                    variant_entry['clinvar_ID'] = variant['ID']
                    
                    # add to the position entry
                    position_entry['pathogenic_variants'].append(variant_entry)
                    
                    # count the variants
                    if variant_entry['type'] == 'missense': metadom_entry['pathogenic_missense_variant_count'] += 1
                    if variant_entry['type'] == 'synonymous': metadom_entry['pathogenic_synonymous_variant_count'] += 1
                    if variant_entry['type'] == 'nonsense': metadom_entry['pathogenic_nonsense_variant_count'] += 1
            
            # add this codon to the metadome entry
            metadom_entry['other_codons'].append(position_entry)
            
            # Update the variant counts
            metadom_entry['normal_variant_count'] += len(position_entry['normal_variants'])
            metadom_entry['pathogenic_variant_count'] += len(position_entry['pathogenic_variants'])
            
    return metadom_entry

@bp.errorhandler(Exception)
def exception_error_handler(error):  # pragma: no cover
    _log.error("Unhandled exception:\n{}".format(error))
    _log.error(traceback.print_exc())
    return render_template('error.html', msg=error, stack_trace=traceback.print_exc()), 500

def conditional_jsonify(_value, _jsonify=True):
    """Conditianally jsonifies a given value"""
    if _jsonify:
        return jsonify(_value)
    return _value