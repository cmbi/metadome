from metadome.domain.repositories import GeneRepository
from metadome.domain.services.metadome import process_visualization_request

from flask import Blueprint, jsonify, render_template
from builtins import Exception

import traceback
import logging

_log = logging.getLogger(__name__)

bp = Blueprint('api', __name__)

##########################################
#########    Route end points    #########
##########################################

@bp.route('/get_transcripts', methods=['GET'])
def get_default_transcript_ids():
    """This endpoint is a stub, to ensure deeper endpoints may be used"""
    pass

@bp.route('/get_transcripts/<string:gene_name>', methods=['GET'])
def get_transcript_ids_for_gene(gene_name):
    _log.debug('get_transcript_ids_for_gene')
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

@bp.route('/submit_gene_analysis', methods=['GET'])
def submit_gene_analysis_job_stub():
    """This endpoint is a stub, to ensure deeper endpoints may be used"""
    pass

@bp.route('/submit_gene_analysis/<transcript_id>/', methods=['GET'])
def submit_gene_analysis_job_for_transcript(transcript_id):
    # create a celery job id
    _log.debug('submit_gene_analysis_job_for_transcript')
    job_id, job_name = process_visualization_request(transcript_id, False)
        
    _log.debug('got job: '+str(job_id)+", "+str(job_name))
    
    return jsonify({'job_id': job_id,
                      'job_name': job_name,})

@bp.route('/status', methods=['GET'])
def get_job_status_stub():
    """This endpoint is a stub, to ensure deeper endpoints may be used"""
    pass

@bp.route('/status/<job_name>/<job_id>/', methods=['GET'])
def get_job_status(job_name, job_id):
    from metadome.tasks import get_task
    task = get_task(job_name)
     
    result = task.AsyncResult(job_id).get()
    
    if len(result) <= 0:
        return jsonify({'error': 'empty result'}), 500
     
    return jsonify({'job_id': job_id,
                      'job_name': job_name,
                      'status': result.status})
 
@bp.route('/result', methods=['GET'])
def get_job_result_stub():
    """This endpoint is a stub, to ensure deeper endpoints may be used"""
    pass
     
@bp.route('/result/<job_name>/<job_id>/', methods=['GET'])
def get_job_result(job_name, job_id):
    from metadome.tasks import get_task
    task = get_task(job_name)
    
    result = task.AsyncResult(job_id).get()
    if len(result) <= 0:
        return jsonify({'error': 'empty result'}), 500
 
    return result

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