from metadom.domain.models.entities.gene_region import GeneRegion
from metadom.domain.services.computation.gene_region_computations import compute_tolerance_landscape
from metadom.domain.services.annotation.annotation import annotateSNVs
from metadom.domain.services.annotation.gene_region_annotators import annotateTranscriptWithHGMDData, annotateTranscriptWithClinvarData
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

def get_or_set_current_gene_region(transcript_id, force_rebuild=False):
    if not force_rebuild and 'gene_region' in session and not session['gene_region'] is None:
        gene_region = jsonpickle.decode(session['gene_region'])
        if gene_region.gencode_transcription_id == transcript_id:
            return gene_region
    
    # Retrieve the gene from the database
    gene = GeneRepository.retrieve_gene(transcript_id)
    
    if not gene is None:
        try:
            # create the gene_region
            gene_region = GeneRegion(gene)
            session['gene_region'] = jsonpickle.encode(gene_region)
        except:
            session['gene_region'] = None
    return  jsonpickle.decode(session['gene_region'])

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
    
    # Retrieve or create the gene region
    gene_region = get_or_set_current_gene_region(transcript_id)
    
    if not gene_region is None:
        region_sliding_window = compute_tolerance_landscape(gene_region, sliding_window, frequency)
        
        return jsonify([{"geneName":gene_region.gene_name}, region_sliding_window])
    else:
        return jsonify(str())

@bp.route('/gene/getPfamDomains', methods=['GET'])
def get_pfam_domains():
    """This endpoint is a stub, to ensure deeper endpoints may be used"""
    pass

@bp.route('/gene/getPfamDomains/<transcript_id>', methods=['GET'])
def get_pfam_domains_for_transcript(transcript_id):
    # Retrieve or create the gene region
    gene_region = get_or_set_current_gene_region(transcript_id)
    Pfam_domains = []
    if not gene_region is None:
        
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

    return jsonify(Pfam_domains)

@bp.route('/gene/annotateHGMD', methods=['GET'])
def get_HGMD_annotation():
    """This endpoint is a stub, to ensure deeper endpoints may be used"""
    pass

@bp.route('/gene/annotateHGMD/<transcript_id>', methods=['GET'])
def get_HGMD_annotation_for_transcript(transcript_id):
    # Retrieve or create the gene region
    gene_region = get_or_set_current_gene_region(transcript_id)
    HGMD_variants = []
    if not gene_region is None:    
         
        HGMD_annotation = annotateSNVs(annotateTranscriptWithHGMDData, gene_region)
        
        for chrom_pos in HGMD_annotation.keys():
            for variant in HGMD_annotation[chrom_pos]:
                HGMD_variant = {}
                HGMD_variant['pos'] = gene_region.mappings_per_chromosome[chrom_pos].uniprot_position
                HGMD_variant['ref'] = variant['REF']
                HGMD_variant['alt'] = variant['ALT']
                
                HGMD_variants.append(HGMD_variant)

    return jsonify(HGMD_variants)

@bp.route('/gene/annotateClinVar', methods=['GET'])
def get_ClinVar_annotation():
    """This endpoint is a stub, to ensure deeper endpoints may be used"""
    pass

@bp.route('/gene/annotateClinVar/<transcript_id>', methods=['GET'])
def get_ClinVar_annotation_for_transcript(transcript_id):
    # Retrieve or create the gene region
    gene_region = get_or_set_current_gene_region(transcript_id)
    ClinVar_variants = []
    if not gene_region is None:    
        ClinVar_annotation = annotateSNVs(annotateTranscriptWithClinvarData, gene_region)
        
        for chrom_pos in ClinVar_annotation.keys():
            for variant in ClinVar_annotation[chrom_pos]:
                ClinVar_variant = {}
                ClinVar_variant['pos'] = gene_region.mappings_per_chromosome[chrom_pos].uniprot_position
                ClinVar_variant['ref'] = variant['REF']
                ClinVar_variant['alt'] = variant['ALT']
                
                ClinVar_variants.append(ClinVar_variant)

    return jsonify(ClinVar_variants)

@bp.route('/pfam/getMetaDomain/<string:domain_id>', methods=['GET'])
def get_metadomain_for_pfam_id(domain_id):
    metadomain = MetaDomain(domain_id)
    return jsonify(str(metadomain))

@bp.route('/gene/getMetaDomain/<string:transcript_id>/<string:domain_id>', methods=['GET'])
def get_metadomains_for_transcript(transcript_id, domain_id):
    # Retrieve the gene from the database
    gene = GeneRepository.retrieve_gene(transcript_id)
    
    return_value = {}
    
    # check if we got a gene from the database
    if not gene is None:
        metadomain = MetaDomain(domain_id)
        
        protein_to_consensus_positions = metadomain.consensus_pos_per_protein[gene.protein_id]
        
        for pos in protein_to_consensus_positions:
            return_value[pos] = str(metadomain.mappings_per_consensus_pos[protein_to_consensus_positions[pos]])
    
    return jsonify(return_value)

# # GET /api/chromosome/:id
# @bp.route('/chromosome/<string:chromosome_id>', methods=['GET'])
# def get_mapping_via_chr_pos(chromosome_id):
#     pass
# #     if len(locus) == 0:
# #         abort(404)
# #     return jsonify({'locus': locus[0]})
# 
# # GET /api/mapping/:id
# @bp.route('/mapping/<string:mapping_id>', methods=['GET'])
# def get_mapping_via_id(mapping_id):
#     pass
# 
# # GET /api/gene/:id
# @bp.route('/gene/<string:gene_id>', methods=['GET'])
# def get_mapping_via_gene_id(gene_id):
#     pass
# 
# 
# # GET /api/protein/:id
# @bp.route('/protein/<string:protein_id>', methods=['GET'])
# def get_mapping_via_protein_id(protein_id):
#     pass
# 
# # GET /api/pfam/:id
# @bp.route('/pfam/<string:pfam_id>', methods=['GET'])
# def get_mapping_via_pfam_id(pfam_id):
# #     for x in session.query(Mapping).join(Interpro).filter(Interpro.pfam_id == pfam_id):
# #         for y in session.query(Chromosome).filter(Chromosome.id == x.chromosome_id):
# #             print(y,x)
#     pass
# 
# # GET /api/pfam/:id/:position
# @bp.route('/pfam/<string:pfam_id>/<int:position>', methods=['GET'])
# def get_mapping_via_pfam_position(pfam_id, position):
# #     for x in session.query(Mapping).join(Interpro).filter(and_(Mapping.pfam_consensus_position==position, Interpro.pfam_id == pfam_id)):
# #         for y in session.query(Chromosome).filter(Chromosome.id == x.chromosome_id):
# #             print(y,x)
#     pass

@bp.errorhandler(Exception)
def exception_error_handler(error):  # pragma: no cover
    _log.error("Unhandled exception:\n{}".format(error))
    _log.error(traceback.print_exc())
    return render_template('error.html', msg=error), 500