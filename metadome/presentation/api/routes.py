from metadome.domain.repositories import GeneRepository
from metadome.domain.services.prebuilding_visualization import prebuild_visualization
from flask import Blueprint, jsonify, render_template
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
    return prebuild_visualization(transcript_id)

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