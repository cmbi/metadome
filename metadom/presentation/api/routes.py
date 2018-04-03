from metadom.domain.models.entities.gene_region import GeneRegion
from metadom.domain.services.computation.gene_region_computations import compute_tolerance_landscape
from metadom.domain.services.annotation.annotation import annotateSNVs
from metadom.domain.services.computation.codon_computations import retieve_empty_variant_type_counter, retrieve_variant_type_counts,\
    retrieve_aggregated_variant_type_counts
from metadom.domain.services.annotation.gene_region_annotators import annotateTranscriptWithClinvarData,\
    annotateTranscriptWithExacData
from metadom.domain.models.entities.meta_domain import MetaDomain
from metadom.domain.repositories import GeneRepository
from flask import abort, Blueprint, jsonify, render_template, session
from flask.globals import request
from builtins import Exception
import traceback
import jsonpickle

import logging

_log = logging.getLogger(__name__)

bp = Blueprint('api', __name__)

##########################################
#########    Route end points    #########
##########################################

@bp.route('/', methods=['GET'])
def api_doc():
    return render_template('api/docs.html')

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
        sliding_window = 0.0
    else:
        sliding_window = float(sliding_window)
    
    frequency = request.args.get('frequency')
    if frequency is None:
        frequency = 0.0
    else:
        frequency = float(frequency)
    
    # Retrieve the gene from the database
    gene = GeneRepository.retrieve_gene(transcript_id)
    
    Pfam_domains = []
    if not gene is None:
        # build the gene region
        gene_region = GeneRegion(gene)
        region_sliding_window = compute_tolerance_landscape(gene_region, sliding_window, frequency)
        
        
        for domain in gene_region.interpro_domains:
            if domain.ext_db_id.startswith('PF'):
                # we have a Pfam domain
                pfam_domain = {}
                pfam_domain["ID"] = domain.ext_db_id
                pfam_domain["Name"] = domain.region_name
                pfam_domain["start"] = domain.uniprot_start
                pfam_domain["stop"] = domain.uniprot_stop
                pfam_domain["domID"] = domain.id
                
                Pfam_domains.append(pfam_domain)
        
        ClinVar_variants = []
        if not gene_region is None:    
            ClinVar_annotation = annotateSNVs(annotateTranscriptWithClinvarData,
                                             mappings_per_chr_pos=gene_region.retrieve_mappings_per_chromosome(),
                                             strand=gene_region.strand, 
                                             chromosome=gene_region.chr,
                                             regions=gene_region.regions)
            
            # retrieve the mappings per chromosome position
            _mappings_per_chromosome = gene_region.retrieve_mappings_per_chromosome()
            
            for chrom_pos in ClinVar_annotation.keys():
                for variant in ClinVar_annotation[chrom_pos]:
                    ClinVar_variant = {}
                    ClinVar_variant['pos'] = _mappings_per_chromosome[chrom_pos].uniprot_position
                    ClinVar_variant['ref'] = variant['REF']
                    ClinVar_variant['alt'] = variant['ALT']
                    
                    ClinVar_variants.append(ClinVar_variant)
#         return jsonify(ClinVar_variants)
        
        return jsonify({"geneName":gene_region.gene_name, "sliding_window":region_sliding_window, "domains":Pfam_domains, "clinvar":ClinVar_variants})
    else:
        return jsonify({'error': 'No gene region could be build for transcript '+str(transcript_id)}), 500

@bp.route('/pfam/getMetaDomain/<string:domain_id>', methods=['GET'])
def get_metadomain_for_pfam_id(domain_id):
    metadomain = MetaDomain(domain_id)
    return jsonify(str(metadomain))

