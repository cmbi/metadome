import logging
import os

from flask import current_app as flask_app
# from metadome import tasks

_log = logging.getLogger(__name__)


def process_visualization_request(transcript_id, rebuild):    
    _log.debug('Received processing visualization request with transcript id = "'+str(transcript_id)+'" and rebuild = "'+str(rebuild)+'"')
    
    # obtain the strategy
    strategy = MetadomeStrategyFactory.create(transcript_id, rebuild)

    
    _log.debug("Using '{}'".format(strategy.__class__.__name__))
    celery_id, job_name = strategy()
    _log.info("Job has id '{}'".format(celery_id))
#     result = task.delay(transcript_id)
#     _log.debug('For job "'+str(job_name)+'" got task "'+str(task.__name__)+'", with id: "'+str(result.id)+'"')
    
    # return task id
    return celery_id, job_name

class MetadomeStrategyFactory(object):
    @classmethod
    def create(cls, transcript_id, rebuild):
        visualization_dir = flask_app.config['PRE_BUILD_VISUALIZATION_DIR'] + transcript_id
        visualization_path = flask_app.config['PRE_BUILD_VISUALIZATION_DIR'] + transcript_id + '/' + flask_app.config['PRE_BUILD_VISUALIZATION_FILE_NAME']
        
        # check if there need be a rebuild
        if rebuild:
            pass
            # return rebuild id
    
        # check for existence of the dir
        if os.path.isdir(visualization_dir):
            # the dir exists
            
            # check file existence, otherwise wait
            
            # ...
            pass
        else:
            # This is the first time this trancript id is queried
            # create the directory
            
            # ...
            
            # start a building task
            job_name = 'create'
        job_name = 'mock_it'
    #     task = tasks.get_task(job_name)
#         task = tasks.get_task('mock_it')
        if job_name == 'pdb_id':
            return CreateVisualizationStrategy(transcript_id)
        elif job_name == 'mock_it':
            return MockVisualizationStrategy(job_name)
        else:
            raise ValueError("Unexpected input type '{}'".format(transcript_id))

class CreateVisualizationStrategy(object):
    def __init__(self, output_format, pdb_id):
        self.output_format = output_format
        self.pdb_id = pdb_id

    def __call__(self):
        from metadome.tasks import get_task
        task = get_task('pdb_id', self.output_format)
        _log.debug("Calling task '{}'".format(task.__name__))

        if 'hssp' in self.output_format:
            result = task.delay(self.pdb_id, self.output_format)
        else:
            result = task.delay(self.pdb_id)
        return result.id
    
class MockVisualizationStrategy(object):
    def __init__(self, job_name):
        self.job_name = job_name
        
    def __call__(self):
        from metadome.tasks import get_task
        task = get_task('mock_it')
        _log.debug("Calling task '{}'".format(task.__name__))

        result = task.delay()
        return result.id, self.job_name


#     from metadome.tasks import get_task
#     task = get_task('pdb_id', self.output_format)
#     _log.debug("Calling task '{}'".format(task.__name__))
# 
#     if 'hssp' in self.output_format:
#         result = task.delay(self.pdb_id, self.output_format)
#     else:
#         result = task.delay(self.pdb_id)
#     return result.id
#     
#     # Save the PDB file if necessary
#     
#     file_path = None
#     if input_type == 'pdb_file':
#         assert 'file_' in uploaded_files
#         pdb_file = uploaded_files['file_']
#         assert hasattr(pdb_file, 'filename')
# 
#         filename = secure_filename(pdb_file.filename)
#         file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         pdb_file.save(file_path)
#         _log.debug("User uploaded '{}'. File saved to {}".format(
#             pdb_file.filename, file_path))
# 
#     # Create and run the job via the strategy for the given input and
#     # output types.
#     _log.debug("Input type '{}' and output type '{}'".format(
#         input_type, output_type))
# 
#     strategy = XsspStrategyFactory.create(input_type, output_type, pdb_id,
#                                           file_path, sequence)
#     _log.debug("Using '{}'".format(strategy.__class__.__name__))
#     celery_id = strategy()
#     _log.info("Job has id '{}'".format(celery_id))
# 
#     return celery_id
