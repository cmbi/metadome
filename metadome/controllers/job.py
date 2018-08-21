import os
import logging
import json

from lockfile import LockFile

from celery.result import AsyncResult
from flask import current_app as flask_app


_log = logging.getLogger(__name__)


def get_visualization_path(transcript_id):
    return os.path.join(_get_visualization_dir_path(transcript_id),
                        flask_app.config['PRE_BUILD_VISUALIZATION_FILE_NAME'])


def _get_visualization_dir_path(transcript_id):
    return os.path.join(flask_app.config['PRE_BUILD_VISUALIZATION_DIR'],
                        transcript_id)


def _get_visualization_task_path(transcript_id):
    return os.path.join(_get_visualization_dir_path(transcript_id),
                        falsk_app.config['PRE_BUILD_VISUALIZATION_TASK_FILE_NAME'])


def get_visualization_error_path(transcript_id):
    return os.path.join(_get_visualization_dir_path(transcript_id),
                        falsk_app.config['PRE_BUILD_VISUALIZATION_ERROR_FILE_NAME'])


def _get_lock_for(transcript_id):
    lock_dir_path = _get_visualization_dir_path(transcript_id)

    if not os.path.isdir(lock_dir_path):
        os.mkdir(lock_dir_path)

    return LockFile(lock_dir_path)


def _cleanup_visualisation_if_needed(transcript_id):
    visualization_path = get_visualization_path(transcript_id)
    task_path = _get_visualization_task_path(transcript_id)

    if os.path.isfile(visualization_path) and os.path.isfile(task_path):
        # Not needed anymore
        os.remove(task_path)


def create_visualization_job_if_needed(transcript_id):

    visualization_path = get_visualization_path(transcript_id)
    task_path = _get_visualization_task_path(transcript_id)

    with _get_lock_for(transcript_id):
        if os.path.isfile(visualization_path):
            _log.info("visualization file for transcript {} already exists"
                      .format(transcript_id))

        elif os.path.isfile(task_path):
            with open(task_path, 'r') as f:
                task_id = f.read()
                _log.info("visualization job for transcript {} is already running as task {}"
                          .format(transcript_id, task_id))

        else:
            from metadome.tasks import create_prebuild_visualization
            create_prebuild_visualization.delay(transcript_id)


def get_visualization_status(transcript_id):
    visualization_path = get_visualization_path(transcript_id)
    task_path = _get_visualization_task_path(transcript_id)

    with _get_lock_for(transcript_id):
        _cleanup_visualisation_if_needed(transcript_id)

        if os.path.isfile(visualization_path):
            return 'SUCCESS'
        elif os.path.isfile(task_path):
            with open(task_path, 'r') as f:
                task_id = f.read()
                result = AsyncResult(task_id)

                return result.status
        else:
            return 'PENDING'


def retrieve_error(transcript_id):
    error_path = get_visualization_error_path(transcript_id)

    with _get_lock_for(transcript_id):
        if os.path.isfile(error_path):
            with open(error_path, 'r') as f:
                return f.read()

        else:
            return 'unknown'


def retrieve_visualization(transcript_id):
    visualization_path = get_visualization_path(transcript_id)

    with _get_lock_for(transcript_id):
        _cleanup_visualisation_if_needed(transcript_id)

        if not os.path.isfile(visualization_path):
            raise FileNotFoundError("missing file: {}".format(visualization_path))

        with open(visualization_path, 'r') as f:
            visualization_content = json.load(f)

            return visualization_content
