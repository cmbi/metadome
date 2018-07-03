import logging
import os

from flask import current_app as flask_app

_log = logging.getLogger(__name__)

def process_visualization_request(transcript_id, rebuild, job_name):    
    _log.debug('Received processing visualization request with transcript id = "'+str(transcript_id)+'" and rebuild = "'+str(rebuild)+'"')
    
    # obtain the strategy
    strategy = MetadomeStrategyFactory.create(transcript_id, rebuild, job_name)
    
    _log.debug("Using '{}'".format(strategy.__class__.__name__))
    celery_id, job_name = strategy()
    _log.info("Job has id '{}'".format(celery_id))
    
    # return task id and job name
    return celery_id, job_name

class MetadomeStrategyFactory(object):
    @classmethod
    def create(cls, transcript_id, rebuild, job_name):
        visualization_path = flask_app.config['PRE_BUILD_VISUALIZATION_DIR'] + transcript_id + '/' + flask_app.config['PRE_BUILD_VISUALIZATION_FILE_NAME']
        
        # check f this was a previous job
        if not job_name is None:
            # check if there need be a rebuild
            if rebuild:
                job_name = 'create'
                # return rebuild id
        
            # check for existence of the dir
            if os.path.exists(visualization_path):
                # the file exists, job is retrieving
                job_name = 'retrieve'
            else:
                # This is the first time this trancript id is queried
                # create the directory
                job_name = 'create'
            
        #TODO: remove the mocking
        job_name = 'retrieve'
        if job_name == 'create':
            return CreateVisualizationStrategy(job_name, transcript_id)
        elif job_name == 'retrieve':
            return RetrieveVisualizationStrategy(job_name, transcript_id)
        elif job_name == 'mock_it':
            return MockVisualizationStrategy(job_name)
        else:
            raise ValueError("Unexpected input type '{}'".format(transcript_id))

class CreateVisualizationStrategy(object):
    def __init__(self, job_name, transcript_id):
        self.job_name = job_name
        self.transcript_id = transcript_id

    def __call__(self):
        from metadome.tasks import get_task
        task = get_task('create')
        _log.debug("Calling task '{}'".format(task.__name__))
        
        result = task.delay(self.transcript_id)
        return result.id, self.job_name

class RetrieveVisualizationStrategy(object):
    def __init__(self, job_name, transcript_id):
        self.job_name = job_name
        self.transcript_id = transcript_id

    def __call__(self):
        from metadome.tasks import get_task
        task = get_task('retrieve')
        _log.debug("Calling task '{}'".format(task.__name__))
        
        result = task.delay(self.transcript_id)
        return result.id, self.job_name
    
class MockVisualizationStrategy(object):
    def __init__(self, job_name):
        self.job_name = job_name
        
    def __call__(self):
        from metadome.tasks import get_task
        task = get_task('mock_it')
        _log.debug("Calling task '{}'".format(task.__name__))

        result = task.delay()
        return result.id, self.job_name
