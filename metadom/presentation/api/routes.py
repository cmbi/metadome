import logging

from flask import abort, Blueprint, jsonify, render_template
from metadom.domain.repositories import GeneRepository, InterproRepository
from builtins import Exception
from metadom.domain.models.entities.gene_region import GeneRegion
from flask.globals import request
import traceback
from metadom.domain.services.computation.gene_region_computations import compute_tolerance_landscape

_log = logging.getLogger(__name__)

bp = Blueprint('api', __name__)

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
    trancript_ids = GeneRepository.retrieve_all_transcript_ids(gene_name)
    
    # check if there was any return value
    if len(trancript_ids) > 0:
        message = "Retrieved transcripts for gene '"+gene_name+"'"
    elif len(trancript_ids) == 0 and gene_name.upper() != gene_name:
        # retrieve the transcript ids for this capitalized form of this gene
        trancript_ids  = GeneRepository.retrieve_all_transcript_ids(gene_name.upper())
            
        # again check if there was any return value
        if len(trancript_ids) == 0:
            message = "Gene '"+str(gene_name)+"' was not present in the database, nor was '"+str(gene_name.upper())+"'"
        else:
            message = "Retrieved transcripts for gene '"+gene_name.upper()+"'"
    else:
        message = "No transcripts available for gene '"+gene_name+"'"
    
    return jsonify(trancript_ids=trancript_ids, message=message)

@bp.route('/gene/geneTolerance', methods=['GET'])
def get_default_tolerance():
    """This endpoint is a stub, to ensure deeper endpoints may be used"""
    pass

@bp.route('/gene/geneTolerance/<transcript_id>/', methods=['GET'])
def get_gene_tolerance_no_end(transcript_id):
    if 'slidingWindow' in request.args:
        sliding_window = float(request.args['slidingWindow'])
    else:
        sliding_window = 0.0
    
    if 'frequency' in request.args:
        frequency = float(request.args['frequency'])
    else:
        frequency = 0.0
    
    if 'startpos' in request.args:
        start_pos = int(request.args['startpos'])
    else:
        start_pos = None
        
    if 'endpos' in request.args:
        end_pos = int(request.args['endpos'])
        
        # type check end pos
        if end_pos <= 0:
            end_pos = None
    else:
        end_pos = None
    
    # Retrieve the gene from the database
    gene = GeneRepository.retrieve_gene(transcript_id)
    
    if not gene is None:
        # build the gene region
        gene_region = GeneRegion(gene, start_pos, end_pos)
        
        region_sliding_window = compute_tolerance_landscape(gene_region, sliding_window, frequency)
        
        return jsonify([{"geneName":gene_region.gene_name}, region_sliding_window])
    else:
        return jsonify(str())

@bp.route('/gene/domainsInGene', methods=['GET'])
def get_default_domains():
    """This endpoint is a stub, to ensure deeper endpoints may be used"""
    pass

@bp.route('/gene/domainsInGene/<transcript_id>', methods=['GET'])
def get_domains_for_transcript(transcript_id):
    # TODO: return as:
#     return jsonify(InterproRepository.get_pfam_domains_for_transcript(transcript_id))
    return jsonify([{"ID": "PF00001", "Name": "test", "start":30, "stop":50, "domID":123}])

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