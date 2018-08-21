from metadome.domain.repositories import GeneRepository
from metadome.domain.services.metadome import process_visualization_request
from metadome.domain.transcript import is_transcript_id

from flask import Blueprint, jsonify, render_template
from builtins import Exception

import traceback
import logging


from metadome.controllers.job import (create_visualization_job_if_needed,
                                      get_visualization_status,
                                      retrieve_visualization)


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
    
    transcript_results = []
    for t in trancripts:
        transcript_entry = {}
        transcript_entry['aa_length'] = t.sequence_length
        transcript_entry['gencode_id'] = t.gencode_transcription_id
        transcript_entry['has_protein_data'] = not t.protein_id is None
        transcript_results.append(transcript_entry)
    
    
    
    return jsonify(trancript_ids=transcript_results, message=message)

@bp.route('/submit_gene_analysis', methods=['GET'])
def submit_gene_analysis_job_stub():
    """This endpoint is a stub, to ensure deeper endpoints may be used"""
    pass

@bp.route('/submit_gene_analysis/<transcript_id>/', methods=['GET'])
def submit_gene_analysis_job_for_transcript(transcript_id):
    # create a celery job id
    _log.debug('submit_gene_analysis_job_for_transcript')
    job_id, job_name = process_visualization_request(transcript_id=transcript_id, rebuild=False)
        
    _log.debug('got job: '+str(job_id)+", "+str(job_name))
    
    return jsonify({'job_id': job_id,
                      'job_name': job_name,})


@bp.route('/submit_visualization/<transcript_id>/', methods=['GET'])
def submit_visualization_job_for_transcript(transcript_id):
    _log.debug("submitted {}".format(transcript_id))

    if is_transcript_id(transcript_id):
        create_visualization_job_if_needed(transcript_id)
        return jsonify({'transcript_id': transcript_id})
    else:
        return jsonify({'error': "not a valid transcript id"}), 400


@bp.route('/status', methods=['GET'])
def get_job_status_stub():
    """This endpoint is a stub, to ensure deeper endpoints may be used"""
    pass


@bp.route('/status/<transcript_id>/', methods=['GET'])
def get_visualization_status_for_transcript(transcript_id):
    status = get_visualization_status(transcript_id)

    return jsonify({'status': status})


@bp.route('/status/<job_name>/<job_id>/', methods=['GET'])
def get_job_status(job_name, job_id):
    from metadome.tasks import get_task
    task = get_task(job_name)
     
    result = task.AsyncResult(job_id)
    
    response = {'job_id': job_id,
                      'job_name': job_name,
                      'status': result.status}
    if result.failed():
        response.update({'message': result.traceback})
    
    return jsonify(response)
 
@bp.route('/result', methods=['GET'])
def get_job_result_stub():
    """This endpoint is a stub, to ensure deeper endpoints may be used"""
    pass
     

@bp.route('/result/<transcript_id>/', methods=['GET'])
def get_visualization_result_for_transcript(transcript_id):
    try:
        result = retrieve_visualization(transcript_id)
        return jsonify(result)
    except FileNotFoundError:
        return jsonify({'error': "file not found"}), 404


@bp.route('/error/<transcript_id>/', methods=['GET'])
def get_visualization_error_for_transcript(transcript_id):
    error = retrieve_error(transcript_id)
    return jsonify({'error': error})


@bp.route('/result/<job_name>/<job_id>/', methods=['GET'])
def get_job_result(job_name, job_id):
    from metadome.tasks import get_task
    task = get_task(job_name)
    
    result = task.AsyncResult(job_id).get()
    if len(result) <= 0:
        return jsonify({'error': 'empty result'}), 500
    
    if 'error' in result.keys():
        return jsonify(result), 500
 
    return jsonify(result)

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