@bp.route('/gene/getMetaDomain/<string:transcript_id>/<string:domain_id>', methods=['GET'])
def get_metadomains_for_transcript(transcript_id, domain_id, _jsonify=True):
    # create the return value
    return_value = dict()
    
    # Retrieve the gene from the database
    gene = GeneRepository.retrieve_gene(transcript_id)
    
    if not gene is None:
        # build the gene region
        gene_region = GeneRegion(gene)
    
    if gene_region is None:
        return jsonify({'error': 'Transcript '+str(transcript_id)+' not present in database'}), 500
     
    # Check if the domain is present in the gene region
    domains_in_gene = gene_region.retrieve_specific_domains_in_gene(domain_id)
    if len(domains_in_gene) == 0:
        return jsonify({'error': 'Domain id '+str(domain_id)+' not present in transcript '+str(transcript_id)+' in the database'}), 500
     
    # create a metadomain for this domain
    metadomain = MetaDomain(domain_id)
     
    # retrieve the context for this protein
    protein_to_consensus_positions = metadomain.consensus_pos_per_protein[gene_region.protein_id]
    
    meta_domain_data = []
    # generate the return value
    for protein_pos in protein_to_consensus_positions:
        metadom_entry = {}
        metadom_entry['protein_pos'] = protein_pos
        metadom_entry['consensus_pos'] = protein_to_consensus_positions[metadom_entry['protein_pos']]
        metadom_entry['other_chr_regions'] = []
        metadom_entry['other_codons'] = []
        metadom_entry['other_amino_acids'] = []
        metadom_entry['other_normal_variation'] = retieve_empty_variant_type_counter()
        metadom_entry['other_pathogenic_variation'] = retieve_empty_variant_type_counter()
        
        # Retrieve the meta codons for this position
        meta_codons = metadomain.get_codons_aligned_to_consensus_position(metadom_entry['consensus_pos'])
        
        # create the variant annotations
        normal_variant_annotation = []
        pathogenic_variant_annotation = []
        
        # iterate over meta_codons and add to metadom_entry
        for meta_codon in meta_codons:
            # Check if we are dealing with the gene and protein_pos of interest
            if gene_region.gene_id in meta_codon.codon_aggregate.keys() \
                and metadom_entry['protein_pos'] == meta_codon.codon_aggregate[gene_region.gene_id].amino_acid_position:
                # yes we are
                metadom_entry['chr_region'] = meta_codon.chr+":"+str(meta_codon.regions)+"(strand: "+str(meta_codon.strand)+")"
                metadom_entry['codon'] = meta_codon.base_pair_representation
                metadom_entry['amino_acid'] = meta_codon.amino_acid_residue
            else:
                # no we are not
                metadom_entry['other_chr_regions'].append(meta_codon.chr+":"+str(meta_codon.regions)+"(strand: "+str(meta_codon.strand)+")")
                metadom_entry['other_codons'].append(meta_codon.base_pair_representation)
                metadom_entry['other_amino_acids'].append(meta_codon.amino_acid_residue)
                
                # annotate missense from exac/gnomad
                normal_variant_annotation.append({'mappings_per_chromosome':meta_codon.retrieve_mappings_per_chromosome(), 
                                        'annotated_region':annotateSNVs(annotateTranscriptWithExacData,
                                         mappings_per_chr_pos=meta_codon.retrieve_mappings_per_chromosome(),
                                         strand=meta_codon.strand, 
                                         chromosome=meta_codon.chr,
                                         regions=meta_codon.regions)})
                
                # annotate pathogenic missense from clinvar
                pathogenic_variant_annotation.append({'mappings_per_chromosome':meta_codon.retrieve_mappings_per_chromosome(), 
                                        'annotated_region':annotateSNVs(annotateTranscriptWithClinvarData,
                                         mappings_per_chr_pos=meta_codon.retrieve_mappings_per_chromosome(),
                                         strand=meta_codon.strand, 
                                         chromosome=meta_codon.chr,
                                         regions=meta_codon.regions)})
        
        # count the number of normal and pathogenic missense
        for normal_variants in normal_variant_annotation:
            metadom_entry['other_normal_variation'].update(retrieve_aggregated_variant_type_counts(retrieve_variant_type_counts(normal_variants['mappings_per_chromosome'], normal_variants['annotated_region'])))
        for pathogenic_variants in pathogenic_variant_annotation:
            metadom_entry['other_pathogenic_variation'].update(retrieve_aggregated_variant_type_counts(retrieve_variant_type_counts(pathogenic_variants['mappings_per_chromosome'], pathogenic_variants['annotated_region'])))
        
        # ensure uniqueness
        metadom_entry['other_chr_regions'] = list(set(metadom_entry['other_chr_regions']))
        metadom_entry['other_codons'] = list(set(metadom_entry['other_codons']))
        metadom_entry['other_amino_acids'] = list(set(metadom_entry['other_amino_acids']))
        
        # add the metadom entry to the return value
        meta_domain_data.append(metadom_entry)
    
    # Add general info on the gene, domain and protein
    meta_domain_info = dict()
    meta_domain_info['gene_name'] = gene_region.gene_name
    meta_domain_info['protein_ac'] = gene_region.uniprot_ac
    meta_domain_info['protein_name'] = gene_region.uniprot_name
    meta_domain_info['transcript'] = gene_region.gencode_transcription_id
    meta_domain_info['strand'] = str(gene_region.strand)
    meta_domain_info['protein_length'] = gene_region.protein_region_length
    meta_domain_info['cDNA_length'] = gene_region.cDNA_region_length
    meta_domain_info['domain_id'] = metadomain.domain_id
    meta_domain_info['domain_occurrences'] = [{'start':domain.uniprot_start, 'stop':domain.uniprot_stop} for domain in domains_in_gene]
    
    ## add everything to the return value
    # sort the return value
    return_value['meta_domain_data'] = sorted(meta_domain_data, key=lambda k: k['protein_pos'])
    return_value['meta_domain_info'] = meta_domain_info
    
    # return to caller
    return conditional_jsonify(return_value, _jsonify)

@bp.route('/gene/getMetaDomainInformation/<string:transcript_id>/<int:amino_acid_position>', methods=['GET'])
def get_metadomain_information_for_gene_position(transcript_id, amino_acid_position):
    # Retrieve the gene from the database
    gene = GeneRepository.retrieve_gene(transcript_id)
    
    if not gene is None:
        # build the gene region
        gene_region = GeneRegion(gene)
    
    return_value = {}
    if not gene_region is None:
        interpro_domains = gene_region.get_domains_for_position(amino_acid_position)
        
        meta_domain_mappings = {}
        
        for interpro_domain in interpro_domains:
            domain_id = interpro_domain.ext_db_id
            metadomain = MetaDomain(domain_id)
            
            protein_to_consensus_positions = metadomain.consensus_pos_per_protein[gene_region.protein_id]
            
            if amino_acid_position in protein_to_consensus_positions:
                meta_domain_mappings[domain_id] = metadomain.mappings_per_consensus_pos[protein_to_consensus_positions[amino_acid_position]]
                #TODO finalize

        
        return jsonify(str(meta_domain_mappings))
        
#         protein_to_consensus_positions = metadomain.consensus_pos_per_protein[gene.protein_id]
#         
#         for pos in protein_to_consensus_positions:
#             return_value[pos] = str(metadomain.mappings_per_consensus_pos[protein_to_consensus_positions[pos]])
#     
    return jsonify(return_value)

@bp.errorhandler(Exception)
def exception_error_handler(error):  # pragma: no cover
    _log.error("Unhandled exception:\n{}".format(error))
    _log.error(traceback.print_exc())
    return render_template('error.html', msg=error, stack_trace=traceback.print_exc()), 500

##########################################
#########   Get/set functions    #########
##########################################

# def get_or_set_current_gene_region(transcript_id, force_rebuild=False):
#     if not force_rebuild and 'gene_region' in session and not session['gene_region'] is None:
#         gene_region = jsonpickle.decode(session['gene_region'])
#         if not gene_region is None and gene_region.gencode_transcription_id == transcript_id:
#             return gene_region
#     
#     # new transcript, lets clear the session
#     session.clear()
#     
#     # Retrieve the gene from the database
#     gene = GeneRepository.retrieve_gene(transcript_id)
#     
#     if not gene is None:
#         try:
#             # create the gene_region
#             gene_region = GeneRegion(gene)            
#             session['gene_region'] = jsonpickle.encode(gene_region)
#             return jsonpickle.decode(session['gene_region'])
#         except Exception as e:
#             _log.error(e)
#             _log.error(traceback.print_exc())
#             # to ensure no bad data got into the session lets clear it
#             session.clear()
#     return None

def conditional_jsonify(_value, _jsonify=True):
    """Conditianally jsonifies a given value"""
    if _jsonify:
        return jsonify(_value)
    return _value